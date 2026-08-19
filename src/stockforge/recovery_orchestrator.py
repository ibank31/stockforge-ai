"""Recovery-aware generation orchestration for durable worker retries."""
from __future__ import annotations
from pathlib import Path
from .artifact import Artifact
from .artifact_ingestion import ArtifactIngestor, ProviderOutputRef
from .database import Database
from .execution_identity import execution_id_for_job
from .execution_record import GenerationExecutionRecord
from .generation import GenerationRequest, GenerationResult
from .generation_provider import GenerationProvider
from .orchestrator import OrchestrationError, OrchestrationResult

class RecoveryGenerationOrchestrator:
    """Run one logical job without creating duplicate provider executions."""
    def __init__(self, database: Database, *, project_id: str, project_root: Path, provider_root: Path, provider: GenerationProvider, artifact_ingestor: ArtifactIngestor | None = None) -> None:
        self.database = database
        self.project_id = project_id
        self.project_root = Path(project_root).resolve()
        self.provider_root = Path(provider_root).resolve()
        self.provider = provider
        self.ingestor = artifact_ingestor or ArtifactIngestor(self.project_root)
        if not self.project_root.is_dir(): raise OrchestrationError("Project root must be an existing directory")
        if not self.provider_root.is_dir(): raise OrchestrationError("Provider root must be an existing directory")

    def _execution(self, request: GenerationRequest, job_id: str) -> GenerationExecutionRecord:
        execution = GenerationExecutionRecord.create(self.project_id, prompt=request.prompt, state="submitted", job_id=job_id, provider_id=self.provider.descriptor.id, model_id=request.model_id, model_version=request.model_version, workflow_hash=request.workflow_hash, input_artifact_ids=tuple(request.input_artifact_ids), parameters=dict(request.parameters))
        return GenerationExecutionRecord.from_dict({**execution.to_dict(), "id": execution_id_for_job(self.project_id, job_id)})

    def _ingest(self, provider_job_id: str) -> tuple[Artifact, ...]:
        artifacts: tuple[Artifact, ...] = ()
        for raw in self.provider.output_refs(provider_job_id):
            ref = ProviderOutputRef(filename=raw["filename"], subfolder=raw.get("subfolder", ""), output_type=raw.get("type", "output"), node_id=raw.get("node_id"))
            artifacts += (self.ingestor.ingest(project_id=self.project_id, provider_root=self.provider_root, ref=ref, kind="generated-image", metadata={"provider_id": self.provider.descriptor.id, "provider_job_id": provider_job_id, "node_id": ref.node_id, "output_type": ref.output_type}),)
        return artifacts

    def run(self, request: GenerationRequest, *, timeout_seconds: float = 600.0, job_id: str | None = None) -> OrchestrationResult:
        if timeout_seconds <= 0: raise OrchestrationError("timeout_seconds must be positive")
        if job_id is None:
            from .orchestrator import GenerationOrchestrator
            return GenerationOrchestrator(self.database, project_id=self.project_id, project_root=self.project_root, provider_root=self.provider_root, provider=self.provider, artifact_ingestor=self.ingestor).run(request, timeout_seconds=timeout_seconds)

        execution = self._execution(request, job_id)
        existing = self.database.get_execution(execution.id)
        if existing is None:
            execution = self.database.create_execution(execution)
        else:
            execution = existing
            if execution.job_id != job_id or execution.project_id != self.project_id: raise OrchestrationError("EXECUTION_IDENTITY_COLLISION")
            if execution.state == "succeeded": return OrchestrationResult(execution=execution)
            if execution.state in {"failed", "cancelled"}: raise OrchestrationError(f"EXECUTION_TERMINAL: {execution.state}")

        provider_job_id = execution.provider_job_id
        try:
            if provider_job_id is None:
                execution = self.database.update_execution(GenerationExecutionRecord.from_dict({**execution.to_dict(), "state": "running"}))
                submit = getattr(self.provider, "submit", None)
                if not callable(submit): raise OrchestrationError("PROVIDER_NOT_ASYNC")
                try:
                    provider_job = submit(request, provider_job_id=execution.id)
                except TypeError as exc:
                    if "provider_job_id" not in str(exc): raise
                    raise OrchestrationError("EXECUTION_SUBMISSION_UNKNOWN: provider adapter cannot accept durable identity") from exc
                provider_job_id = provider_job.provider_job_id
                execution = self.database.update_execution(GenerationExecutionRecord.from_dict({**execution.to_dict(), "provider_job_id": provider_job_id}))

            wait = getattr(self.provider, "wait", None)
            if not callable(wait): raise OrchestrationError("PROVIDER_NOT_RESUMABLE")
            terminal = wait(provider_job_id, timeout_seconds=timeout_seconds)
            if terminal.state == "failed": raise OrchestrationError(f"{terminal.error_code or 'PROVIDER_EXECUTION_FAILED'}: {terminal.error_message or 'Provider execution failed'}")
            if terminal.state == "cancelled": raise OrchestrationError("PROVIDER_EXECUTION_CANCELLED: Provider execution was cancelled")
            if terminal.state != "completed": raise OrchestrationError("PROVIDER_INVALID_TERMINAL_STATE")

            artifacts = self._ingest(provider_job_id)
            if not artifacts: raise OrchestrationError("PROVIDER_NO_OUTPUTS: Provider completed without output artifacts")
            result = GenerationResult(status="succeeded", artifact_ids=tuple(a.id for a in artifacts), provider_job_id=provider_job_id, model_id=request.model_id, model_version=request.model_version, workflow_hash=request.workflow_hash, seed=request.seed, parameters=dict(request.parameters))
            final = GenerationExecutionRecord.from_dict({**execution.to_dict(), "state": "succeeded", "provider_job_id": provider_job_id, "artifact_ids": list(result.artifact_ids), "error_code": None, "error_message": None})
            registered_artifacts, registered_execution = self.database.create_artifacts_and_execution(artifacts, final)
            return OrchestrationResult(execution=registered_execution, artifacts=registered_artifacts)
        except OrchestrationError:
            raise
        except Exception as exc:
            raise OrchestrationError(f"ORCHESTRATION_FAILED: {str(exc) or exc.__class__.__name__}") from exc
