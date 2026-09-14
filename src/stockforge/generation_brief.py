"""Structured Generation Brief builder for StockForge V2.

Converts a reference profile and a deliberately differentiated opportunity into
provider-neutral generation intent. Prompt rendering is intentionally deferred
to model adapters.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .anti_similarity import AntiSimilarityAssessment, require_generation_distance
from .creative_opportunity import CreativeOpportunity
from .reference_intelligence import ReferenceProfile


@dataclass(frozen=True, slots=True)
class GenerationBrief:
    brief_id: str
    subject: str
    composition: str
    viewpoint: str
    color_direction: str
    context: str
    use_case: str
    market_intent: str
    reference_sha256: str
    anti_similarity_risk: str
    changed_dimensions: tuple[str, ...]
    differentiation_rationale: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "brief_id": self.brief_id,
            "subject": self.subject,
            "composition": self.composition,
            "viewpoint": self.viewpoint,
            "color_direction": self.color_direction,
            "context": self.context,
            "use_case": self.use_case,
            "market_intent": self.market_intent,
            "reference_sha256": self.reference_sha256,
            "anti_similarity_risk": self.anti_similarity_risk,
            "changed_dimensions": list(self.changed_dimensions),
            "differentiation_rationale": list(self.differentiation_rationale),
        }


def build_generation_brief(
    profile: ReferenceProfile,
    opportunity: CreativeOpportunity,
) -> GenerationBrief:
    """Build a generation-ready brief only after anti-similarity gating."""
    assessment: AntiSimilarityAssessment = require_generation_distance(profile, opportunity)
    return GenerationBrief(
        brief_id=opportunity.opportunity_id,
        subject=opportunity.proposed_subject,
        composition=opportunity.proposed_composition,
        viewpoint=opportunity.proposed_viewpoint,
        color_direction=opportunity.proposed_color_direction,
        context=opportunity.proposed_context,
        use_case=opportunity.proposed_use_case,
        market_intent=opportunity.market_intent,
        reference_sha256=profile.visual.sha256,
        anti_similarity_risk=assessment.risk,
        changed_dimensions=assessment.changed_dimensions,
        differentiation_rationale=opportunity.differentiation_rationale,
    )
