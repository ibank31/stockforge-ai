"""Durable execution bridge from StockForge jobs to generation providers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_ingestion import ArtifactIngestor, ProviderOutputRef
from .database import Database
from .execution_record import GenerationExecutionRecord
from .generation import GenerationRequest
from .generation_provider import GenerationProvider, ProviderRuntimeError
from .job import Job, JobError
from .job_manager import JobManager

IMAGE_GENERATE_JOB = "image.generate"


class GenerationJobOrchestrator:
    """Execute one claimed image-generation job and persist its execution."""

    def __init__(
        self,
        *,
        job_manager: JobManager,
        database: Database,
        provider: GenerationProvider,
        provider_root: Path,
    ) -> None:
        self.job_manager = job_manager
        self.database = database
        self.provider = provider
        self.provider_root = Path(provider_root).resolve()

    def run(self, job: Job) -> GenerationExecutionRecord:
        if job.status != "running":
            raise JobError("Generation job must be claimed before execution")
        if job.job_type != IMAGE_GENERATE_JOB:
            raise JobError(f"Unsupported generation job type: {job.job_type}")

        payload = job.payload
        raw_request = payload.get("generation")
        if not isinstance(raw_request, dict):
            raise JobError("image.generate payload requires a generation object")
        request = GenerationRequest(**raw_request)
        execution_id = payload.get("execution_id")
        existing = self.database.get_execution(execution_id) if isinstance(execution_id, str) else None
        if existing is not None and existing.job_id not in {None, job.id}:
            raise JobError("execution_id belongs to a different job")

        execution = existing or GenerationExecutionRecord.create(
            job.project_id,
            prompt=request.prompt,
            operation=IMAGE_GENERATE_JOB,
            job_id=job.id,
            provider_id=self.provider.descriptor.id,
            model_id=request.model_id,
            model_version=request.model_version,
            workflow_hash=request.workflow_hash,
            input_artifact_ids=request.input_artifact_ids,
            parameters=request.parameters,
        )
        if existing is None:
            self.database.create_execution(execution)

        provider_job_id = execution.provider_job_id
        submitted = self.provider.submit(request, provider_job_id=provider_job_id)
        execution = self._replace_execution(execution, state="running", provider_job_id=submitted.provider_job_id)
        self.database.update_execution(execution)

        try:
            terminal = self._wait(self.provider, submitted.provider_job_id)
            if terminal.state != "completed":
                raise ProviderRuntimeError(
                    terminal.error_message or f"Provider ended in state: {terminal.state}"
                )

            output_refs = getattr(self.provider, "output_refs", None)
            if not callable(output_refs):
                raise ProviderRuntimeError("Generation provider does not expose output_refs")
            refs = tuple(output_refs(submitted.provider_job_id))
            if not refs:
                raise ProviderRuntimeError("Provider completed without output references")

            ingestor = ArtifactIngestor(Path(self._project_path(job.project_id)))
            artifacts = tuple(
                ingestor.ingest(
                    project_id=job.project_id,
                    provider_root=self.provider_root,
                    ref=ProviderOutputRef(
                        filename=ref["filename"],
                        subfolder=ref.get("subfolder", ""),
                        output_type=ref.get("type", "output"),
                        node_id=ref.get("node_id"),
                    ),
                    metadata={"provider": self.provider.descriptor.id},
                )
                for ref in refs
            )
            self.database.create_artifacts_and_execution(
                artifacts,
                self._replace_execution(
                    execution,
                    state="succeeded",
                    artifact_ids=tuple(a.id for a in artifacts),
                ),
            )
            final = self.database.get_execution(execution.id)
            if final is None:
                raise ProviderRuntimeError("Execution record disappeared after completion")
            self.job_manager.complete(job.id, {"execution_id": final.id, "artifact_ids": list(final.artifact_ids)})
            return final
        except Exception as exc:
            failed = self._replace_execution(
                execution,
                state="failed",
                error_code=type(exc).__name__,
                error_message=str(exc),
            )
            self.database.update_execution(failed)
            self.job_manager.fail(job.id, str(exc))
            raise

    @staticmethod
    def _wait(provider: GenerationProvider, provider_job_id: str):
        wait = getattr(provider, "wait", None)
        if callable(wait):
            return wait(provider_job_id)
        return provider.status(provider_job_id)

    def _project_path(self, project_id: str) -> str:
        for project in self.database.list_projects():
            if project["id"] == project_id:
                return project["path"]
        raise JobError(f"Project not found: {project_id}")

    @staticmethod
    def _replace_execution(record: GenerationExecutionRecord, **changes: Any) -> GenerationExecutionRecord:
        data = record.to_dict()
        data.update(changes)
        return GenerationExecutionRecord.from_dict(data)
