"""Deterministic identity rules for durable generation executions."""

from __future__ import annotations

from uuid import NAMESPACE_URL, UUID, uuid5


class ExecutionIdentityError(ValueError):
    """Raised when a durable execution identity cannot be derived safely."""


def execution_id_for_job(project_id: str, job_id: str) -> str:
    """Return the stable execution UUID for one StockForge job.

    A job represents one logical generation request. Worker retries must therefore
    reuse the same execution identity instead of creating another execution row.
    UUID5 keeps the identity deterministic without requiring a new database table.
    """
    if not project_id or not isinstance(project_id, str):
        raise ExecutionIdentityError("project_id must be a non-empty string")
    if not job_id or not isinstance(job_id, str):
        raise ExecutionIdentityError("job_id must be a non-empty string")
    return str(uuid5(NAMESPACE_URL, f"stockforge:execution:{project_id}:{job_id}"))


def is_execution_uuid(value: str) -> bool:
    """Return whether *value* is a valid UUID string."""
    try:
        UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return True
