from pathlib import Path

from PIL import Image

from stockforge.image_quality import inspect_quality


def test_quality_report_passes_decodable_image(tmp_path: Path) -> None:
    path = tmp_path / "clean.jpg"
    Image.new("RGB", (512, 512), (120, 130, 140)).save(path, quality=95)
    report = inspect_quality(path)
    assert report.width == 512
    assert report.height == 512
    assert not report.failures
    assert any(check.name == "decodability" and check.status == "PASS" for check in report.checks)


def test_quality_report_reviews_missing_file(tmp_path: Path) -> None:
    report = inspect_quality(tmp_path / "missing.jpg")
    assert report.ready_for_review is False
    assert report.failures[0].name == "file_exists"


def test_quality_report_reviews_heavy_clipping(tmp_path: Path) -> None:
    path = tmp_path / "clipped.jpg"
    Image.new("RGB", (256, 256), (255, 255, 255)).save(path)
    report = inspect_quality(path)
    clipping = next(check for check in report.checks if check.name == "exposure_clipping")
    assert clipping.status == "REVIEW"


def test_quality_report_reviews_extreme_saturation(tmp_path: Path) -> None:
    path = tmp_path / "saturated.jpg"
    Image.new("RGB", (256, 256), (255, 0, 0)).save(path)
    report = inspect_quality(path)
    saturation = next(check for check in report.checks if check.name == "extreme_saturation")
    assert saturation.status == "REVIEW"


def test_quality_report_fails_corrupt_image(tmp_path: Path) -> None:
    path = tmp_path / "broken.jpg"
    path.write_bytes(b"not-an-image")
    report = inspect_quality(path)
    assert report.failures
    assert report.failures[0].name == "decodability"
