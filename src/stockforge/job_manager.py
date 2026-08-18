"""Persistent job queue service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from .database import Database
from .job import Job, JobError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class JobManager:
    """Coordinates durable job creation and worker-facing queue operations."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        job_type: str,
        payload: dict | None = None,
        priority: int = 0,
        max_attempts: int = 3,
    ) -> Job:
        job = Job(
            id=str(uuid4()),
            project_id=project_id,
            job_type=job_type,
            priority=priority,
            payload=payload or {},
            max_attempts=max_attempts,
        )
        return self.database.create_job(job)

    def list(self, project_id: str | None = None, status: str | None = None) -> list[Job]:
        if status is not None and status not in {"queued", "running", "succeeded", "failed", "cancelled"}:
            raise JobError(f"Unsupported job status: {status}")
        return self.database.list_jobs(project_id=project_id, status=status)

    def claim_next(self, worker_id: str) -> Job | None:
        if not worker_id or len(worker_id) > 128:
            raise JobError("worker_id must be between 1 and 128 characters.")
        return self.database.claim_next_job(worker_id)

    def complete(self, job_id: str, result: dict | None = None) -> Job:
        return self.database.complete_job(job_id, result or {})

    def fail(self, job_id: str, error: str, retry_delay_seconds: int = 0) -> Job:
        if not error:
            raise JobError("error must be non-empty.")
        if retry_delay_seconds < 0:
            raise JobError("retry_delay_seconds cannot be negative.")
        return self.database.fail_job(job_id, error, retry_delay_seconds)

    def cancel(self, job_id: str) -> Job:
        return self.database.cancel_job(job_id)
