"""Durable job domain model and validation rules."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

JOB_STATUSES = frozenset({"queued", "running", "succeeded", "failed", "cancelled"})


class JobError(ValueError):
    """Raised when a job violates the queue contract."""


@dataclass(slots=True)
class Job:
    """A persistent unit of work that can be claimed by a worker."""

    id: str
    project_id: str
    job_type: str
    status: str = "queued"
    priority: int = 0
    payload: dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    max_attempts: int = 3
    available_at: str | None = None
    worker_id: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None

    def __post_init__(self) -> None:
        try:
            UUID(self.id)
            UUID(self.project_id)
        except (ValueError, AttributeError) as exc:
            raise JobError("Job id and project_id must be valid UUID strings.") from exc
        if not self.job_type or len(self.job_type) > 128:
            raise JobError("job_type must be between 1 and 128 characters.")
        if self.status not in JOB_STATUSES:
            raise JobError(f"Unsupported job status: {self.status}")
        if not isinstance(self.priority, int) or isinstance(self.priority, bool):
            raise JobError("priority must be an integer.")
        if not isinstance(self.attempts, int) or isinstance(self.attempts, bool) or self.attempts < 0:
            raise JobError("attempts must be a non-negative integer.")
        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool) or not 1 <= self.max_attempts <= 100:
            raise JobError("max_attempts must be an integer between 1 and 100.")
        if self.attempts > self.max_attempts:
            raise JobError("attempts cannot exceed max_attempts.")
        if not isinstance(self.payload, dict):
            raise JobError("payload must be a JSON object.")
        try:
            json.dumps(self.payload, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise JobError("payload must contain JSON-serializable values.") from exc
        if self.result is not None and not isinstance(self.result, dict):
            raise JobError("result must be a JSON object or null.")

    def to_record(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "job_type": self.job_type,
            "status": self.status,
            "priority": self.priority,
            "payload": self.payload,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "available_at": self.available_at,
            "worker_id": self.worker_id,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Job":
        return cls(**record)
