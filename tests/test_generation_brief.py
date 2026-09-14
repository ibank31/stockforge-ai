from pathlib import Path

from PIL import Image

from stockforge.creative_opportunity import build_creative_opportunity
from stockforge.generation_brief import build_generation_brief
from stockforge.reference_intelligence import CreativeDistancePlan, profile_reference_image


def test_generation_brief_preserves_traceable_intent(tmp_path: Path):
    path = tmp_path / "ref.png"
    Image.new("RGB", (32, 24), "white").save(path)
    profile = profile_reference_image(path, subject="old bottle")
    opportunity = build_creative_opportunity(
        profile,
        opportunity_id="brief-001",
        market_intent="kitchen packaging",
        proposed_subject="ceramic storage jar",
        proposed_composition="offset asymmetric hero composition",
        proposed_viewpoint="high three-quarter angle",
        proposed_color_direction="muted earth palette",
        proposed_context="minimal kitchen counter",
        proposed_use_case="editorial and packaging",
        differentiation_rationale=("new subject", "new viewpoint", "new context"),
        creative_distance=CreativeDistancePlan(),
    )
    brief = build_generation_brief(profile, opportunity)
    assert brief.reference_sha256 == profile.visual.sha256
    assert brief.subject == "ceramic storage jar"
    assert len(brief.changed_dimensions) == 6
