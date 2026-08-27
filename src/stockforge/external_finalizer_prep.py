"""Prepare imported external assets for the protected format-specific finalizers.

This module prepares requests only. It never submits Kaggle jobs. JPEG scenes
use the existing 4x master request contract. PNG cutouts receive an explicit,
lossless-content-preserving square canvas normalization because the active PNG
worker accepts exactly 1024x1024 input. The original imported artifact remains
immutable and is never overwritten.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import uuid4

from PIL import Image, ImageCms, ImageOps

from .artifact import Artifact, sha256_file
from .execution_record import GenerationExecutionRecord
from .kaggle_png_finalizer import PNG_SOURCE_SIZE, prepare_request as prepare_png_request
from .job_database import JobDatabase
from .master_finalizer import MasterTarget
from .provenance import ArtifactLineage, ProvenanceRecord


class ExternalFinalizerPreparationError(ValueError):
    """Raised when an imported asset cannot meet its protected worker contract."""


def _inside(path: Path, root: Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ExternalFinalizerPreparationError(f"{label} must remain inside the project workspace") from exc
    return resolved


def _srgb_profile() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def _source_for_execution(database: JobDatabase, project_id: str, project_root: Path, execution_id: str, artifact_id: str | None) -> tuple[GenerationExecutionRecord, Artifact, Path, dict[str, Any]]:
    execution = database.get_execution(execution_id)
    if execution is None or execution.project_id != project_id:
        raise ExternalFinalizerPreparationError("Execution does not belong to the requested project.")
    if execution.state != "succeeded" or not execution.artifact_ids:
        raise ExternalFinalizerPreparationError("Only a succeeded execution with an artifact can be prepared for finalization.")
    selected_id = artifact_id or execution.artifact_ids[0]
    if selected_id not in execution.artifact_ids:
        raise ExternalFinalizerPreparationError("Selected artifact is not an output of the supplied execution.")
    artifact = database.get_artifact(selected_id)
    if artifact is None or artifact.project_id != project_id or artifact.kind != "generated-image":
        raise ExternalFinalizerPreparationError("Selected artifact is not an eligible generated image.")
    source = _inside(project_root / artifact.relative_path, project_root, "Finalizer source")
    if not source.is_file():
        raise ExternalFinalizerPreparationError("Finalizer source is missing from the project workspace.")
    portfolio = execution.parameters.get("portfolio")
    if not isinstance(portfolio, dict):
        raise ExternalFinalizerPreparationError("Execution has no immutable portfolio context.")
    asset_spec = portfolio.get("asset_spec")
    if not isinstance(asset_spec, dict):
        raise ExternalFinalizerPreparationError("Portfolio context has no asset specification.")
    return execution, artifact, source, portfolio


def _jpeg_request(*, project_id: str, project_root: Path, execution: GenerationExecutionRecord, artifact: Artifact, source: Path, portfolio: dict[str, Any], minimum_megapixels: float, scale: int) -> tuple[Path, dict[str, Any], Artifact | None, GenerationExecutionRecord]:
    if scale != 4:
        raise ExternalFinalizerPreparationError("The protected JPEG finalizer supports only scale 4.")
    target = MasterTarget(minimum_megapixels=minimum_megapixels, scale=scale)
    try:
        with Image.open(source) as image:
            image.load()
            width, height = image.size
            detected_format = image.format or "unknown"
    except (OSError, ValueError) as exc:
        raise ExternalFinalizerPreparationError(f"JPEG finalizer source cannot be decoded: {exc}") from exc
    expected_width, expected_height = width * target.scale, height * target.scale
    expected_megapixels = (expected_width * expected_height) / 1_000_000
    if expected_megapixels < target.minimum_megapixels:
        raise ExternalFinalizerPreparationError(f"Requested scale produces {expected_megapixels:.2f} MP, below target {target.minimum_megapixels:.2f} MP.")
    if expected_megapixels > 100:
        raise ExternalFinalizerPreparationError(f"Requested scale produces {expected_megapixels:.2f} MP, above 100 MP.")
    request_id = f"master-{artifact.id}-{uuid4().hex[:8]}"
    payload = {
        "schema_version": 1,
        "kind": "stockforge.master_finalizer_request",
        "request_id": request_id,
        "status": "prepared_no_gpu",
        "project_id": project_id,
        "source": {
            "artifact_id": artifact.id,
            "execution_id": execution.id,
            "relative_path": artifact.relative_path,
            "sha256": sha256_file(source),
            "width": width,
            "height": height,
            "format": detected_format,
        },
        "target": {
            "mode": "ai_upscale",
            "scale": target.scale,
            "minimum_megapixels": target.minimum_megapixels,
            "expected_width": expected_width,
            "expected_height": expected_height,
            "expected_megapixels": round(expected_megapixels, 4),
            "format": "jpeg",
            "color_space": "sRGB",
        },
        "destination": f"masters/{artifact.id}-master.jpg",
        "portfolio": portfolio,
        "human_keep_attested": True,
        "human_review_required": True,
        "provider_options": ["kaggle-realesrgan", "future-burst-finalizer"],
        "notice": "Prepared without GPU. Submission remains a separate explicit action; final output requires technical and human visual review.",
    }
    request_dir = project_root / "master-finalizer-requests"
    request_dir.mkdir(parents=True, exist_ok=True)
    request_path = request_dir / f"{request_id}.json"
    request_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return request_path, payload, None, execution


def _normalize_png_source(*, database: JobDatabase, project_id: str, project_root: Path, execution: GenerationExecutionRecord, artifact: Artifact, source: Path, portfolio: dict[str, Any]) -> tuple[Path, Artifact, GenerationExecutionRecord, dict[str, Any]]:
    try:
        with Image.open(source) as opened:
            opened.load()
            image = ImageOps.exif_transpose(opened).convert("RGBA")
    except (OSError, ValueError) as exc:
        raise ExternalFinalizerPreparationError(f"PNG source cannot be decoded for worker normalization: {exc}") from exc
    if image.size[0] <= 0 or image.size[1] <= 0:
        raise ExternalFinalizerPreparationError("PNG source has invalid dimensions.")
    # Preserve the complete source with a transparent 1024 square canvas. This
    # is fit/letterbox, not a crop: no source pixels are discarded.
    canvas_size = PNG_SOURCE_SIZE
    margin = 32
    available = canvas_size[0] - 2 * margin
    scale = min(available / image.width, available / image.height)
    resized = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    position = ((canvas_size[0] - resized.width) // 2, (canvas_size[1] - resized.height) // 2)
    canvas.alpha_composite(resized, dest=position)
    # The active BiRefNet worker deliberately reads RGB and estimates alpha; it
    # ignores any input alpha channel. Feed it the expected white-backed RGB
    # image while retaining the original RGBA import and its lineage unchanged.
    worker_canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    worker_canvas.alpha_composite(canvas)
    worker_input = worker_canvas.convert("RGB")
    destination_dir = project_root / "artifacts" / "external-prepared"
    destination_dir.mkdir(parents=True, exist_ok=True)
    temporary = destination_dir / f"{artifact.id}-square-1024.tmp.png"
    worker_input.save(temporary, format="PNG", optimize=True, compress_level=9, icc_profile=_srgb_profile())
    digest = sha256_file(temporary)
    destination = destination_dir / f"{artifact.id}-square-1024-{digest[:12]}.png"
    if destination.exists():
        temporary.unlink(missing_ok=True)
    else:
        temporary.replace(destination)
    derived = Artifact.from_file(project_id=project_id, relative_path=destination.relative_to(project_root).as_posix(), root=project_root, kind="generated-image")
    derived = replace(derived, metadata={
        "source": "stockforge_external_finalizer_preparation",
        "parent_artifact_id": artifact.id,
        "parent_sha256": artifact.sha256,
        "preparation_policy": "fit-entire-source-to-1024-square-transparent-canvas",
        "crop_performed": False,
        "resize_performed": True,
        "alpha_mutation": "source_alpha_composited_to_white_for_worker",
        "worker_input_mode": "RGB",
        "worker_input_background": "white",
        "worker_contract": "kaggle-birefnet-alpha requires 1024x1024 RGB-capable source and extracts alpha itself",
    })
    derived_execution = GenerationExecutionRecord.create(
        project_id=project_id,
        operation="image.prepare_external_for_finalizer",
        state="completed",
        provider_id="stockforge-local",
        pipeline_id="external-finalizer-preparation",
        pipeline_version=1,
        step_id="png-square-fit",
        plugin_id="stockforge.external_finalizer_prep",
        plugin_version="1",
        model_id="deterministic-pillow",
        model_version=None,
        workflow_hash="external-finalizer-prep-v1",
        input_artifact_ids=(artifact.id,),
        parameters={
            "portfolio": portfolio,
            "preparation": {"target_size": list(PNG_SOURCE_SIZE), "crop": False, "source_artifact_id": artifact.id},
        },
    )
    (actual_derived,), derived_execution = database.create_artifacts_and_execution((derived,), derived_execution)
    derived_execution = replace(derived_execution, state="succeeded", artifact_ids=(actual_derived.id,))
    database.update_execution(derived_execution)
    if not any(item.parent_artifact_id == artifact.id and item.relation == "transformed" for item in database.list_lineage(artifact_id=actual_derived.id)):
        database.create_lineage(ArtifactLineage.create(actual_derived.id, artifact.id, project_id, relation="transformed", execution_id=derived_execution.id))
    database.create_provenance(ProvenanceRecord.create(
        artifact_id=actual_derived.id,
        project_id=project_id,
        operation="image.prepare_external_for_finalizer",
        execution_id=derived_execution.id,
        pipeline_id="external-finalizer-preparation",
        pipeline_version=1,
        step_id="png-square-fit",
        plugin_id="stockforge.external_finalizer_prep",
        plugin_version="1",
        model_id="deterministic-pillow",
        workflow_hash="external-finalizer-prep-v1",
        input_artifact_ids=(artifact.id,),
        parameters={"target_size": list(PNG_SOURCE_SIZE), "crop": False},
        metadata={"parent_sha256": artifact.sha256, "derived_sha256": actual_derived.sha256},
    ))
    report = {
        "format": "PNG",
        "width": PNG_SOURCE_SIZE[0],
        "height": PNG_SOURCE_SIZE[1],
        "color_mode": "RGB",
        "background": "white",
        "true_alpha_in_worker_input": False,
        "worker_behavior": "BiRefNet receives RGB and produces the final alpha mask",
        "crop": False,
        "fit_entire_source": True,
    }
    return project_root / actual_derived.relative_path, actual_derived, derived_execution, report


def prepare_external_finalizer(*, database: JobDatabase, project_id: str, project_root: Path, execution_id: str, artifact_id: str | None = None, minimum_megapixels: float = 6.0, scale: int = 4) -> dict[str, Any]:
    """Prepare the correct protected request for one explicitly kept import."""
    root = Path(project_root).expanduser().resolve()
    execution, artifact, source, portfolio = _source_for_execution(database, project_id, root, execution_id, artifact_id)
    asset_spec = portfolio["asset_spec"]
    delivery_format = str(asset_spec.get("delivery_format", "")).lower()
    if delivery_format == "jpeg":
        request_path, payload, prepared_artifact, prepared_execution = _jpeg_request(
            project_id=project_id, project_root=root, execution=execution, artifact=artifact, source=source, portfolio=portfolio, minimum_megapixels=minimum_megapixels, scale=scale
        )
        preparation_report = {"mode": "jpeg_direct_source", "source_format_preserved": True}
        result = {"status": "prepared_no_gpu", "delivery_format": "jpeg", "request_path": str(request_path), "request": payload, "source_execution_id": execution.id, "source_artifact_id": artifact.id, "prepared_artifact_id": None, "preparation": preparation_report}
    elif delivery_format == "png":
        prepared_path, prepared_artifact, prepared_execution, png_report = _normalize_png_source(database=database, project_id=project_id, project_root=root, execution=execution, artifact=artifact, source=source, portfolio=portfolio)
        request_path, payload = prepare_png_request(source=prepared_path, project_root=root, project_id=project_id)
        payload["source"]["artifact_id"] = prepared_artifact.id
        payload["source"]["execution_id"] = prepared_execution.id
        payload["portfolio"] = portfolio
        payload["human_keep_attested"] = True
        payload["preparation"] = {"parent_artifact_id": artifact.id, "derived_artifact_id": prepared_artifact.id, "crop": False, "fit_entire_source": True}
        request_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        result = {"status": "prepared_no_gpu", "delivery_format": "png", "request_path": str(request_path), "request": payload, "source_execution_id": execution.id, "source_artifact_id": artifact.id, "prepared_artifact_id": prepared_artifact.id, "prepared_execution_id": prepared_execution.id, "preparation": {"mode": "fit_entire_source_to_1024_square", "crop": False, "technical_report": png_report}}
    else:
        raise ExternalFinalizerPreparationError(f"Unsupported portfolio delivery format: {delivery_format!r}")
    report_dir = root / "reports" / "external-finalizer-prep"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{execution.id}-{delivery_format}.json"
    result["report_path"] = str(report_path)
    result["human_keep_attested"] = True
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return result
