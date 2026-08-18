"""Provider configuration contracts with secret-safe references.

Provider credentials are intentionally not stored in jobs, pipelines, or provider
configuration JSON. A provider config may refer to an environment variable by
name; resolving the secret is an explicit runtime operation.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any


PROVIDER_CONFIG_SCHEMA_VERSION = 1
_PROVIDER_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
_ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")


class ProviderConfigError(ValueError):
    """Raised when a provider configuration is invalid."""


@dataclass(frozen=True, slots=True)
class SecretRef:
    """A reference to a secret without containing the secret itself."""

    env: str

    def __post_init__(self) -> None:
        if not _ENV_NAME_RE.fullmatch(self.env):
            raise ProviderConfigError("Secret environment variable must be a valid uppercase name.")

    def to_dict(self) -> dict[str, str]:
        return {"env": self.env}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecretRef":
        if not isinstance(data, dict) or set(data) != {"env"}:
            raise ProviderConfigError("Secret reference must contain only the env field.")
        return cls(env=data["env"])

    def resolve(self, environ: dict[str, str] | None = None) -> str:
        source = os.environ if environ is None else environ
        value = source.get(self.env)
        if not value:
            raise ProviderConfigError(f"Required provider secret is not set: {self.env}")
        return value


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Non-secret configuration for an external or local provider."""

    id: str
    kind: str
    enabled: bool = True
    endpoint: str | None = None
    secret_ref: SecretRef | None = None
    options: dict[str, Any] = field(default_factory=dict)
    schema_version: int = PROVIDER_CONFIG_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not _PROVIDER_ID_RE.fullmatch(self.id):
            raise ProviderConfigError("Provider id must be 1-64 characters using letters, numbers, ., _, or -.")
        if not self.kind or not isinstance(self.kind, str):
            raise ProviderConfigError("Provider kind must be a non-empty string.")
        if self.endpoint is not None and not isinstance(self.endpoint, str):
            raise ProviderConfigError("Provider endpoint must be a string or null.")
        if not isinstance(self.options, dict):
            raise ProviderConfigError("Provider options must be an object.")
        if self.schema_version != PROVIDER_CONFIG_SCHEMA_VERSION:
            raise ProviderConfigError(f"Unsupported provider config schema: {self.schema_version}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "kind": self.kind,
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "secret_ref": self.secret_ref.to_dict() if self.secret_ref else None,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderConfig":
        if not isinstance(data, dict):
            raise ProviderConfigError("Provider configuration must be a JSON object.")
        required = {"schema_version", "id", "kind", "enabled", "endpoint", "secret_ref", "options"}
        if set(data) != required:
            missing = required - set(data)
            extra = set(data) - required
            details = []
            if missing:
                details.append("missing: " + ", ".join(sorted(missing)))
            if extra:
                details.append("unexpected: " + ", ".join(sorted(extra)))
            raise ProviderConfigError("Invalid provider fields (" + "; ".join(details) + ")")
        secret = data["secret_ref"]
        return cls(
            id=data["id"],
            kind=data["kind"],
            enabled=data["enabled"],
            endpoint=data["endpoint"],
            secret_ref=SecretRef.from_dict(secret) if secret is not None else None,
            options=dict(data["options"]),
            schema_version=data["schema_version"],
        )

    def resolve_secret(self, environ: dict[str, str] | None = None) -> str | None:
        return self.secret_ref.resolve(environ) if self.secret_ref else None
