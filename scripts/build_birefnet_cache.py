"""Build a private, offline BiRefNet cache for the isolated PNG worker."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

CACHE = Path("/home/ubuntu/stockforge-ai/cache/stockforge-birefnet-cache")
MODEL_DIR = CACHE / "model"
WHEEL_DIR = CACHE / "wheelhouse"
REQUIREMENTS = Path("/home/ubuntu/stockforge-ai/deploy/kaggle-png-finalizer/requirements.txt")


def digest(path: Path) -> dict[str, object]:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return {"path": str(path.relative_to(CACHE)), "bytes": path.stat().st_size, "sha256": value.hexdigest()}


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    from huggingface_hub import snapshot_download

    snapshot_download(
        repo_id="ZhengPeng7/BiRefNet",
        revision="e2bf8e4460fc8fa32bba5ea4d94b3233d367b0e4",
        local_dir=str(MODEL_DIR),
        local_dir_use_symlinks=False,
        allow_patterns=["config.json", "model.safetensors", "*.py", "README.md", "requirements.txt", "LICENSE*", ".gitattributes"],
    )
    WHEEL_DIR.mkdir(parents=True, exist_ok=True)
    requirements = [line.strip() for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    for requirement in requirements:
        command = [
            sys.executable, "-m", "pip", "download", "--only-binary=:all:", "--no-deps",
            "--platform", "manylinux_2_17_x86_64", "--python-version", "3.12",
            "--implementation", "cp", "--abi", "cp312", "--dest", str(WHEEL_DIR), requirement,
        ]
        subprocess.check_call(command)
    files = [digest(path) for path in sorted(CACHE.rglob("*")) if path.is_file() and path.name != "manifest.json"]
    manifest = {
        "schema_version": 1,
        "model": "ZhengPeng7/BiRefNet",
        "revision": "e2bf8e4460fc8fa32bba5ea4d94b3233d367b0e4",
        "license_declared_by_model_card": "mit",
        "inference_mode": "offline_only",
        "hf_token_used": False,
        "files": files,
        "file_count": len(files),
        "total_bytes": sum(int(item["bytes"]) for item in files),
    }
    (CACHE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
