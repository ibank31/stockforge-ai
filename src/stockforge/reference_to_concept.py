"""Reference-to-concept integration for the Microstock Intelligence pipeline.

The pipeline combines externally supplied market evidence with deterministic
reference-image measurements. A reference supplies constraints for differentiation,
not semantic facts, ownership, legal clearance, or a recipe for reproduction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from .asset_prompt_compiler import compile_asset_prompt
from .intelligence_pipeline import IntelligencePlan, PlannedAsset, build_intelligence_plan
from .reference_intelligence import ReferenceAnalysis, VariationPlan, analyze_reference, build_variation_plan


class ReferenceConceptError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ReferenceConceptPlan:
    intelligence: IntelligencePlan
    reference: ReferenceAnalysis
    variation_plan: VariationPlan
    assets: tuple[PlannedAsset, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "reference": self.reference.to_dict(),
            "variation_plan": self.variation_plan.to_dict(),
            "opportunity": self.intelligence.opportunity.to_dict(),
            "buyer": asdict(self.intelligence.buyer),
            "buyer_match": self.intelligence.buyer_match.to_dict(),
            "concepts": self.intelligence.concepts.to_dict(),
            "assets": [asset.to_dict() for asset in self.assets],
            "notice": (
                "Reference measurements were converted into differentiation constraints. "
                "No semantic similarity, copyright, ownership, originality, legal clearance, "
                "marketplace acceptance, or sales outcome is implied."
            ),
        }


def _layout_mode(target_layout: str) -> str:
    return {
        "square": "square",
        "landscape": "hero_landscape",
        "portrait": "portrait",
    }[target_layout]


def build_reference_concept_plan(
    payload: dict[str, Any],
    reference_path: Path,
    *,
    target_layout: str | None = None,
) -> ReferenceConceptPlan:
    """Compile market evidence and a reference into generation-ready differentiated prompts."""
    intelligence = build_intelligence_plan(payload)
    if intelligence.opportunity.production_recommendation == "REJECT":
        raise ReferenceConceptError("Market opportunity is rejected before reference planning.")

    reference = analyze_reference(reference_path)
    if target_layout is not None and target_layout not in {"square", "landscape", "portrait"}:
        raise ReferenceConceptError("target_layout must be square, landscape, or portrait")
    variation = build_variation_plan(reference, target_layout=target_layout) if target_layout else build_variation_plan(reference)

    chosen_layout = target_layout or {
        "square": "landscape",
        "landscape": "portrait",
        "portrait": "square",
    }[reference.orientation]

    constraints = (
        "Reference-derived differentiation contract:",
        variation.composition_change,
        variation.palette_change,
        variation.lighting_change,
        variation.density_change,
        variation.negative_space_change,
        *variation.distinctness_constraints,
    )
    planned: list[PlannedAsset] = []
    for asset in intelligence.assets:
        spec = replace(
            asset.asset_spec,
            layout_mode=_layout_mode(chosen_layout),
            extra_constraints=(*asset.asset_spec.extra_constraints, *constraints),
            originality_levers=(
                *asset.asset_spec.originality_levers,
                "reference-derived composition change",
                "reference-derived lighting change",
                "reference-derived negative-space change",
            ),
            metadata_hints=(
                *asset.asset_spec.metadata_hints,
                "reference_analysis=deterministic",
                f"reference_orientation={reference.orientation}",
            ),
        )
        planned.append(replace(asset, asset_spec=spec, prompt_package=compile_asset_prompt(spec)))

    return ReferenceConceptPlan(
        intelligence=intelligence,
        reference=reference,
        variation_plan=variation,
        assets=tuple(planned),
    )
