"""Versioned model registry for quota-aware production routing.

The registry stores metadata only. Model weights live in remote object/model
storage such as Hugging Face Hub and are cached ephemerally by GPU workers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MODEL_REGISTRY_SCHEMA_VERSION = 1


class ModelRegistryError(ValueError):
    """Raised when model registry data is invalid or inconsistent."""


@dataclass(frozen=True, slots=True)
class ModelRequirements:
    vram_min_bytes: int
    ram_min_bytes: int
    disk_min_bytes: int = 0

    def __post_init__(self) -> None:
        if self.vram_min_bytes < 0 or self.ram_min_bytes < 0 or self.disk_min_bytes < 0:
            raise ModelRegistryError("Model resource requirements must be non-negative.")


@dataclass(frozen=True, slots=True)
class ModelArtifact:
    repository: str
    revision: str
    storage: str = "huggingface"
    weight_files: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.repository or not self.revision:
            raise ModelRegistryError("Model artifact repository and revision are required.")
        if self.storage != "huggingface":
            raise ModelRegistryError("Only Hugging Face remote model storage is supported by this contract.")


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    id: str
    version: str
    kind: str
    commercial_use: bool
    capabilities: frozenset[str]
    requirements: ModelRequirements
    artifact: ModelArtifact
    providers: tuple[str, ...] = ()
    priority: int = 100
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.version or not self.kind:
            raise ModelRegistryError("Model id, version, and kind are required.")
        if not self.providers:
            raise ModelRegistryError("At least one production provider is required.")
        if self.priority < 0:
            raise ModelRegistryError("Model priority must be non-negative.")

    def supports(self, *, vram_bytes: int | None, ram_bytes: int | None, free_disk_bytes: int | None) -> bool:
        if not self.enabled or not self.commercial_use:
            return False
        if vram_bytes is not None and vram_bytes < self.requirements.vram_min_bytes:
            return False
        if ram_bytes is not None and ram_bytes < self.requirements.ram_min_bytes:
            return False
        if free_disk_bytes is not None and free_disk_bytes < self.requirements.disk_min_bytes:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "kind": self.kind,
            "commercial_use": self.commercial_use,
            "capabilities": sorted(self.capabilities),
            "requirements": {
                "vram_min_bytes": self.requirements.vram_min_bytes,
                "ram_min_bytes": self.requirements.ram_min_bytes,
                "disk_min_bytes": self.requirements.disk_min_bytes,
            },
            "artifact": {
                "repository": self.artifact.repository,
                "revision": self.artifact.revision,
                "storage": self.artifact.storage,
                "weight_files": list(self.artifact.weight_files),
            },
            "providers": list(self.providers),
            "priority": self.priority,
            "enabled": self.enabled,
            "metadata": self.metadata,
        }


class ModelRegistry:
    """Immutable-at-runtime registry loaded from a versioned JSON manifest."""

    def __init__(self, models: tuple[ModelDefinition, ...], schema_version: int = MODEL_REGISTRY_SCHEMA_VERSION) -> None:
        if schema_version != MODEL_REGISTRY_SCHEMA_VERSION:
            raise ModelRegistryError(f"Unsupported model registry schema: {schema_version}")
        self.schema_version = schema_version
        self._models = {model.id: model for model in models}
        if len(self._models) != len(models):
            raise ModelRegistryError("Duplicate model ids are not allowed.")

    def get(self, model_id: str) -> ModelDefinition:
        try:
            return self._models[model_id]
        except KeyError as exc:
            raise ModelRegistryError(f"Unknown model: {model_id}") from exc

    def list(self, *, enabled_only: bool = True) -> tuple[ModelDefinition, ...]:
        models = tuple(self._models.values())
        if enabled_only:
            models = tuple(model for model in models if model.enabled)
        return tuple(sorted(models, key=lambda model: (model.priority, model.id)))

    def eligible(self, *, capability: str | None = None, vram_bytes: int | None = None, ram_bytes: int | None = None, free_disk_bytes: int | None = None) -> tuple[ModelDefinition, ...]:
        candidates = self.list()
        if capability:
            candidates = tuple(model for model in candidates if capability in model.capabilities)
        return tuple(
            model for model in candidates
            if model.supports(vram_bytes=vram_bytes, ram_bytes=ram_bytes, free_disk_bytes=free_disk_bytes)
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelRegistry":
        if data.get("schema_version") != MODEL_REGISTRY_SCHEMA_VERSION:
            raise ModelRegistryError(f"Unsupported model registry schema: {data.get('schema_version')!r}")
        raw_models = data.get("models")
        if not isinstance(raw_models, list):
            raise ModelRegistryError("Model registry models must be an array.")
        models: list[ModelDefinition] = []
        for raw in raw_models:
            requirements = raw["requirements"]
            artifact = raw["artifact"]
            models.append(
                ModelDefinition(
                    id=raw["id"],
                    version=raw["version"],
                    kind=raw["kind"],
                    commercial_use=raw["commercial_use"],
                    capabilities=frozenset(raw["capabilities"]),
                    requirements=ModelRequirements(**requirements),
                    artifact=ModelArtifact(
                        repository=artifact["repository"],
                        revision=artifact["revision"],
                        storage=artifact.get("storage", "huggingface"),
                        weight_files=tuple(artifact.get("weight_files", ())),
                    ),
                    providers=tuple(raw["providers"]),
                    priority=raw.get("priority", 100),
                    enabled=raw.get("enabled", True),
                    metadata=dict(raw.get("metadata", {})),
                )
            )
        return cls(tuple(models), schema_version=data["schema_version"])

    @classmethod
    def from_json(cls, path: Path) -> "ModelRegistry":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ModelRegistryError("Model registry JSON must contain an object.")
        return cls.from_dict(data)
