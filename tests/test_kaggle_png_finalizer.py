import base64
import json
import py_compile
import shutil
import subprocess
from pathlib import Path

from PIL import Image
import pytest

from stockforge.artifact import sha256_file
from stockforge.kaggle_png_finalizer import (
    KaggleWorkerError,
    _request_and_source,
    prepare_request,
    submit,
    validate_local,
)


def _bundle(tmp_path: Path, monkeypatch) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "kernel-metadata.json").write_text(
        json.dumps({
            "id": "ibank31/stockforge-png-finalizer",
            "title": "stockforge-png-finalizer",
            "code_file": "worker.py",
            "language": "python",
            "kernel_type": "script",
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": False,
            "dataset_sources": ["iqbalteguh/stockforge-birefnet-cache"],
        }),
        encoding="utf-8",
    )
    worker_source = Path(__file__).resolve().parents[1] / "deploy" / "kaggle-png-finalizer" / "worker.py"
    shutil.copy2(worker_source, bundle / "worker.py")
    (bundle / "requirements.txt").write_text("pillow\n", encoding="utf-8")
    monkeypatch.setenv("STOCKFORGE_KAGGLE_PNG_FINALIZER_DIR", str(bundle))
    return bundle


def _source(project: Path, name: str = "artifacts/preview.webp", size: tuple[int, int] = (1024, 1024)) -> Path:
    source = project / name
    source.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (240, 240, 240)).save(source, format="WEBP")
    return source


def test_validate_png_bundle_is_private_offline_and_cache_only(tmp_path: Path, monkeypatch) -> None:
    bundle = _bundle(tmp_path, monkeypatch)
    result = validate_local()
    metadata = result["metadata"]
    assert result["worker_dir"] == str(bundle)
    assert metadata["is_private"] is True
    assert metadata["enable_internet"] is False
    assert metadata["dataset_sources"] == ["iqbalteguh/stockforge-birefnet-cache"]
    assert metadata["id"] != "ibank31/stockforge-finalizer"


def test_prepare_request_writes_review_gated_1024_to_4096_contract(tmp_path: Path) -> None:
    project = tmp_path / "project"
    source = _source(project)
    request_path, payload = prepare_request(source=source, project_root=project, project_id="project-1")
    assert request_path.parent == project / "png-finalizer-requests"
    assert payload["kind"] == "stockforge.png_finalizer_request"
    assert payload["status"] == "prepared_no_gpu"
    assert payload["source"]["relative_path"] == "artifacts/preview.webp"
    assert payload["source"]["sha256"] == sha256_file(source)
    assert payload["target"]["expected_width"] == 4096
    assert payload["target"]["expected_height"] == 4096
    assert payload["target"]["format"] == "png"
    assert payload["target"]["color_mode"] == "RGBA"
    assert payload["target"]["color_space"] == "sRGB"
    assert payload["target"]["requires_true_alpha"] is True
    assert payload["human_review_required"] is True
    assert json.loads(request_path.read_text(encoding="utf-8")) == payload


def test_prepare_request_rejects_jpeg_and_non_square_source(tmp_path: Path) -> None:
    project = tmp_path / "project"
    jpeg = project / "artifacts" / "preview.jpg"
    jpeg.parent.mkdir(parents=True)
    Image.new("RGB", (1024, 1024), "white").save(jpeg, format="JPEG")
    with pytest.raises(KaggleWorkerError, match="JPEG is rejected"):
        prepare_request(source=jpeg, project_root=project)

    wide = _source(project, "artifacts/wide.webp", (1344, 768))
    with pytest.raises(KaggleWorkerError, match="1024x1024"):
        prepare_request(source=wide, project_root=project)


def test_submit_rejects_source_escape_and_bad_contract(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    source = _source(project)
    request_path, payload = prepare_request(source=source, project_root=project)
    payload["source"]["relative_path"] = "../outside.webp"
    request_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(KaggleWorkerError, match="escapes project root"):
        _request_and_source(request_path, project)


def test_submit_stages_png_request_and_source_without_jpeg_worker(tmp_path: Path, monkeypatch) -> None:
    _bundle(tmp_path, monkeypatch)
    project = tmp_path / "project"
    source = _source(project)
    request, _payload = prepare_request(source=source, project_root=project)
    calls = []

    def fake_run(args, *, check=False):
        calls.append(args)
        staged = Path(args[args.index("-p") + 1])
        staged_worker = (staged / "worker.py").read_text(encoding="utf-8")
        assert "REQUEST_B64" in staged_worker and "SOURCE_B64" in staged_worker
        assert "stockforge-png-finalizer" in staged_worker
        assert "stockforge-finalizer" not in staged_worker
        assert "RealESRGAN" not in staged_worker
        assert base64.b64encode(request.read_bytes()).decode("ascii") in staged_worker
        assert base64.b64encode(source.read_bytes()).decode("ascii") in staged_worker
        py_compile.compile(str(staged / "worker.py"), doraise=True)
        return subprocess.CompletedProcess(args, 0, "submitted\n")

    monkeypatch.setattr("stockforge.kaggle_png_finalizer._run", fake_run)
    assert submit(request=request, project_root=project) == 0
    assert calls and calls[0][:3] == ["kaggle", "kernels", "push"]


def test_request_submit_requires_true_alpha_contract(tmp_path: Path) -> None:
    project = tmp_path / "project"
    source = _source(project)
    request_path, payload = prepare_request(source=source, project_root=project)
    payload["target"]["requires_true_alpha"] = False
    request_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(KaggleWorkerError, match="true alpha"):
        _request_and_source(request_path, project)


def test_png_worker_and_metadata_have_no_online_or_jpeg_route_references() -> None:
    root = Path(__file__).resolve().parents[1]
    worker = (root / "deploy" / "kaggle-png-finalizer" / "worker.py").read_text(encoding="utf-8")
    metadata = json.loads((root / "deploy" / "kaggle-png-finalizer" / "kernel-metadata.json").read_text(encoding="utf-8"))
    assert metadata["enable_internet"] is False
    assert metadata["dataset_sources"] == ["iqbalteguh/stockforge-birefnet-cache"]
    assert "RealESRGAN" not in worker
    assert "stockforge-finalizer" not in worker
    assert "requests.get" not in worker
    assert "hf_token" not in worker
