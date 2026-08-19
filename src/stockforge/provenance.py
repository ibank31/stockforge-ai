"""Auditable provenance and lineage records for generated artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

PROVENANCE_SCHEMA_VERSION = 1
LINEAGE_RELATIONS = frozenset({"input", "derived", "transformed", "variant", "upscaled", "enhanced"})

class ProvenanceError(ValueError):
    """Raised when a provenance or lineage record is invalid."""

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """Records how an artifact was produced or transformed."""
    id: str
    artifact_id: str
    project_id: str
    operation: str
    job_id: str | None = None
    execution_id: str | None = None
    pipeline_id: str | None = None
    pipeline_version: int | None = None
    pipeline_hash: str | None = None
    step_id: str | None = None
    plugin_id: str | None = None
    plugin_version: str | None = None
    model_id: str | None = None
    model_version: str | None = None
    model_hash: str | None = None
    workflow_hash: str | None = None
    prompt_hash: str | None = None
    input_artifact_ids: tuple[str, ...] = ()
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    schema_version: int = PROVENANCE_SCHEMA_VERSION

    @classmethod
    def create(cls, artifact_id: str, project_id: str, operation: str, **kwargs: Any) -> "ProvenanceRecord":
        return cls(id=str(uuid4()), artifact_id=artifact_id, project_id=project_id, operation=operation, **kwargs)

    def __post_init__(self) -> None:
        for field_name in ("id", "artifact_id", "project_id", "operation"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ProvenanceError(f"{field_name} must be a non-empty string.")
        if self.schema_version != PROVENANCE_SCHEMA_VERSION:
            raise ProvenanceError(f"Unsupported provenance schema: {self.schema_version}")
        if self.pipeline_version is not None and (not isinstance(self.pipeline_version, int) or isinstance(self.pipeline_version, bool) or self.pipeline_version < 1):
            raise ProvenanceError("pipeline_version must be a positive integer or null.")
        if not all(isinstance(item, str) and item for item in self.input_artifact_ids):
            raise ProvenanceError("input_artifact_ids must contain non-empty strings.")
        if not isinstance(self.parameters, dict) or not isinstance(self.metadata, dict):
            raise ProvenanceError("parameters and metadata must be objects.")

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "id": self.id, "artifact_id": self.artifact_id, "project_id": self.project_id, "operation": self.operation, "job_id": self.job_id, "execution_id": self.execution_id, "pipeline_id": self.pipeline_id, "pipeline_version": self.pipeline_version, "pipeline_hash": self.pipeline_hash, "step_id": self.step_id, "plugin_id": self.plugin_id, "plugin_version": self.plugin_version, "model_id": self.model_id, "model_version": self.model_version, "model_hash": self.model_hash, "workflow_hash": self.workflow_hash, "prompt_hash": self.prompt_hash, "input_artifact_ids": list(self.input_artifact_ids), "parameters": self.parameters, "metadata": self.metadata, "created_at": self.created_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProvenanceRecord":
        if not isinstance(data, dict):
            raise ProvenanceError("Provenance record must be a JSON object.")
        allowed = {"id", "artifact_id", "project_id", "operation", "job_id", "execution_id", "pipeline_id", "pipeline_version", "pipeline_hash", "step_id", "plugin_id", "plugin_version", "model_id", "model_version", "model_hash", "workflow_hash", "prompt_hash", "input_artifact_ids", "parameters", "metadata", "created_at", "schema_version"}
        if set(data) != allowed:
            missing, extra = allowed - set(data), set(data) - allowed
            details = []
            if missing: details.append(f"missing: {', '.join(sorted(missing))}")
            if extra: details.append(f"unexpected: {', '.join(sorted(extra))}")
            raise ProvenanceError("Invalid provenance fields (" + "; ".join(details) + ")")
        if not isinstance(data["input_artifact_ids"], list):
            raise ProvenanceError("input_artifact_ids must be an array.")
        return cls(id=data["id"], artifact_id=data["artifact_id"], project_id=data["project_id"], operation=data["operation"], job_id=data["job_id"], execution_id=data["execution_id"], pipeline_id=data["pipeline_id"], pipeline_version=data["pipeline_version"], pipeline_hash=data["pipeline_hash"], step_id=data["step_id"], plugin_id=data["plugin_id"], plugin_version=data["plugin_version"], model_id=data["model_id"], model_version=data["model_version"], model_hash=data["model_hash"], workflow_hash=data["workflow_hash"], prompt_hash=data["prompt_hash"], input_artifact_ids=tuple(data["input_artifact_ids"]), parameters=data["parameters"], metadata=data["metadata"], created_at=data["created_at"], schema_version=data["schema_version"])

    def json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

@dataclass(frozen=True, slots=True)
class ArtifactLineage:
    """Explicit parent/child relationship between immutable artifacts."""
    id: str
    artifact_id: str
    parent_artifact_id: str
    project_id: str
    relation: str = "derived"
    execution_id: str | None = None
    sequence: int = 0
    created_at: str = field(default_factory=utc_now)
    schema_version: int = PROVENANCE_SCHEMA_VERSION

    @classmethod
    def create(cls, artifact_id: str, parent_artifact_id: str, project_id: str, *, relation: str = "derived", **kwargs: Any) -> "ArtifactLineage":
        return cls(id=str(uuid4()), artifact_id=artifact_id, parent_artifact_id=parent_artifact_id, project_id=project_id, relation=relation, **kwargs)

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in (self.id, self.artifact_id, self.parent_artifact_id, self.project_id)):
            raise ProvenanceError("lineage identity fields must be non-empty strings")
        if self.artifact_id == self.parent_artifact_id:
            raise ProvenanceError("artifact cannot be its own lineage parent")
        if self.relation not in LINEAGE_RELATIONS:
            raise ProvenanceError(f"Unsupported lineage relation: {self.relation}")
        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ProvenanceError("sequence must be a non-negative integer")
        if self.schema_version != PROVENANCE_SCHEMA_VERSION:
            raise ProvenanceError(f"Unsupported lineage schema: {self.schema_version}")

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "id": self.id, "artifact_id": self.artifact_id, "parent_artifact_id": self.parent_artifact_id, "project_id": self.project_id, "relation": self.relation, "execution_id": self.execution_id, "sequence": self.sequence, "created_at": self.created_at}
