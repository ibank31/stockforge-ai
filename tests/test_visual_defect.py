from pathlib import Path

from PIL import Image

from stockforge.visual_defect import VisualDefectPolicy, inspect_visual_defects


def make_image(path: Path, value: int) -> None:
    image = Image.new("RGB", (200, 200), (value, value, value))
    image.save(path, format="PNG")


def test_flat_image_fails(tmp_path: Path) -> None:
    path = tmp_path / "flat.png"
    make_image(path, 128)
    report = inspect_visual_defects(path)
    assert report.status == "fail"
    assert report.checks["flat_image"] == "fail"


def test_normal_contrast_image_passes_pixel_gate(tmp_path: Path) -> None:
    path = tmp_path / "normal.png"
    image = Image.new("RGB", (200, 200), (128, 128, 128))
    for x in range(100, 200):
        for y in range(200):
            image.putpixel((x, y), (220, 220, 220))
    image.save(path, format="PNG")
    report = inspect_visual_defects(
        path,
        policy=VisualDefectPolicy(min_luma_stddev=3.0, warn_luma_stddev=8.0),
    )
    assert report.checks["flat_image"] == "pass"
    assert report.luminance_stddev is not None


def test_heavy_highlight_clipping_fails(tmp_path: Path) -> None:
    path = tmp_path / "clipped.png"
    image = Image.new("RGB", (200, 200), (255, 255, 255))
    image.save(path, format="PNG")
    report = inspect_visual_defects(path)
    assert report.status == "fail"
    assert report.checks["bright_clipping"] == "fail"
