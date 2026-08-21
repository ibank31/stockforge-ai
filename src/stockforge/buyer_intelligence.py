"""Buyer-first intelligence primitives for StockForge AI.

The module turns a market opportunity into an actionable buyer/use-case
profile before generation. It deliberately keeps assumptions explicit and
never treats buyer fit as a sales probability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .market_intelligence import BuyerProfile, MarketEvidence, MarketOpportunity

Confidence = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class BuyerRegistryEntry:
    segment: str
    industry: str
    roles: tuple[str, ...]
    communication_jobs: tuple[str, ...]
    channels: tuple[str, ...]
    visual_requirements: tuple[str, ...]
    uniqueness_levers: tuple[str, ...]
    preferred_compositions: tuple[str, ...]

    def to_profile(self) -> BuyerProfile:
        return BuyerProfile(
            segment=self.segment,
            industry=self.industry,
            roles=self.roles,
            communication_jobs=self.communication_jobs,
            channels=self.channels,
            visual_requirements=self.visual_requirements,
            uniqueness_levers=self.uniqueness_levers,
        )


@dataclass(frozen=True, slots=True)
class BuyerMatch:
    buyer: BuyerRegistryEntry
    use_case_fit: float
    channel_fit: float
    visual_fit: float
    uniqueness_fit: float
    evidence_confidence: Confidence
    evidence: tuple[MarketEvidence, ...]

    @property
    def score(self) -> float:
        return round(
            0.30 * self.use_case_fit
            + 0.25 * self.channel_fit
            + 0.25 * self.visual_fit
            + 0.20 * self.uniqueness_fit,
            2,
        )

    @property
    def recommendation(self) -> str:
        if self.evidence_confidence == "low":
            return "REVIEW"
        if self.score >= 80:
            return "PRIORITY"
        if self.score >= 65:
            return "CANDIDATE"
        return "REJECT"

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["score"] = self.score
        data["recommendation"] = self.recommendation
        return data


BUYER_REGISTRY: tuple[BuyerRegistryEntry, ...] = (
    BuyerRegistryEntry(
        segment="construction_saas_marketing",
        industry="construction_technology",
        roles=("product_marketing", "content_marketing", "creative_director"),
        communication_jobs=("website_hero", "blog_article", "case_study", "presentation"),
        channels=("web", "social", "presentation", "email"),
        visual_requirements=("authentic_workflow", "copy_space", "non_branded_ui"),
        uniqueness_levers=("physical_digital_relationship", "specific_workflow"),
        preferred_compositions=("wide_hero", "subject_left_copy_right", "environmental_scene"),
    ),
    BuyerRegistryEntry(
        segment="construction_contractor",
        industry="construction",
        roles=("project_manager", "safety_manager", "business_development"),
        communication_jobs=("website", "tender", "safety_campaign", "training"),
        channels=("web", "presentation", "print", "social"),
        visual_requirements=("credible_site_context", "authentic_ppe", "clear_action"),
        uniqueness_levers=("specific_construction_problem", "safety_workflow", "regional_context"),
        preferred_compositions=("documentary_wide", "action_closeup", "team_workflow"),
    ),
    BuyerRegistryEntry(
        segment="engineering_consultant",
        industry="engineering",
        roles=("engineer", "technical_director", "proposal_manager"),
        communication_jobs=("proposal", "technical_report", "tender", "presentation"),
        channels=("presentation", "print", "web"),
        visual_requirements=("technical_credibility", "measurement_context", "copy_space"),
        uniqueness_levers=("inspection", "risk_assessment", "technical_process"),
        preferred_compositions=("technical_wide", "inspection_detail", "plan_plus_site"),
    ),
    BuyerRegistryEntry(
        segment="property_marketing",
        industry="property_development",
        roles=("marketing_manager", "brand_manager", "sales_director"),
        communication_jobs=("brochure", "website_hero", "campaign", "investor_presentation"),
        channels=("web", "print", "social", "presentation"),
        visual_requirements=("aspirational", "local_context", "architectural_clarity"),
        uniqueness_levers=("regional_specificity", "development_context", "lifestyle"),
        preferred_compositions=("hero_exterior", "editorial_lifestyle", "architectural_wide"),
    ),
    BuyerRegistryEntry(
        segment="saas_enterprise_marketing",
        industry="software",
        roles=("product_marketing", "demand_generation", "content_marketing", "creative_director"),
        communication_jobs=("landing_page", "blog_article", "case_study", "advertising"),
        channels=("web", "social", "presentation", "email"),
        visual_requirements=("human_technology_relationship", "concept_clarity", "copy_space"),
        uniqueness_levers=("specific_workflow", "physical_digital_relationship", "business_context"),
        preferred_compositions=("wide_hero", "human_plus_environment", "conceptual_realism"),
    ),
    BuyerRegistryEntry(
        segment="corporate_esg_communications",
        industry="sustainability",
        roles=("communications_manager", "esg_manager", "investor_relations"),
        communication_jobs=("esg_report", "annual_report", "campaign", "presentation"),
        channels=("print", "presentation", "web"),
        visual_requirements=("credible_action", "restrained_aesthetic", "report_safe"),
        uniqueness_levers=("specific_action", "human_consequence", "workplace_context"),
        preferred_compositions=("report_wide", "documentary_detail", "human_environment"),
    ),
)


def _overlap_score(values: tuple[str, ...], target: tuple[str, ...]) -> float:
    if not values or not target:
        return 0.0
    return round(100.0 * len(set(values) & set(target)) / len(set(target)), 2)


def match_buyer(
    opportunity: MarketOpportunity,
    buyer: BuyerRegistryEntry,
) -> BuyerMatch:
    """Score a buyer against an opportunity using only explicit fields."""
    use_case_fit = _overlap_score(opportunity.buyer.communication_jobs, buyer.communication_jobs)
    channel_fit = _overlap_score(opportunity.buyer.channels, buyer.channels)
    visual_fit = _overlap_score(opportunity.buyer.visual_requirements, buyer.visual_requirements)
    uniqueness_fit = _overlap_score(opportunity.buyer.uniqueness_levers, buyer.uniqueness_levers)
    confidence: Confidence = "high" if opportunity.evidence and all(
        item.confidence == "high" for item in opportunity.evidence
    ) else "medium" if opportunity.evidence else "low"
    return BuyerMatch(
        buyer=buyer,
        use_case_fit=use_case_fit,
        channel_fit=channel_fit,
        visual_fit=visual_fit,
        uniqueness_fit=uniqueness_fit,
        evidence_confidence=confidence,
        evidence=opportunity.evidence,
    )


def rank_buyers(opportunity: MarketOpportunity) -> list[BuyerMatch]:
    """Return buyer candidates ordered by transparent fit score."""
    matches = [match_buyer(opportunity, buyer) for buyer in BUYER_REGISTRY]
    return sorted(matches, key=lambda item: item.score, reverse=True)


def build_buyer_concept_brief(
    opportunity: MarketOpportunity,
    buyer: BuyerRegistryEntry,
    *,
    visual_problem: str,
    subject: str,
    composition: str,
) -> dict[str, object]:
    """Build a generation-ready brief after buyer matching."""
    match = match_buyer(opportunity, buyer)
    if match.recommendation == "REJECT":
        raise ValueError("Buyer fit is too weak for generation.")
    return {
        "buyer": asdict(buyer),
        "buyer_match": match.to_dict(),
        "marketplace": opportunity.marketplace,
        "query": opportunity.query,
        "opportunity_score": opportunity.opportunity_score,
        "visual_problem": visual_problem,
        "subject": subject,
        "composition": composition,
        "generation_constraints": {
            "visual_requirements": list(buyer.visual_requirements),
            "uniqueness_levers": list(buyer.uniqueness_levers),
            "preferred_compositions": list(buyer.preferred_compositions),
        },
        "evidence": [asdict(item) for item in opportunity.evidence],
    }
