"""Validated provider configuration without storing secret values."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROVIDER_CONFIG_SCHEMA_VERSION = 1


class ProviderConfigError(ValueError):
    """Raised when provider configuration violates its contract."""


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Non-secret configuration for one generation provider."""

    provider_id: str
    endpoint: str | None = None
    enabled: bool = True
    timeout_seconds: int = 120
    capabilities: tuple[str, ...] = ()
    secret_env: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = PROVIDER_CONFIG_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ProviderConfigError("provider_id must be non-empty")
        if self.schema_version != PROVIDER_CONFIG_SCHEMA_VERSION:
            raise ProviderConfigError(f"Unsupported provider config schema: {self.schema_version}")
        if self.endpoint is not None and not self.endpoint:
            raise ProviderConfigError("endpoint must be non-empty or null")
        if not isinstance(self.timeout_seconds, int) or isinstance(self.timeout_seconds, bool) or self.timeout_seconds < 1:
            raise ProviderConfigError("timeout_seconds must be a positive integer")
        if not all(isinstance(item, str) and item for item in self.capabilities):
            raise ProviderConfigError("capabilities must contain non-empty strings")
        if self.secret_env is not None and not self.secret_env:
            raise ProviderConfigError("secret_env must be non-empty or null")
        if not isinstance(self.metadata, dict):
            raise ProviderConfigError("metadata must be an object")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "provider_id": self.provider_id,
            "endpoint": self.endpoint,
            "enabled": self.enabled,
            "timeout_seconds": self.timeout_seconds,
            "capabilities": list(self.capabilities),
            "secret_env": self.secret_env,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderConfig":
        if not isinstance(data, dict):
            raise ProviderConfigError("Provider config must be a JSON object")
        required = {"schema_version", "provider_id", "endpoint", "enabled", "timeout_seconds", "capabilities", "secret_env", "metadata"}
        if set(data) != required:
            raise ProviderConfigError("Provider config fields do not match schema")
        if not isinstance(data["capabilities"], list):
            raise ProviderConfigError("capabilities must be an array")
        return cls(
            provider_id=data["provider_id"], endpoint=data["endpoint"], enabled=data["enabled"],
            timeout_seconds=data["timeout_seconds"], capabilities=tuple(data["capabilities"]),
            secret_env=data["secret_env"], metadata=data["metadata"], schema_version=data["schema_version"],
        )

    def resolve_secret(self, environ: dict[str, str] | None = None) -> str | None:
        """Resolve a secret only from an environment variable; never persist it."""
        if not self.secret_env:
            return None
        source = os.environ if environ is None else environ
        return source.get(self.secret_env)


class ProviderConfigStore:
    """Persist provider configuration while keeping secrets outside disk."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load_all(self) -> list[ProviderConfig]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ProviderConfigError("Provider config store must contain an array")
        return [ProviderConfig.from_dict(item) for item in data]

    def save_all(self, configs: list[ProviderConfig]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps([config.to_dict() for config in configs], indent=2, sort_keys=True) + "\n"
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(payload, encoding="utf-8")
        temp.replace(self.path)
