from pathlib import Path

from PIL import Image, ImageDraw

from stockforge.reference_intelligence import analyze_and_plan, analyze_reference, build_variation_plan


def _image(path: Path):
    image = Image.new("RGB", (160, 100), "white")
    ImageDraw.Draw(image).rectangle((8, 20, 70, 90), fill=(20, 40, 120))
    image.save(path)


def test_reference_analysis_extracts_measurable_signals(tmp_path: Path):
    path = tmp_path / "reference.png"
    _image(path)
    result = analyze_reference(path)
    assert result.orientation == "landscape"
    assert result.width == 160
    assert len(result.dominant_palette) >= 1
    assert 0 <= result.edge_density <= 1


def test_variation_plan_changes_layout_and_constraints(tmp_path: Path):
    path = tmp_path / "reference.png"
    _image(path)
    plan = build_variation_plan(analyze_reference(path))
    assert "portrait" in plan.composition_change
    assert len(plan.distinctness_constraints) >= 4


def test_analyze_and_plan_serializes(tmp_path: Path):
    path = tmp_path / "reference.png"
    _image(path)
    output = analyze_and_plan(path, target_layout="square")
    assert output["reference"]["orientation"] == "landscape"
    assert "variation_plan" in output
