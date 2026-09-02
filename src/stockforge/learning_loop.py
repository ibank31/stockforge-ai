"""Conservative post-generation learning loop.

This module runs after a preview is already generated. It never calls a GPU,
never triggers a finalizer, and never treats deterministic pixel checks as a
semantic or aesthetic verdict. It stores immutable per-execution critiques and
small, versioned niche memory that can guide a later brief compiler.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import UTC, datetime
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from .adobe_png_gate import inspect_transparent_png
from .image_quality import inspect_quality

SCHEMA_VERSION = 1
MEMORY_VERSION = 1
AUTO_CRITIQUE_DIR = "learning/auto-critiques"
MEMORY_FILE = "learning/niche-memory.json"


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _key(lane_key: str, buyer_job: str, delivery_format: str) -> str:
    return "|".join(part.strip().casefold() for part in (lane_key, buyer_job, delivery_format))


@dataclass(frozen=True, slots=True)
class LearningSignal:
    name: str
    status: str
    score: float | None
    reason: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AutoCritique:
    critique_id: str
    execution_id: str
    artifact_id: str
    image_path: str
    lane_key: str
    buyer_job: str
    delivery_format: str
    product_kind: str
    title: str
    created_at: str
    technical_score: float | None
    semantic_score: float | None
    aesthetic_score: float | None
    commercial_score: float | None
    differentiation_score: float | None
    decision: str
    recommendation: str
    signals: tuple[LearningSignal, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["signals"] = [item.to_dict() for item in self.signals]
        data["limitations"] = list(self.limitations)
        return data


def _quality_score(statuses: list[str]) -> float:
    if not statuses:
        return 0.0
    weights = {"PASS": 1.0, "REVIEW": 0.65, "FAIL": 0.0}
    return round(sum(weights.get(item, 0.0) for item in statuses) / len(statuses), 3)


def critique_image(
    *,
    image_path: str | Path,
    execution_id: str,
    artifact_id: str,
    lane_key: str,
    buyer_job: str,
    delivery_format: str,
    product_kind: str,
    title: str,
) -> AutoCritique:
    """Create a conservative critique using only deterministic technical checks."""
    path = Path(image_path).expanduser().resolve()
    signals: list[LearningSignal] = []
    limitations = [
        "No semantic vision provider was used; context fit is not automatically verified.",
        "No aesthetic model was used; looks and originality remain human-review signals.",
        "Demand is represented only by the persisted buyer job and research evidence, not by sales prediction.",
    ]
    # Preview outputs are intentionally provider-native (often WEBP at 1024px).
    # The Adobe PNG gate is a final-master contract and must not false-fail a
    # preview before the PNG finalizer has produced RGBA output at target size.
    preview_png_gate_deferred = delivery_format.casefold() == "png"
    if preview_png_gate_deferred:
        limitations.append("PNG alpha, format, target resolution, and sRGB gates are deferred to finalized-master import; this critique is for the preview only.")

    quality = inspect_quality(path)
    quality_statuses = [check.status for check in quality.checks]
    technical_score = _quality_score(quality_statuses)
    for check in quality.checks:
        signals.append(LearningSignal(
            name=check.name,
            status=check.status,
            score=1.0 if check.status == "PASS" else (0.65 if check.status == "REVIEW" else 0.0),
            reason=check.detail,
            source="deterministic:image_quality",
        ))

    if delivery_format.casefold() == "png" and not preview_png_gate_deferred:
        png_report = inspect_transparent_png(path)
        png_statuses = [check.status for check in png_report.checks]
        technical_score = round((technical_score + _quality_score(png_statuses)) / 2, 3)
        for check in png_report.checks:
            signals.append(LearningSignal(
                name=f"png_{check.name}",
                status=check.status,
                score=1.0 if check.status == "PASS" else (0.65 if check.status == "REVIEW" else 0.0),
                reason=check.detail,
                source="deterministic:adobe_png_gate",
            ))

    has_fail = any(item.status == "FAIL" for item in signals)
    decision = "FAIL_TECHNICAL" if has_fail else "REVIEW_REQUIRED"
    recommendation = "DO_NOT_FINALIZE" if has_fail else "HUMAN_REVIEW_REQUIRED"
    return AutoCritique(
        critique_id=f"crit-{uuid4().hex}",
        execution_id=execution_id,
        artifact_id=artifact_id,
        image_path=str(path),
        lane_key=lane_key,
        buyer_job=buyer_job,
        delivery_format=delivery_format,
        product_kind=product_kind,
        title=title,
        created_at=_now(),
        technical_score=technical_score,
        semantic_score=None,
        aesthetic_score=None,
        commercial_score=None,
        differentiation_score=None,
        decision=decision,
        recommendation=recommendation,
        signals=tuple(signals),
        limitations=tuple(limitations),
    )


def critique_path(project_root: str | Path, critique_id: str) -> Path:
    return Path(project_root).expanduser().resolve() / AUTO_CRITIQUE_DIR / f"{critique_id}.json"


def memory_path(project_root: str | Path) -> Path:
    return Path(project_root).expanduser().resolve() / MEMORY_FILE


def load_memory(project_root: str | Path) -> dict[str, Any]:
    path = memory_path(project_root)
    if not path.is_file():
        return {"schema_version": MEMORY_VERSION, "kind": "stockforge.niche_memory", "updated_at": None, "records": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid learning memory: {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("records"), dict):
        raise ValueError(f"Learning memory has invalid schema: {path}")
    return value


def update_memory(project_root: str | Path, critique: AutoCritique) -> Path:
    """Append an observation and keep semantic learning explicitly unverified."""
    path = memory_path(project_root)
    memory = load_memory(project_root)
    key = _key(critique.lane_key, critique.buyer_job, critique.delivery_format)
    records = memory.setdefault("records", {})
    record = records.setdefault(key, {
        "lane_key": critique.lane_key,
        "buyer_job": critique.buyer_job,
        "delivery_format": critique.delivery_format,
        "generation_count": 0,
        "technical_review_count": 0,
        "technical_failures": {},
        "hypotheses": [],
        "validated_by_human_count": 0,
        "last_critique_id": None,
        "last_execution_id": None,
    })
    record["generation_count"] += 1
    record["technical_review_count"] += 1
    for signal in critique.signals:
        if signal.status == "FAIL":
            failures = record.setdefault("technical_failures", {})
            failures[signal.name] = failures.get(signal.name, 0) + 1
    hypothesis = {
        "text": "Technical observations are recorded; semantic, aesthetic, commercial, and differentiation scores remain unverified.",
        "source_critique_id": critique.critique_id,
        "status": "unverified",
    }
    hypotheses = record.setdefault("hypotheses", [])
    if not any(item.get("text") == hypothesis["text"] for item in hypotheses):
        hypotheses.append(hypothesis)
    record["last_critique_id"] = critique.critique_id
    record["last_execution_id"] = critique.execution_id
    memory["updated_at"] = _now()
    _atomic_write(path, memory)
    return path


def save_critique(project_root: str | Path, critique: AutoCritique) -> Path:
    path = critique_path(project_root, critique.critique_id)
    _atomic_write(path, critique.to_dict())
    update_memory(project_root, critique)
    return path


def load_critique(path: str | Path) -> AutoCritique:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    signals = tuple(LearningSignal(**item) for item in value.pop("signals", []))
    value["limitations"] = tuple(value.get("limitations", ()))
    return AutoCritique(signals=signals, **value)


def summarize_learning_memory(project_root: str | Path) -> dict[str, Any]:
    memory = load_memory(project_root)
    records = memory.get("records", {})
    return {
        "schema_version": memory.get("schema_version", MEMORY_VERSION),
        "kind": memory.get("kind", "stockforge.niche_memory"),
        "updated_at": memory.get("updated_at"),
        "record_count": len(records),
        "records": records,
        "notice": "Auto-memory is conservative: it records deterministic observations and unverified hypotheses; it is not a sales forecast or automatic KEEP decision.",
    }


def inspect_existing_critique(project_root: str | Path, critique_id: str) -> AutoCritique:
    return load_critique(critique_path(project_root, critique_id))
