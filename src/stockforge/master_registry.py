"""Persist a finalized StockForge master as an immutable derived artifact."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from .artifact import Artifact
from .database import Database
from .execution_record import GenerationExecutionRecord
from .master_finalizer import MasterFinalizationReport
from .provenance import ArtifactLineage, ProvenanceRecord


class MasterRegistryError(RuntimeError):
    """Raised when a finalized master cannot be attached safely to its project."""


def register_master_candidate(
    *,
    database: Database,
    project_id: str,
    project_root: Path,
    source_artifact: Artifact,
    source_execution: GenerationExecutionRecord,
    report: MasterFinalizationReport,
    reviewed_metadata: dict[str, Any] | None = None,
) -> tuple[Artifact, GenerationExecutionRecord]:
    """Register an upscaled/finalized master and immutable preview-to-master lineage.

    The master retains the source portfolio snapshot when present.  Its quality
    state deliberately stays ``visual_review_required``; technical passing is
    not an approval to submit to any marketplace.
    """

    root = Path(project_root).resolve()
    master_path = Path(report.master_path).resolve()
    try:
        master_relative = master_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise MasterRegistryError("Master path must remain inside the project root.") from exc
    if source_artifact.project_id != project_id or source_execution.project_id != project_id:
        raise MasterRegistryError("Source artifact/execution does not belong to the project.")
    if source_artifact.id not in source_execution.artifact_ids:
        raise MasterRegistryError("Source artifact is not an output of the supplied source execution.")

    portfolio = source_execution.parameters.get("portfolio")
    if portfolio is not None and not isinstance(portfolio, dict):
        raise MasterRegistryError("Source execution portfolio context is invalid.")
    if reviewed_metadata is not None:
        if portfolio is None:
            raise MasterRegistryError("Reviewed metadata requires portfolio lineage.")
        if not isinstance(reviewed_metadata, dict):
            raise MasterRegistryError("Reviewed metadata must be an object.")
        portfolio = {**portfolio, "metadata": reviewed_metadata, "reviewer_checklist": reviewed_metadata["reviewer_checklist"]}

    master = replace(
        Artifact.from_file(project_id, master_relative, root, kind="finalized-master"),
        metadata={
            "quality_state": report.quality_state,
            "source_artifact_id": source_artifact.id,
            "source_execution_id": source_execution.id,
            "master_finalization": report.to_dict(),
        },
    )
    execution_parameters: dict[str, Any] = {
        "master_finalization": report.to_dict(),
        "quality_state": report.quality_state,
        "human_review_required": True,
    }
    if portfolio is not None:
        execution_parameters["portfolio"] = portfolio

    execution = GenerationExecutionRecord.create(
        project_id,
        operation="image.finalize_master",
        state="succeeded",
        provider_id=report.upscale.provider_id,
        model_id=report.upscale.model_id,
        model_version=None,
        pipeline_id="portfolio-master-finalizer",
        pipeline_version=1,
        step_id="finalize-master",
        input_artifact_ids=(source_artifact.id,),
        artifact_ids=(master.id,),
        parameters=execution_parameters,
    )
    actual_artifacts, actual_execution = database.create_artifacts_and_execution((master,), execution)
    actual_master = actual_artifacts[0]

    provenance = ProvenanceRecord.create(
        actual_master.id,
        project_id,
        "image.upscale_and_finalize",
        execution_id=actual_execution.id,
        pipeline_id="portfolio-master-finalizer",
        pipeline_version=1,
        model_id=report.upscale.model_id,
        input_artifact_ids=(source_artifact.id,),
        parameters={
            "scale": report.upscale.scale,
            "minimum_megapixels": report.minimum_megapixels,
            "jpeg_quality": report.jpeg.jpeg_quality,
            "subsampling": report.jpeg.subsampling,
            "assumed_srgb_after_upscale": report.jpeg.assumed_srgb,
        },
        metadata={"quality_state": report.quality_state},
    )
    database.create_provenance(provenance)
    database.create_lineage(
        ArtifactLineage.create(
            actual_master.id,
            source_artifact.id,
            project_id,
            relation="upscaled",
            execution_id=actual_execution.id,
            sequence=0,
        )
    )
    return actual_master, actual_execution
