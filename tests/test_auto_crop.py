from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from stockforge.auto_crop import AutoCropError, CropBox, crop_reference, suggest_crop_candidates


def _screenshot(path: Path) -> None:
    image = Image.new("RGB", (1200, 1000), (15, 15, 18))
    draw = ImageDraw.Draw(image)
    # Simulate dark social UI with one colorful featured visual.
    draw.rectangle((260, 300, 980, 720), fill=(25, 180, 190))
    draw.rectangle((260, 300, 500, 720), fill=(245, 190, 110))
    image.save(path)


def test_suggests_distinct_crop_candidates(tmp_path: Path) -> None:
    source = tmp_path / "screenshot.png"
    _screenshot(source)

    candidates = suggest_crop_candidates(source, limit=4)

    assert 1 <= len(candidates) <= 4
    assert candidates[0].rank == 1
    assert all(item.box.width > 0 and item.box.height > 0 for item in candidates)
    assert all(0 <= item.box.left < item.box.right <= 1200 for item in candidates)
    assert all(0 <= item.box.top < item.box.bottom <= 1000 for item in candidates)


def test_applies_human_confirmed_crop_without_mutating_source(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "crop.jpg"
    _screenshot(source)
    before = source.read_bytes()

    output = crop_reference(source, destination, CropBox(260, 300, 980, 720))

    assert output == destination.resolve()
    assert source.read_bytes() == before
    with Image.open(destination) as image:
        assert image.size == (720, 420)


def test_rejects_out_of_bounds_manual_crop(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    _screenshot(source)

    with pytest.raises(AutoCropError, match="outside"):
        crop_reference(source, tmp_path / "crop.png", CropBox(-1, 0, 20, 20))
