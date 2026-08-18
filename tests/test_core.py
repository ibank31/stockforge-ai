from pathlib import Path

import pytest
from typer.testing import CliRunner

from stockforge.asset import Asset, AssetError, checksum_file, validate_relative_path
from stockforge.asset_manager import AssetManager
from stockforge.cli import app
from stockforge.config import ConfigManager
from stockforge.database import Database
from stockforge.job import Job, JobError
from stockforge.job_database import JobDatabase
from stockforge.job_manager import JobManager
from stockforge.manifest import ManifestError, ProjectManifest


PROJECT_ID = "1c4d2f42-9b13-4d57-bf7d-8b5f0b0f1a10"


def test_init_and_project_create(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    runner = CliRunner()
    assert runner.invoke(app, ["init"]).exit_code == 0

    result = runner.invoke(app, ["project", "create", "demo"])
    assert result.exit_code == 0, result.output
    assert "Created project: demo" in result.output

    manifest = ProjectManifest.read(tmp_path / ".stockforge" / "workspace" / "projects" / "demo" / "project.json")
    assert manifest.name == "demo"
    assert manifest.version == 1
    assert manifest.schema_version == 1
    assert manifest.id

    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0, result.output
    assert "demo" in result.output


def test_version():
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "StockForge AI" in result.output


def test_manifest_rejects_missing_fields():
    with pytest.raises(ManifestError, match="missing fields"):
        ProjectManifest.from_dict({"name": "demo"})


def test_manifest_rejects_unknown_schema():
    with pytest.raises(ManifestError, match="Unsupported project manifest schema"):
        ProjectManifest.from_dict(
            {
                "schema_version": 999,
                "id": "demo-id",
                "name": "demo",
                "version": 1,
                "created_at": "2026-08-18T00:00:00Z",
                "metadata": {},
            }
        )


def test_project_name_validation(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    runner = CliRunner()
    assert runner.invoke(app, ["init"]).exit_code == 0
    result = runner.invoke(app, ["project", "create", "bad name"])
    assert result.exit_code != 0
    assert "Project name must be" in result.output


def test_asset_registry_create_and_list(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    runner = CliRunner()
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0

    result = runner.invoke(
        app,
        ["asset", "create", "--project", "demo", "--name", "hero-image", "--type", "image"],
    )
    assert result.exit_code == 0, result.output
    assert "Registered asset:" in result.output
    assert "Status: registered" in result.output

    result = runner.invoke(app, ["asset", "list", "--project", "demo"])
    assert result.exit_code == 0, result.output
    assert "hero-image" in result.output


def test_asset_file_registration_calculates_checksum(tmp_path: Path):
    manager = ConfigManager(tmp_path / ".stockforge")
    config = manager.initialize()
    database = Database(config.database)
    database.initialize()
    project_path = config.workspace / "projects" / "demo"
    project_path.mkdir(parents=True)
    database.create_project(PROJECT_ID, "demo", project_path)
    source = project_path / "assets" / "sample.txt"
    source.parent.mkdir()
    source.write_bytes(b"stockforge")

    asset = Asset.from_file(
        asset_id="f0d3c2b1-a4e5-4f67-8a90-123456789abc",
        project_id=PROJECT_ID,
        name="sample",
        project_root=project_path,
        file_path=source,
        asset_type="document",
    )
    saved = database.create_asset(asset)
    assert saved.relative_path == "assets/sample.txt"
    assert saved.size_bytes == 10
    assert saved.checksum_sha256 == checksum_file(source)
    assert len(saved.checksum_sha256) == 64
    assert database.list_assets(PROJECT_ID)[0].id == saved.id


def test_asset_path_must_stay_inside_project():
    with pytest.raises(AssetError, match="cannot contain '..'"):
        validate_relative_path("../outside.png")
    with pytest.raises(AssetError, match="relative"):
        validate_relative_path("/absolute/path.png")


def test_asset_manager_rejects_unknown_project(tmp_path: Path):
    manager = ConfigManager(tmp_path / ".stockforge")
    config = manager.initialize()
    database = Database(config.database)
    database.initialize()
    with pytest.raises(AssetError, match="Project not found"):
        AssetManager(config, database).create(project_name="missing", name="asset")


def test_asset_duplicate_name_is_rejected(tmp_path: Path):
    manager = ConfigManager(tmp_path / ".stockforge")
    config = manager.initialize()
    database = Database(config.database)
    database.initialize()
    project_path = config.workspace / "projects" / "demo"
    project_path.mkdir(parents=True)
    database.create_project(PROJECT_ID, "demo", project_path)
    assets = AssetManager(config, database)
    assets.create("demo", "same-name")
    with pytest.raises(AssetError, match="same name or relative path"):
        assets.create("demo", "same-name")


def make_job_database(tmp_path: Path) -> tuple[JobDatabase, str]:
    manager = ConfigManager(tmp_path / ".stockforge")
    config = manager.initialize()
    database = JobDatabase(config.database)
    database.initialize()
    project_path = config.workspace / "projects" / "demo"
    project_path.mkdir(parents=True)
    database.create_project(PROJECT_ID, "demo", project_path)
    return database, PROJECT_ID


def test_job_create_claim_and_complete(tmp_path: Path):
    database, project_id = make_job_database(tmp_path)
    manager = JobManager(database)
    low = manager.create(project_id=project_id, job_type="low", priority=1, payload={"x": 1})
    high = manager.create(project_id=project_id, job_type="high", priority=10, payload={"x": 2})

    claimed = manager.claim_next("worker-a")
    assert claimed is not None
    assert claimed.id == high.id
    assert claimed.status == "running"
    assert claimed.attempts == 1
    assert claimed.worker_id == "worker-a"

    completed = manager.complete(claimed.id, {"asset_id": "abc"})
    assert completed.status == "succeeded"
    assert completed.result == {"asset_id": "abc"}

    second = manager.claim_next("worker-a")
    assert second is not None
    assert second.id == low.id
    assert manager.claim_next("worker-a") is None


def test_job_retry_then_terminal_failure(tmp_path: Path):
    database, project_id = make_job_database(tmp_path)
    manager = JobManager(database)
    job = manager.create(project_id=project_id, job_type="unstable", max_attempts=2)

    first = manager.claim_next("worker-a")
    assert first is not None and first.id == job.id
    retry = manager.fail(job.id, "temporary failure", retry_delay_seconds=0)
    assert retry.status == "queued"
    assert retry.attempts == 1
    assert retry.error == "temporary failure"

    second = manager.claim_next("worker-b")
    assert second is not None and second.attempts == 2
    terminal = manager.fail(job.id, "permanent failure")
    assert terminal.status == "failed"
    assert terminal.finished_at is not None
    assert manager.claim_next("worker-c") is None


def test_job_cancel_and_invalid_transitions(tmp_path: Path):
    database, project_id = make_job_database(tmp_path)
    manager = JobManager(database)
    job = manager.create(project_id=project_id, job_type="cancel-me")

    cancelled = manager.cancel(job.id)
    assert cancelled.status == "cancelled"
    with pytest.raises(JobError, match="Only queued or running jobs"):
        manager.cancel(job.id)
    with pytest.raises(JobError, match="Only a running job"):
        manager.complete(job.id)


def test_job_model_rejects_non_json_payload():
    with pytest.raises(JobError, match="JSON-serializable"):
        Job(
            id="f0d3c2b1-a4e5-4f67-8a90-123456789abc",
            project_id=PROJECT_ID,
            job_type="test",
            payload={"bad": object()},
        )


def test_job_cli_create_list_claim(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    runner = CliRunner()
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0

    result = runner.invoke(
        app,
        [
            "job", "create", "--project", "demo", "--type", "image.generate",
            "--payload", '{"prompt":"house"}', "--priority", "5",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Created job:" in result.output

    result = runner.invoke(app, ["job", "list", "--project", "demo"])
    assert result.exit_code == 0, result.output
    assert "image.generate" in result.output

    result = runner.invoke(app, ["job", "claim", "--worker", "termux-01"])
    assert result.exit_code == 0, result.output
    assert "Claimed job:" in result.output
