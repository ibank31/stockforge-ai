"""StockForge V2 browser API.

Run locally first, then expose only this HTTP service through Cloudflare Tunnel.
The tunnel is transport only; generation and artifacts stay on the StockForge host.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .auto_crop import CropBox, crop_reference, suggest_crop_candidates
from .reference_intelligence import ReferenceIntelligenceError, profile_reference_image

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
UPLOAD_ROOT = Path("runtime/web-references")

app = FastAPI(title="StockForge V2", version="2.0")
app.mount("/files", StaticFiles(directory=str(UPLOAD_ROOT), check_dir=False), name="files")


def _safe_name(name: str | None) -> str:
    suffix = Path(name or "reference.png").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Only JPG, PNG and single-frame WebP references are accepted.")
    return suffix


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>StockForge V2</title><style>body{font-family:system-ui;margin:2rem;max-width:760px}button,input{margin:.5rem 0;padding:.6rem}pre{white-space:pre-wrap;background:#111;color:#ddd;padding:1rem;border-radius:8px}</style></head>
    <body><h1>StockForge V2</h1><p>Upload screenshot → auto-crop candidates → profile reference. Human review remains required.</p>
    <input id="f" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"><br><button onclick="go()">Upload & Analyze</button><pre id="o">Ready.</pre>
    <script>async function go(){let f=document.getElementById('f').files[0];if(!f)return;let d=new FormData();d.append('file',f);let r=await fetch('/api/references',{method:'POST',body:d});let j=await r.json();document.getElementById('o').textContent=JSON.stringify(j,null,2)}</script></body></html>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "stockforge-v2-web"}


@app.post("/api/references")
async def upload_reference(file: UploadFile = File(...)) -> dict:
    suffix = _safe_name(file.filename)
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
        return {
            "reference_id": reference_id,
            "file": f"/files/{destination.name}",
            "profile": profile.to_dict(),
            "crop_candidates": [item.to_dict() for item in crops],
            "decision": "REVIEW_REQUIRED",
            "notice": "Reference facts are measurable. Subject/commercial meaning must be supplied or verified separately.",
        }
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    except (ReferenceIntelligenceError, OSError, ValueError) as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(400, str(exc)) from exc
    finally:
        await file.close()


@app.post("/api/references/{reference_id}/crop")
def apply_crop(reference_id: str, left: int, top: int, right: int, bottom: int) -> dict:
    matches = list(UPLOAD_ROOT.glob(f"{reference_id}.*"))
    if len(matches) != 1:
        raise HTTPException(404, "Reference not found.")
    source = matches[0]
    destination = UPLOAD_ROOT / f"{reference_id}-crop.png"
    try:
        crop_reference(source, destination, CropBox(left, top, right, bottom))
        return {"reference_id": reference_id, "file": f"/files/{destination.name}", "decision": "CROP_CONFIRMED"}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
