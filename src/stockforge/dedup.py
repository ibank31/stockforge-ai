"""Deterministic perceptual-ish duplicate detection for image assets.

The first implementation uses a small grayscale average hash. It is intentionally
simple, deterministic, and dependency-light. It is a similarity signal, not a
claim of semantic equivalence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .image_qa import ImageQAError

DEDUPE_SCHEMA_VERSION = 1


class DedupError(ValueError):
    """Raised when duplicate analysis cannot be performed."""


@dataclass(frozen=True, slots=True)
class ImageFingerprint:
    """Compact perceptual fingerprint for one image."""

    path: str
    algorithm: str
    fingerprint: str
    schema_version: int = DEDUPE_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SimilarityResult:
    """Distance and classification between two image fingerprints."""

    distance: int
    bits: int
    similarity: float
    classification: Literal["duplicate", "similar", "distinct"]


def _require_pillow():
    try:
        from PIL import Image
    except ImportError as exc:
        raise DedupError("Pillow is required for image deduplication; install the image extra") from exc
    return Image


def average_hash(path: Path, *, hash_size: int = 16) -> ImageFingerprint:
    """Create a deterministic grayscale average hash."""
    if hash_size < 4 or hash_size > 64:
        raise DedupError("hash_size must be between 4 and 64")
    image_path = Path(path)
    if not image_path.is_file():
        raise DedupError(f"Image file does not exist: {image_path}")
    Image = _require_pillow()
    try:
        with Image.open(image_path) as image:
            gray = image.convert("L").resize((hash_size, hash_size))
            pixels = list(gray.getdata())
    except Exception as exc:
        raise DedupError(f"Unable to fingerprint image: {image_path}") from exc
    mean = sum(pixels) / len(pixels)
    value = 0
    for pixel in pixels:
        value = (value << 1) | int(pixel >= mean)
    width = (hash_size * hash_size + 3) // 4
    return ImageFingerprint(str(image_path), f"ahash-{hash_size}", f"{value:0{width}x}")


def compare_fingerprints(left: ImageFingerprint, right: ImageFingerprint) -> SimilarityResult:
    """Compare two compatible fingerprints using Hamming distance."""
    if left.algorithm != right.algorithm:
        raise DedupError("fingerprints use different algorithms")
    left_value = int(left.fingerprint, 16)
    right_value = int(right.fingerprint, 16)
    bits = len(left.fingerprint) * 4
    distance = (left_value ^ right_value).bit_count()
    similarity = 1.0 - (distance / bits)
    if similarity >= 0.98:
        classification: Literal["duplicate", "similar", "distinct"] = "duplicate"
    elif similarity >= 0.90:
        classification = "similar"
    else:
        classification = "distinct"
    return SimilarityResult(distance, bits, similarity, classification)
