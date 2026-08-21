"""Headless Kaggle worker controller for StockForge.

This module deliberately shells out to the official ``kaggle`` CLI instead of
importing Kaggle internals.  That keeps StockForge compatible with the CLI
installed in Termux and makes failures visible exactly as Kaggle reports them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence


class KaggleWorkerError(RuntimeError):
    """Raised when the local Kaggle worker configuration is invalid."""


KAGGLE_USER = os.environ.get("STOCKFORGE_KAGGLE_USER", "ibank31")
DEFAULT_ACCELERATOR = "NvidiaTeslaT4"


def repo_root() -> Path:
    """Return the StockForge repository root when installed from this repo."""
    return Path(__file__).resolve().parents[2]


def worker_dir() -> Path:
    """Return the Kaggle worker directory, overridable for custom layouts."""
    configured = os.environ.get("STOCKFORGE_KAGGLE_DIR")
    return Path(configured).expanduser().resolve() if configured else repo_root() / "infrastructure/providers/kaggle"


def metadata_path() -> Path:
    return worker_dir() / "kernel-metadata.json"


def notebook_path() -> Path:
    return worker_dir() / "worker.ipynb"


def _run(args: Sequence[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    """Run a command and return captured text output."""
    try:
        result = subprocess.run(
            list(args),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError as exc:
        raise KaggleWorkerError(
            f"Command not found: {args[0]}. Install/authenticate the Kaggle CLI first."
        ) from exc
    if check and result.returncode != 0:
        raise KaggleWorkerError(result.stdout.strip() or f"Command failed: {' '.join(args)}")
    return result


def load_metadata() -> dict:
    path = metadata_path()
    if not path.is_file():
        raise KaggleWorkerError(f"Metadata not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KaggleWorkerError(f"Invalid metadata JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise KaggleWorkerError("Kaggle metadata must be a JSON object")
    return data


def validate_local() -> dict:
    """Validate worker files without contacting Kaggle or submitting a job."""
    metadata = load_metadata()
    required = {
        "id": str,
        "title": str,
        "code_file": str,
        "language": str,
        "kernel_type": str,
    }
    for key, expected in required.items():
        if not isinstance(metadata.get(key), expected) or not metadata[key]:
            raise KaggleWorkerError(f"Missing/invalid metadata field: {key}")

    code_path = worker_dir() / metadata["code_file"]
    if not code_path.is_file():
        raise KaggleWorkerError(f"Code file not found: {code_path}")

    if metadata["kernel_type"] == "notebook":
        try:
            notebook = json.loads(code_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise KaggleWorkerError(f"Invalid notebook JSON: {code_path}: {exc}") from exc
        if notebook.get("nbformat") != 4 or not notebook.get("cells"):
            raise KaggleWorkerError("Notebook must be nbformat 4 and contain at least one cell")

    return {
        "worker_dir": str(worker_dir()),
        "metadata": metadata,
        "code_file": str(code_path),
    }


def doctor() -> list[tuple[str, bool, str]]:
    """Run local checks only. No push and no GPU job submission."""
    checks: list[tuple[str, bool, str]] = []
    kaggle = shutil.which("kaggle")
    checks.append(("kaggle_cli", bool(kaggle), kaggle or "not found on PATH"))

    token = Path.home() / ".kaggle/access_token"
    checks.append(("kaggle_auth", token.is_file() and token.stat().st_size > 0, str(token)))

    try:
        info = validate_local()
        checks.append(("worker_metadata", True, info["metadata"]["id"]))
        checks.append(("worker_notebook", True, info["code_file"]))
    except KaggleWorkerError as exc:
        checks.append(("worker_files", False, str(exc)))

    return checks


def push(*, accelerator: str = DEFAULT_ACCELERATOR, public: bool | None = None) -> int:
    """Push and run the configured Kaggle worker."""
    validate_local()
    metadata = load_metadata()

    if public is not None and bool(metadata.get("is_private", True)) == public:
        # No rewrite is necessary when the requested privacy already matches.
        pass
    elif public is not None:
        # The CLI's push operation reads the metadata file.  Keep this explicit
        # and reversible instead of silently changing the repository configuration.
        metadata["is_private"] = not public
        metadata_path().write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    result = _run(
        [
            "kaggle",
            "kernels",
            "push",
            "-p",
            str(worker_dir()),
            "--accelerator",
            accelerator,
        ]
    )
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode


def quota() -> int:
    result = _run(["kaggle", "quota"])
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode


def list_kernels(search: str = "stockforge-worker") -> int:
    result = _run(
        [
            "kaggle",
            "kernels",
            "list",
            "--user",
            KAGGLE_USER,
            "--search",
            search,
            "--page-size",
            "50",
            "--sort-by",
            "dateRun",
        ]
    )
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return result.returncode


def remote(action: str, kernel: str | None = None) -> int:
    """Call a read/output action against a kernel without opening a browser."""
    metadata = load_metadata()
    target = kernel or str(metadata.get("id", ""))
    if not target:
        raise KaggleWorkerError("No kernel id configured")

    command = ["kaggle", "kernels", action, target]
    result = _run(command)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.returncode != 0:
        print(
            "STOCKFORGE: Kaggle API rejected this remote read operation. "
            "The worker may still exist/run; use 'stockforge kaggle discover' "
            "or 'stockforge kaggle output' after completion."
        )
    return result.returncode
