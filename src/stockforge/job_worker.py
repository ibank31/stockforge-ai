"""Durable worker bridge from the job queue to the recovery-aware orchestrator."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from .generation import GenerationRequest
from .job import Job
from .job_manager import JobManager
from .recovery_orchestrator import RecoveryGenerationOrchestrator
from .post_generation_verification import verify_generated_candidate
from .workflow_control import HeartbeatLoop, WorkflowControl

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
        control = WorkflowControl(self.job_manager.database); control.initialize()
        workflow_id = dict((job.payload or {}).get("parameters") or {}).get("workflow_id")
        heartbeat = None
        try:
            request = GenerationRequest(**job.payload)
            orchestrator = self.orchestrator_factory(job)
            provider = getattr(orchestrator, "provider", None); descriptor = getattr(provider, "descriptor", None); provider_id = getattr(descriptor, "id", None)
            if workflow_id:
                control.event(workflow_id, stage="GENERATING", message="Generation worker claimed the job.", job_id=job.id, provider_id=provider_id)
                heartbeat = HeartbeatLoop(control, workflow_id, stage="GENERATING", job_id=job.id, provider_id=provider_id); heartbeat.__enter__()
            try:
                outcome = orchestrator.run(request, job_id=job.id)
            finally:
                if heartbeat: heartbeat.__exit__(None, None, None); heartbeat = None
            result = {"execution_id": outcome.execution.id, "artifact_ids": list(outcome.execution.artifact_ids)}
            provider_job_id = getattr(outcome.execution, "provider_job_id", None)
            if workflow_id:
                control.event(workflow_id, stage="INGESTING", message="Provider completed; artifacts were ingested.", job_id=job.id, provider_id=provider_id, provider_job_id=provider_job_id)
                control.event(workflow_id, stage="SIMILARITY_GATE", message="Running post-generation similarity verification.", job_id=job.id, provider_id=provider_id, provider_job_id=provider_job_id)
            verification = self._verify_v2_output(request, outcome, orchestrator)
            if verification is not None: result["post_generation_verification"] = verification
            completed = self.job_manager.complete(job.id, result)
            if workflow_id:
                decision = verification.get("decision") if verification else None
                if decision == "BLOCK": control.event(workflow_id, stage="HUMAN_REVIEW", status="blocked", message="Similarity gate blocked the candidate.", job_id=job.id, provider_id=provider_id, provider_job_id=provider_job_id, details=verification)
                else: control.event(workflow_id, stage="HUMAN_REVIEW", status="human_review", message="Generation completed; human review is required.", job_id=job.id, provider_id=provider_id, provider_job_id=provider_job_id, details=verification or {})
            return WorkerResult(completed.id, completed.status, result)
        except Exception as exc:
            if heartbeat: heartbeat.__exit__(None, None, None)
            error = str(exc) or exc.__class__.__name__
            failed = self.job_manager.fail(job.id, error)
            if workflow_id: control.event(workflow_id, stage="GENERATING", status="failed" if failed.status == "failed" else "active", message=error, job_id=job.id, details={"retry": failed.status == "queued"})
            return WorkerResult(failed.id, failed.status, {"error": error, "retry": failed.status == "queued"})

    @staticmethod
    def _verify_v2_output(request: GenerationRequest, outcome: object, orchestrator: object) -> dict | None:
        """Verify every generated candidate when the V2 request carries a reference.

        Legacy jobs do not contain ``reference_path`` and retain their existing
        behavior. V2 jobs fail closed when the durable reference or artifact path
        is missing, rather than silently skipping the similarity gate.
        """
        reference_value = request.parameters.get("reference_path")
        if not reference_value:
            return None
        reference = Path(str(reference_value)).resolve()
        project_root = Path(getattr(orchestrator, "project_root", ".")).resolve()
        artifacts = getattr(outcome, "artifacts", ())
        if not reference.is_file() or not artifacts:
            raise RuntimeError("V2 similarity verification requires a reference and generated artifact.")
        checks = []
        for artifact in artifacts:
            candidate = (project_root / artifact.relative_path).resolve()
            try:
                candidate.relative_to(project_root)
            except ValueError as exc:
                raise RuntimeError("Generated artifact escaped the project root.") from exc
            checks.append(verify_generated_candidate(reference, candidate).to_dict())
        decision = "BLOCK" if any(item["decision"] == "BLOCK" for item in checks) else "REVIEW"
        return {"decision": decision, "checks": checks, "auto_approved": False}
