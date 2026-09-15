from pathlib import Path

from stockforge.job_database import JobDatabase
from stockforge.job_manager import JobManager
from stockforge.workflow_control import WorkflowControl


def test_workflow_persists_events_and_detects_stuck(monkeypatch, tmp_path: Path):
    db = JobDatabase(tmp_path / "jobs.sqlite")
    db.initialize()
    control = WorkflowControl(db)
    control.initialize()
    workflow = control.create("ref-1")
    control.event(workflow["id"], stage="QUEUED", message="queued")
    snapshot = control.get(workflow["id"])
    assert snapshot["current_stage"] == "QUEUED"
    assert snapshot["events"][-1]["message"] == "queued"
    monkeypatch.setenv("STOCKFORGE_STUCK_SECONDS", "30")
    with db.connect() as conn:
        conn.execute(
            "UPDATE workflows SET updated_at = datetime('now', '-90 seconds') WHERE id = ?",
            (workflow["id"],),
        )
    assert control.get(workflow["id"])["stuck"] is True


def test_job_links_to_workflow(tmp_path: Path):
    db = JobDatabase(tmp_path / "jobs.sqlite")
    db.initialize()
    control = WorkflowControl(db)
    control.initialize()
    workflow = control.create("ref-2")

    # jobs.project_id is intentionally a real foreign key. The test must create
    # the owning project just like the browser API does before enqueueing work.
    project_id = "00000000-0000-0000-0000-000000000001"
    db.create_project(project_id, "workflow-test", tmp_path / "workflow-test")

    manager = JobManager(db)
    job = manager.create(
        project_id=project_id,
        job_type="v2_generation",
        payload={"prompt": "x", "parameters": {"workflow_id": workflow["id"]}},
    )
    assert control.snapshot_for_job(job)["id"] == workflow["id"]
