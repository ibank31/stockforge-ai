"""Durable worker bridge from the job queue to the recovery-aware orchestrator."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .generation import GenerationRequest
from .job import Job
from .job_manager import JobManager
from .recovery_orchestrator import RecoveryGenerationOrchestrator

class JobWorkerError(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class WorkerResult:
    job_id: str
    status: str
    result: dict

class GenerationJobWorker:
    def __init__(self, job_manager: JobManager, orchestrator_factory: Callable[[Job], RecoveryGenerationOrchestrator], *, worker_id: str):
        if not worker_id or len(worker_id) > 128:
            raise JobWorkerError("worker_id must be between 1 and 128 characters")
        self.job_manager = job_manager
        self.orchestrator_factory = orchestrator_factory
        self.worker_id = worker_id

    def run_once(self) -> WorkerResult | None:
        job = self.job_manager.claim_next(self.worker_id)
        if job is None:
            return None
        try:
            request = GenerationRequest(**job.payload)
            orchestrator = self.orchestrator_factory(job)
            outcome = orchestrator.run(request, job_id=job.id)
            result = {"execution_id": outcome.execution.id, "artifact_ids": list(outcome.execution.artifact_ids)}
            completed = self.job_manager.complete(job.id, result)
            return WorkerResult(completed.id, completed.status, result)
        except Exception as exc:
            error = str(exc) or exc.__class__.__name__
            failed = self.job_manager.fail(job.id, error)
            return WorkerResult(failed.id, failed.status, {"error": error, "retry": failed.status == "queued"})
