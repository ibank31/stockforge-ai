from pathlib import Path

import pytest
from PIL import Image

from stockforge.seamless_pattern import SeamlessPatternError, inspect_seamless_raster


def _write_seamless(path: Path) -> None:
    image = Image.new("RGB", (8, 8), "#16324F")
    for y in range(8):
        image.putpixel((0, y), (240, 240, 240))
        image.putpixel((7, y), (240, 240, 240))
    for x in range(8):
        image.putpixel((x, 0), (240, 240, 240))
        image.putpixel((x, 7), (240, 240, 240))
    image.save(path)


def test_seamless_raster_passes_matching_opposite_edges(tmp_path: Path) -> None:
    candidate = tmp_path / "seamless.png"
    _write_seamless(candidate)

    report = inspect_seamless_raster(candidate)

    assert report.ready is True
    assert report.horizontal_error == 0
    assert report.vertical_error == 0
    assert all(check.status == "PASS" for check in report.checks[:2])


def test_seamless_raster_rejects_visible_horizontal_boundary(tmp_path: Path) -> None:
    candidate = tmp_path / "broken.png"
    _write_seamless(candidate)
    with Image.open(candidate) as image:
        image = image.copy()
        image.putpixel((7, 3), (255, 0, 0))
        image.save(candidate)

    report = inspect_seamless_raster(candidate)

    assert report.ready is False
    assert report.horizontal_error is not None and report.horizontal_error > 0
    assert report.vertical_error == 0


def test_seamless_raster_accepts_small_tolerance(tmp_path: Path) -> None:
    candidate = tmp_path / "near-seamless.png"
    _write_seamless(candidate)
    with Image.open(candidate) as image:
        image = image.copy()
        image.putpixel((7, 3), (241, 240, 240))
        image.save(candidate)

    report = inspect_seamless_raster(candidate, tolerance=1.0)

    assert report.ready is True
    assert report.horizontal_error is not None and report.horizontal_error <= 1.0


def test_seamless_raster_rejects_invalid_edge_width(tmp_path: Path) -> None:
    candidate = tmp_path / "pattern.png"
    _write_seamless(candidate)

    with pytest.raises(SeamlessPatternError, match="edge_width"):
        inspect_seamless_raster(candidate, edge_width=0)


def test_seamless_raster_reports_missing_file(tmp_path: Path) -> None:
    report = inspect_seamless_raster(tmp_path / "missing.png")

    assert report.ready is False
    assert report.checks[0].name == "file_exists"
