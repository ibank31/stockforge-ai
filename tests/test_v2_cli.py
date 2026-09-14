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
