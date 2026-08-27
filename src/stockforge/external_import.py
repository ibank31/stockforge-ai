"""Safe ingestion of externally rendered raster images.

External rendering is intentionally treated as an import operation, not as a
provider generation shortcut. The module copies the source into the project,
creates a succeeded ``image.import_external`` execution, records provenance,
and performs CPU-only technical checks. It never calls a remote provider or a
finalizer and never decides KEEP/REJECT.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from .adobe_gate import inspect_image
from .adobe_png_gate import inspect_transparent_png
from .artifact import Artifact, sha256_file
from .execution_record import GenerationExecutionRecord
from .format_router import route_asset_spec
from .asset_spec import AssetSpec
from .job_database import JobDatabase
from .provenance import ProvenanceRecord


class ExternalImportError(ValueError):
    """Raised when an external image cannot be safely imported."""


@dataclass(frozen=True, slots=True)
class ExternalImageFacts:
    detected_format: str
    width: int
    height: int
    mode: str
    has_alpha: bool
    alpha_extrema: tuple[int, int] | None
    transparent_fraction: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "detected_format": self.detected_format,
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "has_alpha": self.has_alpha,
            "alpha_extrema": list(self.alpha_extrema) if self.alpha_extrema else None,
            "transparent_fraction": self.transparent_fraction,
        }


@dataclass(frozen=True, slots=True)
class ExternalImportResult:
    execution: GenerationExecutionRecord
    artifact: Artifact
    report_path: Path
    report: dict[str, Any]


_PRESETS: dict[str, dict[str, Any]] = {
    "png-v2-002": {
        "title": "Folding Produce Crate with Divider",
        "buyer_job": "Drop-in utility object for reusable-packaging explainers, grocery logistics layouts, warehouse diagrams, and circular-commerce presentations.",
        "micro_niche": "reusable produce crate and modular retail logistics",
        "asset_family": "product_illustration",
        "product_kind": "transparent_cutout",
        "delivery_format": "png",
        "layout_mode": "square",
        "background_policy": "transparent",
        "isolation_policy": "isolated",
        "originality_levers": ["visible removable divider", "open-sided reusable crate geometry", "three-quarter utility-object framing"],
        "commercial_use_cases": ["packaging mockup", "grocery delivery diagram", "supply-chain explainer"],
    },
    "jpeg-external-e-cargo-battery-swap": {
        "title": "E-Cargo Bike Battery-Swap Micro-Depot",
        "buyer_job": "Hero scene for last-mile delivery, urban logistics, fleet electrification, and clean-transport explainers with useful copy space.",
        "micro_niche": "urban e-cargo delivery and battery-swap logistics",
        "asset_family": "technical_component_illustration",
        "product_kind": "raster_illustration",
        "delivery_format": "jpeg",
        "layout_mode": "hero_landscape",
        "background_policy": "scene",
        "isolation_policy": "scene",
        "originality_levers": ["battery-swap micro-depot as the narrative anchor", "e-cargo bike shown in a credible service context", "unbranded last-mile infrastructure"],
        "commercial_use_cases": ["mobility campaign", "urban logistics presentation", "fleet electrification editorial"],
    },
}


def _safe_component(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExternalImportError(f"{field} must be a non-empty string.")
    value = value.strip()
    if value in {".", ".."} or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,98}", value):
        raise ExternalImportError(f"{field} must be a simple safe identifier.")
    return value


def inspect_external_image(source: Path) -> ExternalImageFacts:
    """Decode one source safely and collect non-semantic pixel facts."""
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ExternalImportError(f"External source does not exist: {source}")
    try:
        with Image.open(source) as image:
            image_format = image.format or "UNKNOWN"
            width, height = image.size
            mode = image.mode
            bands = image.getbands()
            alpha_extrema: tuple[int, int] | None = None
            transparent_fraction: float | None = None
            if "A" in bands:
                alpha = image.getchannel("A")
                alpha_extrema = tuple(int(v) for v in alpha.getextrema())
                histogram = alpha.histogram()
                transparent_fraction = sum(histogram[:255]) / (width * height)
            image.verify()
        with Image.open(source) as image:
            image.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ExternalImportError(f"Source is not a safely decodable image: {exc}") from exc
    return ExternalImageFacts(
        detected_format=image_format,
        width=width,
        height=height,
        mode=mode,
        has_alpha="A" in bands,
        alpha_extrema=alpha_extrema,
        transparent_fraction=transparent_fraction,
    )


def _portfolio_context(candidate_id: str, values: dict[str, Any], source_facts: ExternalImageFacts) -> dict[str, Any]:
    delivery_format = str(values["delivery_format"]).lower()
    product_kind = str(values["product_kind"])
    layout_mode = str(values.get("layout_mode", "square"))
    if delivery_format not in {"jpeg", "png"}:
        raise ExternalImportError("delivery_format must be jpeg or png.")
    asset_spec = AssetSpec(
        asset_id=f"external-{candidate_id}",
        market_opportunity_id=f"external-import:{candidate_id}",
        buyer_segment="commercial stock buyers",
        buyer_job=str(values["buyer_job"]),
        channel="microstock",
        asset_family=str(values["asset_family"]),
        asset_type="illustration",
        micro_niche=str(values["micro_niche"]),
        subject=str(values["title"]),
        visual_language="externally rendered polished commercial raster",
        medium="digital raster illustration",
        product_kind=product_kind,
        delivery_format=delivery_format,
        layout_mode=layout_mode,
        composition="preserve the complete imported composition; no silent crop or resize during import",
        negative_space="retain the source composition for human review; any final crop or normalization requires an explicit later policy",
        background_policy=str(values.get("background_policy", "transparent" if delivery_format == "png" else "scene")),
        isolation_policy=str(values.get("isolation_policy", "isolated" if delivery_format == "png" else "scene")),
        text_policy="none",
        branding_policy="no_branding",
        originality_levers=tuple(values["originality_levers"]),
        variation_policy="retain only commercially distinct variants; source provenance remains immutable",
        commercial_use_cases=tuple(values.get("commercial_use_cases", ())),
        quality_gates=("safe decoding", "format route fit", "no accidental text or branding", "human visual review", "final output technical gate"),
        model_preferences=("resolution>=1024", "renderer=external"),
        metadata_hints=("external-renderer provenance required", "do not claim marketplace approval"),
        extra_constraints=("No GPU or finalizer call during import", "No silent crop, resize, alpha extraction, or format mutation"),
        tags=("external-import", candidate_id),
        identity_signature="external source preserved byte-for-byte after copy",
        identity_lighting="as rendered by external provider",
        identity_framing=f"source framing {source_facts.width}x{source_facts.height}; final framing is not silently changed",
        identity_context=str(values["micro_niche"]),
        identity_distinctness=tuple(values["originality_levers"]),
        identity_prohibited_shorthand=("generic stock symbol", "brand-like label", "unreadable generated text"),
    )
    route = route_asset_spec(asset_spec)
    return {
        "schema_version": 2,
        "batch_id": f"external-import-{candidate_id}",
        "plan_file": None,
        "brief_id": candidate_id,
        "lane_key": f"external-{delivery_format}",
        "lane_name": "External renderer import",
        "tier": "experimental",
        "evidence_confidence": "unverified",
        "buyer_job": asset_spec.buyer_job,
        "asset_spec": asset_spec.to_dict(),
        "format_route": route.to_dict(),
        "metadata": {"title": values["title"], "source": "external_renderer", "keywords": []},
        "reviewer_checklist": ["Check context and visual quality at 100%", "Check accidental text, logo, and IP-like details", "Check format-specific readiness", "Decide KEEP, REJECT, or REVIEW manually"],
        "human_review_required": True,
        "source_dimensions": {"width": source_facts.width, "height": source_facts.height},
    }


def import_external_image(
    *,
    database: JobDatabase,
    project_id: str,
    project_root: Path,
    source: Path,
    candidate_id: str,
    provider_label: str,
    model_label: str | None = None,
    original_filename: str | None = None,
    prompt: str | None = None,
    title: str | None = None,
    buyer_job: str | None = None,
    micro_niche: str | None = None,
    delivery_format: str | None = None,
) -> ExternalImportResult:
    candidate_id = _safe_component(candidate_id, "candidate_id")
    provider_label = _safe_component(provider_label, "provider_label")
    source = Path(source).expanduser().resolve()
    facts = inspect_external_image(source)
    preset = _PRESETS.get(candidate_id, {})
    values = dict(preset)
    if title:
        values["title"] = title
    if buyer_job:
        values["buyer_job"] = buyer_job
    if micro_niche:
        values["micro_niche"] = micro_niche
    if delivery_format:
        values["delivery_format"] = delivery_format.lower()
    for field in ("title", "buyer_job", "micro_niche", "asset_family", "product_kind", "delivery_format", "originality_levers"):
        if field not in values:
            raise ExternalImportError(f"Import preset/context is missing {field}.")
    context = _portfolio_context(candidate_id, values, facts)
    project_root = Path(project_root).expanduser().resolve()
    if not project_root.is_dir():
        raise ExternalImportError(f"Project root does not exist: {project_root}")
    destination_dir = (project_root / "artifacts" / "external").resolve()
    destination_dir.relative_to(project_root)
    destination_dir.mkdir(parents=True, exist_ok=True)
    digest = sha256_file(source)
    suffix = source.suffix.lower() if source.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} else ".bin"
    destination = destination_dir / f"{candidate_id}-{digest[:12]}{suffix}"
    if not destination.exists():
        shutil.copy2(source, destination)
    copied_digest = sha256_file(destination)
    if copied_digest != digest:
        destination.unlink(missing_ok=True)
        raise ExternalImportError("Copied source hash does not match original; import aborted.")
    artifact = Artifact.from_file(project_id=project_id, relative_path=destination.relative_to(project_root).as_posix(), root=project_root, kind="generated-image")
    artifact = Artifact(
        id=artifact.id,
        project_id=artifact.project_id,
        kind=artifact.kind,
        relative_path=artifact.relative_path,
        mime_type=artifact.mime_type,
        size_bytes=artifact.size_bytes,
        sha256=artifact.sha256,
        metadata={
            "source": "external_renderer",
            "provider_label": provider_label,
            "original_filename": original_filename or source.name,
            "source_sha256": digest,
            "detected_format": facts.detected_format,
            "delivery_format": values["delivery_format"],
            "candidate_id": candidate_id,
        },
    )
    execution = GenerationExecutionRecord.create(
        project_id=project_id,
        prompt=prompt,
        operation="image.import_external",
        state="completed",
        provider_id=provider_label,
        provider_job_id=None,
        pipeline_id="external-import",
        pipeline_version=1,
        step_id="import",
        plugin_id="stockforge.external_import",
        plugin_version="1",
        model_id=model_label or "external-renderer",
        model_version=None,
        workflow_hash="external-import-v1",
        parameters={
            "portfolio": context,
            "external_import": {
                "source_filename": original_filename or source.name,
                "source_sha256": digest,
                "detected_format": facts.detected_format,
                "provider_label": provider_label,
                "model_label": model_label,
                "prompt_supplied": prompt is not None,
                "import_policy": "copy-and-audit-no-mutation",
            },
        },
    )
    (actual_artifact,), execution = database.create_artifacts_and_execution((artifact,), execution)
    execution = replace(execution, state="succeeded", artifact_ids=(actual_artifact.id,))
    database.update_execution(execution)
    provenance = ProvenanceRecord.create(
        artifact_id=actual_artifact.id,
        project_id=project_id,
        operation="image.import_external",
        execution_id=execution.id,
        pipeline_id="external-import",
        pipeline_version=1,
        step_id="import",
        plugin_id="stockforge.external_import",
        plugin_version="1",
        model_id=model_label or "external-renderer",
        workflow_hash="external-import-v1",
        prompt_hash=execution.prompt_hash,
        parameters={"delivery_format": values["delivery_format"], "candidate_id": candidate_id},
        metadata={"provider_label": provider_label, "original_filename": original_filename or source.name, "source_sha256": digest},
    )
    database.create_provenance(provenance)
    actual_path = (project_root / actual_artifact.relative_path).resolve()
    jpeg_report = inspect_image(actual_path).to_dict()
    png_report = inspect_transparent_png(actual_path).to_dict()
    if values["delivery_format"] == "jpeg":
        technical_report = {"intended_delivery_format": "jpeg", "source_encoding": facts.detected_format, "gate": jpeg_report, "note": "The source encoding is preserved at import. A later JPEG finalizer/export must create the actual JPEG delivery file."}
    else:
        technical_report = {"intended_delivery_format": "png", "source_encoding": facts.detected_format, "gate": png_report, "note": "PNG true-alpha is checked from the imported source; no background removal or alpha fabrication was performed."}
    report = {
        "schema_version": 1,
        "kind": "stockforge.external_import_report",
        "status": "review_ready",
        "project_id": project_id,
        "candidate_id": candidate_id,
        "execution_id": execution.id,
        "artifact_id": actual_artifact.id,
        "artifact_relative_path": actual_artifact.relative_path,
        "artifact_sha256": actual_artifact.sha256,
        "provider_label": provider_label,
        "original_filename": original_filename or source.name,
        "source_facts": facts.to_dict(),
        "technical_report": technical_report,
        "portfolio": context,
        "human_review_required": True,
        "actions_performed": ["copied source into project artifacts", "computed SHA-256", "registered artifact and succeeded import execution", "recorded external provenance", "ran CPU-only technical gates"],
        "actions_not_performed": ["no ZeroGPU call", "no Kaggle call", "no alpha extraction", "no resize or crop", "no KEEP/REJECT decision", "no Adobe package or submission"],
    }
    report_dir = project_root / "reports" / "external-imports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{execution.id}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return ExternalImportResult(execution=execution, artifact=actual_artifact, report_path=report_path, report=report)
