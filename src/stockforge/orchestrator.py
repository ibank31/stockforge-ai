"""Controlled generation orchestration from provider execution to durable artifacts."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .artifact import Artifact
from .artifact_ingestion import ArtifactIngestor, ProviderOutputRef
from .database import Database
from .execution_record import GenerationExecutionRecord
from .generation import GenerationRequest, GenerationResult
from .generation_provider import GenerationProvider

class OrchestrationError(RuntimeError): pass
@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    execution: GenerationExecutionRecord
    artifacts: tuple[Artifact,...]=()

class GenerationOrchestrator:
    def __init__(self,database:Database,*,project_id:str,project_root:Path,provider_root:Path,provider:GenerationProvider,artifact_ingestor:ArtifactIngestor|None=None):
        self.database=database; self.project_id=project_id; self.project_root=Path(project_root).resolve(); self.provider_root=Path(provider_root).resolve(); self.provider=provider; self.ingestor=artifact_ingestor or ArtifactIngestor(self.project_root)
        if not self.project_root.is_dir(): raise OrchestrationError("Project root must be an existing directory")
        if not self.provider_root.is_dir(): raise OrchestrationError("Provider root must be an existing directory")

    def run(self,request:GenerationRequest,*,timeout_seconds:float=600.0,job_id:str|None=None)->OrchestrationResult:
        if timeout_seconds<=0: raise OrchestrationError("timeout_seconds must be positive")
        descriptor=self.provider.descriptor; inputs=tuple(request.input_artifact_ids)
        execution=GenerationExecutionRecord.create(self.project_id,prompt=request.prompt,state="submitted",job_id=job_id,provider_id=descriptor.id,model_id=request.model_id,model_version=request.model_version,workflow_hash=request.workflow_hash,input_artifact_ids=inputs,parameters=dict(request.parameters))
        self.database.create_execution(execution)
        provider_job_id=None; artifacts=(); result=None; error_code=None; error_message=None; sync=False
        try:
            execution=self.database.update_execution(GenerationExecutionRecord.from_dict({**execution.to_dict(),"state":"running"}))
            submit=getattr(self.provider,"submit",None); wait=getattr(self.provider,"wait",None); output_refs=getattr(self.provider,"output_refs",None)
            if callable(submit) and callable(wait) and callable(output_refs):
                job=submit(request, provider_job_id=execution.id)
                provider_job_id=job.provider_job_id
                execution=self.database.update_execution(GenerationExecutionRecord.from_dict({**execution.to_dict(),"provider_job_id":provider_job_id}))
                terminal=wait(provider_job_id,timeout_seconds=timeout_seconds)
                if terminal.state=="failed": error_code=terminal.error_code or "PROVIDER_EXECUTION_FAILED"; error_message=terminal.error_message or "Provider execution failed"
                elif terminal.state=="cancelled": error_code="PROVIDER_EXECUTION_CANCELLED"; error_message="Provider execution was cancelled"
                elif terminal.state!="completed" and terminal.result is None: error_code="PROVIDER_INVALID_TERMINAL_STATE"; error_message=f"Unexpected provider terminal state: {terminal.state}"
                else:
                    for raw in output_refs(provider_job_id):
                        ref=ProviderOutputRef(filename=raw["filename"],subfolder=raw.get("subfolder",""),output_type=raw.get("type","output"),node_id=raw.get("node_id"))
                        artifacts += (self.ingestor.ingest(project_id=self.project_id,provider_root=self.provider_root,ref=ref,kind="generated-image",metadata={"provider_id":descriptor.id,"provider_job_id":provider_job_id,"node_id":ref.node_id,"output_type":ref.output_type}),)
                    if not artifacts: error_code="PROVIDER_NO_OUTPUTS"; error_message="Provider completed without any output artifacts"
                    else: result=GenerationResult(status="succeeded",artifact_ids=tuple(a.id for a in artifacts),provider_job_id=provider_job_id,model_id=request.model_id,model_version=request.model_version,workflow_hash=request.workflow_hash,seed=request.seed,parameters=dict(request.parameters))
            else:
                result=self.provider.generate(request); sync=True; provider_job_id=result.provider_job_id
                if result.status=="failed": error_code=result.error_code; error_message=result.error_message
                elif not result.artifact_ids: error_code="PROVIDER_NO_ARTIFACTS"; error_message="Provider reported success without artifact IDs"
        except Exception as exc: error_code="ORCHESTRATION_FAILED"; error_message=str(exc) or exc.__class__.__name__
        if error_code is not None:
            failed=GenerationExecutionRecord.from_dict({**execution.to_dict(),"state":"failed","provider_job_id":provider_job_id,"artifact_ids":[],"error_code":error_code,"error_message":error_message})
            self.database.update_execution(failed); raise OrchestrationError(f"{error_code}: {error_message}")
        if result is None:
            failed=GenerationExecutionRecord.from_dict({**execution.to_dict(),"state":"failed","provider_job_id":provider_job_id,"artifact_ids":[],"error_code":"NO_RESULT","error_message":"Generation completed without a result"}); self.database.update_execution(failed); raise OrchestrationError("NO_RESULT: Generation completed without a result")
        final=GenerationExecutionRecord.from_dict({**execution.to_dict(),"state":"succeeded","provider_job_id":provider_job_id,"artifact_ids":list(result.artifact_ids),"model_id":result.model_id or request.model_id,"model_version":result.model_version or request.model_version,"workflow_hash":result.workflow_hash or request.workflow_hash,"parameters":dict(result.parameters),"error_code":None,"error_message":None})
        if sync: return OrchestrationResult(execution=self.database.update_execution(final))
        try: registered_artifacts,registered_execution=self.database.create_artifacts_and_execution(artifacts,final)
        except Exception as exc:
            failed=GenerationExecutionRecord.from_dict({**execution.to_dict(),"state":"failed","provider_job_id":provider_job_id,"artifact_ids":[],"error_code":"PERSISTENCE_FAILED","error_message":str(exc) or exc.__class__.__name__}); self.database.update_execution(failed); raise OrchestrationError("PERSISTENCE_FAILED: Failed to atomically persist generation outputs") from exc
        return OrchestrationResult(execution=registered_execution,artifacts=registered_artifacts)
