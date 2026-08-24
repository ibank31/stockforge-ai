import json
import subprocess
import py_compile
from pathlib import Path

from PIL import Image

from stockforge.artifact import sha256_file
from stockforge.kaggle_finalizer import submit, validate_local


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
    (bundle / "worker.py").write_text("print('worker')\n", encoding="utf-8")
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
        py_compile.compile(str(staged / "worker.py"), doraise=True)
        return subprocess.CompletedProcess(args, 0, "submitted\n")

    monkeypatch.setattr("stockforge.kaggle_finalizer._run", fake_run)
    assert submit(request=request, project_root=project) == 0
    assert calls and calls[0][:3] == ["kaggle", "kernels", "push"]
