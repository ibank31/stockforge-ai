"""Versioned project manifest contract."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA_VERSION = 1


class ManifestError(ValueError):
    """Raised when a project manifest is invalid or cannot be decoded."""


@dataclass(slots=True)
class ProjectManifest:
    """Persistent identity and metadata for one StockForge project."""

    id: str
    name: str
    created_at: str
    version: int = 1
    schema_version: int = MANIFEST_SCHEMA_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, project_id: str, name: str) -> "ProjectManifest":
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        return cls(id=project_id, name=name, created_at=created_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectManifest":
        if not isinstance(data, dict):
            raise ManifestError("Project manifest must be a JSON object.")

        required = ("schema_version", "id", "name", "version", "created_at", "metadata")
        missing = [key for key in required if key not in data]
        if missing:
            raise ManifestError(f"Project manifest is missing fields: {', '.join(missing)}")

        if data["schema_version"] != MANIFEST_SCHEMA_VERSION:
            raise ManifestError(
                f"Unsupported project manifest schema: {data['schema_version']}. "
                f"Expected {MANIFEST_SCHEMA_VERSION}."
            )
        if not isinstance(data["id"], str) or not data["id"]:
            raise ManifestError("Project manifest id must be a non-empty string.")
        if not isinstance(data["name"], str) or not data["name"]:
            raise ManifestError("Project manifest name must be a non-empty string.")
        if not isinstance(data["version"], int) or isinstance(data["version"], bool):
            raise ManifestError("Project manifest version must be an integer.")
        if not isinstance(data["created_at"], str) or not data["created_at"]:
            raise ManifestError("Project manifest created_at must be a non-empty string.")
        if not isinstance(data["metadata"], dict):
            raise ManifestError("Project manifest metadata must be an object.")

        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            created_at=data["created_at"],
            schema_version=data["schema_version"],
            metadata=dict(data["metadata"]),
        )

    def write(self, path: Path) -> None:
        """Write the manifest atomically to avoid partial JSON files."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        try:
            temporary.write_text(
                json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

    @classmethod
    def read(cls, path: Path) -> "ProjectManifest":
        path = Path(path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ManifestError(f"Unable to read project manifest: {path}") from exc
        return cls.from_dict(data)
