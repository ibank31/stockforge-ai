import pytest

from stockforge.generation import GenerationRequest, GenerationResult
from stockforge.generation_provider import (
    ProviderJob,
    ProviderRuntimeError,
    ensure_provider_capability,
)
from stockforge.plugin import PluginDescriptor


def test_provider_job_lifecycle_validation():
    pending = ProviderJob(provider_job_id="job-1", state="submitted")
    assert pending.state == "submitted"

    result = GenerationResult(status="succeeded", artifact_ids=("asset-1",))
    completed = ProviderJob(provider_job_id="job-1", state="succeeded", result=result)
    assert completed.result == result


def test_provider_job_requires_structured_failure():
    with pytest.raises(ProviderRuntimeError, match="failed provider job requires"):
        ProviderJob(provider_job_id="job-1", state="failed")


def test_provider_job_rejects_errors_on_non_failed_state():
    with pytest.raises(ProviderRuntimeError, match="error fields are only valid"):
        ProviderJob(provider_job_id="job-1", state="running", error_code="TIMEOUT")


def test_provider_capability_guard():
    class FakeProvider:
        descriptor = PluginDescriptor(
            id="fake.generator",
            name="Fake Generator",
            version="1.0.0",
            kind="generator",
            capabilities=frozenset({"image.generate"}),
        )

    provider = FakeProvider()
    ensure_provider_capability(provider, "image.generate")
    with pytest.raises(ProviderRuntimeError, match="does not support capability"):
        ensure_provider_capability(provider, "image.upscale")


def test_provider_contract_can_receive_generation_request():
    request = GenerationRequest(prompt="commercial stock photo")
    assert request.prompt == "commercial stock photo"
