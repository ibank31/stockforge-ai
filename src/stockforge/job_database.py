"""SQLite persistence for the durable job queue."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .database import Database
from .job import Job, JobError


JOB_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    priority INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    available_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    worker_id TEXT,
    result_json TEXT,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    finished_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_jobs_queue ON jobs(status, available_at, priority, created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_project_id ON jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
"""


class JobDatabase(Database):
    """Database extension that owns the persistent job queue schema."""

    def connect(self) -> sqlite3.Connection:
        conn = super().connect()
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def initialize(self) -> None:
        super().initialize()
        with self.connect() as conn:
            conn.executescript(JOB_SCHEMA)

    def create_job(self, job: Job) -> Job:
        record = job.to_record()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO jobs
                (id, project_id, job_type, status, priority, payload_json, attempts, max_attempts,
                 available_at, worker_id, result_json, error, started_at, finished_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?, ?, ?, ?, ?)""",
                (
                    record["id"], record["project_id"], record["job_type"], record["status"],
                    record["priority"], json.dumps(record["payload"], ensure_ascii=False, sort_keys=True),
                    record["attempts"], record["max_attempts"], record["available_at"],
                    record["worker_id"],
                    json.dumps(record["result"], ensure_ascii=False, sort_keys=True) if record["result"] is not None else None,
                    record["error"], record["started_at"], record["finished_at"],
                ),
            )
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job.id,)).fetchone()
        return self._job_from_row(row)

    def get_job(self, job_id: str) -> Job:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise JobError(f"Job not found: {job_id}")
        return self._job_from_row(row)

    def list_jobs(self, project_id: str | None = None, status: str | None = None) -> list[Job]:
        query = "SELECT * FROM jobs"
        clauses: list[str] = []
        params: list[str] = []
        if project_id is not None:
            clauses.append("project_id = ?")
            params.append(project_id)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY priority DESC, created_at ASC"
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._job_from_row(row) for row in rows]

    def claim_next_job(self, worker_id: str) -> Job | None:
        with self.connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """SELECT * FROM jobs
                WHERE status = 'queued' AND available_at <= CURRENT_TIMESTAMP
                ORDER BY priority DESC, created_at ASC
                LIMIT 1"""
            ).fetchone()
            if row is None:
                return None
            updated = conn.execute(
                """UPDATE jobs
                SET status = 'running', worker_id = ?, attempts = attempts + 1,
                    started_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'queued'""",
                (worker_id, row["id"]),
            )
            if updated.rowcount != 1:
                raise JobError("Unable to claim the selected job safely.")
            claimed = conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()
        return self._job_from_row(claimed)

    def complete_job(self, job_id: str, result: dict[str, Any]) -> Job:
        with self.connect() as conn:
            updated = conn.execute(
                """UPDATE jobs
                SET status = 'succeeded', result_json = ?, error = NULL,
                    finished_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'running'""",
                (json.dumps(result, ensure_ascii=False, sort_keys=True), job_id),
            )
            if updated.rowcount != 1:
                raise JobError("Only a running job can be completed.")
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._job_from_row(row)

    def fail_job(self, job_id: str, error: str, retry_delay_seconds: int) -> Job:
        with self.connect() as conn:
            row = conn.execute("SELECT attempts, max_attempts, status FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if row is None:
                raise JobError(f"Job not found: {job_id}")
            if row["status"] != "running":
                raise JobError("Only a running job can be failed.")
            if row["attempts"] < row["max_attempts"]:
                conn.execute(
                    """UPDATE jobs
                    SET status = 'queued', available_at = datetime('now', '+' || ? || ' seconds'),
                        worker_id = NULL, error = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND status = 'running'""",
                    (retry_delay_seconds, error, job_id),
                )
            else:
                conn.execute(
                    """UPDATE jobs
                    SET status = 'failed', worker_id = NULL, error = ?,
                        finished_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND status = 'running'""",
                    (error, job_id),
                )
            result = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._job_from_row(result)

    def cancel_job(self, job_id: str) -> Job:
        with self.connect() as conn:
            updated = conn.execute(
                """UPDATE jobs
                SET status = 'cancelled', worker_id = NULL,
                    finished_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status IN ('queued', 'running')""",
                (job_id,),
            )
            if updated.rowcount != 1:
                raise JobError("Only queued or running jobs can be cancelled.")
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._job_from_row(row)

    @staticmethod
    def _job_from_row(row: sqlite3.Row) -> Job:
        data: dict[str, Any] = dict(row)
        data["payload"] = json.loads(data.pop("payload_json"))
        result_json = data.pop("result_json")
        data["result"] = json.loads(result_json) if result_json is not None else None
        return Job.from_record(data)
