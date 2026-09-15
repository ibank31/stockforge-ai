"""StockForge V2 browser API.

The API keeps reference identity in durable sidecar records and puts only
provider-neutral GenerationRequest payloads on the persistent job queue.
Generation execution remains a worker concern; this boundary never auto-
approves an output.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .auto_crop import CropBox, crop_reference, suggest_crop_candidates
from .creative_opportunity import build_creative_opportunity
from .database import Database
from .job_database import JobDatabase
from .job_manager import JobManager
from .reference_intelligence import (
    CreativeDistancePlan,
    ReferenceIntelligenceError,
    profile_reference_image,
)
from .v2_pipeline import V2PipelineError, build_v2_generation_plan

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
UPLOAD_ROOT = Path("runtime/web-references")
JOB_DATABASE_PATH = Path("runtime/web-jobs.sqlite")
PROJECT_ID = "00000000-0000-0000-0000-000000000001"
PROJECT_NAME = "browser-v2"

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
    return JobManager(database)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html><html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>StockForge V2</title></head><body><h1>StockForge V2</h1><p>Upload → analyze → plan → generate. Human review is required.</p><input id=f type=file accept='.jpg,.jpeg,.png,.webp'><button onclick=go()>Upload & Analyze</button><pre id=o>Ready.</pre><script>async function go(){const f=document.getElementById('f').files[0];if(!f)return;const d=new FormData();d.append('file',f);const r=await fetch('/api/references',{method:'POST',body:d});document.getElementById('o').textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>"""


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
        return {"reference_id": reference_id, "file": f"/files/{destination.name}", "profile": record["profile"], "crop_candidates": [item.to_dict() for item in crops], "decision": "REVIEW_REQUIRED", "notice": "Reference facts are measurable; commercial meaning must be supplied or verified separately."}
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
    request["parameters"] = {**request.get("parameters", {}), "reference_id": reference_id, "reference_path": record["source_path"], "creative_plan": plan}
    try:
        job = _ensure_job_store().create(project_id=PROJECT_ID, job_type="v2_generation", payload=request, max_attempts=2)
    except (OSError, ValueError) as exc:
        raise HTTPException(500, str(exc)) from exc
    record["job_id"] = job.id
    _record_path(reference_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
    return {"reference_id": reference_id, "job_id": job.id, "status": job.status, "job_type": job.job_type, "decision": "QUEUED"}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    try:
        return _ensure_job_store().database.get_job(job_id).to_record()
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
""
