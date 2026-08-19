"""Backward-compatible aliases for the canonical generation provider contract.

The runtime contract is defined in :mod:`stockforge.generation_provider`.
This module remains as a compatibility import surface for existing adapters and
callers while migration completes; new code must import from generation_provider.
"""

from .generation_provider import (
    PROVIDER_API_VERSION,
    PROVIDER_STATES,
    GenerationProvider,
    ProviderJob,
    ProviderRuntimeError,
    ensure_provider_capability,
)

# Compatibility name retained for existing provider adapters.
ProviderError = ProviderRuntimeError

__all__ = [
    "PROVIDER_API_VERSION",
    "PROVIDER_STATES",
    "GenerationProvider",
    "ProviderJob",
    "ProviderRuntimeError",
    "ProviderError",
    "ensure_provider_capability",
]
