"""Library-wide deterministic similarity scan for microstock asset collections."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .dedupe_candidates import SUPPORTED_SUFFIXES
from .dedupe_pipeline import compare_images
from .microstock_similarity import (
    combine_similarity,
    compare_composition,
    composition_fingerprint,
)


class LibrarySimilarityError(ValueError):
    """Raised when a library scan cannot be completed."""


@dataclass(frozen=True, slots=True)
class LibrarySimilarityCandidate:
    left: str
    right: str
    perceptual_similarity: float | None
    perceptual_classification: str
    composition_similarity: float
    composition_classification: str
    risk: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LibrarySimilarityScan:
    root: str
    files: tuple[str, ...]
    candidates: tuple[LibrarySimilarityCandidate, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "files": list(self.files),
            "candidates": [item.to_dict() for item in self.candidates],
            "notice": (
                "Library-wide deterministic scan. HIGH/MEDIUM/LOW are review "
                "priorities, not semantic or marketplace acceptance predictions."
            ),
        }


def scan_library(root: Path, *, perceptual_floor: float = 0.90) -> LibrarySimilarityScan:
    """Compare supported raster files across one library tree, including projects."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise LibrarySimilarityError(f"Directory does not exist: {root}")
    if not 0.0 <= perceptual_floor <= 1.0:
        raise LibrarySimilarityError("perceptual_floor must be between 0 and 1")

    paths = tuple(
        sorted(path for path in root.rglob("*")
               if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES)
    )
    fingerprints = {path: composition_fingerprint(path) for path in paths}
    candidates: list[LibrarySimilarityCandidate] = []
    for index, left in enumerate(paths):
        for right in paths[index + 1:]:
            image_result = compare_images(left, right)
            perceptual_similarity = (
                image_result.comparison.similarity
                if image_result.comparison is not None
                else 1.0
            )
            composition = compare_composition(fingerprints[left], fingerprints[right])
            combined = combine_similarity(
                perceptual_similarity=perceptual_similarity,
                perceptual_classification=image_result.classification,
                composition=composition,
            )
            if (
                image_result.classification != "distinct"
                or composition.classification != "layout_distinct"
            ):
                candidates.append(LibrarySimilarityCandidate(
                    str(left.relative_to(root)),
                    str(right.relative_to(root)),
                    round(perceptual_similarity, 4),
                    image_result.classification,
                    round(composition.similarity, 4),
                    composition.classification,
                    combined.risk,
                ))
    candidates.sort(
        key=lambda item: (
            {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[item.risk],
            -item.composition_similarity,
            -(item.perceptual_similarity or 0),
            item.left,
            item.right,
        )
    )
    return LibrarySimilarityScan(
        str(root),
        tuple(str(path.relative_to(root)) for path in paths),
        tuple(candidates),
    )
