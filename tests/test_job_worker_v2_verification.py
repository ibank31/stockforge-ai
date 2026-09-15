from pathlib import Path
from uuid import uuid4

from PIL import Image

from stockforge.generation import GenerationRequest
from stockforge.generation_provider import ProviderJob
from stockforge.job_database import JobDatabase
from stockforge.job_manager import JobManager
from stockforge.job_worker import GenerationJobWorker
from stockforge.orchestrator import GenerationOrchestrator
from stockforge.plugin import PluginDescriptor


class VerificationProvider:
    def __init__(self, source: Path, output_name: str = "generated.png"):
        self.source = source
        self.output_name = output_name

    @property
    def descriptor(self) -> PluginDescriptor:
        return PluginDescriptor(id="fake.verification", name="Verification Fake", version="1.0", kind="generator", capabilities=frozenset({"image.generate", "generation.async"}))

    def submit(self, request: GenerationRequest, *, provider_job_id: str | None = None) -> ProviderJob:
        return ProviderJob(provider_job_id=provider_job_id or "verification-job", state="submitted")

    def wait(self, provider_job_id: str, *, timeout_seconds: float) -> ProviderJob:
        return ProviderJob(provider_job_id=provider_job_id, state="completed")

    def output_refs(self, provider_job_id: str) -> tuple[dict[str, str], ...]:
        return ({"filename": self.output_name, "subfolder": "", "type": "output", "node_id": "1"},)

    def cancel(self, provider_job_id: str) -> ProviderJob:
        return ProviderJob(provider_job_id=provider_job_id, state="cancelled")


def _run(tmp_path: Path, same_pixels: bool) -> dict:
    project_root = tmp_path / "project"
    provider_root = tmp_path / "provider"
    project_root.mkdir()
    provider_root.mkdir()
    reference = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "orange").save(reference)
    Image.new("RGB", (64, 64), "orange" if same_pixels else "blue").save(provider_root / "generated.png")
    database = JobDatabase(project_root / "stockforge.db")
    database.initialize()
    project_id = str(uuid4())
    database.create_project(project_id, "demo", project_root)
    manager = JobManager(database)
    request = GenerationRequest(prompt="new commercial asset", parameters={"reference_path": str(reference)})
    job = manager.create(project_id=project_id, job_type="v2_generation", payload=request.to_dict())

    def factory(_: object) -> GenerationOrchestrator:
        return GenerationOrchestrator(database, project_id=project_id, project_root=project_root, provider_root=provider_root, provider=VerificationProvider(reference))

    result = GenerationJobWorker(manager, factory, worker_id="worker-v2").run_once()
    assert result is not None
    assert result.status == "succeeded"
    assert database.get_job(job.id).status == "succeeded"
    return result.result


def test_v2_worker_blocks_too_similar_output(tmp_path: Path) -> None:
    result = _run(tmp_path, same_pixels=True)
    gate = result["post_generation_verification"]
    assert gate["decision"] == "BLOCK"
    assert gate["auto_approved"] is False


def test_v2_worker_keeps_distinct_output_in_review(tmp_path: Path) -> None:
    result = _run(tmp_path, same_pixels=False)
    gate = result["post_generation_verification"]
    assert gate["decision"] == "REVIEW"
    assert gate["auto_approved"] is False
