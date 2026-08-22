"""Provider capability discovery and deterministic routing contracts.

This module deliberately does not perform provider execution. It answers one
question: which registered provider is eligible for a generation request?
Actual HTTP/GPU/model logic remains inside provider adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol

from .generation import GenerationRequest
from .generation_provider import GenerationProvider


class ProviderRoutingError(RuntimeError):
    """Raised when no eligible provider can be selected."""


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    """Provider resource/capability snapshot used for scheduling decisions."""

    provider_id: str
    available: bool = True
    generation: bool = True
    max_width: int | None = None
    max_height: int | None = None
    max_batch_size: int | None = None
    models: frozenset[str] = field(default_factory=frozenset)
    free_disk_bytes: int | None = None
    vram_bytes: int | None = None
    ram_bytes: int | None = None
    quota_remaining: float | None = None

    def supports(self, request: GenerationRequest) -> bool:
        if not self.available or not self.generation:
            return False
        if self.quota_remaining is not None and self.quota_remaining <= 0:
            return False
        if self.max_width is not None and request.width > self.max_width:
            return False
        if self.max_height is not None and request.height > self.max_height:
            return False
        if self.max_batch_size is not None and request.batch_size > self.max_batch_size:
            return False
        if request.model_id and self.models and request.model_id not in self.models:
            return False
        return True


class ProviderCapabilityProbe(Protocol):
    """Adapter-owned health/resource discovery boundary."""

    def capabilities(self) -> ProviderCapabilities: ...


@dataclass(frozen=True, slots=True)
class ProviderCandidate:
    provider: GenerationProvider
    capabilities: ProviderCapabilities
    score: float = 0.0


class ProviderRouter:
    """Select an eligible provider without knowing provider implementation details."""

    def __init__(self, candidates: Iterable[ProviderCandidate]) -> None:
        self._candidates = tuple(candidates)

    def candidates_for(self, request: GenerationRequest) -> tuple[ProviderCandidate, ...]:
        return tuple(candidate for candidate in self._candidates if candidate.capabilities.supports(request))

    def select(self, request: GenerationRequest) -> ProviderCandidate:
        candidates = self.candidates_for(request)
        if not candidates:
            raise ProviderRoutingError(
                f"No eligible generation provider for model={request.model_id!r}, "
                f"resolution={request.width}x{request.height}, batch={request.batch_size}"
            )
        return max(candidates, key=lambda candidate: candidate.score)
