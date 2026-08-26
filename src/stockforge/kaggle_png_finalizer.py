"""Termux-side controller for the isolated private Kaggle PNG alpha finalizer."""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

from PIL import Image

from .artifact import sha256_file
from .kaggle_worker import DEFAULT_ACCELERATOR, KAGGLE_USER, KaggleWorkerError, _run, repo_root

PNG_FINALIZER_KERNEL_DEFAULT = f"{KAGGLE_USER}/stockforge-png-finalizer"
PNG_REQUEST_DIR_NAME = "png-finalizer-requests"
PNG_SOURCE_SUFFIXES = {".png", ".webp"}
PNG_SOURCE_SIZE = (1024, 1024)
PNG_SCALE = 4
PNG_TARGET_SIZE = (PNG_SOURCE_SIZE[0] * PNG_SCALE, PNG_SOURCE_SIZE[1] * PNG_SCALE)


def finalizer_dir() -> Path:
    configured = os.environ.get("STOCKFORGE_KAGGLE_PNG_FINALIZER_DIR")
    return Path(configured).expanduser().resolve() if configured else repo_root() / "deploy" / "kaggle-png-finalizer"


def metadata_path() -> Path:
    return finalizer_dir() / "kernel-metadata.json"


def load_metadata() -> dict:
    path = metadata_path()
    if not path.is_file():
        raise KaggleWorkerError(f"PNG finalizer metadata not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KaggleWorkerError(f"Invalid PNG finalizer metadata JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("id"), str) or not data["id"]:
        raise KaggleWorkerError("PNG finalizer metadata must contain a non-empty id")
    if data.get("is_private") is not True or data.get("enable_internet") is not False:
        raise KaggleWorkerError("PNG finalizer must remain private and offline")
    if data.get("id") == f"{KAGGLE_USER}/stockforge-finalizer":
        raise KaggleWorkerError("PNG finalizer cannot target the protected JPEG finalizer")
    if data.get("dataset_sources") != ["iqbalteguh/stockforge-birefnet-cache"]:
        raise KaggleWorkerError("PNG finalizer must use only the pinned BiRefNet cache dataset")
    return data


def validate_local() -> dict:
    metadata = load_metadata()
    required = ("worker.py", "requirements.txt")
    missing = [name for name in required if not (finalizer_dir() / name).is_file()]
    if missing:
        raise KaggleWorkerError("PNG finalizer bundle is incomplete: " + ", ".join(missing))
    return {"worker_dir": str(finalizer_dir()), "metadata": metadata}


def prepare_request(
    *,
    source: str | Path,
    project_root: str | Path,
    project_id: str | None = None,
    destination: str | Path | None = None,
) -> tuple[Path, dict]:
    """Write one validated, no-GPU PNG alpha-finalizer request inside a project."""
    root = Path(project_root).expanduser().resolve()
    source_path = Path(source).expanduser()
    if not source_path.is_absolute():
        source_path = root / source_path
    source_path = source_path.resolve()
    try:
        relative = source_path.relative_to(root)
    except ValueError as exc:
        raise KaggleWorkerError("PNG source must remain inside the project workspace") from exc
    if source_path.suffix.casefold() not in PNG_SOURCE_SUFFIXES:
        raise KaggleWorkerError("PNG alpha worker accepts only .png or .webp sources; JPEG is rejected")
    if not source_path.is_file():
        raise KaggleWorkerError(f"PNG source does not exist: {source_path}")
    try:
        with Image.open(source_path) as opened:
            opened.load()
            width, height = opened.size
            image_format = opened.format or "unknown"
            color_mode = opened.mode
    except (OSError, ValueError) as exc:
        raise KaggleWorkerError(f"PNG source cannot be decoded: {exc}") from exc
    if (width, height) != PNG_SOURCE_SIZE:
        raise KaggleWorkerError(
            f"Current PNG worker requires a square 1024x1024 source; received {width}x{height}"
        )
    checksum = sha256_file(source_path)
    request_id = f"png-{checksum[:12]}-{uuid4().hex[:8]}"
    expected_width, expected_height = PNG_TARGET_SIZE
    payload = {
        "schema_version": 1,
        "kind": "stockforge.png_finalizer_request",
        "request_id": request_id,
        "status": "prepared_no_gpu",
        "project_id": project_id,
        "source": {
            "relative_path": relative.as_posix(),
            "sha256": checksum,
            "width": width,
            "height": height,
            "format": image_format,
            "color_mode": color_mode,
        },
        "target": {
            "mode": "alpha_finalize",
            "scale": PNG_SCALE,
            "expected_width": expected_width,
            "expected_height": expected_height,
            "expected_megapixels": round((expected_width * expected_height) / 1_000_000, 4),
            "format": "png",
            "color_mode": "RGBA",
            "color_space": "sRGB",
            "requires_true_alpha": True,
        },
        "destination": f"png-masters/{request_id}-master.png",
        "human_review_required": True,
        "review_gate": {
            "technical": ["PNG", "RGBA", "true_alpha", "sRGB", "4_to_100_MP", "under_45_MB"],
            "visual": ["100_percent_edge_review", "no_halo", "no_missing_details", "no_false_holes", "no_unwanted_shadow"],
            "marketplace_submission": "manual_only",
        },
        "provider_options": ["kaggle-birefnet-alpha"],
        "notice": "No GPU was called while preparing this request. Output remains visual_review_required until technical and human edge gates pass.",
    }
    request_path = Path(destination).expanduser().resolve() if destination else root / PNG_REQUEST_DIR_NAME / f"{request_id}.json"
    try:
        request_path.relative_to(root)
    except ValueError as exc:
        raise KaggleWorkerError("PNG request destination must remain inside the project workspace") from exc
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return request_path, payload


