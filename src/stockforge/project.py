"""Project management services."""

from __future__ import annotations

import re
import sqlite3
import shutil
from pathlib import Path
from uuid import uuid4

from .config import StockForgeConfig
from .database import Database
from .manifest import ProjectManifest


_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


class ProjectManager:
    def __init__(self, config: StockForgeConfig, database: Database) -> None:
        self.config = config
        self.database = database

    def create(self, name: str) -> dict:
        if not _NAME_RE.fullmatch(name):
            raise ValueError("Project name must be 1-64 characters and use letters, numbers, ., _, or -.")

        project_path = self.config.workspace / "projects" / name
        if project_path.exists():
            raise FileExistsError(f"Project already exists: {name}")

        project_id = str(uuid4())
        manifest = ProjectManifest.create(project_id=project_id, name=name)

        try:
            project_path.mkdir(parents=True)
            for folder in ("assets", "output", "temp", "logs", "metadata"):
                (project_path / folder).mkdir()
            manifest.write(project_path / "project.json")
            return self.database.create_project(
                project_id=project_id,
                name=name,
                project_path=project_path,
            )
        except sqlite3.IntegrityError as exc:
            shutil.rmtree(project_path, ignore_errors=True)
            raise ValueError(f"Project already exists: {name}") from exc
        except Exception:
            shutil.rmtree(project_path, ignore_errors=True)
            raise

    def list(self) -> list[dict]:
        return self.database.list_projects()
