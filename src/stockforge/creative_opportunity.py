"""Creative opportunity planning for StockForge V2.

Turns a reference profile plus explicit commercial intent into a NEW direction.
This module does not reproduce source pixels or infer market facts from an image.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .reference_intelligence import CreativeDistancePlan, ReferenceProfile


class CreativeOpportunityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CreativeOpportunity:
    opportunity_id: str
    market_intent: str
    proposed_subject: str
    proposed_composition: str
    proposed_viewpoint: str
    proposed_color_direction: str
    proposed_context: str
    proposed_use_case: str
    differentiation_rationale: tuple[str, ...]
    creative_distance: CreativeDistancePlan

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "market_intent": self.market_intent,
            "proposed_subject": self.proposed_subject,
            "proposed_composition": self.proposed_composition,
            "proposed_viewpoint": self.proposed_viewpoint,
            "proposed_color_direction": self.proposed_color_direction,
            "proposed_context": self.proposed_context,
            "proposed_use_case": self.proposed_use_case,
            "differentiation_rationale": list(self.differentiation_rationale),
            "creative_distance": self.creative_distance.to_dict(),
        }


def build_creative_opportunity(
    profile: ReferenceProfile,
    *,
    opportunity_id: str,
    market_intent: str,
    proposed_subject: str,
    proposed_composition: str,
    proposed_viewpoint: str,
    proposed_color_direction: str,
    proposed_context: str,
    proposed_use_case: str,
    differentiation_rationale: tuple[str, ...],
    creative_distance: CreativeDistancePlan | None = None,
) -> CreativeOpportunity:
    """Build an explicit new direction and refuse copy-like planning."""

    values = {
        "opportunity_id": opportunity_id,
        "market_intent": market_intent,
        "proposed_subject": proposed_subject,
        "proposed_composition": proposed_composition,
        "proposed_viewpoint": proposed_viewpoint,
        "proposed_color_direction": proposed_color_direction,
        "proposed_context": proposed_context,
        "proposed_use_case": proposed_use_case,
    }
    missing = [name for name, value in values.items() if not value.strip()]
    if missing:
        raise CreativeOpportunityError("Missing creative opportunity fields: " + ", ".join(missing))

    if len(tuple(item for item in differentiation_rationale if item.strip())) < 3:
        raise CreativeOpportunityError(
            "Creative opportunity requires at least three explicit differentiation rationales."
        )

    distance = creative_distance or CreativeDistancePlan()
    distance.validate()

    # A profile's subject is reference context, never a reproduction instruction.
    # Reusing the exact subject is allowed only when several other dimensions are
    # deliberately changed; callers must record why.
    if profile.subject and proposed_subject.strip().casefold() == profile.subject.strip().casefold():
        if len(differentiation_rationale) < 4:
            raise CreativeOpportunityError(
                "Reusing a declared reference subject requires stronger documented differentiation."
            )

    return CreativeOpportunity(
        opportunity_id=opportunity_id.strip(),
        market_intent=market_intent.strip(),
        proposed_subject=proposed_subject.strip(),
        proposed_composition=proposed_composition.strip(),
        proposed_viewpoint=proposed_viewpoint.strip(),
        proposed_color_direction=proposed_color_direction.strip(),
        proposed_context=proposed_context.strip(),
        proposed_use_case=proposed_use_case.strip(),
        differentiation_rationale=tuple(item.strip() for item in differentiation_rationale if item.strip()),
        creative_distance=distance,
    )
