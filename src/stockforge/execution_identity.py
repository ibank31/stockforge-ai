"""Deterministic identity rules for durable generation executions."""

from __future__ import annotations

from uuid import NAMESPACE_URL, UUID, uuid5


class ExecutionIdentityError(ValueError):
    """Raised when a durable execution identity cannot be derived safely."""


def execution_id_for_job(project_id: str, job_id: str) -> str:
    """Return the stable execution UUID for one StockForge job."""
    if not isinstance(project_id, str) or not project_id:
        raise ExecutionIdentityError("project_id must be a non-empty string")
    if not isinstance(job_id, str) or not job_id:
        raise ExecutionIdentityError("job_id must be a non-empty string")
    return str(uuid5(NAMESPACE_URL, f"stockforge:execution:{project_id}:{job_id}"))


def is_execution_uuid(value: str) -> bool:
    """Return whether *value* is a valid UUID string."""
    try:
        UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True
