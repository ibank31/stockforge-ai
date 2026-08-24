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
        segment="web_product_teams",
        industry="software_and_digital_products",
        roles=("product_designer", "developer_advocate", "product_marketer", "creative_director"),
        communication_jobs=("landing_page", "feature_explainer", "developer_documentation", "presentation"),
        channels=("web", "app", "presentation", "email"),
        visual_requirements=("clear_silhouette", "compositing_flexibility", "copy_space"),
        uniqueness_levers=("single_visual_metaphor", "material_specificity", "modular_series"),
        preferred_compositions=("centered_isolated", "subject_left_copy_right", "transparent_ready"),
    ),
    BuyerRegistryEntry(
        segment="brand_marketing_teams",
        industry="cross_industry_marketing",
        roles=("brand_manager", "campaign_creative", "content_marketer", "art_director"),
        communication_jobs=("campaign", "advertising", "social_post", "website_hero"),
        channels=("web", "social", "email", "presentation"),
        visual_requirements=("immediate_impact", "copy_space", "brand_adaptability"),
        uniqueness_levers=("unexpected_metaphor", "sensory_material", "distinctive_palette"),
        preferred_compositions=("centered_isolated", "editorial_object", "vertical_social"),
    ),
    BuyerRegistryEntry(
        segment="editorial_content_teams",
        industry="publishing_and_content",
        roles=("editor", "content_strategist", "illustrator", "newsletter_producer"),
        communication_jobs=("article_illustration", "newsletter", "blog_article", "explainer"),
        channels=("web", "email", "social", "presentation"),
        visual_requirements=("concept_clarity", "thumbnail_readability", "headline_safe_space"),
        uniqueness_levers=("clear_metaphor", "editorial_craft", "non_literal_interpretation"),
        preferred_compositions=("centered_isolated", "top_weighted", "editorial_object"),
    ),
    BuyerRegistryEntry(
        segment="small_business_commerce",
        industry="retail_and_ecommerce",
        roles=("merchant", "shop_manager", "growth_marketer", "designer"),
        communication_jobs=("product_page", "campaign", "seasonal_promotion", "packaging_insert"),
        channels=("web", "email", "social", "print"),
        visual_requirements=("clean_edges", "adaptable_background", "material_credibility"),
        uniqueness_levers=("tactile_detail", "seasonal_variation", "colorway_system"),
        preferred_compositions=("centered_isolated", "flat_lay_single", "transparent_ready"),
    ),
    BuyerRegistryEntry(
        segment="social_creator_teams",
        industry="creator_and_community",
        roles=("social_media_manager", "community_manager", "creator", "motion_designer"),
        communication_jobs=("social_post", "story_asset", "thumbnail", "content_series"),
        channels=("social", "web", "presentation"),
        visual_requirements=("fast_recognition", "playful_distinction", "crop_flexibility"),
        uniqueness_levers=("playful_surrealism", "tactile_craft", "series_consistency"),
        preferred_compositions=("centered_isolated", "vertical_social", "square_thumbnail"),
    ),
    BuyerRegistryEntry(
        segment="local_brand_storytelling",
        industry="culture_and_hospitality",
        roles=("local_marketer", "hospitality_designer", "brand_storyteller", "publisher"),
        communication_jobs=("campaign", "editorial", "website_hero", "packaging"),
        channels=("web", "social", "print", "presentation"),
        visual_requirements=("authentic_craft", "respectful_specificity", "copy_space"),
        uniqueness_levers=("local_material", "human_made_imperfection", "place_aware_palette"),
        preferred_compositions=("centered_isolated", "editorial_object", "flat_lay_single"),
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
