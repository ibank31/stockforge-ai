"""Secure ingestion of provider output references into StockForge artifacts."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .artifact import Artifact, ArtifactError


class ArtifactIngestionError(ArtifactError):
    """Raised when a provider output cannot be safely ingested."""


@dataclass(frozen=True, slots=True)
class ProviderOutputRef:
    """Provider-owned reference to a generated output file."""

    filename: str
    subfolder: str = ""
    output_type: str = "output"
    node_id: str | None = None


class ArtifactIngestor:
    """Copies provider outputs into a controlled project-owned artifact area."""

    def __init__(self, project_root: Path, *, output_dir: str = "artifacts") -> None:
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise ArtifactIngestionError("Project root must be an existing directory")
        candidate = (self.project_root / output_dir).resolve()
        try:
            candidate.relative_to(self.project_root)
        except ValueError as exc:
            raise ArtifactIngestionError("Artifact output directory must remain inside the project root") from exc
        self.output_root = candidate
        self.output_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_component(value: str, field: str) -> str:
        if not isinstance(value, str) or not value or value in {".", ".."}:
            raise ArtifactIngestionError(f"Provider {field} must be a non-empty path component")
        path = Path(value)
        if path.is_absolute() or len(path.parts) != 1 or path.name != value:
            raise ArtifactIngestionError(f"Provider {field} must be a single safe path component")
        return value

    def resolve_source(self, provider_root: Path, ref: ProviderOutputRef) -> Path:
        """Resolve a provider reference without allowing traversal or absolute paths."""
        root = Path(provider_root).resolve()
        filename = self._safe_component(ref.filename, "filename")
        relative = Path(ref.subfolder) / filename if ref.subfolder else Path(filename)
        source = (root / relative).resolve()
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise ArtifactIngestionError("Provider output escapes the configured provider root") from exc
        if not source.is_file():
            raise ArtifactIngestionError(f"Provider output does not exist: {relative.as_posix()}")
        return source

    def ingest(
        self,
        *,
        project_id: str,
        provider_root: Path,
        ref: ProviderOutputRef,
        kind: str = "generated-image",
        metadata: dict | None = None,
    ) -> Artifact:
        """Import one provider output and return its immutable artifact identity."""
        source = self.resolve_source(provider_root, ref)
        suffix = source.suffix.lower()
        artifact_name = f"{uuid4().hex}{suffix}"
        destination = (self.output_root / artifact_name).resolve()
        destination.relative_to(self.output_root)
        shutil.copy2(source, destination)
        try:
            artifact = Artifact.from_file(
                project_id=project_id,
                relative_path=destination.relative_to(self.project_root).as_posix(),
                root=self.project_root,
                kind=kind,
            )
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        if metadata:
            artifact = Artifact(
                id=artifact.id,
                project_id=artifact.project_id,
                kind=artifact.kind,
                relative_path=artifact.relative_path,
                mime_type=artifact.mime_type,
                size_bytes=artifact.size_bytes,
                sha256=artifact.sha256,
                metadata=dict(metadata),
            )
        return artifact
