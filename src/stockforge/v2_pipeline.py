"""Bridge StockForge V2 creative opportunities into the existing production contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .anti_similarity import AntiSimilarityAssessment, require_generation_distance
from .asset_prompt_compiler import compile_asset_prompt
from .asset_spec import AssetSpec
from .creative_opportunity import CreativeOpportunity
from .generation import GenerationRequest
from .reference_intelligence import ReferenceProfile
from .visual_dna import VisualDNA, extract_visual_dna


class V2PipelineError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class V2GenerationPlan:
    reference_profile: ReferenceProfile
    visual_dna: VisualDNA
    opportunity: CreativeOpportunity
    asset_spec: AssetSpec
    prompt: str
    negative_prompt: str
    generation_request: GenerationRequest
    anti_similarity: AntiSimilarityAssessment

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_profile": self.reference_profile.to_dict(),
            "visual_dna": self.visual_dna.to_dict(),
            "opportunity": self.opportunity.to_dict(),
            "asset_spec": self.asset_spec.to_dict(),
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "generation_request": self.generation_request.to_dict(),
            "anti_similarity": {
                "changed_dimensions": list(self.anti_similarity.changed_dimensions),
                "unchanged_dimensions": list(self.anti_similarity.unchanged_dimensions),
                "risk": self.anti_similarity.risk,
                "decision": self.anti_similarity.decision,
                "rationale": list(self.anti_similarity.rationale),
            },
        }


def build_v2_generation_plan(
    profile: ReferenceProfile,
    opportunity: CreativeOpportunity,
    *,
    asset_id: str | None = None,
    asset_family: str = "generic",
    asset_type: str = "illustration",
    visual_language: str = "commercial product illustration",
    medium: str = "high-detail studio illustration",
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    seed: int | None = None,
    model_id: str | None = None,
) -> V2GenerationPlan:
    """Compile a new direction into existing AssetSpec and GenerationRequest contracts."""

    if opportunity.creative_distance.to_dict()["change_subject"] is False and not profile.subject:
        raise V2PipelineError("Reference subject must be explicit before allowing subject retention.")

    anti_similarity = require_generation_distance(profile, opportunity)
    visual_dna = extract_visual_dna(profile)
    spec = AssetSpec(
        asset_id=(asset_id or opportunity.opportunity_id).strip(),
        market_opportunity_id=opportunity.opportunity_id,
        buyer_segment="v2_reference_intelligence",
        buyer_job=opportunity.market_intent,
        channel=opportunity.proposed_use_case,
        asset_family=asset_family,
        asset_type=asset_type,
        micro_niche=profile.category or "reference_derived_commercial_direction",
        subject=opportunity.proposed_subject,
        visual_language=visual_language,
        medium=medium,
        product_kind="raster_illustration",
        delivery_format="jpeg",
        layout_mode="square",
        palette=(opportunity.proposed_color_direction,),
        composition=opportunity.proposed_composition,
        negative_space="clean controlled separation around the primary subject",
        background_policy="white",
        isolation_policy="isolated",
        text_policy="none",
        branding_policy="no_branding",
        originality_levers=opportunity.differentiation_rationale,
        variation_policy="materially distinct from reference direction",
        commercial_use_cases=(opportunity.proposed_use_case,),
        quality_gates=(
            "no direct reproduction of reference composition",
            "no reference-derived branding or text",
            "human review required before finalization",
        ),
        model_preferences=("resolution>=1024",),
        metadata_hints=("stockforge_v2", opportunity.market_intent, opportunity.proposed_use_case),
        extra_constraints=(
            f"Reference context only: sha256={profile.visual.sha256}.",
            f"Creative context: {opportunity.proposed_context}.",
            f"Reference visual DNA: palette={visual_dna.palette_family}; texture={visual_dna.texture_profile}; density={visual_dna.visual_density}.",
            "Do not reproduce the reference image, its exact composition, or its distinctive visual identity.",
        ),
        tags=("stockforge_v2", "reference_intelligence"),
    )
    package = compile_asset_prompt(spec)
    request = GenerationRequest(
        prompt=package.prompt,
        negative_prompt=package.negative_prompt,
        width=width,
        height=height,
        steps=steps,
        seed=seed,
        model_id=model_id,
        parameters={
            "stockforge_v2": True,
            "reference_sha256": profile.visual.sha256,
            "visual_dna": visual_dna.to_dict(),
            "creative_distance": opportunity.creative_distance.to_dict(),
            "opportunity_id": opportunity.opportunity_id,
        },
    )
    return V2GenerationPlan(
        reference_profile=profile,
        visual_dna=visual_dna,
        opportunity=opportunity,
        asset_spec=spec,
        prompt=package.prompt,
        negative_prompt=package.negative_prompt,
        generation_request=request,
        anti_similarity=anti_similarity,
    )
