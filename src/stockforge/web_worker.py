"""Run durable V2 generation jobs for the browser API.

Production defaults to the public StockForge Hugging Face ZeroGPU worker.
A local/managed ComfyUI provider remains an explicit opt-in compatibility
path, but the browser workflow no longer requires a local ComfyUI endpoint.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from .comfyui import ComfyUIProvider
from .job_database import JobDatabase
from .job_manager import JobManager
from .job_worker import GenerationJobWorker
from .provider import ProviderConfig
from .recovery_orchestrator import RecoveryGenerationOrchestrator
from .remote_gradio import RemoteGradioProvider

PROJECT_ID = "00000000-0000-0000-0000-000000000001"
UPLOAD_ROOT = Path(os.getenv("STOCKFORGE_WEB_UPLOAD_ROOT", "runtime/web-references"))
DATABASE_PATH = Path(os.getenv("STOCKFORGE_WEB_DATABASE", "runtime/web-jobs.sqlite"))
PROJECT_ROOT = UPLOAD_ROOT.parent
PROVIDER_ROOT = Path(os.getenv("STOCKFORGE_PROVIDER_ROOT", "runtime/provider"))
DEFAULT_ZEROGPU_SPACE = "ibank31/stockforge-zerogpu"
DEFAULT_ZEROGPU_URL = "https://ibank31-stockforge-zerogpu.hf.space"


def _build_provider():
    """Build the real production provider without requiring local GPU state.

    ZeroGPU is the default because it is the intended free remote compute
    boundary. A bearer token is optional: when present it uses the account's
    authenticated ZeroGPU quota; when absent the public Space remains callable
    under Hugging Face's unauthenticated/shared quota rules.
    """
    PROVIDER_ROOT.mkdir(parents=True, exist_ok=True)

    provider_mode = os.getenv("STOCKFORGE_PROVIDER_MODE", "zerogpu").strip().lower()
    if provider_mode == "zerogpu":
        space = os.getenv("STOCKFORGE_ZEROGPU_SPACE", DEFAULT_ZEROGPU_SPACE).strip()
        base_url = os.getenv("STOCKFORGE_ZEROGPU_URL", DEFAULT_ZEROGPU_URL).strip().rstrip("/")
        token = os.getenv("STOCKFORGE_HF_TOKEN", "").strip() or None
        if not base_url:
            raise RuntimeError("STOCKFORGE_ZEROGPU_URL must not be empty")
        return RemoteGradioProvider(
            provider_id="hf.zerogpu",
            base_url=base_url,
            output_dir=PROVIDER_ROOT,
            token=token,
            api_name=os.getenv("STOCKFORGE_ZEROGPU_API", "generate_remote"),
            timeout_seconds=float(os.getenv("STOCKFORGE_PROVIDER_TIMEOUT", "300")),
        )

    if provider_mode == "comfyui":
        endpoint = os.getenv("STOCKFORGE_COMFYUI_URL", "").strip()
        if not endpoint:
            raise RuntimeError("STOCKFORGE_COMFYUI_URL is required when STOCKFORGE_PROVIDER_MODE=comfyui")
        config = ProviderConfig(
            id=os.getenv("STOCKFORGE_PROVIDER_ID", "comfyui.browser"),
            kind="comfyui",
            endpoint=endpoint,
            enabled=True,
            options={
                "timeout_seconds": float(os.getenv("STOCKFORGE_PROVIDER_TIMEOUT", "120")),
                "poll_interval_seconds": float(os.getenv("STOCKFORGE_PROVIDER_POLL_INTERVAL", "1")),
            },
        )
        return ComfyUIProvider(config)

    raise RuntimeError(
        f"Unsupported STOCKFORGE_PROVIDER_MODE={provider_mode!r}; "
        "allowed values are 'zerogpu' and 'comfyui'."
    )


def build_worker() -> GenerationJobWorker:
    provider = _build_provider()
    database = JobDatabase(DATABASE_PATH)
    database.initialize()
    manager = JobManager(database)

    def factory(job):
        return RecoveryGenerationOrchestrator(
            database,
            project_id=job.project_id,
            project_root=PROJECT_ROOT,
            provider_root=PROVIDER_ROOT,
            provider=provider,
        )

    return GenerationJobWorker(
        manager,
        factory,
        worker_id=os.getenv("STOCKFORGE_WORKER_ID", "stockforge-web-worker"),
    )


def run_once() -> object | None:
    return build_worker().run_once()


def main() -> None:
    interval = max(0.2, float(os.getenv("STOCKFORGE_WORKER_INTERVAL", "2")))
    while True:
        result = run_once()
        if result is None:
            time.sleep(interval)


if __name__ == "__main__":
    main()
