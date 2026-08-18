from pathlib import Path

from stockforge.dedupe_candidates import scan_directory


def _write_pgm(path: Path, rows: list[list[int]]) -> None:
    height = len(rows)
    width = len(rows[0])
    body = bytes(pixel for row in rows for pixel in row)
    path.write_bytes(f"P5\n{width} {height}\n255\n".encode() + body)


def test_scan_groups_exact_duplicates(tmp_path: Path) -> None:
    first = tmp_path / "a.png"
    duplicate = tmp_path / "b.png"
    distinct = tmp_path / "c.png"
    _write_pgm(first, [[0, 0, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255], [0, 0, 255, 255]])
    duplicate.write_bytes(first.read_bytes())
    _write_pgm(distinct, [[0, 255, 0, 255], [255, 0, 255, 0], [0, 255, 0, 255], [255, 0, 255, 0]])
    scan = scan_directory(tmp_path, hash_size=8, similarity_floor=0.90)
    assert len(scan.files) == 3
    assert len(scan.exact_groups) == 1
    assert set(scan.exact_groups[0].paths) == {str(first), str(duplicate)}
    assert len(scan.perceptual) == 2


def test_scan_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "z.png"
    second = tmp_path / "a.png"
    _write_pgm(first, [[0, 0], [255, 255]])
    _write_pgm(second, [[0, 255], [0, 255]])
    assert scan_directory(tmp_path, hash_size=8) == scan_directory(tmp_path, hash_size=8)
