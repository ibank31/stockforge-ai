from pathlib import Path

from stockforge.dedupe_pipeline import compare_images, sha256_file


def _write_pgm(path: Path, rows: list[list[int]]) -> None:
    height = len(rows)
    width = len(rows[0])
    body = bytes(pixel for row in rows for pixel in row)
    path.write_bytes(f"P5\n{width} {height}\n255\n".encode() + body)


def test_sha256_is_stable(tmp_path: Path) -> None:
    path = tmp_path / "image.pgm"
    _write_pgm(path, [[0, 255], [255, 0]])
    first = sha256_file(path)
    second = sha256_file(path)
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


def test_identical_bytes_short_circuit_as_exact_duplicate(tmp_path: Path) -> None:
    left = tmp_path / "left.pgm"
    right = tmp_path / "right.pgm"
    _write_pgm(left, [[0, 255], [255, 0]])
    right.write_bytes(left.read_bytes())
    result = compare_images(left, right, hash_size=4)
    assert result.classification == "exact_duplicate"
    assert result.comparison is None


def test_non_identical_spatial_pattern_uses_perceptual_comparison(tmp_path: Path) -> None:
    left = tmp_path / "left.pgm"
    right = tmp_path / "right.pgm"
    _write_pgm(left, [[0, 0, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255]])
    _write_pgm(right, [[0, 255, 0, 255], [255, 0, 255, 0], [0, 255, 0, 255], [255, 0, 255, 0]])
    result = compare_images(left, right, hash_size=8)
    assert result.classification in {"duplicate", "similar", "distinct"}
    assert result.comparison is not None
