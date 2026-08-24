import json
import zipfile
from pathlib import Path
from uuid import uuid4

import pytest
from typer.testing import CliRunner

from stockforge.artifact import Artifact
from stockforge.cli import app
from stockforge.database import Database
from stockforge.execution_record import GenerationExecutionRecord
from stockforge.portfolio_io import PortfolioPlanError, load_project_plan, portfolio_snapshot, select_brief
from stockforge.release_package import build_release_package


runner = CliRunner()


def _portfolio_context() -> dict[str, object]:
    return {
        "schema_version": 1,
        "batch_id": "batch-001",
        "plan_file": "batch-001.json",
        "brief_id": "ai_governance--review-gate",
        "lane_key": "ai_governance",
        "lane_name": "AI governance visual systems",
        "tier": "first",
        "evidence_confidence": "medium",
        "metadata": {
            "title": "AI governance visual system: review gate",
            "keywords": ["AI governance", "responsible AI", "AI oversight"],
            "created_using_generative_ai": True,
            "people_or_property": "none depicted; human review required to confirm",
            "status": "human_review_required",
            "human_review_required": True,
        },
        "reviewer_checklist": ["Confirm visible metadata accuracy."],
        "human_review_required": True,
    }


def test_portfolio_release_package_includes_metadata_worksheet_and_review_checklist(tmp_path: Path):
    project_id = str(uuid4())
    project_root = tmp_path / "project"
    image_path = project_root / "artifacts" / "candidate.png"
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"png-bytes")
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project(project_id, "demo", project_root)
    artifact = Artifact.from_file(project_id, "artifacts/candidate.png", project_root, kind="generated-image")
    database.create_artifact(artifact)
    execution = GenerationExecutionRecord.create(
        project_id,
        state="succeeded",
        operation="image.generate",
        provider_id="zerogpu",
        artifact_ids=(artifact.id,),
        parameters={"profile": "z-image-turbo", "portfolio": _portfolio_context()},
    )
    database.create_execution(execution)

    package = build_release_package(
        database=database,
        project_id=project_id,
        project_root=project_root,
        execution_id=execution.id,
    )

    with zipfile.ZipFile(package.path) as archive:
        assert sorted(archive.namelist()) == [
            "README.txt",
            "REVIEW_CHECKLIST.md",
            "TECHNICAL_READINESS.json",
            f"images/{artifact.id}.png",
            "manifest.json",
            "portfolio_metadata_draft.csv",
            "portfolio_metadata_draft.json",
        ]
        manifest = json.loads(archive.read("manifest.json"))
        metadata = json.loads(archive.read("portfolio_metadata_draft.json"))
        worksheet = archive.read("portfolio_metadata_draft.csv").decode("utf-8")
        checklist = archive.read("REVIEW_CHECKLIST.md").decode("utf-8")
        technical = json.loads(archive.read("TECHNICAL_READINESS.json"))

    assert manifest["portfolio"]["brief_id"] == "ai_governance--review-gate"
    assert metadata["created_using_generative_ai"] is True
    assert "AI governance" in worksheet
    assert "review_ready" in checklist
    assert "submission" in checklist
    assert technical[0]["artifact_id"] == artifact.id
    assert technical[0]["report"]["ready"] is False


def test_saved_plan_cannot_be_loaded_from_another_project(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    plan = first / "portfolio-plans" / "plan.json"
    plan.parent.mkdir(parents=True)
    second.mkdir()
    plan.write_text("{}", encoding="utf-8")

    with pytest.raises(PortfolioPlanError, match="inside this project's"):
        load_project_plan(second, plan)


def test_portfolio_show_and_generate_dry_run_from_saved_plan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0
    assert runner.invoke(
        app,
        ["provider", "configure", "--id", "zerogpu", "--endpoint", "https://example.invalid"],
    ).exit_code == 0
    created = runner.invoke(
        app,
        ["portfolio", "create-batch", "--project", "demo", "--lane", "ai_governance", "--count", "1"],
    )
    assert created.exit_code == 0, created.output
    batch = json.loads(created.output)
    brief = batch["brief_ids"][0]

    shown = runner.invoke(
        app,
        ["portfolio", "show", "--project", "demo", "--plan", batch["path"], "--brief", brief],
    )
    assert shown.exit_code == 0, shown.output
    assert json.loads(shown.output)["brief"]["brief_id"] == brief

    preview = runner.invoke(
        app,
        [
            "portfolio", "generate", "--project", "demo", "--plan", batch["path"], "--brief", brief,
            "--provider", "zerogpu", "--dry-run",
        ],
    )
    assert preview.exit_code == 0, preview.output
    output = json.loads(preview.output)
    assert output["dry_run"] is True
    assert output["portfolio"]["brief_id"] == brief
    assert output["portfolio"]["human_review_required"] is True


def test_portfolio_snapshot_freezes_selected_brief_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0
    created = runner.invoke(
        app,
        ["portfolio", "create-batch", "--project", "demo", "--lane", "tactile_material_atmospheres", "--count", "1"],
    )
    batch = json.loads(created.output)
    project_root = Path(batch["path"]).parents[1]
    path, plan = load_project_plan(project_root, batch["path"])
    selected = select_brief(plan, batch["brief_ids"][0])
    snapshot = portfolio_snapshot(plan, selected, path)

    assert snapshot["batch_id"] == batch["batch_id"]
    assert snapshot["metadata"]["created_using_generative_ai"] is True
    assert snapshot["human_review_required"] is True
