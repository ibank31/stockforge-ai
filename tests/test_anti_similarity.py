from pathlib import Path

from PIL import Image
import pytest

from stockforge.anti_similarity import AntiSimilarityError, require_generation_distance
from stockforge.creative_opportunity import build_creative_opportunity
from stockforge.reference_intelligence import CreativeDistancePlan, ReferenceIntelligenceError, profile_reference_image


def _profile(tmp_path: Path):
    source = tmp_path / "reference.png"
    Image.new("RGB", (32, 32), "white").save(source)
    return profile_reference_image(source, subject="bottle")


def _opportunity(profile, distance, rationale=("subject", "composition", "context")):
    return build_creative_opportunity(
        profile, opportunity_id="v2-test", market_intent="product utility",
        proposed_subject="jar", proposed_composition="asymmetric product arrangement",
        proposed_viewpoint="high angle", proposed_color_direction="earth tones",
        proposed_context="kitchen", proposed_use_case="editorial",
        differentiation_rationale=rationale, creative_distance=distance,
    )


def test_blocks_insufficient_creative_distance(tmp_path):
    profile = _profile(tmp_path)
    distance = CreativeDistancePlan(
        change_subject=True, change_composition=True, change_viewpoint=False,
        change_color_direction=False, change_context=False, change_use_case=False,
    )
    with pytest.raises(ReferenceIntelligenceError):
        _opportunity(profile, distance)


def test_allows_review_when_multiple_dimensions_change(tmp_path):
    profile = _profile(tmp_path)
    assessment = require_generation_distance(profile, _opportunity(profile, CreativeDistancePlan()))
    assert assessment.risk == "low"
    assert assessment.decision == "REVIEW"
    assert len(assessment.changed_dimensions) == 6
