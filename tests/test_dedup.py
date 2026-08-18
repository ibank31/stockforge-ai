from pathlib import Path

import pytest

from stockforge.dedup import DedupError, average_hash, compare_fingerprints


def _write_pgm(path: Path, rows: list[list[int]]) -> None:
    height = len(rows)
    width = len(rows[0])
    body = bytes(pixel for row in rows for pixel in row)
    path.write_bytes(f"P5\n{width} {height}\n255\n".encode() + body)


def test_fingerprints_are_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "image.pgm"
    _write_pgm(path, [[0, 0, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255]])
    first = average_hash(path, hash_size=4)
    second = average_hash(path, hash_size=4)
    assert first.fingerprint == second.fingerprint
    assert first.algorithm == "ahash-4"


def test_identical_fingerprints_are_duplicates(tmp_path: Path) -> None:
    path = tmp_path / "image.pgm"
    _write_pgm(path, [[0, 255], [255, 0]])
    fingerprint = average_hash(path, hash_size=4)
    result = compare_fingerprints(fingerprint, fingerprint)
    assert result.distance == 0
    assert result.similarity == 1.0
    assert result.classification == "duplicate"


def test_different_spatial_pattern_is_distinct(tmp_path: Path) -> None:
    left = tmp_path / "left.pgm"
    right = tmp_path / "right.pgm"
    _write_pgm(left, [[0, 0], [255, 255]])
    _write_pgm(right, [[0, 255], [0, 255]])
    result = compare_fingerprints(average_hash(left, hash_size=4), average_hash(right, hash_size=4))
    assert result.similarity < 0.90
    assert result.classification == "distinct"


def test_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(DedupError):
        average_hash(tmp_path / "missing.png")


def test_mismatched_algorithms_fail(tmp_path: Path) -> None:
    path = tmp_path / "image.pgm"
    _write_pgm(path, [[0, 255], [255, 0]])
    first = average_hash(path, hash_size=4)
    second = average_hash(path, hash_size=8)
    with pytest.raises(DedupError):
        compare_fingerprints(first, second)
