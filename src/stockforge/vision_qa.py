"""Semantic vision QA contracts for commercial stock assets.

This module intentionally separates the QA contract from the actual vision
backend. A real vision model can be plugged in later without changing the
production gate or report schema. The default provider never pretends that
pixel heuristics can detect anatomy or semantic defects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

VisionStatus = Literal["pass", "warn", "fail", "review"]
VISION_QA_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class VisionQAPolicy:
    min_overall_score: float = 0.78
    min_commercial_score: float = 0.70
    min_integrity_score: float = 0.80
    max_artifact_score: float = 0.20
    require_provider_for_submission: bool = True

    def __post_init__(self) -> None:
        values = (self.min_overall_score, self.min_commercial_score, self.min_integrity_score, self.max_artifact_score)
        if any(v < 0 or v > 1 for v in values):
            raise ValueError("vision QA thresholds must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class VisionAssessment:
    """Normalized semantic assessment returned by a vision provider."""
    overall_score: float
    commercial_score: float
    integrity_score: float
    artifact_score: float
    anatomy_ok: bool | None = None
    realism_ok: bool | None = None
    composition_ok: bool | None = None
    subject_integrity_ok: bool | None = None
    text_or_logo_risk: bool | None = None
    notes: tuple[str, ...] = ()
    provider: str = "unknown"

    def __post_init__(self) -> None:
        scores = (self.overall_score, self.commercial_score, self.integrity_score, self.artifact_score)
        if any(v < 0 or v > 1 for v in scores):
            raise ValueError("vision assessment scores must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class VisionQAReport:
    status: VisionStatus
    path: str
    assessment: VisionAssessment | None
    reasons: tuple[str, ...] = ()
    schema_version: int = VISION_QA_SCHEMA_VERSION


class VisionQAProvider(Protocol):
    name: str

    def assess(self, path: Path, *, context: str = "") -> VisionAssessment:
        """Assess image semantics using a vision-capable backend."""


@dataclass(frozen=True, slots=True)
class ReviewRequiredProvider:
    """Safe default: blocks submission until a real vision provider is used."""
    name: str = "review-required"

    def assess(self, path: Path, *, context: str = "") -> VisionAssessment:
        raise RuntimeError("No vision provider configured; semantic review is required")


def evaluate_vision(
    path: Path,
    *,
    provider: VisionQAProvider | None,
    policy: VisionQAPolicy | None = None,
    context: str = "",
) -> VisionQAReport:
    """Apply a provider assessment to the stock submission gate."""
    policy = policy or VisionQAPolicy()
    image_path = Path(path)
    if not image_path.is_file():
        return VisionQAReport("fail", str(image_path), None, ("image file does not exist",))
    if provider is None:
        status: VisionStatus = "fail" if policy.require_provider_for_submission else "review"
        return VisionQAReport(status, str(image_path), None, ("semantic vision provider is not configured",))

    try:
        assessment = provider.assess(image_path, context=context)
    except Exception as exc:
        return VisionQAReport("review", str(image_path), None, (f"vision provider unavailable: {type(exc).__name__}",))

    reasons: list[str] = []
    if assessment.overall_score < policy.min_overall_score:
        reasons.append("overall visual quality below threshold")
    if assessment.commercial_score < policy.min_commercial_score:
        reasons.append("commercial usefulness below threshold")
    if assessment.integrity_score < policy.min_integrity_score:
        reasons.append("subject or scene integrity below threshold")
    if assessment.artifact_score > policy.max_artifact_score:
        reasons.append("AI artifact risk above threshold")
    if assessment.anatomy_ok is False:
        reasons.append("anatomy or hands failed")
    if assessment.realism_ok is False:
        reasons.append("realism failed")
    if assessment.composition_ok is False:
        reasons.append("composition failed")
    if assessment.subject_integrity_ok is False:
        reasons.append("subject integrity failed")
    if assessment.text_or_logo_risk is True:
        reasons.append("text or logo risk detected")

    status = "fail" if reasons else "pass"
    return VisionQAReport(status, str(image_path), assessment, tuple(reasons))
