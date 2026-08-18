"""End-to-end production proof orchestration.

This module exercises the existing contracts as one deterministic pipeline. It
uses an injected provider, so CI can prove the full lifecycle without requiring
a live ComfyUI server. A real ComfyUI adapter can be injected unchanged in a
runtime environment.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .artifact import Artifact
from .dedupe_pipeline import compare_images
from .generation import GenerationRequest, GenerationResult, ImageGenerator
from .image_qa import ImageQAReport, inspect_image
from .visual_qa import VisualQAReport, inspect_visual


class ProductionProofError(RuntimeError):
    """Raised when the end-to-end production proof fails."""


class OutputReferenceProvider(Protocol):
    def generate_output(self, request: GenerationRequest, output_dir: Path) -> Path: ...


@dataclass(frozen=True, slots=True)
class ProductionProofResult:
    request: GenerationRequest
    generation: GenerationResult
    artifact: Artifact
    structural_qa: ImageQAReport
    visual_qa: VisualQAReport
    duplicate_classification: str


def run_production_proof(
    generator: ImageGenerator,
    request: GenerationRequest,
    *,
    project_id: str,
    project_root: Path,
    output_relative_path: str,
    comparison_path: Path | None = None,
) -> ProductionProofResult:
    """Run generation through artifact, QA, and dedup boundaries."""
    root = Path(project_root).resolve()
    output_path = (root / output_relative_path).resolve()
    try:
        output_path.relative_to(root)
    except ValueError as exc:
        raise ProductionProofError("Production output must remain inside project root") from exc

    result = generator.generate(request)
    if result.status != "succeeded" or not result.artifact_ids:
        raise ProductionProofError(result.error_message or "Generation failed")
    if not output_path.is_file():
        raise ProductionProofError("Generator succeeded but expected output file is missing")

    artifact = Artifact.from_file(
        project_id=project_id,
        relative_path=output_path.relative_to(root).as_posix(),
        root=root,
        kind="generated_image",
    )
    structural = inspect_image(output_path)
    if structural.status == "fail":
        raise ProductionProofError("Generated asset failed structural QA")
    visual = inspect_visual(output_path, structural=structural)
    if visual.status == "fail":
        raise ProductionProofError("Generated asset failed visual QA")

    classification = "no_comparison"
    if comparison_path is not None:
        comparison = compare_images(output_path, comparison_path)
        classification = comparison.classification

    return ProductionProofResult(request, result, artifact, structural, visual, classification)
