from pathlib import Path
from PIL import Image
import pytest

from stockforge.creative_opportunity import build_creative_opportunity
from stockforge.generation_brief import build_generation_brief
from stockforge.model_prompt_adapter import render_generation_prompt
from stockforge.reference_intelligence import CreativeDistancePlan, profile_reference_image


@pytest.fixture()
def brief(tmp_path: Path):
    path = tmp_path / "ref.png"
    Image.new("RGB", (20, 20), "white").save(path)
    profile = profile_reference_image(path, subject="glass bottle")
    opportunity = build_creative_opportunity(
        profile, opportunity_id="adapter-001", market_intent="retail",
        proposed_subject="ceramic jar", proposed_composition="asymmetric composition",
        proposed_viewpoint="high angle", proposed_color_direction="earth palette",
        proposed_context="clean kitchen", proposed_use_case="packaging",
        differentiation_rationale=("new subject", "new composition", "new context"),
        creative_distance=CreativeDistancePlan(),
    )
    return build_generation_brief(profile, opportunity)


@pytest.mark.parametrize("model_id", ["z-image-turbo", "flux", "gemini-image"])
def test_adapters_render_same_brief_for_supported_models(brief, model_id):
    rendered = render_generation_prompt(brief, model_id)
    assert rendered.model_id == model_id
    assert "ceramic jar" in rendered.prompt
    assert rendered.parameters["reference_mode"] == "intent_only"


def test_unknown_adapter_fails_closed(brief):
    with pytest.raises(ValueError):
        render_generation_prompt(brief, "unknown-model")
