from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT = Path(os.getenv("STOCKFORGE_BRIDGE_ROOT", "/app/runtime/kaggle-jobs"))
ROOT.mkdir(parents=True, exist_ok=True)
KERNEL_ID = os.getenv("STOCKFORGE_KAGGLE_KERNEL", "iqbalteguh/stockforge-finalizer")
REPO_RAW = os.getenv("STOCKFORGE_REPO_RAW", "https://raw.githubusercontent.com/ibank31/stockforge-ai/main/deploy/kaggle-finalizer")
ACCELERATOR = os.getenv("STOCKFORGE_KAGGLE_ACCELERATOR", "NvidiaTeslaT4")
POLL_SECONDS = max(5, int(os.getenv("STOCKFORGE_KAGGLE_POLL_SECONDS", "10")))

app = FastAPI(title="StockForge Kaggle Upscale Bridge", version="1.0")
_lock = threading.Lock()

class SubmitRequest(BaseModel):
    source_url: str
    job_id: str
    scale: int = Field(default=4, ge=4, le=4)


def _run(args: list[str], cwd: Path | None = None, timeout: int = 120) -> str:
    env = os.environ.copy()
    if not env.get("KAGGLE_API_TOKEN") and not (env.get("KAGGLE_USERNAME") and env.get("KAGGLE_KEY")):
        raise RuntimeError("KAGGLE_API_TOKEN or KAGGLE_USERNAME/KAGGLE_KEY is required")
    result = subprocess.run(args, cwd=str(cwd) if cwd else None, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(result.stdout[-4000:] or f"command failed: {' '.join(args)}")
    return result.stdout


def _save(job_dir: Path, data: dict) -> None:
    (job_dir / "state.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load(job_id: str) -> dict:
    path = ROOT / job_id / "state.json"
    if not path.is_file():
        raise HTTPException(404, "Kaggle bridge job not found")
    return json.loads(path.read_text(encoding="utf-8"))


def _status_text() -> str:
    return _run(["kaggle", "kernels", "status", KERNEL_ID])


def _kernel_status(text: str) -> str:
    for line in text.splitlines():
        if line.strip().lower().startswith("status:"):
            return line.split(":", 1)[1].strip().lower().replace(" ", "_")
    return "unknown"


def _download_worker(job_dir: Path, source_url: str, job_id: str) -> None:
    try:
        request = urllib.request.Request(source_url, headers={"user-agent": "StockForge-Kaggle-Bridge/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            source = response.read()
        if len(source) < 1024:
            raise RuntimeError("Source asset download was unexpectedly small")
        source_path = job_dir / "source.jpg"
        source_path.write_bytes(source)

        request_payload = {
            "schema_version": 1,
            "kind": "stockforge.master_finalizer_request",
            "request_id": job_id,
            "status": "prepared_no_gpu",
            "source": {
                "relative_path": "source.jpg",
                "sha256": __import__("hashlib").sha256(source).hexdigest(),
            },
            "target": {"mode": "ai_upscale", "scale": 4, "format": "jpeg", "color_space": "sRGB"},
            "destination": f"masters/{job_id}-master.jpg",
        }
        from PIL import Image
        with Image.open(source_path) as im:
            im.load()
            request_payload["source"].update({"width": im.width, "height": im.height, "format": im.format or "unknown", "color_mode": im.mode})
            request_payload["target"].update({
                "expected_width": im.width * 4,
                "expected_height": im.height * 4,
                "minimum_megapixels": max(6.0, (im.width * 4 * im.height * 4) / 1_000_000),
            })
        request_path = job_dir / "request.json"
        request_path.write_text(json.dumps(request_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        worker_dir = Path(tempfile.mkdtemp(prefix="stockforge-kaggle-worker-"))
        try:
            for name in ("worker.py", "requirements.txt", "kernel-metadata.json"):
                urllib.request.urlretrieve(f"{REPO_RAW.rstrip('/')}/{name}", worker_dir / name)
            worker_path = worker_dir / "worker.py"
            worker_text = worker_path.read_text(encoding="utf-8")
            entry = '\nif __name__ == "__main__":\n'
            if entry not in worker_text:
                raise RuntimeError("Kaggle finalizer worker entrypoint not found")
            payload = (
                "\nREQUEST_B64 = " + repr(base64.b64encode(request_path.read_bytes()).decode("ascii")) +
                "\nSOURCE_NAME = 'source.jpg'\nSOURCE_B64 = " + repr(base64.b64encode(source).decode("ascii")) + "\n"
            )
            worker_path.write_text(worker_text.replace(entry, payload + entry, 1), encoding="utf-8")
            output = _run(["kaggle", "kernels", "push", "-p", str(worker_dir), "--accelerator", ACCELERATOR], timeout=180)
        finally:
            shutil.rmtree(worker_dir, ignore_errors=True)

        _save(job_dir, {"job_id": job_id, "state": "submitted", "kernel_id": KERNEL_ID, "push_output": output[-2000:], "updated_at": time.time()})
    except Exception as exc:
        _save(job_dir, {"job_id": job_id, "state": "failed", "error": str(exc), "updated_at": time.time()})


@app.get("/health")
def health() -> dict:
    configured = bool(os.getenv("KAGGLE_API_TOKEN") or (os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")))
    return {"status": "ok", "service": "stockforge-kaggle-upscale-bridge", "kaggle_configured": configured, "kernel": KERNEL_ID}


@app.post("/upscale/submit")
def submit(request: SubmitRequest) -> dict:
    if not request.source_url.startswith(("https://", "http://")):
        raise HTTPException(400, "source_url must be HTTP(S)")
    if not request.job_id or len(request.job_id) > 128:
        raise HTTPException(400, "job_id is required")
    job_id = "kb-" + uuid.uuid4().hex
    job_dir = ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    _save(job_dir, {"job_id": job_id, "state": "queued", "stockforge_job_id": request.job_id, "updated_at": time.time()})
    thread = threading.Thread(target=_download_worker, args=(job_dir, request.source_url, request.job_id), daemon=True)
    thread.start()
    return {"provider_job_id": job_id, "state": "submitted"}


@app.get("/upscale/status/{provider_job_id}")
def status(provider_job_id: str) -> dict:
    data = _load(provider_job_id)
    if data.get("state") in {"completed", "failed"}:
        return data
    try:
        status_text = _status_text()
        state = _kernel_status(status_text)
        if state in {"complete", "completed"}:
            job_dir = ROOT / provider_job_id
            result_dir = job_dir / "result"
            result_dir.mkdir(exist_ok=True)
            _run(["kaggle", "kernels", "output", KERNEL_ID, "-p", str(result_dir), "--force"], timeout=180)
            result_file = next(result_dir.rglob("result.json"), None)
            master_file = next(result_dir.rglob("master.jpg"), None)
            if not result_file or not master_file:
                raise RuntimeError("Kaggle completed but result.json/master.jpg was not returned")
            result = json.loads(result_file.read_text(encoding="utf-8"))
            data = {**data, "state": "completed", "result": result, "artifact_path": str(master_file), "updated_at": time.time()}
            _save(job_dir, data)
        elif state in {"error", "failed", "cancelled"}:
            data = {**data, "state": "failed", "error": status_text[-4000:], "updated_at": time.time()}
            _save(job_dir, data)
        else:
            data = {**data, "state": "running", "kaggle_status": state, "updated_at": time.time()}
            _save(job_dir, data)
    except Exception as exc:
        data = {**data, "state": "failed", "error": str(exc), "updated_at": time.time()}
        _save(ROOT / provider_job_id, data)
    return {k: v for k, v in data.items() if k != "artifact_path"}


@app.get("/upscale/artifact/{provider_job_id}")
def artifact(provider_job_id: str):
    data = _load(provider_job_id)
    if data.get("state") != "completed":
        raise HTTPException(409, "Kaggle job is not complete")
    path = Path(data.get("artifact_path", ""))
    if not path.is_file():
        raise HTTPException(404, "Final master is missing")
    return FileResponse(path, media_type="image/jpeg", filename="master.jpg")
