"""Runtime lifecycle contract for StockForge generation providers.

This module is intentionally separate from provider configuration. Configuration
owns non-secret settings and secret references; this module owns execution
lifecycle and provider-side job identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .generation import GenerationRequest, GenerationResult
from .plugin import PluginDescriptor

PROVIDER_API_VERSION = "1"
PROVIDER_STATES = frozenset({"submitted", "running", "completed", "succeeded", "failed", "cancelled"})


class ProviderError(RuntimeError):
    """Raised when a provider adapter cannot execute an operation."""


@dataclass(frozen=True, slots=True)
class ProviderJob:
    """Provider-side identity and lifecycle state.

    ``completed`` means the provider finished and outputs are available for
    ingestion, but StockForge has not registered those outputs as artifacts yet.
    ``succeeded`` is reserved for the post-ingestion state with real artifact IDs.
    """

    provider_job_id: str
    state: str
    result: GenerationResult | None = None
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.provider_job_id:
            raise ProviderError("provider_job_id must be non-empty")
        if self.state not in PROVIDER_STATES:
            raise ProviderError(f"Unsupported provider job state: {self.state}")
        if self.state == "succeeded" and self.result is None:
            raise ProviderError("succeeded provider job requires a result")
        if self.state == "failed" and (not self.error_code or not self.error_message):
            raise ProviderError("failed provider job requires error_code and error_message")
        if self.state in {"submitted", "running", "completed", "cancelled"} and self.result is not None:
            raise ProviderError(f"{self.state} provider job cannot contain a terminal generation result")


class GenerationProvider(Protocol):
    """Runtime interface implemented by concrete generator adapters."""

    @property
    def descriptor(self) -> PluginDescriptor: ...

    def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def submit(self, request: GenerationRequest) -> ProviderJob: ...

    def status(self, provider_job_id: str) -> ProviderJob: ...

    def cancel(self, provider_job_id: str) -> ProviderJob: ...


def ensure_provider_capability(provider: GenerationProvider, capability: str) -> None:
    """Fail early when an adapter cannot provide the requested operation."""
    if capability not in provider.descriptor.capabilities:
        raise ProviderError(
            f"Provider {provider.descriptor.id!r} does not support capability {capability!r}"
        )
