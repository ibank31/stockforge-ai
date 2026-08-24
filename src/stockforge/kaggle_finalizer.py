"""Termux-side controller for the one-shot private Kaggle master finalizer."""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

from .artifact import sha256_file
from .kaggle_worker import DEFAULT_ACCELERATOR, KAGGLE_USER, KaggleWorkerError, _run, repo_root


FINALIZER_KERNEL_DEFAULT = f"{KAGGLE_USER}/stockforge-finalizer"


def finalizer_dir() -> Path:
    configured = os.environ.get("STOCKFORGE_KAGGLE_FINALIZER_DIR")
    return Path(configured).expanduser().resolve() if configured else repo_root() / "deploy" / "kaggle-finalizer"


def metadata_path() -> Path:
    return finalizer_dir() / "kernel-metadata.json"


def load_metadata() -> dict:
    path = metadata_path()
    if not path.is_file():
        raise KaggleWorkerError(f"Finalizer metadata not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KaggleWorkerError(f"Invalid finalizer metadata JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("id"), str) or not data["id"]:
        raise KaggleWorkerError("Finalizer metadata must contain a non-empty id")
    if data.get("is_private") is not True:
        raise KaggleWorkerError("StockForge finalizer must remain private")
    return data


def validate_local() -> dict:
    metadata = load_metadata()
    required = ("worker.py", "requirements.txt")
    missing = [name for name in required if not (finalizer_dir() / name).is_file()]
    if missing:
        raise KaggleWorkerError("Finalizer worker is incomplete: " + ", ".join(missing))
    return {"worker_dir": str(finalizer_dir()), "metadata": metadata}


def doctor() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("kaggle_cli", bool(shutil.which("kaggle")), shutil.which("kaggle") or "not found on PATH"))
    token = Path.home() / ".kaggle/access_token"
    checks.append(("kaggle_auth", token.is_file() and token.stat().st_size > 0, str(token)))
    try:
        info = validate_local()
        checks.append(("finalizer_bundle", True, info["metadata"]["id"]))
    except KaggleWorkerError as exc:
        checks.append(("finalizer_bundle", False, str(exc)))
    return checks


def _request_and_source(request_path: Path, project_root: Path) -> tuple[dict, Path]:
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KaggleWorkerError(f"Finalizer request is not valid JSON: {exc}") from exc
    if request.get("kind") != "stockforge.master_finalizer_request":
        raise KaggleWorkerError("Unexpected finalizer request kind")
    if request.get("status") != "prepared_no_gpu":
        raise KaggleWorkerError("Finalizer request must be prepared_no_gpu")
    source = request.get("source")
    target = request.get("target")
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise KaggleWorkerError("Finalizer request lacks source/target")
    relative = source.get("relative_path")
    checksum = source.get("sha256")
    if not isinstance(relative, str) or not isinstance(checksum, str):
        raise KaggleWorkerError("Finalizer source path/checksum is invalid")
    source_path = (project_root / relative).resolve()
    try:
        source_path.relative_to(project_root)
    except ValueError as exc:
        raise KaggleWorkerError("Finalizer source escapes project root") from exc
    if not source_path.is_file():
        raise KaggleWorkerError(f"Finalizer source is missing: {source_path}")
    if sha256_file(source_path) != checksum:
        raise KaggleWorkerError("Finalizer source checksum no longer matches its request")
    if target.get("mode") != "ai_upscale" or target.get("scale") != 4:
        raise KaggleWorkerError("Kaggle finalizer currently supports only 4x ai_upscale")
    return request, source_path


def submit(*, request: str | Path, project_root: str | Path, accelerator: str = DEFAULT_ACCELERATOR) -> int:
    """Stage one source/request into a temporary private Kaggle kernel and run it."""
    validate_local()
    root = Path(project_root).expanduser().resolve()
    request_path = Path(request).expanduser().resolve()
    try:
        request_path.relative_to(root)
    except ValueError as exc:
        raise KaggleWorkerError("Finalizer request must be inside the project workspace") from exc
    _, source_path = _request_and_source(request_path, root)

    with tempfile.TemporaryDirectory(prefix="stockforge-kaggle-finalizer-") as temporary:
        staged = Path(temporary) / "worker"
        shutil.copytree(finalizer_dir(), staged)
        # Kaggle pushes only the declared code file reliably. Embed the one
        # selected request/preview directly in its transient copy of worker.py;
        # this file is deleted with the staging directory and is never committed.
        worker_path = staged / str(load_metadata()["code_file"])
        request_b64 = base64.b64encode(request_path.read_bytes()).decode("ascii")
        source_b64 = base64.b64encode(source_path.read_bytes()).decode("ascii")
        with worker_path.open("a", encoding="utf-8") as handle:
            handle.write("\n# StockForge transient staged input; do not commit.\n")
            handle.write(f"REQUEST_B64 = {request_b64!r}\n")
            handle.write(f"SOURCE_NAME = {source_path.name!r}\n")
            handle.write(f"SOURCE_B64 = {source_b64!r}\n")
        result = _run(
            ["kaggle", "kernels", "push", "-p", str(staged), "--accelerator", accelerator]
        )
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode


def remote(action: str, kernel: str | None = None, output_dir: str | Path | None = None) -> int:
    """Read finalizer status/logs or download its latest output through Kaggle CLI."""
    metadata = load_metadata()
    target = kernel or str(metadata.get("id") or FINALIZER_KERNEL_DEFAULT)
    if action not in {"status", "output"}:
        raise KaggleWorkerError("Finalizer action must be status or output")
    command: list[str] = ["kaggle", "kernels", action, target]
    if action == "output" and output_dir is not None:
        destination = Path(output_dir).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        command.extend(["-p", str(destination)])
    result = _run(command)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.returncode != 0:
        print("STOCKFORGE: Kaggle finalizer read/output command failed; inspect the kernel status or logs before retrying.")
    return result.returncode
