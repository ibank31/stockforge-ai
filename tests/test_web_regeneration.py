from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from stockforge import web_app


def _blocked_job(tmp_path: Path, monkeypatch) -> tuple[TestClient, str]:
    monkeypatch.setattr(web_app, "UPLOAD_ROOT", tmp_path / "uploads")
    monkeypatch.setattr(web_app, "JOB_DATABASE_PATH", tmp_path / "jobs.sqlite")
    client = TestClient(web_app.app)
    source = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "orange").save(source)
    with source.open("rb") as handle:
        uploaded = client.post("/api/references", files={"file": ("reference.png", handle, "image/png")}).json()
    reference_id = uploaded["reference_id"]
    plan = {
        "market_intent": "commercial sustainability asset",
        "proposed_subject": "reusable insulated drink tumbler",
        "proposed_composition": "elevated three-quarter isolated view",
        "proposed_viewpoint": "slightly elevated",
        "proposed_color_direction": "muted earth tones",
        "proposed_context": "minimal studio product asset",
        "proposed_use_case": "sustainability campaign",
        "differentiation_rationale": ["change subject", "change composition", "change color"],
    }
    assert client.post(f"/api/references/{reference_id}/plan", json=plan).status_code == 200
    queued = client.post(f"/api/references/{reference_id}/generate").json()
    manager = web_app._ensure_job_store()
    parent = manager.database.get_job(queued["job_id"])
    claimed = manager.claim(parent.id, "test-worker")
    manager.complete(claimed.id, {"post_generation_verification": {"decision": "BLOCK", "auto_approved": False}})
    return client, parent.id


def test_regeneration_is_bounded_and_preserves_parent_identity(tmp_path, monkeypatch):
    client, parent_id = _blocked_job(tmp_path, monkeypatch)
    first = client.post(f"/api/jobs/{parent_id}/regenerate")
    assert first.status_code == 200
    body = first.json()
    assert body["parent_job_id"] == parent_id
    assert body["regeneration_attempt"] == 1
    child = client.get(f"/api/jobs/{body['job_id']}").json()
    assert child["payload"]["parameters"]["parent_job_id"] == parent_id
    assert child["payload"]["parameters"]["regeneration_attempt"] == 1

    duplicate = client.post(f"/api/jobs/{parent_id}/regenerate")
    assert duplicate.status_code == 409


def test_regeneration_rejects_non_blocked_jobs(tmp_path, monkeypatch):
    client, parent_id = _blocked_job(tmp_path, monkeypatch)
    manager = web_app._ensure_job_store()
    with manager.database.connect() as connection:
        connection.execute(
            "UPDATE jobs SET result_json = ? WHERE id = ?",
            ('{"post_generation_verification":{"decision":"REVIEW"}}', parent_id),
        )
    response = client.post(f"/api/jobs/{parent_id}/regenerate")
    assert response.status_code == 409
