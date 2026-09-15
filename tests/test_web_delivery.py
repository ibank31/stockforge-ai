from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image

from stockforge import web_app
from stockforge.artifact import Artifact
from stockforge.execution_record import GenerationExecutionRecord


def _ready_job(tmp_path: Path, monkeypatch) -> tuple[TestClient, str]:
    monkeypatch.setattr(web_app, "UPLOAD_ROOT", tmp_path / "runtime" / "web-references")
    monkeypatch.setattr(web_app, "JOB_DATABASE_PATH", tmp_path / "runtime" / "jobs.sqlite")
    root = web_app.UPLOAD_ROOT.parent
    root.mkdir(parents=True)
    image_path = root / "artifacts" / "candidate.png"
    image_path.parent.mkdir()
    Image.new("RGB", (2000, 2000), "blue").save(image_path)
    manager = web_app._ensure_job_store()
    artifact = Artifact.from_file(web_app.PROJECT_ID, "artifacts/candidate.png", root, kind="generated-image")
    manager.database.create_artifact(artifact)
    execution = GenerationExecutionRecord.create(web_app.PROJECT_ID, state="succeeded", artifact_ids=(artifact.id,), parameters={})
    manager.database.create_execution(execution)
    job = manager.create(project_id=web_app.PROJECT_ID, job_type="v2_generation", payload={"prompt": "test"})
    claimed = manager.claim(job.id, "test-worker")
    manager.complete(claimed.id, {"execution_id": execution.id, "artifact_ids": [artifact.id], "post_generation_verification": {"decision": "REVIEW"}})
    return TestClient(web_app.app), job.id


def test_delivery_requires_qa_then_approval_then_package(tmp_path, monkeypatch):
    client, job_id = _ready_job(tmp_path, monkeypatch)
    qa = client.post(f"/api/jobs/{job_id}/qa")
    assert qa.status_code == 200
    assert qa.json()["technical_qa"]["status"] in {"PASS", "WARN"}
    approved = client.post(f"/api/jobs/{job_id}/approve")
    assert approved.status_code == 200
    release = client.post(f"/api/jobs/{job_id}/release")
    assert release.status_code == 200
    assert release.json()["download_url"].endswith("/download")
    download = client.get(f"/api/jobs/{job_id}/download")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/zip"


def test_delivery_cannot_package_without_approval(tmp_path, monkeypatch):
    client, job_id = _ready_job(tmp_path, monkeypatch)
    assert client.post(f"/api/jobs/{job_id}/release").status_code == 409
