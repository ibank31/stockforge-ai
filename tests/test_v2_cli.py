from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from stockforge.v2_cli import app


def test_profile_command_returns_reference_facts(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    Image.new("RGB", (32, 16), "white").save(source)
    result = CliRunner().invoke(app, ["profile", "--reference", str(source)])
    assert result.exit_code == 0
    assert '"orientation": "landscape"' in result.stdout
    assert '"semantic"' in result.stdout


def test_plan_command_requires_real_creative_distance(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    Image.new("RGB", (32, 32), "white").save(source)
    result = CliRunner().invoke(
        app,
        [
            "plan", "--reference", str(source),
            "--opportunity-id", "v2-demo",
            "--market-intent", "recipe layout",
            "--proposed-subject", "ceramic soup bowl",
            "--proposed-composition", "overhead with negative space",
            "--proposed-viewpoint", "top down",
            "--proposed-color-direction", "earthy warm palette",
            "--proposed-context", "editorial food layout",
            "--proposed-use-case", "recipe cards",
            "--differentiate", "change subject",
            "--differentiate", "change composition",
            "--differentiate", "change color",
        ],
    )
    assert result.exit_code == 0
    assert '"stockforge_v2": true' in result.stdout


def test_autocrop_command_returns_reviewable_candidates(tmp_path: Path) -> None:
    source = tmp_path / "screenshot.png"
    image = Image.new("RGB", (400, 300), (10, 10, 10))
    for x in range(100, 300):
        for y in range(80, 220):
            image.putpixel((x, y), (220, 150 if x < 200 else 40, 80))
    image.save(source)

    result = CliRunner().invoke(
        app,
        ["autocrop", "--reference", str(source), "--limit", "3"],
    )

    assert result.exit_code == 0
    assert '"decision": "REVIEW_REQUIRED"' in result.stdout
    assert '"candidates"' in result.stdout


def test_crop_command_applies_confirmed_box(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    output = tmp_path / "confirmed.jpg"
    Image.new("RGB", (100, 80), "orange").save(source)

    result = CliRunner().invoke(
        app,
        [
            "crop", "--reference", str(source), "--output", str(output),
            "--left", "10", "--top", "10", "--right", "90", "--bottom", "70",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert '"decision": "CROP_CONFIRMED"' in result.stdout
