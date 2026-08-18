"""SQLite persistence layer."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class Database:
    """Small SQLite wrapper used by the core MVP."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def create_project(self, project_id: str, name: str, project_path: Path) -> dict:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO projects (id, name, path) VALUES (?, ?, ?)",
                (project_id, name, str(project_path)),
            )
        return {"id": project_id, "name": name, "path": str(project_path), "status": "active"}

    def list_projects(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, name, path, status, created_at, updated_at FROM projects ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]
