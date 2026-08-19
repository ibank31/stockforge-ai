"""Runtime lifecycle boundary for generation provider adapters.

No HTTP, ComfyUI, Diffusers, or vendor-specific logic belongs here. This
contract lets the orchestrator handle synchronous and asynchronous providers
without changing the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .generation import GenerationRequest, GenerationResult
from .plugin import PluginDescriptor

PROVIDER_API_VERSION = "1"
PROVIDER_STATES = frozenset({"submitted", "running", "completed", "succeeded", "failed", "cancelled"})


class ProviderRuntimeError(RuntimeError):
    """Raised when a provider adapter violates the runtime contract."""


@dataclass(frozen=True, slots=True)
class ProviderJob:
    """Provider-side execution identity and terminal/intermediate state."""

    provider_job_id: str
    state: str
    result: GenerationResult | None = None
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.provider_job_id:
            raise ProviderRuntimeError("provider_job_id must be non-empty")
        if self.state not in PROVIDER_STATES:
            raise ProviderRuntimeError(f"Unsupported provider job state: {self.state}")
        if self.state == "succeeded" and self.result is None:
            raise ProviderRuntimeError("succeeded provider job requires a result")
        if self.state == "failed" and (not self.error_code or not self.error_message):
            raise ProviderRuntimeError("failed provider job requires error_code and error_message")
        if self.state != "failed" and (self.error_code is not None or self.error_message is not None):
            raise ProviderRuntimeError("error fields are only valid for failed provider jobs")


class GenerationProvider(Protocol):
    """Runtime interface implemented by a generation adapter."""

    @property
    def descriptor(self) -> PluginDescriptor: ...

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Run a generation to completion for providers with synchronous execution."""
        ...

    def submit(self, request: GenerationRequest, *, provider_job_id: str | None = None) -> ProviderJob:
        """Start asynchronous execution, optionally reusing a durable provider identity."""
        ...

    def status(self, provider_job_id: str) -> ProviderJob:
        """Read provider-side state without changing it."""
        ...

    def cancel(self, provider_job_id: str) -> ProviderJob:
        """Request cancellation and return the provider's resulting state."""
        ...


def ensure_provider_capability(provider: GenerationProvider, capability: str) -> None:
    """Fail before execution when an adapter lacks a required capability."""
    if capability not in provider.descriptor.capabilities:
        raise ProviderRuntimeError(
            f"Provider {provider.descriptor.id!r} does not support capability {capability!r}"
        )
