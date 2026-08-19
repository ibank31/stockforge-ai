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


class FakeProvider:
    @property
    def descriptor(self) -> PluginDescriptor:
        return PluginDescriptor(
            id="fake.worker",
            name="Worker Fake",
            version="1.0",
            kind="generator",
            capabilities=frozenset({"image.generate", "generation.async"}),
        )

    def submit(self, request: GenerationRequest) -> ProviderJob:
        return ProviderJob(provider_job_id="worker-job", state="submitted")

    def wait(self, provider_job_id: str, *, timeout_seconds: float) -> ProviderJob:
        return ProviderJob(provider_job_id=provider_job_id, state="completed")

    def output_refs(self, provider_job_id: str) -> tuple[dict[str, str], ...]:
        return ({"filename": "generated.png", "subfolder": "", "type": "output", "node_id": "1"},)

    def cancel(self, provider_job_id: str) -> ProviderJob:
        return ProviderJob(provider_job_id=provider_job_id, state="cancelled")


def test_worker_claims_orchestrates_and_completes_job(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    provider_root = tmp_path / "provider"
    project_root.mkdir()
    provider_root.mkdir()
    Image.new("RGB", (2000, 2000), (128, 128, 128)).save(provider_root / "generated.png", format="PNG")

    database = JobDatabase(project_root / "stockforge.db")
    database.initialize()
    project_id = str(uuid4())
    database.create_project(project_id, "demo", project_root)
    manager = JobManager(database)
    request = GenerationRequest(prompt="stock office", model_id="model-a", model_version="1", seed=1)
    job = manager.create(project_id=project_id, job_type="image.generate", payload=request.to_dict())

    def factory(_: object) -> GenerationOrchestrator:
        return GenerationOrchestrator(
            database,
            project_id=project_id,
            project_root=project_root,
            provider_root=provider_root,
            provider=FakeProvider(),
        )

    worker = GenerationJobWorker(manager, factory, worker_id="worker-1")
    result = worker.run_once()

    assert result is not None
    assert result.status == "succeeded", result.result
    persisted = database.get_job(job.id)
    assert persisted.status == "succeeded"
    assert persisted.result is not None
    assert persisted.result["artifact_ids"]


def test_worker_returns_none_when_queue_is_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    database = JobDatabase(project_root / "stockforge.db")
    database.initialize()
    manager = JobManager(database)
    worker = GenerationJobWorker(manager, lambda _: None, worker_id="worker-1")
    assert worker.run_once() is None
