"""Canonical, resumable orchestration state for internal and external image flows.

This module deliberately coordinates existing commands; it does not replace the
protected JPEG/PNG workers and never submits a finalizer before KEEP.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class WorkflowError(RuntimeError):
    """Raised when a workflow transition is unsafe or invalid."""


VALID_MODES = {"internal", "external"}
VALID_STATES = {
    "BRIEF_READY", "PREVIEW_READY", "WAITING_FOR_EXTERNAL_SOURCE",
    "WAITING_FOR_KEEP", "KEEP", "REJECTED", "FINALIZER_READY",
    "FINALIZING", "MASTER_READY", "VISUAL_REVIEW_REQUIRED", "READY_UPLOAD",
}


@dataclass(frozen=True)
class WorkflowRecord:
    workflow_id: str
    mode: str
    project: str
    project_id: str
    candidate_id: str
    delivery_format: str
    state: str
    created_at: str
    updated_at: str
    plan: str | None = None
    brief: str | None = None
    execution_id: str | None = None
    artifact_id: str | None = None
    master_execution_id: str | None = None
    master_artifact_id: str | None = None
    source_path: str | None = None
    preview_path: str | None = None
    ready_path: str | None = None
    notice: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def workflow_path(project_root: Path, workflow_id: str) -> Path:
    return project_root / "workflows" / f"{workflow_id}.json"


def save_workflow(project_root: Path, record: WorkflowRecord) -> Path:
    directory = project_root / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    path = workflow_path(project_root, record.workflow_id)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def load_workflow(project_root: Path, workflow_id: str) -> WorkflowRecord:
    path = workflow_path(project_root, workflow_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return WorkflowRecord(**data)
    except FileNotFoundError as exc:
        raise WorkflowError(f"Workflow tidak ditemukan: {workflow_id}") from exc
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        raise WorkflowError(f"Workflow state rusak: {path}") from exc


def start_internal(*, project: str, project_id: str, candidate_id: str, delivery_format: str, plan: str, brief: str, execution_id: str, artifact_id: str, preview_path: str | None, project_root: Path) -> WorkflowRecord:
    if delivery_format not in {"jpeg", "png"}:
        raise WorkflowError("delivery_format harus jpeg atau png.")
    now = _now()
    record = WorkflowRecord(
        workflow_id=f"internal-{candidate_id}-{uuid4().hex[:10]}", mode="internal", project=project,
        project_id=project_id, candidate_id=candidate_id, delivery_format=delivery_format,
        state="WAITING_FOR_KEEP", created_at=now, updated_at=now, plan=plan, brief=brief,
        execution_id=execution_id, artifact_id=artifact_id, preview_path=preview_path,
        notice="Preview internal siap. Finalizer terkunci sampai user memberi KEEP.",
    )
    save_workflow(project_root, record)
    return record


def start_external(*, project: str, project_id: str, candidate_id: str, delivery_format: str, execution_id: str, artifact_id: str, source_path: str, preview_path: str | None, project_root: Path) -> WorkflowRecord:
    if delivery_format not in {"jpeg", "png"}:
        raise WorkflowError("delivery_format harus jpeg atau png.")
    now = _now()
    record = WorkflowRecord(
        workflow_id=f"external-{candidate_id}-{uuid4().hex[:10]}", mode="external", project=project,
        project_id=project_id, candidate_id=candidate_id, delivery_format=delivery_format,
        state="WAITING_FOR_KEEP", created_at=now, updated_at=now, execution_id=execution_id,
        artifact_id=artifact_id, source_path=source_path, preview_path=preview_path,
        notice="External source ter-import. Finalizer terkunci sampai user memberi KEEP.",
    )
    save_workflow(project_root, record)
    return record


def attest_keep(*, project_root: Path, workflow_id: str, keep: bool) -> WorkflowRecord:
    current = load_workflow(project_root, workflow_id)
    if current.state not in {"WAITING_FOR_KEEP", "PREVIEW_READY"}:
        raise WorkflowError(f"KEEP tidak valid pada state {current.state}.")
    state = "KEEP" if keep else "REJECTED"
    notice = "KEEP tercatat; boleh menyiapkan finalizer format-spesifik." if keep else "REJECT tercatat; finalizer diblokir."
    updated = WorkflowRecord(**{**current.to_dict(), "state": state, "updated_at": _now(), "notice": notice})
    save_workflow(project_root, updated)
    return updated


def mark_finalizer_ready(*, project_root: Path, workflow_id: str, master_request_path: str) -> WorkflowRecord:
    current = load_workflow(project_root, workflow_id)
    if current.state != "KEEP":
        raise WorkflowError("Finalizer hanya boleh disiapkan setelah KEEP.")
    updated = WorkflowRecord(**{**current.to_dict(), "state": "FINALIZER_READY", "updated_at": _now(), "ready_path": master_request_path, "notice": "Request finalizer siap; submit GPU masih merupakan langkah eksplisit terpisah."})
    save_workflow(project_root, updated)
    return updated


def mark_master_ready(*, project_root: Path, workflow_id: str, master_execution_id: str, master_artifact_id: str, master_path: str) -> WorkflowRecord:
    current = load_workflow(project_root, workflow_id)
    if current.state not in {"FINALIZER_READY", "FINALIZING"}:
        raise WorkflowError("Master tidak dapat dicatat sebelum request finalizer siap.")
    updated = WorkflowRecord(**{**current.to_dict(), "state": "VISUAL_REVIEW_REQUIRED", "updated_at": _now(), "master_execution_id": master_execution_id, "master_artifact_id": master_artifact_id, "ready_path": master_path, "notice": "Master teknis tersedia; wajib review visual 100% sebelum READY_UPLOAD."})
    save_workflow(project_root, updated)
    return updated
