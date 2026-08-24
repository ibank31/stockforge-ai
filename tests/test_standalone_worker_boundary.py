from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_zerogpu_worker_has_no_construction_reality_compiler_in_generation_path():
    source = (ROOT / "deploy" / "zerogpu" / "app.py").read_text(encoding="utf-8").lower()

    assert "reality_engine" not in source
    assert "wall_moisture_inspection" not in source
    assert "compile_prompt(" not in source
    assert "standalone asset portfolio" in source


def test_kaggle_worker_has_no_construction_reality_compiler_in_generation_path():
    source = (ROOT / "deploy" / "kaggle" / "worker.py").read_text(encoding="utf-8").lower()

    assert "reality_engine" not in source
    assert "wall_moisture_inspection" not in source
    assert "compile_prompt(" not in source
