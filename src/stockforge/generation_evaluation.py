"""Structured human feedback for improving future generation decisions.

This module is deliberately offline and append-only. It records what happened
when a generated asset was reviewed; it never predicts sales, changes a prompt
retroactively, or triggers another generation.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4


class EvaluationError(ValueError):
    """Raised when an evaluation record is incomplete or unsafe."""


DECISIONS = frozenset({"accept", "reject", "review"})
MARKETPLACE_OUTCOMES = frozenset({
    "not_submitted",
    "submitted",
    "accepted",
    "rejected",
    "downloaded",
})
SCORE_FIELDS = (
    "visual_quality",
    "technical_quality",
    "buyer_fit",
    "metadata_accuracy",
)


def _required(value: object, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise EvaluationError(f"{field} is required.")
    if len(result) > 240:
        raise EvaluationError(f"{field} exceeds 240 characters.")
    return result


def _score(value: int, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 5:
        raise EvaluationError(f"{field} must be an integer from 0 to 5.")
    return value


@dataclass(frozen=True, slots=True)
class GenerationEvaluation:
    """One human review outcome tied to an immutable generation identity."""

    evaluation_id: str
    execution_id: str
    artifact_id: str
    lane_key: str
    buyer_job: str
    product_kind: str
    delivery_format: str
    provider_id: str
    model_id: str
    workflow_hash: str
    decision: str
    visual_quality: int
    technical_quality: int
    buyer_fit: int
    metadata_accuracy: int
    rejection_reasons: tuple[str, ...] = ()
    marketplace: str = "adobe_stock"
    marketplace_outcome: str = "not_submitted"
    notes: str = ""
    created_at: str = ""

    def __post_init__(self) -> None:
        for value, field in (
            (self.evaluation_id, "evaluation_id"),
            (self.execution_id, "execution_id"),
            (self.artifact_id, "artifact_id"),
            (self.lane_key, "lane_key"),
            (self.buyer_job, "buyer_job"),
            (self.product_kind, "product_kind"),
            (self.delivery_format, "delivery_format"),
            (self.provider_id, "provider_id"),
            (self.model_id, "model_id"),
            (self.workflow_hash, "workflow_hash"),
            (self.marketplace, "marketplace"),
        ):
            _required(value, field)
        if self.decision not in DECISIONS:
            raise EvaluationError(f"Unsupported decision: {self.decision!r}.")
        if self.marketplace_outcome not in MARKETPLACE_OUTCOMES:
            raise EvaluationError(f"Unsupported marketplace outcome: {self.marketplace_outcome!r}.")
        for field in SCORE_FIELDS:
            _score(getattr(self, field), field)
        if self.decision == "reject" and not self.rejection_reasons:
            raise EvaluationError("A rejected asset requires at least one rejection reason.")
        if any(not str(reason).strip() or len(str(reason).strip()) > 160 for reason in self.rejection_reasons):
            raise EvaluationError("Each rejection reason must contain 1-160 characters.")
        if len(self.notes) > 2000:
            raise EvaluationError("Evaluation notes exceed 2000 characters.")
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.now(UTC).isoformat())

    @property
    def overall_score(self) -> float:
        return round(sum(getattr(self, field) for field in SCORE_FIELDS) / len(SCORE_FIELDS), 2)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["rejection_reasons"] = list(self.rejection_reasons)
        data["overall_score"] = self.overall_score
        return data


def new_evaluation(
    *,
    execution_id: str,
    artifact_id: str,
    lane_key: str,
    buyer_job: str,
    product_kind: str,
    delivery_format: str,
    provider_id: str,
    model_id: str,
    workflow_hash: str,
    decision: str,
    visual_quality: int,
    technical_quality: int,
    buyer_fit: int,
    metadata_accuracy: int,
    rejection_reasons: tuple[str, ...] = (),
    marketplace: str = "adobe_stock",
    marketplace_outcome: str = "not_submitted",
    notes: str = "",
) -> GenerationEvaluation:
    """Create a validated evaluation with a fresh local identity."""
    return GenerationEvaluation(
        evaluation_id=f"eval-{uuid4().hex}",
        execution_id=execution_id,
        artifact_id=artifact_id,
        lane_key=lane_key,
        buyer_job=buyer_job,
        product_kind=product_kind,
        delivery_format=delivery_format,
        provider_id=provider_id,
        model_id=model_id,
        workflow_hash=workflow_hash,
        decision=decision,
        visual_quality=visual_quality,
        technical_quality=technical_quality,
        buyer_fit=buyer_fit,
        metadata_accuracy=metadata_accuracy,
        rejection_reasons=tuple(rejection_reasons),
        marketplace=marketplace,
        marketplace_outcome=marketplace_outcome,
        notes=notes,
    )


def evaluation_log_path(project_root: str | Path) -> Path:
    return Path(project_root).expanduser().resolve() / "evaluations" / "generation_evaluations.jsonl"


def append_evaluation(project_root: str | Path, evaluation: GenerationEvaluation) -> Path:
    """Append one validated record and fsync it; never overwrites prior feedback."""
    path = evaluation_log_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(evaluation.to_dict(), sort_keys=True, ensure_ascii=False) + "\n"
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise EvaluationError(f"Could not append evaluation ledger: {exc}") from exc
    return path


def load_evaluations(project_root: str | Path) -> list[GenerationEvaluation]:
    """Load the ledger and fail closed if a record is malformed."""
    path = evaluation_log_path(project_root)
    if not path.is_file():
        return []
    records: list[GenerationEvaluation] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvaluationError(f"Could not read evaluation ledger: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TypeError("record is not an object")
            value.pop("overall_score", None)
            records.append(
                GenerationEvaluation(
                    **{
                        **value,
                        "rejection_reasons": tuple(value.get("rejection_reasons", ())),
                    }
                )
            )
        except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            raise EvaluationError(f"Invalid evaluation ledger record at line {line_number}: {exc}") from exc
    return records


def summarize_evaluations(project_root: str | Path) -> dict[str, object]:
    """Return transparent aggregates for future prompt/format/provider review."""
    records = load_evaluations(project_root)
    if not records:
        return {
            "record_count": 0,
            "decision_counts": {},
            "format_counts": {},
            "average_scores": {field: None for field in SCORE_FIELDS},
            "rejection_reasons": {},
            "notice": "No human evaluation records exist yet; no learning conclusion can be drawn.",
        }
    decision_counts = Counter(record.decision for record in records)
    format_counts = Counter(record.delivery_format for record in records)
    reason_counts = Counter(reason for record in records for reason in record.rejection_reasons)
    return {
        "record_count": len(records),
        "decision_counts": dict(sorted(decision_counts.items())),
        "format_counts": dict(sorted(format_counts.items())),
        "average_scores": {
            field: round(sum(getattr(record, field) for record in records) / len(records), 2)
            for field in SCORE_FIELDS
        },
        "overall_average": round(sum(record.overall_score for record in records) / len(records), 2),
        "rejection_reasons": dict(sorted(reason_counts.items())),
        "notice": "Aggregates describe reviewed records only; they are not sales forecasts or automatic policy decisions.",
    }
