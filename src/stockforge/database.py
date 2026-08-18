"""SQLite persistence layer."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .asset import Asset


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'registered',
    relative_path TEXT,
    mime_type TEXT,
    size_bytes INTEGER,
    checksum_sha256 TEXT,
    source TEXT NOT NULL DEFAULT 'manual',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, relative_path),
    UNIQUE(project_id, name)
);

CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_checksum ON assets(checksum_sha256);
"""


class Database:
    """Small SQLite wrapper used by the StockForge core."""

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

    def create_asset(self, asset: Asset) -> Asset:
        record = asset.to_record()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO assets
                (id, project_id, name, asset_type, status, relative_path, mime_type,
                 size_bytes, checksum_sha256, source, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record["id"], record["project_id"], record["name"], record["asset_type"],
                    record["status"], record["relative_path"], record["mime_type"],
                    record["size_bytes"], record["checksum_sha256"], record["source"],
                    json.dumps(record["metadata"], ensure_ascii=False, sort_keys=True),
                ),
            )
            row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset.id,)).fetchone()
        return self._asset_from_row(row)

    def list_assets(self, project_id: str | None = None) -> list[Asset]:
        with self.connect() as conn:
            if project_id:
                rows = conn.execute(
                    "SELECT * FROM assets WHERE project_id = ? ORDER BY created_at DESC",
                    (project_id,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM assets ORDER BY created_at DESC").fetchall()
        return [self._asset_from_row(row) for row in rows]

    @staticmethod
    def _asset_from_row(row: sqlite3.Row) -> Asset:
        data: dict[str, Any] = dict(row)
        data["metadata"] = json.loads(data.pop("metadata_json"))
        return Asset.from_record(data)
