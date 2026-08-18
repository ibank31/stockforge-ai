"""Immutable record binding generation execution to its outputs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal
from uuid import uuid4

EXECUTION_RECORD_SCHEMA_VERSION = 1
EXECUTION_STATES = frozenset({"submitted", "running", "completed", "succeeded", "failed", "cancelled"})


class ExecutionRecordError(ValueError):
    """Raised when an execution record violates its contract."""


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class GenerationExecutionRecord:
    """Canonical audit record for one generation attempt.

    Provider completion is deliberately distinct from StockForge success. A
    completed provider job may have outputs awaiting secure artifact ingestion.
    Only an execution with registered artifact IDs may become succeeded.
    """

    id: str
    project_id: str
    operation: str = "image.generate"
    state: Literal["submitted", "running", "completed", "succeeded", "failed", "cancelled"] = "submitted"
    job_id: str | None = None
    provider_id: str | None = None
    provider_job_id: str | None = None
    pipeline_id: str | None = None
    pipeline_version: int | None = None
    step_id: str | None = None
    plugin_id: str | None = None
    plugin_version: str | None = None
    model_id: str | None = None
    model_version: str | None = None
    workflow_hash: str | None = None
    prompt_hash: str | None = None
    artifact_ids: tuple[str, ...] = ()
    input_artifact_ids: tuple[str, ...] = ()
    parameters: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    schema_version: int = EXECUTION_RECORD_SCHEMA_VERSION

    @classmethod
    def create(cls, project_id: str, *, prompt: str | None = None, **kwargs: Any) -> "GenerationExecutionRecord":
        return cls(
            id=str(uuid4()),
            project_id=project_id,
            prompt_hash=_hash_prompt(prompt) if prompt is not None else kwargs.pop("prompt_hash", None),
            **kwargs,
        )

    def __post_init__(self) -> None:
        if not self.id or not self.project_id or not self.operation:
            raise ExecutionRecordError("id, project_id, and operation must be non-empty")
        if self.state not in EXECUTION_STATES:
            raise ExecutionRecordError(f"Unsupported execution state: {self.state}")
        if self.schema_version != EXECUTION_RECORD_SCHEMA_VERSION:
            raise ExecutionRecordError(f"Unsupported execution record schema: {self.schema_version}")
        if self.pipeline_version is not None and (not isinstance(self.pipeline_version, int) or isinstance(self.pipeline_version, bool) or self.pipeline_version < 1):
            raise ExecutionRecordError("pipeline_version must be a positive integer or null")
        if not all(isinstance(item, str) and item for item in self.artifact_ids + self.input_artifact_ids):
            raise ExecutionRecordError("artifact IDs must contain non-empty strings")
        if not isinstance(self.parameters, dict):
            raise ExecutionRecordError("parameters must be an object")
        if self.state == "succeeded" and not self.artifact_ids:
            raise ExecutionRecordError("succeeded execution requires at least one artifact")
        if self.state == "failed" and (not self.error_code or not self.error_message):
            raise ExecutionRecordError("failed execution requires error_code and error_message")
        if self.state == "succeeded" and (self.error_code is not None or self.error_message is not None):
            raise ExecutionRecordError("succeeded execution cannot contain an error")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "project_id": self.project_id,
            "operation": self.operation,
            "state": self.state,
            "job_id": self.job_id,
            "provider_id": self.provider_id,
            "provider_job_id": self.provider_job_id,
            "pipeline_id": self.pipeline_id,
            "pipeline_version": self.pipeline_version,
            "step_id": self.step_id,
            "plugin_id": self.plugin_id,
            "plugin_version": self.plugin_version,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "workflow_hash": self.workflow_hash,
            "prompt_hash": self.prompt_hash,
            "artifact_ids": list(self.artifact_ids),
            "input_artifact_ids": list(self.input_artifact_ids),
            "parameters": self.parameters,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }

    def json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
