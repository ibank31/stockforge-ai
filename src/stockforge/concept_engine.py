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
    if buyer.segment == "construction_saas_marketing":
        return (
            "site supervisor reviewing project information on a tablet",
            "compare live field conditions with non-branded digital project data",
            "active construction site with authentic equipment and restrained technology cues",
        )
    if buyer.segment == "construction_contractor":
        return (
            "construction supervisor conducting a documented site safety inspection",
            "identify and document a specific site safety condition",
            "active worksite with credible PPE, materials, barriers, and work context",
        )
    if buyer.segment == "engineering_consultant":
        return (
            "engineer inspecting infrastructure while reviewing technical documentation",
            "measure and assess a real engineering condition",
            "infrastructure site with realistic surveying and inspection context",
        )
    if buyer.segment == "property_marketing":
        return (
            "resident or prospective buyer experiencing a completed development",
            "show how the built environment supports a specific lifestyle need",
            "regionally grounded residential environment with believable materials and landscaping",
        )
    if buyer.segment == "saas_enterprise_marketing":
        return (
            "professional using software to solve a concrete workplace problem",
            "show a human decision enabled by technology rather than abstract holograms",
            "credible workplace with restrained, non-branded digital interface cues",
        )
    return (
        "professional performing a concrete sustainability-related workplace action",
        "show a measurable human action and its real-world consequence",
        "credible workplace or operational environment with restrained visual symbolism",
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
        ("hero", "wide environmental hero", "right", "subject left, clean copy space right"),
        ("workflow", "observational workflow scene", "left", "balanced editorial composition with negative space"),
        ("detail", "operational detail", "top", "tight detail with controlled background separation"),
        ("decision", "human decision moment", "right", "medium shot with contextual environment and copy space"),
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
