"""Controlled generation orchestration from provider execution to durable artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .artifact import Artifact
from .artifact_ingestion import ArtifactIngestor, ProviderOutputRef
from .database import Database
from .execution_record import GenerationExecutionRecord
from .generation import GenerationRequest, GenerationResult
from .generation_provider import GenerationProvider, ProviderJob


class OrchestrationError(RuntimeError):
    """Raised when a generation cannot be completed and recorded safely."""


class AsyncArtifactProvider(GenerationProvider, Protocol):
    """Optional provider capabilities required for provider-output ingestion."""

    def wait(self, provider_job_id: str, *, timeout_seconds: float) -> ProviderJob: ...

    def output_refs(self, provider_job_id: str) -> tuple[dict[str, str], ...]: ...


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    """Durable outcome of one StockForge generation operation."""

    execution: GenerationExecutionRecord
    artifacts: tuple[Artifact, ...] = ()


class GenerationOrchestrator:
    """Coordinates provider execution, output ingestion, and provenance."""

    def __init__(
        self,
        database: Database,
        *,
        project_id: str,
        project_root: Path,
        provider_root: Path,
        provider: GenerationProvider,
        artifact_ingestor: ArtifactIngestor | None = None,
    ) -> None:
        self.database = database
        self.project_id = project_id
        self.project_root = Path(project_root).resolve()
        self.provider_root = Path(provider_root).resolve()
        self.provider = provider
        self.ingestor = artifact_ingestor or ArtifactIngestor(self.project_root)

        if not self.project_root.is_dir():
            raise OrchestrationError("Project root must be an existing directory")
        if not self.provider_root.is_dir():
            raise OrchestrationError("Provider root must be an existing directory")

    def run(self, request: GenerationRequest, *, timeout_seconds: float = 600.0) -> OrchestrationResult:
        """Execute one request and persist a final immutable execution record."""
        if timeout_seconds <= 0:
            raise OrchestrationError("timeout_seconds must be positive")

        descriptor = self.provider.descriptor
        provider_job_id: str | None = None
        artifacts: tuple[Artifact, ...] = ()
        result: GenerationResult | None = None
        error_code: str | None = None
        error_message: str | None = None

        try:
            submit = getattr(self.provider, "submit", None)
            wait = getattr(self.provider, "wait", None)
            output_refs = getattr(self.provider, "output_refs", None)

            if callable(submit) and callable(wait) and callable(output_refs):
                job = submit(request)
                provider_job_id = job.provider_job_id
                terminal = wait(provider_job_id, timeout_seconds=timeout_seconds)
                if terminal.state == "failed":
                    error_code = terminal.error_code or "PROVIDER_EXECUTION_FAILED"
                    error_message = terminal.error_message or "Provider execution failed"
                elif terminal.state == "cancelled":
                    error_code = "PROVIDER_EXECUTION_CANCELLED"
                    error_message = "Provider execution was cancelled"
                elif terminal.state != "completed" and terminal.result is None:
                    error_code = "PROVIDER_INVALID_TERMINAL_STATE"
                    error_message = f"Unexpected provider terminal state: {terminal.state}"
                else:
                    refs = output_refs(provider_job_id)
                    for raw_ref in refs:
                        ref = ProviderOutputRef(
                            filename=raw_ref["filename"],
                            subfolder=raw_ref.get("subfolder", ""),
                            output_type=raw_ref.get("type", "output"),
                            node_id=raw_ref.get("node_id"),
                        )
                        artifacts += (self.ingestor.ingest(
                            project_id=self.project_id,
                            provider_root=self.provider_root,
                            ref=ref,
                            kind="generated-image",
                            metadata={
                                "provider_id": descriptor.id,
                                "provider_job_id": provider_job_id,
                                "node_id": ref.node_id,
                                "output_type": ref.output_type,
                            },
                        ),)
                    if not artifacts:
                        error_code = "PROVIDER_NO_OUTPUTS"
                        error_message = "Provider completed without any output artifacts"
                    else:
                        result = GenerationResult(
                            status="succeeded",
                            artifact_ids=tuple(artifact.id for artifact in artifacts),
                            provider_job_id=provider_job_id,
                            model_id=request.model_id,
                            model_version=request.model_version,
                            workflow_hash=request.workflow_hash,
                            seed=request.seed,
                            parameters=dict(request.parameters),
                        )
            else:
                result = self.provider.generate(request)
                provider_job_id = result.provider_job_id
                if result.status == "failed":
                    error_code = result.error_code
                    error_message = result.error_message
                elif not result.artifact_ids:
                    error_code = "PROVIDER_NO_ARTIFACTS"
                    error_message = "Provider reported success without artifact IDs"

        except Exception as exc:
            error_code = "ORCHESTRATION_FAILED"
            error_message = str(exc) or exc.__class__.__name__

        if error_code is not None:
            execution = GenerationExecutionRecord.create(
                self.project_id,
                prompt=request.prompt,
                state="failed",
                provider_id=descriptor.id,
                provider_job_id=provider_job_id,
                model_id=request.model_id,
                model_version=request.model_version,
                workflow_hash=request.workflow_hash,
                input_artifact_ids=request.input_artifact_ids,
                parameters=dict(request.parameters),
                error_code=error_code,
                error_message=error_message,
            )
            self.database.create_execution(execution)
            raise OrchestrationError(f"{error_code}: {error_message}")

        if result is None:
            raise OrchestrationError("Generation completed without a result")

        execution = GenerationExecutionRecord.create(
            self.project_id,
            prompt=request.prompt,
            state="succeeded",
            provider_id=descriptor.id,
            provider_job_id=provider_job_id,
            model_id=result.model_id or request.model_id,
            model_version=result.model_version or request.model_version,
            workflow_hash=result.workflow_hash or request.workflow_hash,
            artifact_ids=result.artifact_ids,
            input_artifact_ids=request.input_artifact_ids,
            parameters=dict(result.parameters),
        )
        for artifact in artifacts:
            self.database.create_artifact(artifact)
        self.database.create_execution(execution)
        return OrchestrationResult(execution=execution, artifacts=artifacts)
