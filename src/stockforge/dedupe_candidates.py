"""Deterministic batch candidate discovery for image deduplication."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .dedup import ImageFingerprint, SimilarityResult, average_hash, compare_fingerprints
from .dedupe_pipeline import ExactFingerprint, sha256_file

SUPPORTED_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp"})


class CandidateScanError(ValueError):
    """Raised when candidate scanning input is invalid."""


@dataclass(frozen=True, slots=True)
class DuplicateGroup:
    sha256: str
    paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SimilarityCandidate:
    left: str
    right: str
    result: SimilarityResult


@dataclass(frozen=True, slots=True)
class CandidateScan:
    files: tuple[str, ...]
    exact_groups: tuple[DuplicateGroup, ...]
    perceptual: tuple[ImageFingerprint, ...]
    candidates: tuple[SimilarityCandidate, ...]


def scan_directory(root: Path, *, hash_size: int = 16, similarity_floor: float = 0.90) -> CandidateScan:
    """Discover exact duplicate groups and perceptual similarity candidates."""
    root = Path(root)
    if not root.is_dir():
        raise CandidateScanError(f"Directory does not exist: {root}")
    if not 4 <= hash_size <= 64:
        raise CandidateScanError("hash_size must be between 4 and 64")
    if not 0 <= similarity_floor <= 1:
        raise CandidateScanError("similarity_floor must be between 0 and 1")

    paths = tuple(sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES))
    exact_by_hash: dict[str, list[str]] = {}
    exact_records: dict[str, ExactFingerprint] = {}
    for path in paths:
        record = sha256_file(path)
        exact_by_hash.setdefault(record.fingerprint, []).append(str(path))
        exact_records[str(path)] = record

    groups = tuple(
        DuplicateGroup(digest, tuple(sorted(items)))
        for digest, items in sorted(exact_by_hash.items())
        if len(items) > 1
    )

    unique_paths = tuple(sorted(path for digest, items in exact_by_hash.items() for path in items[:1]))
    perceptual = tuple(average_hash(Path(path), hash_size=hash_size) for path in unique_paths)
    candidates: list[SimilarityCandidate] = []
    for index, left in enumerate(perceptual):
        for right in perceptual[index + 1 :]:
            result = compare_fingerprints(left, right)
            if result.similarity >= similarity_floor:
                candidates.append(SimilarityCandidate(left.path, right.path, result))

    candidates.sort(key=lambda item: (-item.result.similarity, item.left, item.right))
    return CandidateScan(tuple(str(p) for p in paths), groups, perceptual, tuple(candidates))
