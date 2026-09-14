"""Centralized security boundary for untrusted raster image ingestion."""
from __future__ import annotations
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from PIL import Image, ImageOps, UnidentifiedImageError

DEFAULT_MAX_BYTES: Final = 45 * 1024 * 1024
DEFAULT_MAX_PIXELS: Final = 80_000_000
ALLOWED_FORMATS: Final = frozenset({"JPEG", "PNG", "WEBP"})

class ImageSecurityError(ValueError):
    pass

@dataclass(frozen=True, slots=True)
class SecureImageFacts:
    detected_format: str
    width: int
    height: int
    mode: str
    size_bytes: int
    had_metadata: bool

def secure_raster_image(source: Path, *, max_bytes: int = DEFAULT_MAX_BYTES, max_pixels: int = DEFAULT_MAX_PIXELS) -> SecureImageFacts:
    source = Path(source).expanduser().resolve(strict=True)
    if not source.is_file() or source.is_symlink():
        raise ImageSecurityError("Source must be a regular non-symlink file.")
    size = source.stat().st_size
    if size <= 0 or size > max_bytes:
        raise ImageSecurityError(f"Source size exceeds secure limit of {max_bytes} bytes.")
    old_limit = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = max_pixels
    try:
        with Image.open(source) as image:
            image.verify()
        with Image.open(source) as image:
            fmt = image.format or "UNKNOWN"
            if fmt not in ALLOWED_FORMATS:
                raise ImageSecurityError(f"Unsupported raster format: {fmt}")
            if getattr(image, "n_frames", 1) != 1:
                raise ImageSecurityError("Animated or multi-frame images are not accepted.")
            width, height = image.size
            if width * height > max_pixels:
                raise ImageSecurityError("Image pixel count exceeds secure limit.")
            mode = image.mode
            had_metadata = bool(image.getexif())
            image.load()
    except (UnidentifiedImageError, OSError, ValueError, RuntimeError) as exc:
        if isinstance(exc, ImageSecurityError):
            raise
        raise ImageSecurityError(f"Source is not a safely decodable image: {exc}") from exc
    finally:
        Image.MAX_IMAGE_PIXELS = old_limit
    return SecureImageFacts(fmt, width, height, mode, size, had_metadata)

def sanitized_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=destination.suffix, delete=False) as handle:
        tmp = Path(handle.name)
    with Image.open(source) as image:
        image.load()
        clean = ImageOps.exif_transpose(image)
        fmt = image.format
        if fmt == "JPEG":
            clean = clean.convert("RGB")
            clean.save(tmp, format="JPEG", quality=95, optimize=True)
        elif fmt == "PNG":
            clean.save(tmp, format="PNG")
        elif fmt == "WEBP":
            clean.save(tmp, format="WEBP", quality=95)
        else:
            raise ImageSecurityError(f"Unsupported raster format: {fmt}")
    os.replace(tmp, destination)
