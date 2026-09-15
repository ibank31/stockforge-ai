"""StockForge V2 browser API.

The API keeps reference identity in durable sidecar records and puts only
provider-neutral GenerationRequest payloads on the persistent job queue.
Generation execution remains a worker concern; this boundary never auto-
approves an output.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .auto_crop import CropBox, crop_reference, suggest_crop_candidates
from .creative_opportunity import build_creative_opportunity
from .database import Database
from .job_database import JobDatabase
from .job_manager import JobManager
from .image_qa import ImageQAError, inspect_image
from .release_package import ReleasePackageError, build_release_package
from .reference_intelligence import (
    CreativeDistancePlan,
    ReferenceIntelligenceError,
    profile_reference_image,
)
from .v2_pipeline import V2PipelineError, build_v2_generation_plan
from .workflow_control import WorkflowControl

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
UPLOAD_ROOT = Path("runtime/web-references")
JOB_DATABASE_PATH = Path("runtime/web-jobs.sqlite")
PROJECT_ID = "00000000-0000-0000-0000-000000000001"
PROJECT_NAME = "browser-v2"
DEFAULT_MAX_REGENERATIONS = 2

app = FastAPI(title="StockForge V2", version="2.0")
app.mount("/files", StaticFiles(directory=str(UPLOAD_ROOT), check_dir=False), name="files")


class OpportunityInput(BaseModel):
    market_intent: str
    proposed_subject: str
    proposed_composition: str
    proposed_viewpoint: str
    proposed_color_direction: str
    proposed_context: str
    proposed_use_case: str
    differentiation_rationale: list[str] = Field(min_length=3)
    subject: str | None = None
    category: str | None = None
    commercial_intent: str | None = None
    buyer_relevance: str | None = None
    change_subject: bool = True
    change_composition: bool = True
    change_viewpoint: bool = True
    change_color_direction: bool = True
    change_context: bool = True
    change_use_case: bool = True
    seed: int | None = Field(default=None, ge=0)
    model_id: str | None = None


def _safe_suffix(name: str | None) -> str:
    suffix = Path(name or "reference.png").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Only JPG, PNG and single-frame WebP references are accepted.")
    return suffix


def _record_path(reference_id: str) -> Path:
    return UPLOAD_ROOT / f"{reference_id}.json"


def _find_reference(reference_id: str) -> tuple[Path, dict[str, Any]]:
    record_path = _record_path(reference_id)
    if not record_path.is_file():
        raise HTTPException(404, "Reference not found.")
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        source = Path(record["source_path"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(500, "Reference record is invalid.") from exc
    if not source.is_file():
        raise HTTPException(404, "Reference file is missing.")
    return source, record


def _ensure_job_store() -> JobManager:
    database = JobDatabase(JOB_DATABASE_PATH)
    database.initialize()
    # The browser API uses one explicit local project for queue ownership.
    with database.connect() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO projects (id, name, path) VALUES (?, ?, ?)",
            (PROJECT_ID, PROJECT_NAME, str(UPLOAD_ROOT.parent)),
        )
    manager = JobManager(database)
    WorkflowControl(database).initialize()
    return manager


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>StockForge V2</title><style>
body{font-family:system-ui,sans-serif;background:#f5f7fb;color:#172033;margin:0}.wrap{max-width:980px;margin:0 auto;padding:28px 18px}
.card{background:white;border:1px solid #dfe5ef;border-radius:14px;padding:20px;margin:14px 0;box-shadow:0 2px 8px #15294d0b}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
label{display:block;font-size:.84rem;font-weight:650;color:#526078}input,textarea,button{box-sizing:border-box;width:100%;padding:10px;border:1px solid #cbd4e3;border-radius:8px;font:inherit;margin-top:5px}textarea{min-height:66px}button{background:#2457d6;color:white;border:0;font-weight:700;cursor:pointer}button.secondary{background:#64748b}button:disabled{opacity:.5;cursor:not-allowed}pre{white-space:pre-wrap;overflow:auto;background:#111827;color:#dbeafe;padding:14px;border-radius:9px;max-height:420px}.status{font-weight:700}.blocked{color:#b42318}.review{color:#97600a}.ok{color:#147a4b}small{color:#65748b}
</style></head><body><main class="wrap"><h1>StockForge V2</h1><p>Reference intelligence → creative distance → generation → similarity gate. <b>Final human review is required.</b></p>
<section class="card"><h2>1. Upload reference</h2><input id="file" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"><button id="upload" onclick="uploadReference()">Upload &amp; analyze</button><p id="referenceStatus" class="status">Ready.</p><pre id="profile">No reference uploaded.</pre></section>
<section class="card"><h2>Pipeline monitor</h2><p id="workflowStatus" class="status">No workflow yet.</p><div id="workflowProgress"></div><pre id="workflowResult">Upload a reference to start durable tracking.</pre></section><section class="card"><h2>2. Define a new creative opportunity</h2><div class="grid">
<label>Market intent<input id="market_intent" value="commercial sustainability asset"></label><label>New subject<input id="proposed_subject" value="reusable insulated drink tumbler"></label>
<label>Composition<input id="proposed_composition" value="elevated three-quarter isolated view"></label><label>Viewpoint<input id="proposed_viewpoint" value="slightly elevated"></label>
<label>Color direction<input id="proposed_color_direction" value="muted earth tones"></label><label>Context<input id="proposed_context" value="minimal studio product asset"></label>
<label>Use case<input id="proposed_use_case" value="sustainability campaign"></label><label>Seed (optional)<input id="seed" type="number" min="0"></label></div>
<label>Why is it materially different? <small>Use at least three separate changes.</small><textarea id="differentiation_rationale">change subject\nchange composition\nchange color</textarea>
<button id="plan" onclick="createPlan()" disabled>Analyze &amp; create plan</button><pre id="planResult">Upload a reference first.</pre></section>
<section class="card"><h2>3. Generate and review</h2><button id="generate" onclick="queueGeneration()" disabled>Queue generation</button><div class="grid"><button id="qa" class="secondary" onclick="runQA()" disabled>Run technical QA</button><button id="approve" class="secondary" onclick="approveJob()" disabled>Approve for package</button><button id="release" onclick="releaseJob()" disabled>Create download package</button></div><p id="jobStatus" class="status">No generation job queued.</p><div id="preview"></div><pre id="jobResult">The similarity gate result will appear here.</pre></section>
</main><script>
let referenceId=null, workflowId=null, jobId=null, pollTimer=null, workflowTimer=null;
const $=id=>document.getElementById(id); const show=(id,value)=>$(id).textContent=typeof value==='string'?value:JSON.stringify(value,null,2);
async function api(url,options={}){const r=await fetch(url,options);let body;try{body=await r.json()}catch(_){body={detail:await r.text()}}if(!r.ok)throw Error(body.detail||'Request failed');return body}
async function uploadReference(){const file=$('file').files[0];if(!file){show('referenceStatus','Choose an image first.');return}$('upload').disabled=true;show('referenceStatus','Uploading and profiling…');try{const data=new FormData();data.append('file',file);const result=await api('/api/references',{method:'POST',body:data});referenceId=result.reference_id;workflowId=result.workflow_id;show('profile',result.profile);$('plan').disabled=false;show('referenceStatus','Reference ready: '+referenceId);startWorkflowPolling()}catch(e){show('referenceStatus','Error: '+e.message)}finally{$('upload').disabled=false}}
function opportunity(){const value=id=>$(id).value.trim();return {market_intent:value('market_intent'),proposed_subject:value('proposed_subject'),proposed_composition:value('proposed_composition'),proposed_viewpoint:value('proposed_viewpoint'),proposed_color_direction:value('proposed_color_direction'),proposed_context:value('proposed_context'),proposed_use_case:value('proposed_use_case'),differentiation_rationale:$('differentiation_rationale').value.split('\\n').map(x=>x.trim()).filter(Boolean),seed:$('seed').value?Number($('seed').value):null}}
async function createPlan(){if(!referenceId)return;$('plan').disabled=true;show('planResult','Building anti-similarity plan…');try{const result=await api('/api/references/'+referenceId+'/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(opportunity())});show('planResult',result);$('generate').disabled=false}catch(e){show('planResult','Error: '+e.message)}finally{$('plan').disabled=false}}
async function queueGeneration(){if(!referenceId)return;$('generate').disabled=true;try{const result=await api('/api/references/'+referenceId+'/generate',{method:'POST'});workflowId=result.workflow_id||workflowId;jobId=result.job_id;show('jobStatus','Queued: '+jobId);startWorkflowPolling();pollTimer=setInterval(pollJob,1500);await pollJob()}catch(e){show('jobStatus','Error: '+e.message);$('generate').disabled=false}}
async function pollJob(){if(!jobId)return;try{const job=await api('/api/jobs/'+jobId);show('jobResult',job);const status=job.status;show('jobStatus','Job status: '+status);if(status==='succeeded'||status==='failed'||status==='cancelled'){clearInterval(pollTimer);$('generate').disabled=false;const gate=job.result&&job.result.post_generation_verification;if(gate){$('jobStatus').className='status '+(gate.decision==='BLOCK'?'blocked':'review');show('jobStatus',status+' — similarity decision: '+gate.decision+' (human review required)')}if(status==='succeeded'){$('qa').disabled=false;renderArtifacts(job.result)}}}catch(e){clearInterval(pollTimer);show('jobStatus','Polling error: '+e.message);$('generate').disabled=false}}
function startWorkflowPolling(){if(!workflowId)return;if(workflowTimer)clearInterval(workflowTimer);workflowTimer=setInterval(pollWorkflow,1500);pollWorkflow()}
async function pollWorkflow(){if(!workflowId)return;try{const wf=await api('/api/workflows/'+workflowId);const pct=wf.progress||0;show('workflowStatus',wf.current_stage+' — '+pct+'% — '+wf.status+(wf.stuck?' — MAY BE STUCK':''));$('workflowProgress').innerHTML='<progress max="100" value="'+pct+'" style="width:100%;height:18px"></progress><p><small>Last update: '+(wf.updated_at||'n/a')+'</small></p>';show('workflowResult',wf);if(['ready','blocked','failed','cancelled'].includes(wf.status)){clearInterval(workflowTimer);workflowTimer=null}}catch(e){show('workflowStatus','Monitor error: '+e.message)}}
function renderArtifacts(result){const ids=result.artifact_ids||[];$('preview').innerHTML=ids.map(id=>`<p><a href="/api/artifacts/${id}" target="_blank">Open generated artifact ${id}</a><br><img src="/api/artifacts/${id}" style="max-width:100%;max-height:360px;border-radius:8px"></p>`).join('')}
async function runQA(){try{const result=await api('/api/jobs/'+jobId+'/qa',{method:'POST'});show('jobResult',result);if(result.technical_qa&&result.technical_qa.status!=='FAIL')$('approve').disabled=false}catch(e){show('jobStatus','QA error: '+e.message)}}
async function approveJob(){try{const result=await api('/api/jobs/'+jobId+'/approve',{method:'POST'});show('jobResult',result);$('release').disabled=false;show('jobStatus','Approved for package only — manual marketplace upload remains required.')}catch(e){show('jobStatus','Approval blocked: '+e.message)}}
async function releaseJob(){try{const result=await api('/api/jobs/'+jobId+'/release',{method:'POST'});show('jobResult',result);show('jobStatus','Package ready. Download it for manual review and upload.');$('release').outerHTML=`<a href="${result.download_url}" target="_blank">Download review package</a>`}catch(e){show('jobStatus','Packaging error: '+e.message)}}
async function regenerate(){if(!jobId)return;try{const result=await api('/api/jobs/'+jobId+'/regenerate',{method:'POST'});jobId=result.job_id;show('jobStatus','Regeneration queued: '+jobId);pollTimer=setInterval(pollJob,1500);await pollJob()}catch(e){show('jobStatus','Regeneration stopped: '+e.message)}}
</script></body></html>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "stockforge-v2-web"}


@app.post("/api/references")
async def upload_reference(file: UploadFile = File(...)) -> dict[str, Any]:
    suffix = _safe_suffix(file.filename)
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    reference_id = uuid.uuid4().hex
    destination = UPLOAD_ROOT / f"{reference_id}{suffix}"
    total = 0
    try:
        with destination.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "Reference exceeds 20 MB limit.")
                out.write(chunk)
        profile = profile_reference_image(destination)
        crops = suggest_crop_candidates(destination, limit=5)
        record = {"reference_id": reference_id, "source_path": str(destination.resolve()), "profile": profile.to_dict()}
        _record_path(reference_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
        control = WorkflowControl(_ensure_job_store().database); control.initialize()
        workflow = control.create(reference_id, metadata={"filename": file.filename or destination.name})
        control.event(workflow["id"], stage="ANALYZING", message="Reference profiling completed; awaiting creative planning.")
        return {"reference_id": reference_id, "workflow_id": workflow["id"], "file": f"/files/{destination.name}", "profile": record["profile"], "crop_candidates": [item.to_dict() for item in crops], "decision": "REVIEW_REQUIRED", "notice": "Reference facts are measurable; commercial meaning must be supplied or verified separately."}
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except (ReferenceIntelligenceError, OSError, ValueError) as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(400, str(exc)) from exc
    finally:
        await file.close()


@app.post("/api/references/{reference_id}/crop")
def apply_crop(reference_id: str, left: int, top: int, right: int, bottom: int) -> dict[str, Any]:
    source, record = _find_reference(reference_id)
    destination = UPLOAD_ROOT / f"{reference_id}-crop.png"
    try:
        crop_reference(source, destination, CropBox(left, top, right, bottom))
        record["source_path"] = str(destination.resolve())
        record["profile"] = profile_reference_image(destination).to_dict()
        _record_path(reference_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
        return {"reference_id": reference_id, "file": f"/files/{destination.name}", "decision": "CROP_CONFIRMED", "profile": record["profile"]}
    except (ValueError, OSError, ReferenceIntelligenceError) as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/references/{reference_id}")
def get_reference(reference_id: str) -> dict[str, Any]:
    _source, record = _find_reference(reference_id)
    return record


@app.post("/api/references/{reference_id}/plan")
def create_plan(reference_id: str, payload: OpportunityInput) -> dict[str, Any]:
    source, record = _find_reference(reference_id)
    try:
        semantic = payload.model_dump(include={"subject", "category", "commercial_intent", "buyer_relevance"})
        profile = profile_reference_image(source, **semantic)
        distance = CreativeDistancePlan(**payload.model_dump(include={"change_subject", "change_composition", "change_viewpoint", "change_color_direction", "change_context", "change_use_case"}))
        opportunity = build_creative_opportunity(profile, opportunity_id=uuid.uuid4().hex, market_intent=payload.market_intent, proposed_subject=payload.proposed_subject, proposed_composition=payload.proposed_composition, proposed_viewpoint=payload.proposed_viewpoint, proposed_color_direction=payload.proposed_color_direction, proposed_context=payload.proposed_context, proposed_use_case=payload.proposed_use_case, differentiation_rationale=tuple(payload.differentiation_rationale), creative_distance=distance)
        plan = build_v2_generation_plan(profile, opportunity, seed=payload.seed, model_id=payload.model_id)
        record["profile"] = profile.to_dict()
        record["plan"] = plan.to_dict()
        control = WorkflowControl(_ensure_job_store().database); control.initialize(); workflow = control.get_for_reference(reference_id)
        if workflow: control.event(workflow["id"], stage="PLANNING", message="Creative opportunity and anti-similarity plan are ready.")
        _record_path(reference_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
        return {"reference_id": reference_id, "plan": plan.to_dict(), "decision": "READY_TO_GENERATE"}
    except (ReferenceIntelligenceError, V2PipelineError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/references/{reference_id}/generate")
def enqueue_generation(reference_id: str) -> dict[str, Any]:
    _source, record = _find_reference(reference_id)
    plan = record.get("plan")
    if not isinstance(plan, dict):
        raise HTTPException(409, "Create and review a creative plan before generating.")
    request = dict(plan["generation_request"])
    control = WorkflowControl(_ensure_job_store().database); control.initialize(); workflow = control.get_for_reference(reference_id)
    request["parameters"] = {**request.get("parameters", {}), "reference_id": reference_id, "reference_path": record["source_path"], "creative_plan": plan}
    if workflow: request["parameters"]["workflow_id"] = workflow["id"]
    try:
        job = _ensure_job_store().create(project_id=PROJECT_ID, job_type="v2_generation", payload=request, max_attempts=2)
    except (OSError, ValueError) as exc:
        raise HTTPException(500, str(exc)) from exc
    record["job_id"] = job.id
    if workflow:
        control.attach_job(workflow["id"], job.id)
        control.event(workflow["id"], stage="QUEUED", message="Generation job queued.", job_id=job.id)
    _record_path(reference_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
    return {"reference_id": reference_id, "workflow_id": workflow["id"] if workflow else None, "job_id": job.id, "status": job.status, "job_type": job.job_type, "decision": "QUEUED"}


@app.post("/api/jobs/{job_id}/regenerate")
def regenerate_job(job_id: str) -> dict[str, Any]:
    """Queue one bounded regeneration only after a post-generation BLOCK."""
    manager = _ensure_job_store()
    try:
        parent = manager.database.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    if parent.project_id != PROJECT_ID or parent.job_type != "v2_generation":
        raise HTTPException(400, "Only V2 generation jobs can be regenerated.")
    result = parent.result or {}
    gate = result.get("post_generation_verification")
    if parent.status != "succeeded" or not isinstance(gate, dict) or gate.get("decision") != "BLOCK":
        raise HTTPException(409, "Regeneration is allowed only for a completed job blocked by similarity verification.")
    parameters = dict(parent.payload.get("parameters") or {})
    attempt = int(parameters.get("regeneration_attempt", 0))
    maximum = int(parameters.get("max_regeneration_attempts", DEFAULT_MAX_REGENERATIONS))
    if maximum < 1 or maximum > DEFAULT_MAX_REGENERATIONS:
        maximum = DEFAULT_MAX_REGENERATIONS
    if attempt >= maximum:
        raise HTTPException(409, f"Regeneration limit reached ({maximum} attempts).")
    for existing in manager.list(project_id=PROJECT_ID):
        existing_parameters = dict(existing.payload.get("parameters") or {})
        if existing_parameters.get("parent_job_id") == job_id and existing.status in {"queued", "running", "succeeded"}:
            raise HTTPException(409, "A regeneration for this blocked job already exists.")
    payload = dict(parent.payload)
    payload["seed"] = (int(payload["seed"]) if payload.get("seed") is not None else 0) + attempt + 1
    payload["prompt"] = str(payload["prompt"]) + f" Regeneration attempt {attempt + 1}: use a materially different subject, composition, palette, and visual structure."
    payload["parameters"] = {**parameters, "parent_job_id": job_id, "regeneration_attempt": attempt + 1, "max_regeneration_attempts": maximum}
    child = manager.create(project_id=PROJECT_ID, job_type="v2_generation", payload=payload, max_attempts=2)
    control = WorkflowControl(manager.database)
    control.initialize()
    workflow = control.get_for_reference(str(parameters.get("reference_id"))) if parameters.get("reference_id") else None
    if workflow:
        control.attach_job(workflow["id"], child.id)
        control.event(workflow["id"], stage="QUEUED", status="active", message="Regeneration queued after similarity block.", job_id=child.id, details={"parent_job_id": job_id, "regeneration_attempt": attempt + 1})
    return {"reference_id": parameters.get("reference_id"), "workflow_id": workflow["id"] if workflow else None, "job_id": child.id, "parent_job_id": job_id, "regeneration_attempt": attempt + 1, "max_regeneration_attempts": maximum, "status": child.status, "decision": "REGENERATION_QUEUED"}


@app.get("/api/workflows/{workflow_id}")
def get_workflow(workflow_id: str) -> dict[str, Any]:
    control = WorkflowControl(_ensure_job_store().database); control.initialize()
    try: return control.get(workflow_id)
    except KeyError as exc: raise HTTPException(404, str(exc)) from exc

@app.get("/api/references/{reference_id}/workflow")
def get_reference_workflow(reference_id: str) -> dict[str, Any]:
    _find_reference(reference_id)
    control = WorkflowControl(_ensure_job_store().database); control.initialize(); workflow = control.get_for_reference(reference_id)
    if workflow is None: raise HTTPException(404, "Workflow not found.")
    return workflow

@app.get("/api/workflows/{workflow_id}/events")
def get_workflow_events(workflow_id: str) -> dict[str, Any]:
    workflow = get_workflow(workflow_id)
    return {"workflow_id": workflow_id, "events": workflow["events"]}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    manager = _ensure_job_store()
    try: job = manager.database.get_job(job_id)
    except ValueError as exc: raise HTTPException(404, str(exc)) from exc
    record = job.to_record(); control = WorkflowControl(manager.database); control.initialize(); record["workflow"] = control.snapshot_for_job(job); return record


def _update_job_result(job_id: str, result: dict[str, Any]) -> dict[str, Any]:
    manager = _ensure_job_store()
    job = manager.database.get_job(job_id)
    merged = {**(job.result or {}), **result}
    with manager.database.connect() as connection:
        connection.execute(
            "UPDATE jobs SET result_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(merged, ensure_ascii=False, sort_keys=True), job_id),
        )
    return manager.database.get_job(job_id).to_record()


@app.post("/api/jobs/{job_id}/qa")
def inspect_job_output(job_id: str) -> dict[str, Any]:
    """Run deterministic technical QA against the worker's registered artifacts."""
    manager = _ensure_job_store()
    try:
        job = manager.database.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    if job.status != "succeeded" or not job.result:
        raise HTTPException(409, "Technical QA requires a succeeded generation job.")
    artifact_ids = job.result.get("artifact_ids", [])
    if not artifact_ids:
        raise HTTPException(409, "Generation job has no registered artifacts.")
    reports = []
    project_root = UPLOAD_ROOT.parent.resolve()
    for artifact_id in artifact_ids:
        artifact = manager.database.get_artifact(artifact_id)
        if artifact is None:
            raise HTTPException(500, f"Artifact not found: {artifact_id}")
        path = (project_root / artifact.relative_path).resolve()
        try:
            path.relative_to(project_root)
            report = asdict(inspect_image(path))
        except (ValueError, OSError, ImageQAError) as exc:
            raise HTTPException(422, str(exc)) from exc
        reports.append({"artifact_id": artifact.id, "file": f"/api/artifacts/{artifact.id}", "report": report})
    status = "FAIL" if any(item["report"]["status"] == "fail" for item in reports) else ("WARN" if any(item["report"]["status"] == "warn" for item in reports) else "PASS")
    updated = _update_job_result(job_id, {"technical_qa": {"status": status, "reports": reports, "human_review_required": True}})
    control = WorkflowControl(manager.database); control.initialize(); workflow = control.snapshot_for_job(job)
    if workflow: control.event(workflow["id"], stage="TECHNICAL_QA", message=f"Technical QA completed with status {status}.", job_id=job_id, details={"status": status})
    return updated["result"]


