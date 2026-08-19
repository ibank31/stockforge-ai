"""Durable worker bridge from the job queue to the generation orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .generation import GenerationRequest
from .job import Job
from .job_manager import JobManager
from .orchestrator import GenerationOrchestrator


class JobWorkerError(RuntimeError):
    """Raised when a worker cannot process a job safely."""


@dataclass(frozen=True, slots=True)
class WorkerResult:
    job_id: str
    status: str
    result: dict


class GenerationJobWorker:
    """Claims generation jobs and routes them through the canonical orchestrator."""

    def __init__(
        self,
        job_manager: JobManager,
        orchestrator_factory: Callable[[Job], GenerationOrchestrator],
        *,
        worker_id: str,
    ) -> None:
        if not worker_id or len(worker_id) > 128:
            raise JobWorkerError("worker_id must be between 1 and 128 characters")
        self.job_manager = job_manager
        self.orchestrator_factory = orchestrator_factory
        self.worker_id = worker_id

    def run_once(self) -> WorkerResult | None:
        """Claim and process at most one queued generation job."""
        job = self.job_manager.claim_next(self.worker_id)
        if job is None:
            return None
        try:
            request = GenerationRequest(**job.payload)
            orchestrator = self.orchestrator_factory(job)
            outcome = orchestrator.run(request)
            result = {
                "execution_id": outcome.execution.id,
                "artifact_ids": list(outcome.execution.artifact_ids),
            }
            completed = self.job_manager.complete(job.id, result)
            return WorkerResult(completed.id, completed.status, result)
        except Exception as exc:
            error = str(exc) or exc.__class__.__name__
            failed = self.job_manager.fail(job.id, error)
            failure_result = {"error": error, "retry": failed.status == "queued"}
            return WorkerResult(failed.id, failed.status, failure_result)
