"""Layered exact and perceptual image deduplication.

The pipeline keeps exact identity separate from perceptual similarity so an
identical byte stream is never confused with a merely similar image.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .dedup import ImageFingerprint, SimilarityResult, average_hash, compare_fingerprints


class DedupePipelineError(ValueError):
    """Raised when layered deduplication cannot be completed."""


@dataclass(frozen=True, slots=True)
class ExactFingerprint:
    path: str
    algorithm: str
    fingerprint: str


@dataclass(frozen=True, slots=True)
class DedupeResult:
    exact: ExactFingerprint
    perceptual: ImageFingerprint
    comparison: SimilarityResult | None
    classification: Literal["exact_duplicate", "duplicate", "similar", "distinct"]


def sha256_file(path: Path) -> ExactFingerprint:
    """Compute the immutable byte-level identity of a file."""
    image_path = Path(path)
    if not image_path.is_file():
        raise DedupePipelineError(f"Image file does not exist: {image_path}")
    digest = hashlib.sha256()
    try:
        with image_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise DedupePipelineError(f"Unable to hash image: {image_path}") from exc
    return ExactFingerprint(str(image_path), "sha256", digest.hexdigest())


def compare_images(left: Path, right: Path, *, hash_size: int = 16) -> DedupeResult:
    """Run exact comparison first, then perceptual comparison when needed."""
    left_exact = sha256_file(left)
    right_exact = sha256_file(right)
    if left_exact.fingerprint == right_exact.fingerprint:
        left_perceptual = average_hash(left, hash_size=hash_size)
        return DedupeResult(left_exact, left_perceptual, None, "exact_duplicate")

    left_perceptual = average_hash(left, hash_size=hash_size)
    right_perceptual = average_hash(right, hash_size=hash_size)
    comparison = compare_fingerprints(left_perceptual, right_perceptual)
    return DedupeResult(left_exact, left_perceptual, comparison, comparison.classification)
