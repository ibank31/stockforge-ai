from pathlib import Path

import pytest

from stockforge.database import Database
from stockforge.execution_identity import execution_id_for_job
from stockforge.execution_record import GenerationExecutionRecord
from stockforge.generation import GenerationRequest
from stockforge.generation_provider import ProviderJob
from stockforge.plugin import PluginDescriptor
from stockforge.recovery_orchestrator import RecoveryGenerationOrchestrator
from stockforge.orchestrator import OrchestrationError


class FakeProvider:
    def __init__(self, provider_root: Path):
        self.provider_root = provider_root
        self.submit_calls = 0
        self.wait_calls = 0

    @property
    def descriptor(self):
        return PluginDescriptor(id="fake.generator", name="Fake Generator", version="1.0", kind="generator", capabilities=frozenset({"image.generate", "generation.async"}))

    def submit(self, request, *, provider_job_id=None):
        self.submit_calls += 1
        return ProviderJob(provider_job_id=provider_job_id or "provider-1", state="submitted")

    def wait(self, provider_job_id, *, timeout_seconds=600.0):
        self.wait_calls += 1
        return ProviderJob(provider_job_id=provider_job_id, state="completed")

    def output_refs(self, provider_job_id):
        return ({"filename": "generated.png", "subfolder": "", "type": "output", "node_id": "9"},)


def make_request():
    return GenerationRequest(prompt="commercial stock photo", model_id="model-a", model_version="1", seed=42)


def setup(tmp_path: Path):
    project_root = tmp_path / "project"
    provider_root = tmp_path / "provider"
    project_root.mkdir()
    provider_root.mkdir()
    (provider_root / "generated.png").write_bytes(b"PNG test output")
    database = Database(project_root / "stockforge.db")
    database.initialize()
    database.create_project("project-1", "demo", project_root)
    provider = FakeProvider(provider_root)
    orchestrator = RecoveryGenerationOrchestrator(database, project_id="project-1", project_root=project_root, provider_root=provider_root, provider=provider)
    return database, provider, orchestrator


def test_retry_reuses_one_execution_and_one_provider_submission(tmp_path: Path):
    database, provider, orchestrator = setup(tmp_path)
    first = orchestrator.run(make_request(), job_id="job-1")
    second = orchestrator.run(make_request(), job_id="job-1")
    assert first.execution.id == execution_id_for_job("project-1", "job-1")
    assert second.execution.id == first.execution.id
    assert provider.submit_calls == 1
    assert database.get_execution(first.execution.id).state == "succeeded"


def test_running_execution_with_provider_id_is_resumed_without_resubmission(tmp_path: Path):
    database, provider, orchestrator = setup(tmp_path)
    request = make_request()
    execution = GenerationExecutionRecord.create("project-1", prompt=request.prompt, state="running", job_id="job-2", provider_id=provider.descriptor.id, provider_job_id="provider-existing", model_id=request.model_id, model_version=request.model_version, parameters=dict(request.parameters))
    execution = GenerationExecutionRecord.from_dict({**execution.to_dict(), "id": execution_id_for_job("project-1", "job-2")})
    database.create_execution(execution)
    result = orchestrator.run(request, job_id="job-2")
    assert result.execution.state == "succeeded"
    assert result.execution.provider_job_id == "provider-existing"
    assert provider.submit_calls == 0
    assert provider.wait_calls == 1


def test_terminal_execution_is_not_implicitly_resubmitted(tmp_path: Path):
    database, provider, orchestrator = setup(tmp_path)
    request = make_request()
    execution = GenerationExecutionRecord.create("project-1", prompt=request.prompt, state="failed", job_id="job-3", provider_id=provider.descriptor.id, error_code="PROVIDER_EXECUTION_FAILED", error_message="provider failed", parameters=dict(request.parameters))
    execution = GenerationExecutionRecord.from_dict({**execution.to_dict(), "id": execution_id_for_job("project-1", "job-3")})
    database.create_execution(execution)
    with pytest.raises(OrchestrationError, match="EXECUTION_TERMINAL"):
        orchestrator.run(request, job_id="job-3")
    assert provider.submit_calls == 0
