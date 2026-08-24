"""Buyer- and evidence-aware concept generation primitives.

This is deliberately a deterministic concept planner, not a generative LLM.
It converts an already-evaluated market opportunity and buyer match into
commercially useful visual concepts. Prompt generation can consume these
concepts later without inventing market facts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .buyer_intelligence import BuyerMatch, BuyerRegistryEntry, match_buyer
from .market_intelligence import MarketOpportunity


@dataclass(frozen=True, slots=True)
class ConceptVariant:
    concept_id: str
    angle: str
    visual_problem: str
    subject: str
    action: str
    environment: str
    composition: str
    copy_space: str
    uniqueness_levers: tuple[str, ...]
    buyer_job: str
    channel: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConceptPlan:
    opportunity_query: str
    buyer_segment: str
    buyer_match_score: float
    concepts: tuple[ConceptVariant, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "opportunity_query": self.opportunity_query,
            "buyer_segment": self.buyer_segment,
            "buyer_match_score": self.buyer_match_score,
            "concepts": [item.to_dict() for item in self.concepts],
        }


def _slug(text: str) -> str:
    return "-".join(part for part in text.lower().replace("/", " ").split() if part)


def _jobs(buyer: BuyerRegistryEntry) -> tuple[str, ...]:
    return buyer.communication_jobs or ("marketing_content",)


def _channels(buyer: BuyerRegistryEntry) -> tuple[str, ...]:
    return buyer.channels or ("web",)


def _default_scene(buyer: BuyerRegistryEntry) -> tuple[str, str, str]:
    """Return a broad, standalone-first default without importing an industry scene."""
    if buyer.segment == "web_product_teams":
        return (
            "a single tactile 3D interface metaphor with a clear, extraction-friendly silhouette",
            "give a product team a flexible hero or explainer asset without UI text or branding",
            "clean white studio background with no people, hands, screens, devices, or extra props",
        )
    if buyer.segment == "brand_marketing_teams":
        return (
            "one playful surreal object with a readable visual metaphor",
            "create immediate campaign impact while preserving generous copy space",
            "clean white studio background with no people, hands, tools, devices, or unrelated props",
        )
    if buyer.segment == "editorial_content_teams":
        return (
            "one editorial symbolic object with tactile crafted material detail",
            "communicate a story at thumbnail size without requiring headline text inside the image",
            "clean white studio background with no people, hands, screens, numbers, or decorative frames",
        )
    if buyer.segment == "small_business_commerce":
        return (
            "one material-rich generic product-adjacent prop with no brand identity",
            "supply a flexible visual accent for commerce, email, and packaging layouts",
            "clean white studio background with no people, hands, labels, packaging text, or extra props",
        )
    if buyer.segment == "social_creator_teams":
        return (
            "one bold, playful, standalone icon-like object",
            "achieve immediate recognition across square and vertical social crops",
            "clean white studio background with no people, hands, text, numbers, screens, or props",
        )
    return (
        "one tactile craft or natural motif with a complete silhouette",
        "support authentic brand storytelling without claiming a culture or location not in the brief",
        "clean white studio background with no people, hands, stamps, postmarks, tools, or extra props",
    )


def build_concept_plan(
    opportunity: MarketOpportunity,
    buyer: BuyerRegistryEntry,
    *,
    visual_problem: str | None = None,
    subject: str | None = None,
    environment: str | None = None,
    max_variants: int = 4,
) -> ConceptPlan:
    """Create differentiated concepts for one buyer, without fabricating evidence."""
    if max_variants < 1 or max_variants > 8:
        raise ValueError("max_variants must be between 1 and 8")

    match: BuyerMatch = match_buyer(opportunity, buyer)
    if match.recommendation == "REJECT":
        raise ValueError("Buyer fit is too weak for concept generation.")
    if not opportunity.evidence:
        raise ValueError("Concept generation requires market evidence.")

    default_subject, default_action, default_environment = _default_scene(buyer)
    subject = subject or default_subject
    visual_problem = visual_problem or default_action
    environment = environment or default_environment
    jobs = _jobs(buyer)
    channels = _channels(buyer)
    lever_a = buyer.uniqueness_levers[0] if buyer.uniqueness_levers else "specific_workflow"
    lever_b = buyer.uniqueness_levers[1] if len(buyer.uniqueness_levers) > 1 else "human_context"

    variants: list[ConceptVariant] = []
    templates = (
        ("hero", "standalone hero asset", "right", "single centered object with clean copy space right"),
        ("editorial", "standalone editorial object", "left", "single object with balanced negative space and no environmental context"),
        ("detail", "material detail asset", "top", "single complete object with tactile detail and controlled edge separation"),
        ("social", "standalone social asset", "right", "single bold object with square-crop resilience and no supporting props"),
    )
    for index, (angle, composition_name, copy_space, composition) in enumerate(templates[:max_variants], start=1):
        variants.append(
            ConceptVariant(
                concept_id=f"{_slug(buyer.segment)}-{angle}-{index}",
                angle=angle,
                visual_problem=visual_problem,
                subject=subject,
                action=default_action,
                environment=environment,
                composition=composition,
                copy_space=copy_space,
                uniqueness_levers=(lever_a, lever_b),
                buyer_job=jobs[(index - 1) % len(jobs)],
                channel=channels[(index - 1) % len(channels)],
            )
        )
    return ConceptPlan(
        opportunity_query=opportunity.query,
        buyer_segment=buyer.segment,
        buyer_match_score=match.score,
        concepts=tuple(variants),
    )