@app.get("/api/artifacts/{artifact_id}")
def download_artifact(artifact_id: str) -> FileResponse:
    manager = _ensure_job_store()
    artifact = manager.database.get_artifact(artifact_id)
    if artifact is None or artifact.project_id != PROJECT_ID:
        raise HTTPException(404, "Artifact not found.")
    root = UPLOAD_ROOT.parent.resolve()
    path = (root / artifact.relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise HTTPException(404, "Artifact not found.") from exc
    if not path.is_file():
        raise HTTPException(404, "Artifact file not found.")
    return FileResponse(path, media_type=artifact.mime_type or "application/octet-stream", filename=path.name)


@app.post("/api/jobs/{job_id}/approve")
def approve_job_for_release(job_id: str) -> dict[str, Any]:
    """Record explicit human approval; this does not upload or publish externally."""
    manager = _ensure_job_store()
    try:
        job = manager.database.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    result = job.result or {}
    gate = result.get("post_generation_verification") or {}
    qa = result.get("technical_qa") or {}
    if job.status != "succeeded":
        raise HTTPException(409, "Only succeeded jobs can be approved.")
    if gate.get("decision") == "BLOCK":
        raise HTTPException(409, "Blocked output cannot be approved.")
    if qa.get("status") == "FAIL":
        raise HTTPException(409, "Technical QA failed; approval is not allowed.")
    updated = _update_job_result(job_id, {"approval": {"status": "approved_for_release", "human_review_required": True, "notice": "Approved for package preparation only; manual marketplace upload remains required."}})
    control = WorkflowControl(manager.database); control.initialize(); workflow = control.snapshot_for_job(job)
    if workflow: control.event(workflow["id"], stage="FINALIZATION", progress=92, message="Human approval recorded; preparing release package.", job_id=job_id)
    return updated["result"]


@app.post("/api/jobs/{job_id}/release")
def create_release_package(job_id: str) -> dict[str, Any]:
    manager = _ensure_job_store()
    try:
        job = manager.database.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    if (job.result or {}).get("approval", {}).get("status") != "approved_for_release":
        raise HTTPException(409, "Explicit human approval is required before packaging.")
    execution_id = (job.result or {}).get("execution_id")
    if not execution_id:
        raise HTTPException(409, "Generation execution is missing.")
    try:
        package = build_release_package(database=manager.database, project_id=PROJECT_ID, project_root=UPLOAD_ROOT.parent, execution_id=execution_id)
    except (ReleasePackageError, OSError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
    updated = _update_job_result(job_id, {"release_package": {**package.to_dict(), "download_url": f"/api/jobs/{job_id}/download"}})
    control = WorkflowControl(manager.database); control.initialize(); workflow = control.snapshot_for_job(job)
    if workflow: control.event(workflow["id"], stage="READY_UPLOAD_ADOBE", status="ready", progress=100, message="Release package is ready for manual Adobe Stock review and upload.", job_id=job_id)
    return updated["result"]["release_package"]


@app.get("/api/jobs/{job_id}/download")
def download_release_package(job_id: str) -> FileResponse:
    manager = _ensure_job_store()
    try:
        job = manager.database.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    package = (job.result or {}).get("release_package", {})
    path = Path(str(package.get("path", ""))).resolve()
    deliveries = (UPLOAD_ROOT.parent / "deliveries").resolve()
    try:
        path.relative_to(deliveries)
    except ValueError as exc:
        raise HTTPException(404, "Release package not found.") from exc
    if not path.is_file():
        raise HTTPException(404, "Release package not found.")
    return FileResponse(path, media_type="application/zip", filename=path.name)
""
