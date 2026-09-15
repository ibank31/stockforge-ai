"""StockForge CPU control plane for a Hugging Face Space.

This service hosts the browser API and runs the durable job worker in the same
CPU process. The worker delegates image generation to the configured remote
ZeroGPU Space, so the control plane itself never needs a local GPU.
"""
from __future__ import annotations

import os
import threading
import time

# Keep all mutable runtime state inside the container filesystem. The API
# contract remains identical to the repository's StockForge V2 web app.
os.environ.setdefault("STOCKFORGE_WEB_UPLOAD_ROOT", "/app/runtime/web-references")
os.environ.setdefault("STOCKFORGE_WEB_DATABASE", "/app/runtime/web-jobs.sqlite")
os.environ.setdefault("STOCKFORGE_PROVIDER_ROOT", "/app/runtime/provider")
os.environ.setdefault("STOCKFORGE_PROVIDER_MODE", "zerogpu")
os.environ.setdefault("STOCKFORGE_ZEROGPU_SPACE", "ibank31/stockforge-zerogpu")
os.environ.setdefault("STOCKFORGE_ZEROGPU_URL", "https://ibank31-stockforge-zerogpu.hf.space")
os.environ.setdefault("STOCKFORGE_WORKER_INTERVAL", "2")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stockforge.web_app import app as control_plane_app
from stockforge.web_worker import build_worker


app = FastAPI(title="StockForge V2 Control Plane", version="2.0")

_allowed = [
    origin.strip()
    for origin in os.getenv(
        "STOCKFORGE_ALLOWED_ORIGINS",
        "https://stockforge-ai.pages.dev",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed or ["https://stockforge-ai.pages.dev"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_state = {
    "worker": None,
    "thread": None,
    "stop": threading.Event(),
    "last_error": None,
    "started_at": None,
}


def _worker_loop() -> None:
    interval = max(0.2, float(os.getenv("STOCKFORGE_WORKER_INTERVAL", "2")))
    try:
        worker = build_worker()
        _state["worker"] = worker
        while not _state["stop"].is_set():
            try:
                worker.run_once()
                _state["last_error"] = None
            except Exception as exc:  # keep the API alive while a single job fails
                _state["last_error"] = f"{type(exc).__name__}: {exc}"
            _state["stop"].wait(interval)
    except Exception as exc:
        _state["last_error"] = f"worker_startup: {type(exc).__name__}: {exc}"


@app.on_event("startup")
def start_background_worker() -> None:
    if _state["thread"] is not None and _state["thread"].is_alive():
        return
    _state["stop"].clear()
    _state["started_at"] = time.time()
    thread = threading.Thread(
        target=_worker_loop,
        name="stockforge-web-worker",
        daemon=True,
    )
    _state["thread"] = thread
    thread.start()


@app.on_event("shutdown")
def stop_background_worker() -> None:
    _state["stop"].set()
    thread = _state.get("thread")
    if thread is not None:
        thread.join(timeout=5)
    _state["thread"] = None
    _state["worker"] = None


@app.get("/health")
def health() -> dict[str, object]:
    thread = _state.get("thread")
    return {
        "status": "ok",
        "service": "stockforge-v2-control-plane",
        "worker": "running" if thread is not None and thread.is_alive() else "starting",
        "provider_mode": os.getenv("STOCKFORGE_PROVIDER_MODE", "zerogpu"),
        "zerogpu_space": os.getenv("STOCKFORGE_ZEROGPU_SPACE", "ibank31/stockforge-zerogpu"),
        "last_worker_error": _state.get("last_error"),
    }


# All StockForge browser routes live under the mounted application. The
# wrapper only adds deployment health and worker lifecycle management.
app.mount("/", control_plane_app)
