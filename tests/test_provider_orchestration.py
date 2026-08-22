from dataclasses import dataclass

import pytest

from stockforge.generation import GenerationRequest, GenerationResult
from stockforge.generation_provider import ProviderJob
from stockforge.plugin import PluginDescriptor
from stockforge.provider_orchestration import (
    ProviderCandidate,
    ProviderCapabilities,
    ProviderRouter,
    ProviderRoutingError,
)


@dataclass
class FakeProvider:
    provider_id: str

    @property
    def descriptor(self):
        return PluginDescriptor(
            id=self.provider_id,
            name=self.provider_id,
            version="1.0.0",
            api_version="1",
            kind="generator",
            capabilities=frozenset({"image.generate"}),
        )

    def generate(self, request):
        return GenerationResult(status="succeeded", artifact_ids=("a",))

    def submit(self, request, *, provider_job_id=None):
        return ProviderJob(provider_job_id or "job", "succeeded", self.generate(request))

    def status(self, provider_job_id):
        return self.submit(GenerationRequest(prompt="test"), provider_job_id=provider_job_id)

    def cancel(self, provider_job_id):
        return ProviderJob(provider_job_id, "cancelled")


def test_router_filters_ineligible_provider():
    request = GenerationRequest(prompt="test", model_id="qwen-image")
    unsupported = ProviderCandidate(
        FakeProvider("small"),
        ProviderCapabilities(provider_id="small", models=frozenset({"other-model"})),
        score=100,
    )
    eligible = ProviderCandidate(
        FakeProvider("qwen-worker"),
        ProviderCapabilities(provider_id="qwen-worker", models=frozenset({"qwen-image"})),
        score=10,
    )

    selected = ProviderRouter([unsupported, eligible]).select(request)
    assert selected.capabilities.provider_id == "qwen-worker"


def test_router_prefers_highest_score_among_eligible():
    request = GenerationRequest(prompt="test")
    candidates = [
        ProviderCandidate(FakeProvider("a"), ProviderCapabilities(provider_id="a"), score=1),
        ProviderCandidate(FakeProvider("b"), ProviderCapabilities(provider_id="b"), score=5),
    ]
    assert ProviderRouter(candidates).select(request).capabilities.provider_id == "b"


def test_router_rejects_exhausted_quota():
    request = GenerationRequest(prompt="test")
    exhausted = ProviderCandidate(
        FakeProvider("zerogpu"),
        ProviderCapabilities(provider_id="zerogpu", quota_remaining=0),
        score=100,
    )
    fallback = ProviderCandidate(
        FakeProvider("kaggle"),
        ProviderCapabilities(provider_id="kaggle", quota_remaining=1),
        score=10,
    )
    assert ProviderRouter([exhausted, fallback]).select(request).capabilities.provider_id == "kaggle"


def test_router_fails_when_no_provider_is_eligible():
    request = GenerationRequest(prompt="test")
    candidate = ProviderCandidate(
        FakeProvider("offline"),
        ProviderCapabilities(provider_id="offline", available=False),
    )
    with pytest.raises(ProviderRoutingError):
        ProviderRouter([candidate]).select(request)
