from pathlib import Path

from PIL import Image, ImageCms

from stockforge.adobe_gate import inspect_image


def _save_jpeg(path: Path, size: tuple[int, int], *, profile: bool = True) -> None:
    image = Image.new("RGB", size, (128, 128, 128))
    kwargs = {"format": "JPEG", "quality": 90}
    if profile:
        kwargs["icc_profile"] = ImageCms.createProfile("sRGB").tobytes()
    image.save(path, **kwargs)


def test_valid_4mp_srgb_jpeg_passes(tmp_path: Path) -> None:
    path = tmp_path / "valid.jpg"
    _save_jpeg(path, (2000, 2000))

    report = inspect_image(path)

    assert report.ready is True
    assert not report.failures
    assert report.megapixels == 4.0


def test_webp_fails_format(tmp_path: Path) -> None:
    path = tmp_path / "image.webp"
    Image.new("RGB", (2000, 2000), (128, 128, 128)).save(path, format="WEBP")

    report = inspect_image(path)

    assert report.ready is False
    assert any(check.name == "format" and check.status == "FAIL" for check in report.checks)


def test_small_image_fails_resolution(tmp_path: Path) -> None:
    path = tmp_path / "small.jpg"
    _save_jpeg(path, (1536, 1536))

    report = inspect_image(path)

    resolution = next(check for check in report.checks if check.name == "resolution")
    assert resolution.status == "FAIL"
    assert report.megapixels == 1536 * 1536 / 1_000_000


def test_missing_icc_profile_requires_review(tmp_path: Path) -> None:
    path = tmp_path / "no-profile.jpg"
    _save_jpeg(path, (2000, 2000), profile=False)

    report = inspect_image(path)

    color = next(check for check in report.checks if check.name == "color_space")
    assert color.status == "REVIEW"
    assert report.ready is False


def test_cmyk_jpeg_fails_color_mode(tmp_path: Path) -> None:
    path = tmp_path / "cmyk.jpg"
    Image.new("CMYK", (2000, 2000), (0, 0, 0, 0)).save(path, format="JPEG")

    report = inspect_image(path)

    color_mode = next(check for check in report.checks if check.name == "color_mode")
    assert color_mode.status == "FAIL"
