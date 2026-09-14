"""Filesystem/database reconciliation for artifact files."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .database import Database

@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    scanned_files: int
    registered_files: int
    orphan_files: tuple[str, ...]

def find_orphan_artifacts(database: Database, project_id: str, project_root: Path) -> ReconciliationReport:
    root = Path(project_root).resolve()
    artifact_root = root / "artifacts"
    registered = {a.relative_path for a in database.list_artifacts(project_id)}
    files = []
    if artifact_root.is_dir():
        for path in artifact_root.rglob("*"):
            if path.is_file():
                files.append(path.relative_to(root).as_posix())
    orphans = tuple(sorted(path for path in files if path not in registered))
    return ReconciliationReport(len(files), len(registered), orphans)
