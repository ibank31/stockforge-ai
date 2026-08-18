"""Asset domain model and validation rules."""

from __future__ import annotations

import hashlib
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import UUID

ASSET_STATUSES = frozenset({"registered", "processing", "ready", "failed", "archived"})
ASSET_TYPES = frozenset({"image", "vector", "video", "audio", "document", "other"})


class AssetError(ValueError):
    """Raised when an asset violates the registry contract."""


def validate_relative_path(path: str | None) -> str | None:
    if path is None or path == "":
        return None
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise AssetError("Asset path must be relative to the project workspace and cannot contain '..'.")
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        raise AssetError("Asset path must reference a file path.")
    return normalized


def checksum_file(path: Path) -> str:
    """Return the SHA-256 checksum of a file using bounded memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(slots=True)
class Asset:
    id: str
    project_id: str
    name: str
    asset_type: str = "image"
    status: str = "registered"
    relative_path: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    checksum_sha256: str | None = None
    source: str = "manual"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        try:
            UUID(self.id)
            UUID(self.project_id)
        except (ValueError, AttributeError) as exc:
            raise AssetError("Asset id and project_id must be valid UUID strings.") from exc
        if not self.name or len(self.name) > 255:
            raise AssetError("Asset name must be between 1 and 255 characters.")
        if self.asset_type not in ASSET_TYPES:
            raise AssetError(f"Unsupported asset type: {self.asset_type}")
        if self.status not in ASSET_STATUSES:
            raise AssetError(f"Unsupported asset status: {self.status}")
        self.relative_path = validate_relative_path(self.relative_path)
        if self.size_bytes is not None and (not isinstance(self.size_bytes, int) or self.size_bytes < 0):
            raise AssetError("size_bytes must be a non-negative integer or null.")
        if self.checksum_sha256 is not None:
            if len(self.checksum_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.checksum_sha256.lower()):
                raise AssetError("checksum_sha256 must be a 64-character SHA-256 hex digest.")

    @classmethod
    def from_file(
        cls,
        *,
        asset_id: str,
        project_id: str,
        name: str,
        project_root: Path,
        file_path: Path,
        asset_type: str = "image",
        source: str = "manual",
        metadata: dict[str, Any] | None = None,
    ) -> "Asset":
        root = Path(project_root).resolve()
        source_path = Path(file_path).resolve()
        try:
            relative = source_path.relative_to(root).as_posix()
        except ValueError as exc:
            raise AssetError("Asset file must be located inside the project workspace.") from exc
        if not source_path.is_file():
            raise AssetError(f"Asset file does not exist: {source_path}")
        mime_type, _ = mimetypes.guess_type(source_path.name)
        return cls(
            id=asset_id,
            project_id=project_id,
            name=name,
            asset_type=asset_type,
            relative_path=relative,
            mime_type=mime_type,
            size_bytes=source_path.stat().st_size,
            checksum_sha256=checksum_file(source_path),
            source=source,
            metadata=metadata or {},
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "status": self.status,
            "relative_path": self.relative_path,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "checksum_sha256": self.checksum_sha256,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Asset":
        return cls(**record)
