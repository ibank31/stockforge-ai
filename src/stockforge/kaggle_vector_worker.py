"""Isolated Kaggle controller for the free StarVector SVG worker.

This module is deliberately separate from the existing Kaggle image worker. It submits only the StarVector vector bundle and never reads, rewrites, stages, or imports JPEG inputs.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


class KaggleVectorWorkerError(RuntimeError):
    """Raised when the isolated StarVector worker is invalid."""


KAGGLE_USER = os.environ.get("STOCKFORGE_KAGGLE_USER", "iqbalteguh")
DEFAULT_KERNEL = f"{KAGGLE_USER}/stockforge-starvector-vector"
DEFAULT_ACCELERATOR = "NvidiaTeslaT4"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def worker_dir() -> Path:
    configured = os.environ.get("STOCKFORGE_KAGGLE_VECTOR_DIR")
    return Path(configured).expanduser().resolve() if configured else repo_root() / "deploy" / "kaggle-vector-starvector"


def metadata_path() -> Path:
    return worker_dir() / "kernel-metadata.json"


def load_metadata() -> dict:
    path = metadata_path()
    if not path.is_file():
        raise KaggleVectorWorkerError(f"StarVector metadata not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KaggleVectorWorkerError(f"Invalid StarVector metadata JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise KaggleVectorWorkerError("StarVector metadata must be a JSON object")
    required = ("id", "title", "code_file", "language", "kernel_type")
    for key in required:
        if not isinstance(data.get(key), str) or not data[key]:
            raise KaggleVectorWorkerError(f"Missing/invalid StarVector metadata field: {key}")
    if data.get("is_private") is not True:
        raise KaggleVectorWorkerError("StarVector worker must remain private")
    if data["id"] == f"{KAGGLE_USER}/stockforge-finalizer":
        raise KaggleVectorWorkerError("StarVector worker cannot reuse the JPEG finalizer kernel")
    return data


def validate_local() -> dict:
    metadata = load_metadata()
    code_path = worker_dir() / metadata["code_file"]
    requirements_path = worker_dir() / "requirements.txt"
    if not code_path.is_file():
        raise KaggleVectorWorkerError(f"StarVector code file not found: {code_path}")
    if not requirements_path.is_file():
        raise KaggleVectorWorkerError(f"StarVector requirements not found: {requirements_path}")
    code = code_path.read_text(encoding="utf-8")
    if "RealESRGAN" in code or "master_finalizer" in code or "jpeg_finalizer" in code:
        raise KaggleVectorWorkerError("StarVector worker contains a forbidden JPEG pipeline reference")
    if ".jpg" in code.lower() or ".jpeg" in code.lower():
        raise KaggleVectorWorkerError("StarVector worker must not write JPEG artifacts")
    return {
        "worker_dir": str(worker_dir()),
        "metadata": metadata,
        "code_file": str(code_path),
        "requirements_file": str(requirements_path),
        "jpeg_isolation": True,
    }


def _run(args: Sequence[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            list(args),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError as exc:
        raise KaggleVectorWorkerError(
            f"Command not found: {args[0]}. Install/authenticate the Kaggle CLI first."
        ) from exc
    if check and result.returncode != 0:
        raise KaggleVectorWorkerError(result.stdout.strip() or f"Command failed: {' '.join(args)}")
    return result


def doctor() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    kaggle = shutil.which("kaggle")
    checks.append(("kaggle_cli", bool(kaggle), kaggle or "not found on PATH"))
    token = Path.home() / ".kaggle/access_token"
    checks.append(("kaggle_auth", token.is_file() and token.stat().st_size > 0, str(token)))
    try:
        info = validate_local()
        checks.append(("starvector_bundle", True, info["metadata"]["id"]))
        checks.append(("jpeg_isolation", True, "no finalizer/JPEG references in vector worker"))
    except KaggleVectorWorkerError as exc:
        checks.append(("starvector_bundle", False, str(exc)))
    return checks


def _cache_mode_enabled(metadata: dict) -> bool:
    sources = metadata.get("dataset_sources", [])
    return isinstance(sources, list) and "iqbalteguh/stockforge-starvector-cache" in sources


def _prompt_from_file(prompt_file: str | Path) -> str:
    path = Path(prompt_file).expanduser().resolve()
    if not path.is_file():
        raise KaggleVectorWorkerError(f"Prompt file not found: {path}")
    prompt = path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise KaggleVectorWorkerError("Vector prompt file is empty")
    if len(prompt) > 12000:
        raise KaggleVectorWorkerError("Vector prompt is too long for the one-shot worker")
    return prompt


def submit(*, prompt_file: str | Path, input_image_file: str | Path, accelerator: str = DEFAULT_ACCELERATOR) -> int:
    """Submit one isolated image-to-SVG job backed by the private Kaggle cache."""
    validate_local()
    prompt = _prompt_from_file(prompt_file)
    input_image = Path(input_image_file).expanduser().resolve()
    if not input_image.is_file():
        raise KaggleVectorWorkerError(f"Input PNG not found: {input_image}")
    if input_image.suffix.lower() != ".png":
        raise KaggleVectorWorkerError("StarVector image-to-SVG input must be a PNG file")
    image_bytes = input_image.read_bytes()
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise KaggleVectorWorkerError("StarVector input image is not a valid PNG")
    if len(image_bytes) > 5 * 1024 * 1024:
        raise KaggleVectorWorkerError("StarVector input PNG is larger than the 5 MB one-shot limit")
    metadata = load_metadata()
    if not _cache_mode_enabled(metadata):
        raise KaggleVectorWorkerError("StarVector submit requires the private Kaggle model cache dataset")
    with tempfile.TemporaryDirectory(prefix="stockforge-kaggle-starvector-") as temporary:
        staged = Path(temporary) / "worker"
        shutil.copytree(worker_dir(), staged)
        worker_path = staged / metadata["code_file"]
        worker_text = worker_path.read_text(encoding="utf-8")
        entrypoint = "\nif __name__ == \"__main__\":\n"
        if entrypoint not in worker_text:
            raise KaggleVectorWorkerError("StarVector worker has no recognized __main__ entrypoint")
        prompt_b64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        payload = (
            "\n# StockForge transient inputs; this staged copy is deleted after submit.\n"
            f"STOCKFORGE_VECTOR_PROMPT_B64 = {prompt_b64!r}\n"
            f"STOCKFORGE_VECTOR_INPUT_IMAGE_B64 = {image_b64!r}\n"
        )
        worker_path.write_text(worker_text.replace(entrypoint, payload + entrypoint, 1), encoding="utf-8")
        result = _run(
            ["kaggle", "kernels", "push", "-p", str(staged), "--accelerator", accelerator]
        )
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode


def remote(
    action: str,
    kernel: str | None = None,
    output_dir: str | Path | None = None,
    *,
    force: bool = False,
) -> int:
    """Read status/logs or download output for the isolated vector kernel."""
    metadata = load_metadata()
    target = kernel or str(metadata.get("id") or DEFAULT_KERNEL)
    if target == f"{KAGGLE_USER}/stockforge-finalizer":
        raise KaggleVectorWorkerError("Vector remote action cannot target the JPEG finalizer")
    if action not in {"status", "output"}:
        raise KaggleVectorWorkerError("Vector action must be status or output")
    command: list[str] = ["kaggle", "kernels", action, target]
    if action == "output" and output_dir is not None:
        destination = Path(output_dir).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        command.extend(["-p", str(destination)])
        if force:
            command.append("--force")
    result = _run(command)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode
