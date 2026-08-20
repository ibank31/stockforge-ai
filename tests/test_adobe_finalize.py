from pathlib import Path

import pytest
from PIL import Image, ImageCms

from stockforge.adobe_finalize import AdobeFinalizationError, finalize_image
from stockforge.adobe_gate import inspect_image


def _save_png(path: Path, size: tuple[int, int], *, profile: bool = False) -> None:
    image = Image.new("RGB", size, (128, 128, 128))
    kwargs: dict[str, object] = {"format": "PNG"}
    if profile:
        kwargs["icc_profile"] = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    image.save(path, **kwargs)


def test_finalize_unprofiled_source_requires_explicit_assumption(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "final.jpg"
    _save_png(source, (2000, 2000))

    with pytest.raises(AdobeFinalizationError, match="no embedded ICC profile"):
        finalize_image(source, destination)

    report = finalize_image(source, destination, assume_srgb=True)
    gate = inspect_image(destination)

    assert report.assumed_srgb is True
    assert report.width == 2000
    assert report.height == 2000
    assert report.jpeg_quality >= 85
    assert gate.ready is True
    assert gate.format == "JPEG"
    assert gate.color_mode == "RGB"
    assert gate.icc_profile is not None


def test_finalize_profiled_source_converts_to_embedded_srgb(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "nested" / "final.jpg"
    _save_png(source, (2000, 2000), profile=True)

    report = finalize_image(source, destination)
    gate = inspect_image(destination)

    assert report.assumed_srgb is False
    assert report.source_profile is not None
    assert gate.ready is True
    assert "sRGB" in (gate.icc_profile or "")


def test_finalize_rejects_transparency(tmp_path: Path) -> None:
    source = tmp_path / "transparent.png"
    destination = tmp_path / "final.jpg"
    image = Image.new("RGBA", (2000, 2000), (128, 128, 128, 200))
    image.save(source, format="PNG")

    with pytest.raises(AdobeFinalizationError, match="non-opaque transparency"):
        finalize_image(source, destination, assume_srgb=True)


def test_finalize_rejects_below_adobe_minimum(tmp_path: Path) -> None:
    source = tmp_path / "small.png"
    destination = tmp_path / "final.jpg"
    _save_png(source, (1536, 1536))

    with pytest.raises(AdobeFinalizationError, match="4-100 MP"):
        finalize_image(source, destination, assume_srgb=True)


def test_finalize_refuses_in_place_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    _save_png(source, (2000, 2000))

    with pytest.raises(AdobeFinalizationError, match="different files"):
        finalize_image(source, source, assume_srgb=True)
