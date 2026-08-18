"""SQLite persistence layer."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .artifact import Artifact
from .asset import Asset
from .execution_record import GenerationExecutionRecord


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

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    mime_type TEXT,
    size_bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, relative_path),
    UNIQUE(project_id, sha256)
);

CREATE TABLE IF NOT EXISTS generation_executions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    state TEXT NOT NULL,
    job_id TEXT,
    provider_id TEXT,
    provider_job_id TEXT,
    pipeline_id TEXT,
    pipeline_version INTEGER,
    step_id TEXT,
    plugin_id TEXT,
    plugin_version TEXT,
    model_id TEXT,
    model_version TEXT,
    workflow_hash TEXT,
    prompt_hash TEXT,
    artifact_ids_json TEXT NOT NULL DEFAULT '[]',
    input_artifact_ids_json TEXT NOT NULL DEFAULT '[]',
    parameters_json TEXT NOT NULL DEFAULT '{}',
    error_code TEXT,
    error_message TEXT,
    schema_version INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_checksum ON assets(checksum_sha256);
CREATE INDEX IF NOT EXISTS idx_artifacts_project_id ON artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_sha256 ON artifacts(sha256);
CREATE INDEX IF NOT EXISTS idx_execution_project_id ON generation_executions(project_id);
CREATE INDEX IF NOT EXISTS idx_execution_provider_job ON generation_executions(provider_job_id);
CREATE INDEX IF NOT EXISTS idx_execution_state ON generation_executions(state);
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

    def create_artifact(self, artifact: Artifact) -> Artifact:
        record = artifact.to_dict()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO artifacts
                (id, project_id, kind, relative_path, mime_type, size_bytes, sha256, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record["id"], record["project_id"], record["kind"], record["relative_path"],
                    record["mime_type"], record["size_bytes"], record["sha256"],
                    json.dumps(record["metadata"], ensure_ascii=False, sort_keys=True),
                ),
            )
        return artifact

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)).fetchone()
        return self._artifact_from_row(row) if row else None

    def list_artifacts(self, project_id: str | None = None) -> list[Artifact]:
        with self.connect() as conn:
            if project_id:
                rows = conn.execute(
                    "SELECT * FROM artifacts WHERE project_id = ? ORDER BY created_at DESC", (project_id,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM artifacts ORDER BY created_at DESC").fetchall()
        return [self._artifact_from_row(row) for row in rows]

    def create_execution(self, record: GenerationExecutionRecord) -> GenerationExecutionRecord:
        data = record.to_dict()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO generation_executions
                (id, project_id, operation, state, job_id, provider_id, provider_job_id,
                 pipeline_id, pipeline_version, step_id, plugin_id, plugin_version,
                 model_id, model_version, workflow_hash, prompt_hash, artifact_ids_json,
                 input_artifact_ids_json, parameters_json, error_code, error_message, schema_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["id"], data["project_id"], data["operation"], data["state"], data["job_id"],
                    data["provider_id"], data["provider_job_id"], data["pipeline_id"], data["pipeline_version"],
                    data["step_id"], data["plugin_id"], data["plugin_version"], data["model_id"],
                    data["model_version"], data["workflow_hash"], data["prompt_hash"],
                    json.dumps(data["artifact_ids"], sort_keys=True), json.dumps(data["input_artifact_ids"], sort_keys=True),
                    json.dumps(data["parameters"], ensure_ascii=False, sort_keys=True), data["error_code"],
                    data["error_message"], data["schema_version"],
                ),
            )
        return record

    def get_execution(self, execution_id: str) -> GenerationExecutionRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM generation_executions WHERE id = ?", (execution_id,)).fetchone()
        return self._execution_from_row(row) if row else None

    @staticmethod
    def _asset_from_row(row: sqlite3.Row) -> Asset:
        data: dict[str, Any] = dict(row)
        data["metadata"] = json.loads(data.pop("metadata_json"))
        return Asset.from_record(data)

    @staticmethod
    def _artifact_from_row(row: sqlite3.Row) -> Artifact:
        data: dict[str, Any] = dict(row)
        data.pop("created_at", None)
        data["metadata"] = json.loads(data.pop("metadata_json"))
        data["schema_version"] = 1
        return Artifact.from_dict(data)

    @staticmethod
    def _execution_from_row(row: sqlite3.Row) -> GenerationExecutionRecord:
        data: dict[str, Any] = dict(row)
        data["artifact_ids"] = json.loads(data.pop("artifact_ids_json"))
        data["input_artifact_ids"] = json.loads(data.pop("input_artifact_ids_json"))
        data["parameters"] = json.loads(data.pop("parameters_json"))
        data.pop("created_at", None)
        return GenerationExecutionRecord.from_dict(data)
