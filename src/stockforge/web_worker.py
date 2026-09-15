"""Run durable V2 generation jobs for the browser API.

This runner deliberately requires an explicitly configured provider. It never
silently falls back to a fake generator or claims a job succeeded without a
real provider output.
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

PROJECT_ID = "00000000-0000-0000-0000-000000000001"
UPLOAD_ROOT = Path(os.getenv("STOCKFORGE_WEB_UPLOAD_ROOT", "runtime/web-references"))
DATABASE_PATH = Path(os.getenv("STOCKFORGE_WEB_DATABASE", "runtime/web-jobs.sqlite"))
PROJECT_ROOT = UPLOAD_ROOT.parent
PROVIDER_ROOT = Path(os.getenv("STOCKFORGE_PROVIDER_ROOT", "runtime/provider"))


def build_worker() -> GenerationJobWorker:
    endpoint = os.getenv("STOCKFORGE_COMFYUI_URL", "").strip()
    if not endpoint:
        raise RuntimeError("STOCKFORGE_COMFYUI_URL is required; no generation provider is configured.")
    PROVIDER_ROOT.mkdir(parents=True, exist_ok=True)
    config = ProviderConfig(
        id=os.getenv("STOCKFORGE_PROVIDER_ID", "comfyui.browser"),
        kind="comfyui",
        endpoint=endpoint,
        enabled=True,
        options={"timeout_seconds": float(os.getenv("STOCKFORGE_PROVIDER_TIMEOUT", "120")), "poll_interval_seconds": float(os.getenv("STOCKFORGE_PROVIDER_POLL_INTERVAL", "1"))},
    )
    provider = ComfyUIProvider(config)
    database = JobDatabase(DATABASE_PATH)
    database.initialize()
    manager = JobManager(database)

    def factory(job):
        return RecoveryGenerationOrchestrator(database, project_id=job.project_id, project_root=PROJECT_ROOT, provider_root=PROVIDER_ROOT, provider=provider)

    return GenerationJobWorker(manager, factory, worker_id=os.getenv("STOCKFORGE_WORKER_ID", "stockforge-web-worker"))


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
