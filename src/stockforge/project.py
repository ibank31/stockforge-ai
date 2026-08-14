"""Project management services."""

from __future__ import annotations

import re
from pathlib import Path

from .config import StockForgeConfig
from .database import Database


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
        project_path.mkdir(parents=True)
        for folder in ("assets", "output", "temp", "logs", "metadata"):
            (project_path / folder).mkdir()
        (project_path / "project.json").write_text(
            '{\n  "name": ' + repr(name).replace("'", '"') + ',\n  "version": 1\n}\n',
            encoding="utf-8",
        )
        return self.database.create_project(name, project_path)

    def list(self) -> list[dict]:
        return self.database.list_projects()
