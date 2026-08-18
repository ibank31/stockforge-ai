from pathlib import Path

from PIL import Image, ImageDraw

from stockforge.generation import GenerationRequest, GenerationResult, ImageGenerator
from stockforge.proof_of_production import ProductionProofError, run_production_proof


class FakeProductionGenerator(ImageGenerator):
    def __init__(self, output_name: str = "generated.png") -> None:
        self.output_name = output_name

    def generate(self, request: GenerationRequest) -> GenerationResult:
        output = self.output_path
        output.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (2000, 2000), (120, 130, 140))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 999, 999), fill=(30, 70, 120))
        draw.rectangle((1000, 0, 1999, 999), fill=(190, 150, 80))
        draw.rectangle((0, 1000, 999, 1999), fill=(80, 150, 100))
        draw.rectangle((1000, 1000, 1999, 1999), fill=(170, 80, 90))
        image.save(output, format="PNG")
        return GenerationResult(
            status="succeeded",
            artifact_ids=("provider-output-ref",),
            provider_job_id="proof-job-001",
            model_id=request.model_id,
            model_version=request.model_version,
            workflow_hash=request.workflow_hash,
            seed=request.seed,
        )

    def bind_output(self, path: Path) -> None:
        self.output_path = path


def request() -> GenerationRequest:
    return GenerationRequest(
        prompt="commercial construction workspace",
        width=2000,
        height=2000,
        model_id="proof-model",
        model_version="1",
        workflow_hash="proof-workflow",
    )


def test_production_proof_runs_generation_to_artifact_qa_and_dedup(tmp_path: Path) -> None:
    generator = FakeProductionGenerator()
    output = tmp_path / "outputs" / "generated.png"
    generator.bind_output(output)

    result = run_production_proof(
        generator,
        request(),
        project_id="project-001",
        project_root=tmp_path,
        output_relative_path="outputs/generated.png",
    )

    assert result.generation.status == "succeeded"
    assert result.artifact.kind == "generated_image"
    assert len(result.artifact.sha256) == 64
    assert result.structural_qa.status == "warn"
    assert result.visual_qa.status == "pass"
    assert result.duplicate_classification == "no_comparison"


def test_production_proof_rejects_output_outside_project(tmp_path: Path) -> None:
    generator = FakeProductionGenerator()
    generator.bind_output(tmp_path / "outside.png")
    try:
        run_production_proof(
            generator,
            request(),
            project_id="project-001",
            project_root=tmp_path,
            output_relative_path="../outside.png",
        )
    except ProductionProofError as exc:
        assert "inside project root" in str(exc)
    else:
        raise AssertionError("expected ProductionProofError")


def test_production_proof_rejects_failed_generation(tmp_path: Path) -> None:
    class FailedGenerator(ImageGenerator):
        def generate(self, request: GenerationRequest) -> GenerationResult:
            return GenerationResult(
                status="failed",
                provider_job_id="proof-job-fail",
                error_code="PROVIDER_ERROR",
                error_message="provider unavailable",
            )

    try:
        run_production_proof(
            FailedGenerator(),
            request(),
            project_id="project-001",
            project_root=tmp_path,
            output_relative_path="outputs/generated.png",
        )
    except ProductionProofError as exc:
        assert "provider unavailable" in str(exc)
    else:
        raise AssertionError("expected ProductionProofError")
