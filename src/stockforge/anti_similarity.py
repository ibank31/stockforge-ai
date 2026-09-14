"""Pre-generation creative-distance controls for StockForge V2.

This layer does not pretend to prove originality. It blocks a generation brief
when too few independently documented dimensions differ from the reference.
Perceptual duplicate checks remain a separate post-generation signal.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .creative_opportunity import CreativeOpportunity
from .reference_intelligence import ReferenceProfile


class AntiSimilarityError(ValueError):
    """Raised when a proposed concept is too close to its reference plan."""


RiskLevel = Literal["high", "medium", "low"]


@dataclass(frozen=True, slots=True)
class AntiSimilarityAssessment:
    changed_dimensions: tuple[str, ...]
    unchanged_dimensions: tuple[str, ...]
    risk: RiskLevel
    decision: Literal["BLOCK", "REVIEW"]
    rationale: tuple[str, ...]


_DIMENSIONS = (
    "subject",
    "composition",
    "viewpoint",
    "color_direction",
    "context",
    "use_case",
)


def assess_creative_distance(
    profile: ReferenceProfile,
    opportunity: CreativeOpportunity,
) -> AntiSimilarityAssessment:
    """Assess documented creative distance before a provider is called.

    Semantic fields from the reference are only compared when explicitly known.
    Unknown reference semantics never become fabricated similarity evidence.
    """
    plan = opportunity.creative_distance.to_dict()
    changed = tuple(
        name.removeprefix("change_")
        for name, enabled in plan.items()
        if enabled
    )
    unchanged = tuple(name for name in _DIMENSIONS if name not in changed)

    rationale = list(opportunity.differentiation_rationale)
    if profile.subject and opportunity.proposed_subject.casefold() == profile.subject.casefold():
        rationale.append("Declared reference subject is reused; stronger differentiation required.")

    if len(changed) < 3:
        risk: RiskLevel = "high"
        decision: Literal["BLOCK", "REVIEW"] = "BLOCK"
    elif len(changed) < 5:
        risk = "medium"
        decision = "REVIEW"
    else:
        risk = "low"
        decision = "REVIEW"

    return AntiSimilarityAssessment(
        changed_dimensions=changed,
        unchanged_dimensions=unchanged,
        risk=risk,
        decision=decision,
        rationale=tuple(rationale),
    )


def require_generation_distance(
    profile: ReferenceProfile,
    opportunity: CreativeOpportunity,
) -> AntiSimilarityAssessment:
    assessment = assess_creative_distance(profile, opportunity)
    if assessment.decision == "BLOCK":
        raise AntiSimilarityError(
            "Generation blocked: creative plan changes fewer than three independent dimensions."
        )
    return assessment
