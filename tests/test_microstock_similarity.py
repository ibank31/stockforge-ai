from pathlib import Path

from PIL import Image, ImageDraw

from stockforge.microstock_similarity import (
    combine_similarity,
    compare_composition,
    composition_fingerprint,
)


def _layout(path: Path, *, side: str) -> None:
    image = Image.new("RGB", (160, 160), "white")
    draw = ImageDraw.Draw(image)
    if side == "left":
        draw.rectangle((12, 24, 68, 138), fill="black")
    else:
        draw.rectangle((92, 24, 148, 138), fill="black")
    image.save(path)


def test_composition_fingerprint_is_deterministic(tmp_path: Path):
    path = tmp_path / "left.png"
    _layout(path, side="left")
    first = composition_fingerprint(path)
    second = composition_fingerprint(path)
    assert first.fingerprint == second.fingerprint
    assert first.algorithm == "edge-grid-8"


def test_shifted_layout_has_lower_composition_similarity(tmp_path: Path):
    left = tmp_path / "left.png"
    right = tmp_path / "right.png"
    _layout(left, side="left")
    _layout(right, side="right")
    result = compare_composition(
        composition_fingerprint(left),
        composition_fingerprint(right),
    )
    assert result.similarity < 0.94


def test_combined_similarity_prioritizes_layout_risk():
    result = combine_similarity(
        perceptual_similarity=0.60,
        perceptual_classification="distinct",
        composition=type("R", (), {"similarity": 0.97, "classification": "layout_duplicate"})(),
    )
    assert result.risk == "HIGH"
