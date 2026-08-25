"""Persist one locally built native SVG asset with explicit no-GPU provenance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .artifact import Artifact
from .asset_spec import AssetSpec
from .database import Database
from .execution_record import GenerationExecutionRecord
from .format_router import require_production_route
from .native_vector import NativeVectorReport, build_svg_for_preset
from .provenance import ProvenanceRecord


class LocalVectorBuildError(RuntimeError):
    """Raised when a local native-vector asset cannot be persisted safely."""


@dataclass(frozen=True, slots=True)
class LocalVectorBuildResult:
    execution_id: str
    artifact_id: str
    path: Path
    report: NativeVectorReport

    def to_dict(self) -> dict[str, object]:
        return {
            "execution_id": self.execution_id,
            "artifact_id": self.artifact_id,
            "path": str(self.path),
            "report": self.report.to_dict(),
            "remote_gpu_called": False,
            "status": "review_ready",
        }


def build_local_native_vector(
    *,
    database: Database,
    project_id: str,
    project_root: Path,
    spec: AssetSpec,
    portfolio_context: dict[str, object] | None = None,
) -> LocalVectorBuildResult:
    """Build a native SVG product and persist it as a successful local execution."""
    route = require_production_route(spec)
    if route.execution_mode != "local_native_vector_build":
        raise LocalVectorBuildError("Asset specification is not routed to the local native-vector builder.")
    root = Path(project_root).resolve()
    destination = root / "vectors" / f"{spec.asset_id}.svg"
    tags = tuple(str(item).casefold() for item in spec.tags)
    if any("pattern" in item for item in tags):
        preset = "geometric_pattern"
    elif any("document-lifecycle-diagram-kit" in item or "document_lifecycle_diagram_kit" in item for item in tags):
        preset = "document_lifecycle_diagram_kit"
    elif any("document-review-delivery" in item or "document_review_delivery" in item for item in tags):
        preset = "document_review_delivery_micro_set"
    elif any("file-flow-micro-set" in item or "icon_set" in item for item in tags):
        preset = "file_flow_micro_set"
    elif any("folder" in item and "upload" in item for item in tags):
        preset = "folder_upload"
    elif any("technical" in item or "badge" in item for item in tags):
        preset = "technical_badge"
    else:
        preset = "modular_ribbon"
    report = build_svg_for_preset(spec, destination, preset=preset)
    if not report.ready:
        raise LocalVectorBuildError("Native vector did not pass its technical gate.")
    artifact = Artifact.from_file(
        project_id=project_id,
        relative_path=destination.relative_to(root).as_posix(),
        root=root,
        kind="native-vector",
    )
    parameters: dict[str, object] = {
        "asset_spec": spec.to_dict(),
        "format_route": route.to_dict(),
        "local_no_gpu": True,
    }
    if portfolio_context is not None:
        parameters["portfolio"] = portfolio_context
    execution = GenerationExecutionRecord.create(
        project_id,
        prompt=spec.subject,
        operation="vector.build_native",
        state="succeeded",
        provider_id="local-native-vector",
        pipeline_id="stockforge-native-vector",
        pipeline_version=1,
        plugin_id="native_vector",
        plugin_version="1",
        model_id="deterministic-svg",
        model_version="1",
        artifact_ids=(artifact.id,),
        parameters=parameters,
    )
    try:
        artifacts, execution = database.create_artifacts_and_execution((artifact,), execution)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise LocalVectorBuildError(f"Could not persist native vector artifact: {exc}") from exc
    registered = artifacts[0]
    provenance = ProvenanceRecord.create(
        registered.id,
        project_id,
        "vector.build_native",
        execution_id=execution.id,
        pipeline_id="stockforge-native-vector",
        pipeline_version=1,
        plugin_id="native_vector",
        plugin_version="1",
        model_id="deterministic-svg",
        model_version="1",
        parameters={"format_route": route.to_dict(), "remote_gpu_called": False},
        metadata={"technical_report": report.to_dict()},
    )
    database.create_provenance(provenance)
    return LocalVectorBuildResult(
        execution_id=execution.id,
        artifact_id=registered.id,
        path=destination,
        report=report,
    )
