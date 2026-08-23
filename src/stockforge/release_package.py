"""Build a bounded Termux-downloadable package from one successful execution."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .database import Database


class ReleasePackageError(RuntimeError):
    """Raised when an execution cannot safely be released for download."""


@dataclass(frozen=True, slots=True)
class ReleasePackage:
    """A zip package containing only generated image outputs and provenance."""

    path: Path
    execution_id: str
    artifact_ids: tuple[str, ...]
    status: str = "review_ready"

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "execution_id": self.execution_id,
            "artifact_ids": list(self.artifact_ids),
            "status": self.status,
        }


def build_release_package(
    *,
    database: Database,
    project_id: str,
    project_root: Path,
    execution_id: str,
    destination_dir: Path | None = None,
) -> ReleasePackage:
    """Package one successful generation without including logs or raw worker data."""
    root = Path(project_root).resolve()
    execution = database.get_execution(execution_id)
    if execution is None:
        raise ReleasePackageError(f"Execution not found: {execution_id}")
    if execution.project_id != project_id:
        raise ReleasePackageError("Execution does not belong to the requested project.")
    if execution.state != "succeeded":
        raise ReleasePackageError("Only succeeded executions can be packaged for download.")
    if not execution.artifact_ids:
        raise ReleasePackageError("Execution has no generated artifacts.")

    artifacts = []
    for artifact_id in execution.artifact_ids:
        artifact = database.get_artifact(artifact_id)
        if artifact is None:
            raise ReleasePackageError(f"Execution artifact is missing: {artifact_id}")
        if artifact.project_id != project_id or artifact.kind != "generated-image":
            raise ReleasePackageError(f"Execution artifact is not an eligible generated image: {artifact_id}")
        source = (root / artifact.relative_path).resolve()
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise ReleasePackageError("Artifact path escapes the project workspace.") from exc
        if not source.is_file():
            raise ReleasePackageError(f"Generated artifact file is missing: {artifact.relative_path}")
        artifacts.append((artifact, source))

    target_dir = Path(destination_dir or root / "deliveries").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    package_path = target_dir / f"stockforge-{execution.id}.zip"
    manifest = {
        "schema_version": 1,
        "status": "review_ready",
        "notice": "This package contains generated outputs that passed execution persistence. It is not a marketplace acceptance guarantee; human compliance review remains required.",
        "execution": execution.to_dict(),
        "artifacts": [
            {
                "id": artifact.id,
                "sha256": artifact.sha256,
                "mime_type": artifact.mime_type,
                "size_bytes": artifact.size_bytes,
                "file": f"images/{artifact.id}{source.suffix.lower()}",
            }
            for artifact, source in artifacts
        ],
    }
    readme = (
        "StockForge review-ready download package\n\n"
        "This archive contains only image outputs from the referenced successful execution and a manifest with reproducibility metadata. "
        "It does not guarantee marketplace acceptance. Perform human rights, policy, and visual review before submission.\n"
    )
    temporary_path = package_path.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for artifact, source in artifacts:
                archive.write(source, f"images/{artifact.id}{source.suffix.lower()}")
            archive.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            archive.writestr("README.txt", readme)
        temporary_path.replace(package_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return ReleasePackage(
        path=package_path,
        execution_id=execution.id,
        artifact_ids=tuple(artifact.id for artifact, _ in artifacts),
    )
