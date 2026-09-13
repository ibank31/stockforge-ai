"""Deterministic composition-aware similarity signals for microstock review.

This module intentionally adds a third similarity layer without pretending to
solve semantic equivalence. It measures coarse spatial structure using a grid
of local edge-energy values. The result is useful for detecting near-identical
layouts that average hash alone can miss, but human review remains mandatory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .dedup import DedupError


class MicrostockSimilarityError(ValueError):
    """Raised when composition similarity cannot be calculated."""


COMPOSITION_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class CompositionFingerprint:
    path: str
    algorithm: str
    fingerprint: tuple[int, ...]
    grid_size: int
    schema_version: int = COMPOSITION_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class CompositionResult:
    distance: int
    cells: int
    similarity: float
    classification: Literal["layout_duplicate", "layout_similar", "layout_distinct"]
    notice: str = (
        "Coarse spatial-layout signal only; it does not establish semantic, "
        "conceptual, aesthetic, legal, or commercial equivalence."
    )


def _require_pillow():
    try:
        from PIL import Image, ImageFilter
    except ImportError as exc:
        raise MicrostockSimilarityError(
            "Pillow is required for composition similarity; install the image extra"
        ) from exc
    return Image, ImageFilter


def composition_fingerprint(path: Path, *, grid_size: int = 8) -> CompositionFingerprint:
    """Create a deterministic coarse layout fingerprint from local edge energy."""
    if not 4 <= grid_size <= 32:
        raise MicrostockSimilarityError("grid_size must be between 4 and 32")
    image_path = Path(path)
    if not image_path.is_file():
        raise MicrostockSimilarityError(f"Image file does not exist: {image_path}")
    Image, ImageFilter = _require_pillow()
    sample = grid_size * 8
    try:
        with Image.open(image_path) as image:
            gray = image.convert("L").resize((sample, sample))
            edges = gray.filter(ImageFilter.FIND_EDGES)
            pixels = list(edges.getdata())
    except Exception as exc:
        raise MicrostockSimilarityError(
            f"Unable to calculate composition fingerprint: {image_path}"
        ) from exc

    cells: list[int] = []
    block = sample // grid_size
    for gy in range(grid_size):
        for gx in range(grid_size):
            energy = 0
            for y in range(gy * block, (gy + 1) * block):
                start = y * sample + gx * block
                energy += sum(pixels[start:start + block])
            cells.append(energy // (block * block))
    mean = sum(cells) / len(cells)
    fingerprint = tuple(int(value >= mean) for value in cells)
    return CompositionFingerprint(
        str(image_path),
        f"edge-grid-{grid_size}",
        fingerprint,
        grid_size,
    )


def compare_composition(
    left: CompositionFingerprint, right: CompositionFingerprint
) -> CompositionResult:
    """Compare two compatible coarse composition fingerprints."""
    if left.algorithm != right.algorithm or left.grid_size != right.grid_size:
        raise MicrostockSimilarityError("composition fingerprints use different algorithms")
    cells = len(left.fingerprint)
    if cells == 0 or cells != len(right.fingerprint):
        raise MicrostockSimilarityError("composition fingerprints are incompatible")
    distance = sum(a != b for a, b in zip(left.fingerprint, right.fingerprint))
    similarity = 1.0 - (distance / cells)
    if similarity >= 0.94:
        classification: Literal["layout_duplicate", "layout_similar", "layout_distinct"] = "layout_duplicate"
    elif similarity >= 0.78:
        classification = "layout_similar"
    else:
        classification = "layout_distinct"
    return CompositionResult(distance, cells, similarity, classification)


@dataclass(frozen=True, slots=True)
class SimilarityV2Result:
    perceptual_similarity: float | None
    perceptual_classification: str
    composition_similarity: float
    composition_classification: str
    risk: Literal["HIGH", "MEDIUM", "LOW"]
    notice: str = (
        "Risk is a deterministic review priority, not a marketplace rejection "
        "prediction or a claim of semantic similarity."
    )


def combine_similarity(
    *,
    perceptual_similarity: float | None,
    perceptual_classification: str,
    composition: CompositionResult,
) -> SimilarityV2Result:
    """Combine existing perceptual output with the composition signal conservatively."""
    if perceptual_classification in {"exact_duplicate", "duplicate"}:
        risk: Literal["HIGH", "MEDIUM", "LOW"] = "HIGH"
    elif composition.classification == "layout_duplicate":
        risk = "HIGH"
    elif (
        perceptual_classification == "similar"
        or composition.classification == "layout_similar"
    ):
        risk = "MEDIUM"
    else:
        risk = "LOW"
    return SimilarityV2Result(
        perceptual_similarity,
        perceptual_classification,
        composition.similarity,
        composition.classification,
        risk,
    )