def doctor() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("kaggle_cli", bool(shutil.which("kaggle")), shutil.which("kaggle") or "not found on PATH"))
    token = Path.home() / ".kaggle/access_token"
    checks.append(("kaggle_auth", token.is_file() and token.stat().st_size > 0, str(token)))
    try:
        info = validate_local()
        checks.append(("png_finalizer_bundle", True, info["metadata"]["id"]))
    except KaggleWorkerError as exc:
        checks.append(("png_finalizer_bundle", False, str(exc)))
    return checks


def _request_and_source(request_path: Path, project_root: Path) -> tuple[dict, Path]:
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KaggleWorkerError(f"PNG request is not valid JSON: {exc}") from exc
    if request.get("kind") != "stockforge.png_finalizer_request" or request.get("status") != "prepared_no_gpu":
        raise KaggleWorkerError("PNG request must be stockforge.png_finalizer_request/prepared_no_gpu")
    source = request.get("source")
    target = request.get("target")
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise KaggleWorkerError("PNG request lacks source/target objects")
    relative = source.get("relative_path")
    checksum = source.get("sha256")
    if not isinstance(relative, str) or not isinstance(checksum, str):
        raise KaggleWorkerError("PNG source path/checksum is invalid")
    source_path = (project_root / relative).resolve()
    try:
        source_path.relative_to(project_root)
    except ValueError as exc:
        raise KaggleWorkerError("PNG source escapes project root") from exc
    if not source_path.is_file() or sha256_file(source_path) != checksum:
        raise KaggleWorkerError("PNG source is missing or checksum no longer matches request")
    if source_path.suffix.casefold() not in PNG_SOURCE_SUFFIXES:
        raise KaggleWorkerError("PNG request source must use .png or .webp; JPEG sources are rejected")
    try:
        with Image.open(source_path) as opened:
            opened.load()
            if opened.size != PNG_SOURCE_SIZE:
                raise KaggleWorkerError(
                    f"PNG request source must be 1024x1024; received {opened.size[0]}x{opened.size[1]}"
                )
    except KaggleWorkerError:
        raise
    except (OSError, ValueError) as exc:
        raise KaggleWorkerError(f"PNG request source cannot be decoded: {exc}") from exc
    if target.get("mode") != "alpha_finalize" or target.get("format") != "png" or int(target.get("scale", 0)) != PNG_SCALE:
        raise KaggleWorkerError("PNG finalizer supports only 4x alpha_finalize targets")
    if target.get("expected_width") != PNG_TARGET_SIZE[0] or target.get("expected_height") != PNG_TARGET_SIZE[1]:
        raise KaggleWorkerError("PNG request target must be 4096x4096")
    if target.get("color_mode") != "RGBA" or target.get("color_space") != "sRGB" or target.get("requires_true_alpha") is not True:
        raise KaggleWorkerError("PNG request must require RGBA true alpha in sRGB")
    return request, source_path


def submit(*, request: str | Path, project_root: str | Path, accelerator: str = DEFAULT_ACCELERATOR) -> int:
    """Stage one PNG source/request and push the isolated private kernel."""
    validate_local()
    root = Path(project_root).expanduser().resolve()
    request_path = Path(request).expanduser().resolve()
    try:
        request_path.relative_to(root)
    except ValueError as exc:
        raise KaggleWorkerError("PNG request must be inside the project workspace") from exc
    _, source_path = _request_and_source(request_path, root)
    with tempfile.TemporaryDirectory(prefix="stockforge-kaggle-png-finalizer-") as temporary:
        staged = Path(temporary) / "worker"
        shutil.copytree(finalizer_dir(), staged)
        worker_path = staged / str(load_metadata()["code_file"])
        request_b64 = base64.b64encode(request_path.read_bytes()).decode("ascii")
        source_b64 = base64.b64encode(source_path.read_bytes()).decode("ascii")
        worker_text = worker_path.read_text(encoding="utf-8")
        entrypoint = "\n\nif __name__ == \"__main__\":\n"
        if entrypoint not in worker_text:
            raise KaggleWorkerError("PNG worker has no recognized __main__ entrypoint")
        payload = (
            "\n# StockForge transient staged input; do not commit.\n"
            f"REQUEST_B64 = {request_b64!r}\n"
            f"SOURCE_NAME = {source_path.name!r}\n"
            f"SOURCE_B64 = {source_b64!r}\n"
        )
        worker_path.write_text(worker_text.replace(entrypoint, payload + entrypoint, 1), encoding="utf-8")
        result = _run(["kaggle", "kernels", "push", "-p", str(staged), "--accelerator", accelerator])
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode


def remote(action: str, kernel: str | None = None, output_dir: str | Path | None = None, *, force: bool = False) -> int:
    metadata = load_metadata()
    target = kernel or str(metadata.get("id") or PNG_FINALIZER_KERNEL_DEFAULT)
    if action not in {"status", "output"}:
        raise KaggleWorkerError("PNG finalizer action must be status or output")
    command: list[str] = ["kaggle", "kernels", action, target]
    if action == "output" and output_dir is not None:
        destination = Path(output_dir).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        command.extend(["-p", str(destination)])
    if force:
        if action != "output":
            raise KaggleWorkerError("Force download is supported only for PNG output")
        command.append("--force")
    result = _run(command)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.returncode != 0:
        print("STOCKFORGE: Kaggle PNG finalizer command failed; inspect status/logs before retrying.")
    return result.returncode
