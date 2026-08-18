"""Dependency-free structural quality checks for generated raster images.

This stage intentionally avoids computer vision and heavyweight image libraries.
It answers a narrower question first: is the generated file a plausible image,
and does its technical shape meet the configured production policy?
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

QA_SCHEMA_VERSION = 1
QA_STATUSES = frozenset({"pass", "warn", "fail"})
SUPPORTED_FORMATS = frozenset({"png", "jpeg", "webp"})


class ImageQAError(ValueError):
    """Raised when an image QA request is invalid."""


@dataclass(frozen=True, slots=True)
class ImageQAPolicy:
    """Configurable technical acceptance policy."""

    min_width: int = 2000
    min_height: int = 2000
    min_megapixels: float = 4.0
    max_bytes: int = 100 * 1024 * 1024
    warn_below_megapixels: float = 8.0
    allowed_formats: frozenset[str] = field(default_factory=lambda: SUPPORTED_FORMATS)

    def __post_init__(self) -> None:
        if self.min_width < 1 or self.min_height < 1:
            raise ImageQAError("minimum dimensions must be positive")
        if self.min_megapixels <= 0 or self.warn_below_megapixels <= 0:
            raise ImageQAError("megapixel thresholds must be positive")
        if self.max_bytes < 1:
            raise ImageQAError("max_bytes must be positive")
        if not self.allowed_formats or not self.allowed_formats <= SUPPORTED_FORMATS:
            raise ImageQAError("allowed_formats contains an unsupported format")


@dataclass(frozen=True, slots=True)
class ImageQAReport:
    """Stable result of one structural image inspection."""

    status: Literal["pass", "warn", "fail"]
    path: str
    format: str | None
    width: int | None
    height: int | None
    megapixels: float | None
    size_bytes: int
    checks: dict[str, str]
    schema_version: int = QA_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.status not in QA_STATUSES:
            raise ImageQAError(f"Unsupported QA status: {self.status}")
        if self.schema_version != QA_SCHEMA_VERSION:
            raise ImageQAError(f"Unsupported QA schema: {self.schema_version}")


def _detect_format(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return "webp"
    return None


def _png_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise ImageQAError("PNG is missing a valid IHDR header")
    width, height = struct.unpack(">II", data[16:24])
    if width < 1 or height < 1:
        raise ImageQAError("PNG dimensions are invalid")
    return width, height


def _jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 4 or not data.startswith(b"\xff\xd8"):
        raise ImageQAError("JPEG header is invalid")
    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            break
        segment_length = struct.unpack(">H", data[offset : offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(data):
            break
        if marker in set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0)):
            if segment_length < 7:
                break
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            if width < 1 or height < 1:
                break
            return width, height
        offset += segment_length
    raise ImageQAError("JPEG dimensions could not be read")


def _webp_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ImageQAError("WebP header is invalid")
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8 " and len(data) >= 30:
        start = data.find(b"\x9d\x01\x2a", 20)
        if start >= 0 and start + 7 <= len(data):
            width, height = struct.unpack("<HH", data[start + 3 : start + 7])
            return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        width = 1 + (bits & 0x3FFF)
        height = 1 + ((bits >> 14) & 0x3FFF)
        return width, height
    raise ImageQAError("WebP dimensions could not be read")


def _dimensions(data: bytes, image_format: str) -> tuple[int, int]:
    if image_format == "png":
        return _png_dimensions(data)
    if image_format == "jpeg":
        return _jpeg_dimensions(data)
    if image_format == "webp":
        return _webp_dimensions(data)
    raise ImageQAError(f"Unsupported image format: {image_format}")


def inspect_image(path: Path, *, policy: ImageQAPolicy | None = None) -> ImageQAReport:
    """Inspect one image file without decoding pixel data."""
    policy = policy or ImageQAPolicy()
    image_path = Path(path)
    if not image_path.is_file():
        raise ImageQAError(f"Image file does not exist: {image_path}")

    size_bytes = image_path.stat().st_size
    data = image_path.read_bytes()
    image_format = _detect_format(data)
    checks: dict[str, str] = {}

    if image_format is None:
        checks["format"] = "fail"
        return ImageQAReport("fail", str(image_path), None, None, None, None, size_bytes, checks)
    checks["format"] = "pass" if image_format in policy.allowed_formats else "fail"

    width: int | None = None
    height: int | None = None
    megapixels: float | None = None
    try:
        width, height = _dimensions(data, image_format)
        megapixels = (width * height) / 1_000_000
        checks["decode_header"] = "pass"
    except ImageQAError:
        checks["decode_header"] = "fail"

    if width is not None and height is not None:
        checks["minimum_dimensions"] = "pass" if width >= policy.min_width and height >= policy.min_height else "fail"
        checks["minimum_megapixels"] = "pass" if megapixels >= policy.min_megapixels else "fail"
        checks["recommended_megapixels"] = "pass" if megapixels >= policy.warn_below_megapixels else "warn"
    else:
        checks["minimum_dimensions"] = "fail"
        checks["minimum_megapixels"] = "fail"
        checks["recommended_megapixels"] = "fail"

    checks["file_size"] = "pass" if size_bytes <= policy.max_bytes else "fail"

    if "fail" in checks.values():
        status: Literal["pass", "warn", "fail"] = "fail"
    elif "warn" in checks.values():
        status = "warn"
    else:
        status = "pass"

    return ImageQAReport(status, str(image_path), image_format, width, height, megapixels, size_bytes, checks)
