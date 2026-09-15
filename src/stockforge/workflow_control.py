"""Durable workflow observability and control for StockForge browser jobs."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

STAGES = {"RECEIVED": 5, "ANALYZING": 12, "PLANNING": 20, "QUEUED": 28, "GENERATING": 55, "INGESTING": 68, "SIMILARITY_GATE": 78, "TECHNICAL_QA": 86, "FINALIZATION": 92, "HUMAN_REVIEW": 96, "READY_UPLOAD_ADOBE": 100}

class WorkflowControl:
    def __init__(self, database: Any) -> None:
        self.database = database
        self._lock = threading.Lock()

    def initialize(self) -> None:
        with self.database.connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY, reference_id TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'active', current_stage TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0, provider_id TEXT, provider_job_id TEXT,
                current_job_id TEXT, error TEXT, metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
            CREATE TABLE IF NOT EXISTS workflow_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, workflow_id TEXT NOT NULL, job_id TEXT,
                stage TEXT NOT NULL, status TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT NOT NULL,
                provider_id TEXT, provider_job_id TEXT, details_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_events_workflow ON workflow_events(workflow_id, id);
            """)

    def create(self, reference_id: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        workflow_id = str(uuid.uuid4())
        with self.database.connect() as conn:
            conn.execute("INSERT INTO workflows (id, reference_id, current_stage, progress, metadata_json) VALUES (?, ?, 'RECEIVED', ?, ?)", (workflow_id, reference_id, STAGES['RECEIVED'], json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)))
        return self.event(workflow_id, stage="RECEIVED", message="Reference received.")

    def get_for_reference(self, reference_id: str) -> dict[str, Any] | None:
        with self.database.connect() as conn:
            row = conn.execute("SELECT id FROM workflows WHERE reference_id = ?", (reference_id,)).fetchone()
        return self.get(str(row["id"])) if row else None

    def get(self, workflow_id: str) -> dict[str, Any]:
        with self.database.connect() as conn:
            row = conn.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()
            if row is None:
                raise KeyError(f"Workflow not found: {workflow_id}")
            rows = conn.execute("SELECT * FROM workflow_events WHERE workflow_id = ? ORDER BY id ASC LIMIT 200", (workflow_id,)).fetchall()
        data = dict(row)
        data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
        data["events"] = [self._event(r) for r in rows]
        data["last_event"] = data["events"][-1] if data["events"] else None
        data["stuck"] = self._stuck(data)
        return data

    def snapshot_for_job(self, job: Any) -> dict[str, Any] | None:
        workflow_id = dict((job.payload or {}).get("parameters") or {}).get("workflow_id")
        if not workflow_id:
            return None
        try:
            return self.get(str(workflow_id))
        except KeyError:
            return None

    def attach_job(self, workflow_id: str, job_id: str) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE workflows SET current_job_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (job_id, workflow_id))

    def event(self, workflow_id: str, *, stage: str, status: str = "active", progress: int | None = None, message: str, job_id: str | None = None, provider_id: str | None = None, provider_job_id: str | None = None, details: dict[str, Any] | None = None) -> dict[str, Any]:
        if stage not in STAGES:
            raise ValueError(f"Unknown workflow stage: {stage}")
        progress = STAGES[stage] if progress is None else max(0, min(100, int(progress)))
        terminal = status in {"ready", "blocked", "failed", "cancelled"}
        with self._lock, self.database.connect() as conn:
            conn.execute("""UPDATE workflows SET status = ?, current_stage = ?, progress = ?,
                provider_id = COALESCE(?, provider_id), provider_job_id = COALESCE(?, provider_job_id),
                current_job_id = COALESCE(?, current_job_id), error = CASE WHEN ? = 'failed' THEN ? ELSE error END,
                updated_at = CURRENT_TIMESTAMP, completed_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE completed_at END
                WHERE id = ?""", (status, stage, progress, provider_id, provider_job_id, job_id, status, message, terminal, workflow_id))
            conn.execute("INSERT INTO workflow_events (workflow_id, job_id, stage, status, progress, message, provider_id, provider_job_id, details_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (workflow_id, job_id, stage, status, progress, message, provider_id, provider_job_id, json.dumps(details or {}, ensure_ascii=False, sort_keys=True)))
        return self.get(workflow_id)

    def heartbeat(self, workflow_id: str, *, stage: str, job_id: str | None = None, provider_id: str | None = None, provider_job_id: str | None = None) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE workflows SET current_stage = ?, progress = ?, provider_id = COALESCE(?, provider_id), provider_job_id = COALESCE(?, provider_job_id), current_job_id = COALESCE(?, current_job_id), updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'active'", (stage, STAGES.get(stage, 0), provider_id, provider_job_id, job_id, workflow_id))

    def _stuck(self, data: dict[str, Any]) -> bool:
        if data.get("status") != "active":
            return False
        try:
            stamp = datetime.fromisoformat(str(data["updated_at"]).replace("Z", "+00:00")).astimezone(timezone.utc)
            threshold = max(30, int(os.getenv("STOCKFORGE_STUCK_SECONDS", "180")))
            return (datetime.now(timezone.utc) - stamp).total_seconds() >= threshold
        except (ValueError, TypeError, KeyError):
            return False

    @staticmethod
    def _event(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["details"] = json.loads(data.pop("details_json") or "{}")
        return data

class HeartbeatLoop:
    def __init__(self, control: WorkflowControl, workflow_id: str, *, stage: str, job_id: str, provider_id: str | None = None, interval: float = 15.0) -> None:
        self.control, self.workflow_id, self.stage, self.job_id, self.provider_id = control, workflow_id, stage, job_id, provider_id
        self.provider_job_id = None
        self.interval = max(2.0, float(interval))
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
    def __enter__(self) -> "HeartbeatLoop":
        self._thread.start(); return self
    def __exit__(self, *_: object) -> None:
        self._stop.set(); self._thread.join(timeout=self.interval + 1)
    def set_provider_job_id(self, value: str | None) -> None:
        self.provider_job_id = value
    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            try: self.control.heartbeat(self.workflow_id, stage=self.stage, job_id=self.job_id, provider_id=self.provider_id, provider_job_id=self.provider_job_id)
            except Exception: pass
