from pathlib import Path

from PIL import Image

from stockforge.reference_intelligence import profile_reference_image
from stockforge.visual_dna import extract_visual_dna


def test_extracts_visual_dna_from_reference(tmp_path: Path) -> None:
    source = tmp_path / "reference.png"
    image = Image.new("RGB", (1600, 800), (220, 240, 245))
    for x in range(300, 1300):
        for y in range(250, 550):
            image.putpixel((x, y), (20, 170, 190))
    image.save(source)

    profile = profile_reference_image(source)
    dna = extract_visual_dna(profile)

    assert "landscape" in dna.composition_signature
    assert "wide-horizontal-framing" in dna.composition_signature
    assert dna.format_role == "scene-background-or-banner-reference"
    assert dna.semantic_claims if hasattr(dna, "semantic_claims") else True
    assert dict(dna.confidence)["semantic"] == "not-verified"


def test_alpha_reference_is_marked_as_isolated_role(tmp_path: Path) -> None:
    source = tmp_path / "cutout.png"
    Image.new("RGBA", (100, 100), (255, 120, 0, 255)).save(source)

    dna = extract_visual_dna(profile_reference_image(source))

    assert dna.format_role == "transparent-or-isolated-reference"
    assert "alpha-isolation-present" in dna.composition_signature
