from pathlib import Path

import pytest
from PIL import Image

from stockforge.reference_intelligence import (
    CreativeDistancePlan,
    ReferenceIntelligenceError,
    profile_reference_image,
)


def test_profiles_real_visual_facts_without_semantic_overclaim(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    image = Image.new("RGBA", (120, 80), (240, 120, 20, 255))
    image.save(source)

    profile = profile_reference_image(source)

    assert profile.visual.detected_format == "PNG"
    assert profile.visual.orientation == "landscape"
    assert profile.visual.has_alpha is True
    assert profile.visual.aspect_ratio == 1.5
    assert len(profile.visual.dominant_colors) >= 1
    assert profile.semantic_status == "not_verified"


def test_semantic_fields_are_explicit_user_inputs(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), (20, 40, 60)).save(source)

    profile = profile_reference_image(
        source,
        subject="reusable food container",
        category="sustainable packaging",
        commercial_intent="product explainer",
    )

    assert profile.subject == "reusable food container"
    assert profile.semantic_status == "user_supplied"


def test_rejects_animated_reference(tmp_path: Path) -> None:
    source = tmp_path / "animated.gif"
    first = Image.new("RGB", (16, 16), "red")
    second = Image.new("RGB", (16, 16), "blue")
    first.save(source, save_all=True, append_images=[second], format="GIF")

    with pytest.raises(ReferenceIntelligenceError, match="Animated"):
        profile_reference_image(source)


def test_creative_distance_requires_real_change() -> None:
    with pytest.raises(ReferenceIntelligenceError, match="at least three"):
        CreativeDistancePlan(
            change_subject=True,
            change_composition=True,
            change_viewpoint=False,
            change_color_direction=False,
            change_context=False,
            change_use_case=False,
        ).validate()

    CreativeDistancePlan().validate()
