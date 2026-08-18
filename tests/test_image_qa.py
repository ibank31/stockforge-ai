import struct
from pathlib import Path

from stockforge.image_qa import ImageQAPolicy, ImageQAError, inspect_image


def png_bytes(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x02\x00\x00\x00" + b"\x00\x00\x00\x00"


def test_valid_png_passes_structural_checks(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(png_bytes(3000, 3000))

    report = inspect_image(path)

    assert report.status == "pass"
    assert report.format == "png"
    assert report.width == 3000
    assert report.height == 3000
    assert report.megapixels == 9.0
    assert report.checks["minimum_megapixels"] == "pass"


def test_small_image_fails_minimum_resolution(tmp_path: Path) -> None:
    path = tmp_path / "small.png"
    path.write_bytes(png_bytes(1000, 1000))

    report = inspect_image(path)

    assert report.status == "fail"
    assert report.checks["minimum_dimensions"] == "fail"
    assert report.checks["minimum_megapixels"] == "fail"


def test_medium_image_warns_but_can_be_structurally_valid(tmp_path: Path) -> None:
    path = tmp_path / "medium.png"
    path.write_bytes(png_bytes(2500, 2000))
    policy = ImageQAPolicy(min_megapixels=4.0, warn_below_megapixels=8.0)

    report = inspect_image(path, policy=policy)

    assert report.status == "warn"
    assert report.checks["minimum_megapixels"] == "pass"
    assert report.checks["recommended_megapixels"] == "warn"


def test_unknown_format_fails(tmp_path: Path) -> None:
    path = tmp_path / "not-image.bin"
    path.write_bytes(b"not an image")

    report = inspect_image(path)

    assert report.status == "fail"
    assert report.format is None
    assert report.checks["format"] == "fail"


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    try:
        inspect_image(tmp_path / "missing.png")
    except ImageQAError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError("expected ImageQAError")
