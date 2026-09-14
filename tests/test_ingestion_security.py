from pathlib import Path
import pytest
from PIL import Image
from stockforge.ingestion_security import ImageSecurityError, secure_raster_image, sanitized_copy

def test_secure_raster_rejects_oversized_limit(tmp_path: Path):
    source = tmp_path / "x.png"
    Image.new("RGB", (10, 10), "white").save(source)
    with pytest.raises(ImageSecurityError):
        secure_raster_image(source, max_bytes=1)

def test_secure_raster_accepts_single_png(tmp_path: Path):
    source = tmp_path / "x.png"
    Image.new("RGB", (10, 10), "white").save(source)
    facts = secure_raster_image(source)
    assert facts.detected_format == "PNG"
    assert facts.width == 10

def test_sanitized_copy_strips_exif_metadata(tmp_path: Path):
    source = tmp_path / "x.jpg"
    destination = tmp_path / "clean.jpg"
    image = Image.new("RGB", (10, 10), "white")
    exif = image.getexif(); exif[270] = "secret"
    image.save(source, exif=exif)
    sanitized_copy(source, destination)
    with Image.open(destination) as result:
        assert 270 not in result.getexif()
