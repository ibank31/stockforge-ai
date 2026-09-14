from pathlib import Path
from stockforge.database import Database
from stockforge.orphan_reconciliation import find_orphan_artifacts

def test_find_orphan_artifacts(tmp_path: Path):
    db = Database(tmp_path / "db.sqlite"); db.initialize()
    db.create_project("p1", "project", tmp_path)
    path = tmp_path / "artifacts" / "external" / "orphan.png"
    path.parent.mkdir(parents=True); path.write_bytes(b"orphan")
    report = find_orphan_artifacts(db, "p1", tmp_path)
    assert report.orphan_files == ("artifacts/external/orphan.png",)
