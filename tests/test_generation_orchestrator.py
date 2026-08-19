from pathlib import Path

from stockforge.config import StockForgeConfig
from stockforge.database import Database
from stockforge.execution_record import GenerationExecutionRecord
from stockforge.generation_orchestrator import GenerationJobOrchestrator
from stockforge.generation_provider import ProviderJob
from stockforge.job_database import JobDatabase
from stockforge.job_manager import JobManager
from stockforge.plugin import PluginDescriptor
from stockforge.project import ProjectManager


class FakeProvider:
    descriptor = PluginDescriptor(
        id="fake",
        name="Fake Generator",
        version="1",
        kind="generator",
        capabilities=frozenset({"image.generate", "generation.async"}),
    )

    def __init__(self):
        self.submitted_ids = []

    def submit(self, request, *, provider_job_id=None):
        self.submitted_ids.append(provider_job_id)
        return ProviderJob(provider_job_id=provider_job_id or "provider-1", state="submitted")

    def status(self, provider_job_id):
        return ProviderJob(provider_job_id=provider_job_id, state="completed")

    def output_refs(self, provider_job_id):
        return ({"filename": "result.png", "subfolder": "", "type": "output", "node_id": "1"},)

    def wait(self, provider_job_id):
        return ProviderJob(provider_job_id=provider_job_id, state="completed")

    def cancel(self, provider_job_id):
        return ProviderJob(provider_job_id=provider_job_id, state="cancelled")

    def generate(self, request):
        raise AssertionError("async provider should use submit")


def _setup(tmp_path: Path):
    config = StockForgeConfig(
        workspace=tmp_path / "workspace",
        database=tmp_path / "db.sqlite",
        project_root=tmp_path / "projects",
    )
    config.project_root.mkdir(parents=True)
    database = JobDatabase(config.database)
    database.initialize()
    project = ProjectManager(config, database).create("stock-assets")
    provider_root = tmp_path / "comfyui-output"
    provider_root.mkdir()
    (provider_root / "result.png").write_bytes(b"png-test")
    return config, database, project, provider_root


def test_image_generate_job_ingests_output_and_completes(tmp_path: Path):
    _, database, project, provider_root = _setup(tmp_path)
    jobs = JobManager(database)
    job = jobs.create(
        project_id=project["id"],
        job_type="image.generate",
        payload={"generation": {"prompt": "test image", "parameters": {"comfyui_workflow": {"1": {"class_type": "SaveImage"}}}}},
        max_attempts=1,
    )
    claimed = jobs.claim_next("test-worker")
    assert claimed is not None and claimed.id == job.id

    provider = FakeProvider()
    final = GenerationJobOrchestrator(
        job_manager=jobs,
        database=database,
        provider=provider,
        provider_root=provider_root,
    ).run(claimed)

    assert final.state == "succeeded"
    assert len(final.artifact_ids) == 1
    assert (Path(project["path"]) / "artifacts").is_dir()
    assert len(database.list_artifacts(project["id"])) == 1
    assert jobs.list(project["id"], "succeeded")[0].result["artifact_ids"] == list(final.artifact_ids)


def test_existing_execution_identity_is_reused(tmp_path: Path):
    _, database, project, provider_root = _setup(tmp_path)
    jobs = JobManager(database)
    execution = GenerationExecutionRecord.create(
        project["id"],
        prompt="test",
        operation="image.generate",
        job_id=None,
        provider_id="fake",
        provider_job_id="durable-42",
    )
    database.create_execution(execution)
    job = jobs.create(
        project_id=project["id"],
        job_type="image.generate",
        payload={"execution_id": execution.id, "generation": {"prompt": "test", "parameters": {"comfyui_workflow": {"1": {"class_type": "SaveImage"}}}}},
        max_attempts=1,
    )
    claimed = jobs.claim_next("test-worker")
    assert claimed is not None
    database.update_execution(GenerationExecutionRecord.from_dict({**execution.to_dict(), "job_id": claimed.id}))

    provider = FakeProvider()
    GenerationJobOrchestrator(
        job_manager=jobs,
        database=database,
        provider=provider,
        provider_root=provider_root,
    ).run(claimed)
    assert provider.submitted_ids == ["durable-42"]
