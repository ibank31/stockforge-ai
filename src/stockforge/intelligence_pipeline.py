"""Integrated market-to-prompt planning pipeline for StockForge.

This module connects the previously isolated market, buyer, concept, AssetSpec,
and prompt layers into one deterministic planning path. It does not fabricate
market evidence, call a generation provider, or auto-approve an asset.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .asset_prompt_compiler import compile_asset_prompt
from .asset_spec import AssetSpec, standalone_asset_spec
from .buyer_intelligence import BUYER_REGISTRY, BuyerMatch, BuyerRegistryEntry, rank_buyers
from .concept_engine import ConceptPlan, build_concept_plan
from .market_intelligence import MarketEvidence, MarketOpportunity
from .prompt_compiler import PromptPackage


class IntelligencePipelineError(ValueError):
    """Raised when an intelligence planning payload is incomplete or invalid."""


@dataclass(frozen=True, slots=True)
class PlannedAsset:
    concept_id: str
    buyer_match_score: float
    opportunity_score: float
    asset_spec: AssetSpec
    prompt_package: PromptPackage

    def to_dict(self) -> dict[str, object]:
        return {
            "concept_id": self.concept_id,
            "buyer_match_score": self.buyer_match_score,
            "opportunity_score": self.opportunity_score,
            "asset_spec": self.asset_spec.to_dict(),
            "prompt_package": self.prompt_package.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class IntelligencePlan:
    opportunity: MarketOpportunity
    buyer: BuyerRegistryEntry
    buyer_match: BuyerMatch
    concepts: ConceptPlan
    assets: tuple[PlannedAsset, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "opportunity": self.opportunity.to_dict(),
            "buyer": asdict(self.buyer),
            "buyer_match": self.buyer_match.to_dict(),
            "concepts": self.concepts.to_dict(),
            "assets": [item.to_dict() for item in self.assets],
            "notice": (
                "Evidence-backed planning only. No provider was called and no "
                "marketplace acceptance, originality, legal clearance, or sales "
                "outcome is implied."
            ),
        }


def _registry_entry(segment: str | None) -> BuyerRegistryEntry | None:
    if not segment:
        return None
    for entry in BUYER_REGISTRY:
        if entry.segment == segment:
            return entry
    raise IntelligencePipelineError(f"Unknown buyer_segment: {segment}")


def _evidence(values: Any) -> tuple[MarketEvidence, ...]:
    if not isinstance(values, list) or not values:
        raise IntelligencePipelineError("evidence must be a non-empty list of timestamped records")
    records: list[MarketEvidence] = []
    for item in values:
        if not isinstance(item, dict):
            raise IntelligencePipelineError("each evidence record must be an object")
        try:
            records.append(MarketEvidence(
                source=str(item["source"]),
                url=str(item["url"]),
                observed_at=str(item["observed_at"]),
                signal=str(item["signal"]),
                value=str(item["value"]),
                confidence=str(item.get("confidence", "medium")),
            ))
        except KeyError as exc:
            raise IntelligencePipelineError(f"evidence record missing field: {exc.args[0]}") from exc
    return tuple(records)


def _number(payload: dict[str, Any], key: str) -> float:
    try:
        return float(payload[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise IntelligencePipelineError(f"{key} must be a number") from exc


def build_intelligence_plan(payload: dict[str, Any]) -> IntelligencePlan:
    """Compile externally supplied evidence into buyer-aware prompts.

    The payload is deliberately explicit so a SaaS/API layer can supply data
    from manual research, approved APIs, or future collectors without changing
    the deterministic planning core.
    """
    if not isinstance(payload, dict):
        raise IntelligencePipelineError("planning payload must be an object")

    requested_buyer = _registry_entry(
        str(payload.get("buyer_segment", "")).strip() or None
    )
    evidence = _evidence(payload.get("evidence"))
    seed_buyer = requested_buyer or BUYER_REGISTRY[0]
    opportunity = MarketOpportunity(
        marketplace=str(payload.get("marketplace", "adobe_stock")),
        query=str(payload.get("query", "")).strip(),
        result_count=(int(payload["result_count"]) if payload.get("result_count") is not None else None),
        demand_score=_number(payload, "demand_score"),
        growth_score=_number(payload, "growth_score"),
        saturation_score=_number(payload, "saturation_score"),
        buyer_fit_score=_number(payload, "buyer_fit_score"),
        visual_differentiation_score=_number(payload, "visual_differentiation_score"),
        variation_score=_number(payload, "variation_score"),
        commercial_clarity_score=_number(payload, "commercial_clarity_score"),
        buyer=seed_buyer.to_profile(),
        evidence=evidence,
        risk_flags=tuple(str(item) for item in payload.get("risk_flags", ())),
    )
    if not opportunity.query:
        raise IntelligencePipelineError("query is required")
    opportunity.validate()

    matches = rank_buyers(opportunity)
    match = next(
        (item for item in matches if item.buyer.segment == requested_buyer.segment),
        matches[0],
    ) if requested_buyer is not None else matches[0]
    if match.recommendation == "REJECT":
        raise IntelligencePipelineError("buyer fit is too weak for concept planning")

    concepts = build_concept_plan(
        opportunity,
        match.buyer,
        visual_problem=payload.get("visual_problem"),
        subject=payload.get("subject"),
        environment=payload.get("environment"),
        max_variants=int(payload.get("max_variants", 4)),
    )

    asset_family = str(payload.get("asset_family", "generic"))
    asset_type = str(payload.get("asset_type", "illustration"))
    micro_niche = str(payload.get("micro_niche", opportunity.query))
    visual_language = str(payload.get("visual_language", "commercial stock visual"))
    medium = str(payload.get("medium", "high-quality digital illustration"))
    planned: list[PlannedAsset] = []
    for concept in concepts.concepts:
        spec = standalone_asset_spec(
            asset_id=concept.concept_id,
            market_opportunity_id=str(payload.get("opportunity_id", opportunity.query)),
            buyer_segment=match.buyer.segment,
            buyer_job=concept.buyer_job,
            channel=concept.channel,
            asset_family=asset_family,
            asset_type=asset_type,
            micro_niche=micro_niche,
            subject=concept.subject,
            visual_language=visual_language,
            medium=medium,
            originality_levers=concept.uniqueness_levers,
            commercial_use_cases=(concept.buyer_job, concept.channel),
            delivery_format=str(payload.get("delivery_format", "jpeg")),
            layout_mode=str(payload.get("layout_mode", "square")),
            metadata_hints=(opportunity.query, concept.angle, match.buyer.segment),
            extra_constraints=(
                concept.visual_problem,
                concept.environment,
                concept.composition,
                f"copy space: {concept.copy_space}",
            ),
        )
        planned.append(PlannedAsset(
            concept_id=concept.concept_id,
            buyer_match_score=match.score,
            opportunity_score=opportunity.opportunity_score,
            asset_spec=spec,
            prompt_package=compile_asset_prompt(spec),
        ))

    return IntelligencePlan(
        opportunity=opportunity,
        buyer=match.buyer,
        buyer_match=match,
        concepts=concepts,
        assets=tuple(planned),
    )
