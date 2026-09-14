from pathlib import Path

from PIL import Image

from stockforge.creative_opportunity import build_creative_opportunity
from stockforge.reference_intelligence import profile_reference_image
from stockforge.v2_pipeline import build_v2_generation_plan


def test_v2_plan_reuses_existing_production_contracts(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "orange").save(source)
    profile = profile_reference_image(source, subject="orange beverage bottle", category="drinkware")
    opportunity = build_creative_opportunity(
        profile,
        opportunity_id="v2-tumbler-01",
        market_intent="commercial sustainability asset",
        proposed_subject="reusable insulated drink tumbler",
        proposed_composition="elevated three-quarter isolated view",
        proposed_viewpoint="slightly elevated",
        proposed_color_direction="muted earth tones",
        proposed_context="minimal studio product asset",
        proposed_use_case="sustainability campaign",
        differentiation_rationale=(
            "subject changes from bottle to tumbler",
            "composition changes to elevated three-quarter view",
            "color direction changes to muted earth tones",
        ),
    )
    plan = build_v2_generation_plan(profile, opportunity, seed=42)

    assert plan.anti_similarity.decision == "REVIEW"
    assert len(plan.anti_similarity.changed_dimensions) >= 3
    assert plan.asset_spec.subject == opportunity.proposed_subject
    assert plan.generation_request.seed == 42
    assert plan.generation_request.parameters["stockforge_v2"] is True
    assert plan.generation_request.parameters["reference_sha256"] == profile.visual.sha256
    assert plan.generation_request.parameters["visual_dna"]["palette_family"]
    assert plan.visual_dna.palette_family
    assert "reusable insulated drink tumbler" in plan.prompt
    assert "Reference pixels are not a generation input" not in plan.prompt
