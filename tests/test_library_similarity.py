from pathlib import Path

from PIL import Image, ImageDraw

from stockforge.library_similarity import scan_library


def _write(path: Path, side: str) -> None:
    image = Image.new("RGB", (128, 128), "white")
    draw = ImageDraw.Draw(image)
    x = 12 if side == "left" else 72
    draw.rectangle((x, 20, x + 36, 108), fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def test_library_scan_crosses_project_boundaries(tmp_path: Path):
    _write(tmp_path / "project-a" / "asset.png", "left")
    _write(tmp_path / "project-b" / "asset.png", "left")
    scan = scan_library(tmp_path)
    assert len(scan.files) == 2
    assert len(scan.candidates) == 1
    assert scan.candidates[0].risk == "HIGH"
