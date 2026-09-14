from pathlib import Path

import pytest
from PIL import Image

from stockforge.creative_opportunity import (
    CreativeOpportunityError,
    build_creative_opportunity,
)
from stockforge.reference_intelligence import CreativeDistancePlan, profile_reference_image


def _profile(tmp_path: Path):
    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "orange").save(source)
    return profile_reference_image(source, subject="orange beverage bottle")


def test_builds_distinct_commercial_direction(tmp_path: Path) -> None:
    result = build_creative_opportunity(
        _profile(tmp_path),
        opportunity_id="sustainable-drinkware-01",
        market_intent="commercial product communication",
        proposed_subject="reusable insulated drink tumbler",
        proposed_composition="three-quarter isolated composition",
        proposed_viewpoint="slightly elevated angle",
        proposed_color_direction="muted earth tones",
        proposed_context="minimal studio utility asset",
        proposed_use_case="sustainability campaign",
        differentiation_rationale=(
            "subject changes from bottle to tumbler",
            "composition changes to elevated three-quarter view",
            "color direction changes",
        ),
    )
    assert result.proposed_subject == "reusable insulated drink tumbler"


def test_rejects_weak_documented_differentiation(tmp_path: Path) -> None:
    with pytest.raises(CreativeOpportunityError, match="three explicit"):
        build_creative_opportunity(
            _profile(tmp_path),
            opportunity_id="x",
            market_intent="commercial",
            proposed_subject="new tumbler",
            proposed_composition="new composition",
            proposed_viewpoint="new viewpoint",
            proposed_color_direction="new palette",
            proposed_context="new context",
            proposed_use_case="new use",
            differentiation_rationale=("only one",),
        )


def test_reusing_subject_requires_stronger_rationale(tmp_path: Path) -> None:
    with pytest.raises(CreativeOpportunityError, match="stronger"):
        build_creative_opportunity(
            _profile(tmp_path),
            opportunity_id="x",
            market_intent="commercial",
            proposed_subject="orange beverage bottle",
            proposed_composition="top view",
            proposed_viewpoint="top down",
            proposed_color_direction="blue",
            proposed_context="outdoor campaign",
            proposed_use_case="editorial",
            differentiation_rationale=("composition", "viewpoint", "color"),
            creative_distance=CreativeDistancePlan(
                change_subject=False,
                change_composition=True,
                change_viewpoint=True,
                change_color_direction=True,
                change_context=True,
                change_use_case=True,
            ),
        )
