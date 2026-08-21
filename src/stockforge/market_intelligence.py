"""Market-aware concept planning primitives for StockForge.

This module intentionally does not scrape marketplaces or invent demand data.
It consumes externally collected, timestamped evidence and turns it into a
transparent opportunity/buyer score. The separation keeps evidence collection
replaceable and prevents model intuition from being presented as market fact.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


Confidence = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class MarketEvidence:
    source: str
    url: str
    observed_at: str
    signal: str
    value: str
    confidence: Confidence = "medium"


@dataclass(frozen=True, slots=True)
class BuyerProfile:
    segment: str
    industry: str
    roles: tuple[str, ...]
    communication_jobs: tuple[str, ...]
    channels: tuple[str, ...]
    visual_requirements: tuple[str, ...]
    uniqueness_levers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MarketOpportunity:
    marketplace: str
    query: str
    result_count: int | None
    demand_score: float
    growth_score: float
    saturation_score: float
    buyer_fit_score: float
    visual_differentiation_score: float
    variation_score: float
    commercial_clarity_score: float
    buyer: BuyerProfile
    evidence: tuple[MarketEvidence, ...] = field(default_factory=tuple)
    risk_flags: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        scores = (
            self.demand_score,
            self.growth_score,
            self.saturation_score,
            self.buyer_fit_score,
            self.visual_differentiation_score,
            self.variation_score,
            self.commercial_clarity_score,
        )
        if any(not 0 <= score <= 100 for score in scores):
            raise ValueError("All opportunity scores must be between 0 and 100.")
        if self.result_count is not None and self.result_count < 0:
            raise ValueError("result_count cannot be negative.")
        if not self.evidence:
            raise ValueError("A market opportunity requires timestamped evidence.")

    @property
    def opportunity_score(self) -> float:
        """Transparent internal score; not a marketplace sales probability."""
        self.validate()
        # Saturation is a penalty, while demand/growth and buyer utility are
        # positive signals. Weights are documented internal heuristics.
        return round(
            0.20 * self.demand_score
            + 0.15 * self.growth_score
            + 0.20 * (100 - self.saturation_score)
            + 0.20 * self.buyer_fit_score
            + 0.15 * self.visual_differentiation_score
            + 0.05 * self.variation_score
            + 0.05 * self.commercial_clarity_score,
            2,
        )

    @property
    def production_recommendation(self) -> str:
        score = self.opportunity_score
        if self.risk_flags:
            return "REVIEW"
        if score >= 80:
            return "PRIORITY"
        if score >= 65:
            return "CANDIDATE"
        return "REJECT"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["opportunity_score"] = self.opportunity_score
        data["production_recommendation"] = self.production_recommendation
        return data


def build_concept_brief(
    opportunity: MarketOpportunity,
    *,
    visual_problem: str,
    subject: str,
    composition: str,
) -> dict[str, object]:
    """Compile market evidence + buyer context into a generation-ready brief."""
    opportunity.validate()
    return {
        "marketplace": opportunity.marketplace,
        "query": opportunity.query,
        "opportunity_score": opportunity.opportunity_score,
        "recommendation": opportunity.production_recommendation,
        "buyer": opportunity.buyer.segment,
        "industry": opportunity.buyer.industry,
        "roles": list(opportunity.buyer.roles),
        "communication_jobs": list(opportunity.buyer.communication_jobs),
        "channels": list(opportunity.buyer.channels),
        "visual_problem": visual_problem,
        "subject": subject,
        "composition": composition,
        "uniqueness_levers": list(opportunity.buyer.uniqueness_levers),
        "risk_flags": list(opportunity.risk_flags),
        "evidence": [asdict(item) for item in opportunity.evidence],
    }
