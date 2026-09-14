from pathlib import Path

from PIL import Image

from stockforge.similarity_risk import analyze_similarity_risk


def test_identical_images_are_blocked(tmp_path: Path):
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (64, 64), "red").save(source)
    Image.new("RGB", (64, 64), "red").save(candidate)

    result = analyze_similarity_risk(source, candidate)

    assert result.level == "blocked"
    assert result.score >= 95


def test_different_images_have_lower_risk(tmp_path: Path):
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (64, 64), "red").save(source)
    Image.new("RGB", (64, 64), "blue").save(candidate)

    result = analyze_similarity_risk(source, candidate)

    assert result.score < 95
    assert result.level in {"low", "medium", "high"}
