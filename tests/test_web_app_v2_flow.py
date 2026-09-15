from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from stockforge import web_app


def _upload(client: TestClient, tmp_path: Path) -> str:
    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "orange").save(source)
    with source.open("rb") as handle:
        response = client.post("/api/references", files={"file": ("reference.png", handle, "image/png")})
    assert response.status_code == 200
    return response.json()["reference_id"]


def _opportunity() -> dict:
    return {
        "market_intent": "commercial sustainability asset",
        "proposed_subject": "reusable insulated drink tumbler",
        "proposed_composition": "elevated three-quarter isolated view",
        "proposed_viewpoint": "slightly elevated",
        "proposed_color_direction": "muted earth tones",
        "proposed_context": "minimal studio product asset",
        "proposed_use_case": "sustainability campaign",
        "differentiation_rationale": ["change subject", "change composition", "change color"],
    }


def test_plan_and_generate_preserve_reference_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(web_app, "UPLOAD_ROOT", tmp_path / "uploads")
    monkeypatch.setattr(web_app, "JOB_DATABASE_PATH", tmp_path / "jobs.sqlite")
    client = TestClient(web_app.app)
    reference_id = _upload(client, tmp_path)

    planned = client.post(f"/api/references/{reference_id}/plan", json=_opportunity())
    assert planned.status_code == 200
    assert planned.json()["decision"] == "READY_TO_GENERATE"

    queued = client.post(f"/api/references/{reference_id}/generate")
    assert queued.status_code == 200
    job = client.get(f"/api/jobs/{queued.json()['job_id']}").json()
    assert job["status"] == "queued"
    assert job["job_type"] == "v2_generation"
    assert job["payload"]["parameters"]["reference_id"] == reference_id
    assert Path(job["payload"]["parameters"]["reference_path"]).is_file()


def test_generate_requires_plan(tmp_path, monkeypatch):
    monkeypatch.setattr(web_app, "UPLOAD_ROOT", tmp_path / "uploads")
    monkeypatch.setattr(web_app, "JOB_DATABASE_PATH", tmp_path / "jobs.sqlite")
    client = TestClient(web_app.app)
    reference_id = _upload(client, tmp_path)
    response = client.post(f"/api/references/{reference_id}/generate")
    assert response.status_code == 409
