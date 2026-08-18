"""Artifact identity and provenance primitives."""

from __future__ import annotations

import hashlib
import json
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4


ARTIFACT_SCHEMA_VERSION = 1


class ArtifactError(ValueError):
    """Raised when an artifact contract is invalid."""


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class Artifact:
    """Immutable identity and physical description of a project artifact."""

    id: str
    project_id: str
    kind: str
    relative_path: str
    mime_type: str | None
    size_bytes: int
    sha256: str
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = ARTIFACT_SCHEMA_VERSION

    @classmethod
    def from_file(cls, project_id: str, relative_path: str, root: Path, kind: str = "file") -> "Artifact":
        path = (Path(root) / relative_path).resolve()
        root_resolved = Path(root).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError as exc:
            raise ArtifactError("Artifact path must remain inside the project root.") from exc
        if not path.is_file():
            raise ArtifactError(f"Artifact file does not exist: {relative_path}")
        mime_type, _ = mimetypes.guess_type(path.name)
        return cls(
            id=str(uuid4()),
            project_id=project_id,
            kind=kind,
            relative_path=path.relative_to(root_resolved).as_posix(),
            mime_type=mime_type,
            size_bytes=path.stat().st_size,
            sha256=sha256_file(path),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "project_id": self.project_id,
            "kind": self.kind,
            "relative_path": self.relative_path,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Artifact":
        required = ("schema_version", "id", "project_id", "kind", "relative_path", "mime_type", "size_bytes", "sha256", "metadata")
        if not isinstance(data, dict):
            raise ArtifactError("Artifact must be a JSON object.")
        missing = [key for key in required if key not in data]
        if missing:
            raise ArtifactError(f"Artifact is missing fields: {', '.join(missing)}")
        if data["schema_version"] != ARTIFACT_SCHEMA_VERSION:
            raise ArtifactError(f"Unsupported artifact schema: {data['schema_version']}")
        if not all(isinstance(data[key], str) and data[key] for key in ("id", "project_id", "kind", "relative_path", "sha256")):
            raise ArtifactError("Artifact identity fields must be non-empty strings.")
        if data["relative_path"].startswith("/") or "\\" in data["relative_path"]:
            raise ArtifactError("Artifact relative_path must use safe POSIX-relative paths.")
        if not isinstance(data["size_bytes"], int) or isinstance(data["size_bytes"], bool) or data["size_bytes"] < 0:
            raise ArtifactError("Artifact size_bytes must be a non-negative integer.")
        if data["mime_type"] is not None and not isinstance(data["mime_type"], str):
            raise ArtifactError("Artifact mime_type must be a string or null.")
        if not isinstance(data["metadata"], dict):
            raise ArtifactError("Artifact metadata must be an object.")
        return cls(**{key: data[key] for key in required})

    def fingerprint(self) -> str:
        """Return a stable content fingerprint for deterministic deduplication."""
        return self.sha256

    def json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
