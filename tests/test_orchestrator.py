from pathlib import Path

import pytest

from stockforge.database import Database
from stockforge.generation import GenerationRequest, GenerationResult
from stockforge.generation_provider import ProviderJob
from stockforge.orchestrator import GenerationOrchestrator, OrchestrationError
from stockforge.plugin import PluginDescriptor


class FakeAsyncProvider:
    def __init__(self) -> None:
        self.submitted_provider_job_id = None

    @property
    def descriptor(self) -> PluginDescriptor:
        return PluginDescriptor(id="fake.generator", name="Fake Generator", version="1.0", kind="generator", capabilities=frozenset({"image.generate", "generation.async"}))
    def submit(self, request: GenerationRequest, *, provider_job_id: str | None = None) -> ProviderJob:
        self.submitted_provider_job_id = provider_job_id
        return ProviderJob(provider_job_id=provider_job_id or "job-1", state="submitted")
    def wait(self, provider_job_id: str, *, timeout_seconds: float) -> ProviderJob: return ProviderJob(provider_job_id=provider_job_id, state="completed")
    def output_refs(self, provider_job_id: str) -> tuple[dict[str, str], ...]: return ()
    def cancel(self, provider_job_id: str) -> ProviderJob: return ProviderJob(provider_job_id=provider_job_id, state="cancelled")


class FakeAsyncProviderWithOutput(FakeAsyncProvider):
    def output_refs(self, provider_job_id: str) -> tuple[dict[str, str], ...]:
        return ({"filename": "generated.png", "subfolder": "", "type": "output", "node_id": "9"},)


class FakeSyncProvider:
    @property
    def descriptor(self) -> PluginDescriptor:
        return PluginDescriptor(id="fake.sync", name="Fake Sync", version="1.0", kind="generator", capabilities=frozenset({"image.generate"}))
    def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(status="succeeded", artifact_ids=("external-artifact-1",), provider_job_id="sync-1", model_id="model-a", model_version="1", workflow_hash="workflow-hash", seed=request.seed, parameters={"seed": request.seed})


def make_request() -> GenerationRequest:
    return GenerationRequest(prompt="commercial stock photo of a modern office", model_id="model-a", model_version="1", seed=42)


def test_async_provider_output_is_ingested_and_recorded(tmp_path: Path) -> None:
    project_root = tmp_path / "project"; provider_root = tmp_path / "provider"; project_root.mkdir(); provider_root.mkdir(); (provider_root / "generated.png").write_bytes(b"PNG test output")
    database = Database(project_root / "stockforge.db"); database.initialize(); project_id = "project-1"; database.create_project(project_id, "demo", project_root)
    provider = FakeAsyncProviderWithOutput()
    result = GenerationOrchestrator(database, project_id=project_id, project_root=project_root, provider_root=provider_root, provider=provider).run(make_request())
    assert len(result.artifacts) == 1; assert result.execution.state == "succeeded"; assert result.execution.provider_job_id == provider.submitted_provider_job_id == result.execution.id; assert result.execution.artifact_ids == (result.artifacts[0].id,); assert database.get_artifact(result.artifacts[0].id) is not None; persisted = database.get_execution(result.execution.id); assert persisted is not None; assert persisted.state == "succeeded"; assert persisted.artifact_ids == result.execution.artifact_ids


def test_async_provider_without_outputs_is_recorded_as_failure(tmp_path: Path) -> None:
    project_root = tmp_path / "project"; provider_root = tmp_path / "provider"; project_root.mkdir(); provider_root.mkdir(); database = Database(project_root / "stockforge.db"); database.initialize(); database.create_project("project-1", "demo", project_root)
    orchestrator = GenerationOrchestrator(database, project_id="project-1", project_root=project_root, provider_root=provider_root, provider=FakeAsyncProvider())
    with pytest.raises(OrchestrationError, match="PROVIDER_NO_OUTPUTS"): orchestrator.run(make_request())


def test_sync_provider_result_is_persisted(tmp_path: Path) -> None:
    project_root = tmp_path / "project"; provider_root = tmp_path / "provider"; project_root.mkdir(); provider_root.mkdir(); database = Database(project_root / "stockforge.db"); database.initialize(); database.create_project("project-1", "demo", project_root)
    result = GenerationOrchestrator(database, project_id="project-1", project_root=project_root, provider_root=provider_root, provider=FakeSyncProvider()).run(make_request())
    assert result.artifacts == (); assert result.execution.state == "succeeded"; assert result.execution.artifact_ids == ("external-artifact-1",); persisted = database.get_execution(result.execution.id); assert persisted is not None; assert persisted.state == "succeeded"
