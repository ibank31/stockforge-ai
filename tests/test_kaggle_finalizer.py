import json
import subprocess
import py_compile
import runpy
import shutil
from pathlib import Path

from PIL import Image
import pytest

from stockforge.artifact import sha256_file
from stockforge.kaggle_finalizer import KaggleWorkerError, remote, submit, validate_local


def _bundle(tmp_path: Path, monkeypatch) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "kernel-metadata.json").write_text(
        json.dumps({
            "id": "ibank31/stockforge-finalizer",
            "title": "stockforge-finalizer",
            "code_file": "worker.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": True,
        }),
        encoding="utf-8",
    )
    worker_source = Path(__file__).resolve().parents[1] / "deploy" / "kaggle-finalizer" / "worker.py"
    shutil.copy2(worker_source, bundle / "worker.py")
    (bundle / "requirements.txt").write_text("pillow\n", encoding="utf-8")
    monkeypatch.setenv("STOCKFORGE_KAGGLE_FINALIZER_DIR", str(bundle))
    return bundle


def _request(project: Path) -> Path:
    source = project / "artifacts" / "preview.webp"
    source.parent.mkdir(parents=True)
    Image.new("RGB", (1024, 1024), (12, 34, 56)).save(source, format="WEBP")
    request = {
        "kind": "stockforge.master_finalizer_request",
        "status": "prepared_no_gpu",
        "source": {
            "relative_path": "artifacts/preview.webp",
            "sha256": sha256_file(source),
        },
        "target": {"mode": "ai_upscale", "scale": 4},
    }
    request_path = project / "master-finalizer-requests" / "request.json"
    request_path.parent.mkdir(parents=True)
    request_path.write_text(json.dumps(request), encoding="utf-8")
    return request_path


def test_validate_finalizer_bundle(tmp_path: Path, monkeypatch) -> None:
    bundle = _bundle(tmp_path, monkeypatch)
    result = validate_local()
    assert result["worker_dir"] == str(bundle)
    assert result["metadata"]["is_private"] is True


def test_remote_output_force_overwrites_stale_result(tmp_path: Path, monkeypatch) -> None:
    _bundle(tmp_path, monkeypatch)
    calls = []

    def fake_run(args, *, check=False):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "downloaded\n")

    monkeypatch.setattr("stockforge.kaggle_finalizer._run", fake_run)
    assert remote("output", output_dir=tmp_path / "output", force=True) == 0
    assert calls == [["kaggle", "kernels", "output", "ibank31/stockforge-finalizer", "-p", str((tmp_path / "output").resolve()), "--force"]]

    with pytest.raises(KaggleWorkerError, match="only for finalizer output"):
        remote("status", force=True)


def test_submit_stages_verified_request_and_preview(tmp_path: Path, monkeypatch) -> None:
    _bundle(tmp_path, monkeypatch)
    project = tmp_path / "project"
    request = _request(project)
    calls = []

    def fake_run(args, *, check=False):
        calls.append(args)
        staged = Path(args[args.index("-p") + 1])
        staged_worker = (staged / "worker.py").read_text(encoding="utf-8")
        assert "REQUEST_B64" in staged_worker and "SOURCE_B64" in staged_worker
        assert "preview.webp" in staged_worker
        assert staged_worker.index("REQUEST_B64") < staged_worker.index('if __name__ == "__main__":')
        py_compile.compile(str(staged / "worker.py"), doraise=True)
        monkeypatch.chdir(staged)
        namespace = runpy.run_path(str(staged / "worker.py"), run_name="stockforge_kaggle_test")
        namespace["materialize_staged_input"]()
        assert json.loads((staged / "request.json").read_text())["status"] == "prepared_no_gpu"
        assert (staged / "input" / "preview.webp").is_file()
        return subprocess.CompletedProcess(args, 0, "submitted\n")

    monkeypatch.setattr("stockforge.kaggle_finalizer._run", fake_run)
    assert submit(request=request, project_root=project) == 0
    assert calls and calls[0][:3] == ["kaggle", "kernels", "push"]
