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


class _FourXUpscaler:
    provider_id = "test-upscaler"
    model_id = "test-x4"

    def healthcheck(self) -> bool:
        return True

    def upscale(self, request):
        from PIL import Image
        from stockforge.upscaler import UpscaleReport

        with Image.open(request.source) as source:
            source.load()
            width, height = source.size
            output = source.convert("RGB").resize((width * 4, height * 4))
        request.destination.parent.mkdir(parents=True, exist_ok=True)
        output.save(request.destination, format="PNG")
        return UpscaleReport(
            source_path=str(request.source),
            output_path=str(request.destination),
            provider_id=self.provider_id,
            model_id=self.model_id,
            scale=4,
            source_width=width,
            source_height=height,
            output_width=width * 4,
            output_height=height * 4,
        )


def test_master_candidate_is_registered_with_lineage_and_packaged(tmp_path: Path):
    from PIL import Image
    from stockforge.master_finalizer import finalize_master_candidate
    from stockforge.master_registry import register_master_candidate

    project_id = str(uuid4())
    project_root = tmp_path / "project"
    source_path = project_root / "artifacts" / "preview.webp"
    source_path.parent.mkdir(parents=True)
    Image.new("RGB", (1024, 1024), (25, 50, 90)).save(source_path, format="WEBP")

    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project(project_id, "demo", project_root)
    source_artifact = Artifact.from_file(project_id, "artifacts/preview.webp", project_root, kind="generated-image")
    database.create_artifact(source_artifact)
    source_execution = GenerationExecutionRecord.create(
        project_id,
        state="succeeded",
        operation="image.generate",
        provider_id="zerogpu",
        artifact_ids=(source_artifact.id,),
        parameters={"portfolio": _portfolio_context()},
    )
    database.create_execution(source_execution)

    report = finalize_master_candidate(
        source=source_path,
        destination=project_root / "masters" / "candidate.jpg",
        upscaler=_FourXUpscaler(),
    )
    master, execution = register_master_candidate(
        database=database,
        project_id=project_id,
        project_root=project_root,
        source_artifact=source_artifact,
        source_execution=source_execution,
        report=report,
    )
    package = build_release_package(
        database=database,
        project_id=project_id,
        project_root=project_root,
        execution_id=execution.id,
    )

    lineage = database.list_lineage(artifact_id=master.id)
    provenance = database.list_provenance(artifact_id=master.id)
    with zipfile.ZipFile(package.path) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("manifest.json"))
        technical = json.loads(archive.read("TECHNICAL_READINESS.json"))
        master_finalization = json.loads(archive.read("MASTER_FINALIZATION.json"))

    assert master.kind == "finalized-master"
    assert lineage[0].parent_artifact_id == source_artifact.id
    assert lineage[0].relation == "upscaled"
    assert provenance[0].operation == "image.upscale_and_finalize"
    assert f"masters/{master.id}.jpg" in names
    assert "MASTER_FINALIZATION.json" in names
    assert manifest["status"] == "review_ready"
    assert technical[0]["report"]["ready"] is True
    assert master_finalization["quality_state"] == "visual_review_required"


def test_portfolio_prepare_master_creates_lineage_bound_no_gpu_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from PIL import Image
    from stockforge.config import ConfigManager

    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0

    config = ConfigManager().load()
    database = Database(config.database)
    database.initialize()
    project = next(item for item in database.list_projects() if item["name"] == "demo")
    project_root = Path(project["path"])
    source_path = project_root / "artifacts" / "preview.webp"
    source_path.parent.mkdir(parents=True)
    Image.new("RGB", (1024, 1024), (10, 20, 30)).save(source_path, format="WEBP")
    source = Artifact.from_file(project["id"], "artifacts/preview.webp", project_root, kind="generated-image")
    database.create_artifact(source)
    execution = GenerationExecutionRecord.create(
        project["id"],
        state="succeeded",
        operation="image.generate",
        artifact_ids=(source.id,),
        parameters={"portfolio": _portfolio_context()},
    )
    database.create_execution(execution)

    result = runner.invoke(
        app,
        [
            "portfolio", "prepare-master", "--project", "demo", "--execution", execution.id,
            "--minimum-megapixels", "6", "--scale", "4",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    request = json.loads(Path(payload["path"]).read_text(encoding="utf-8"))

    assert request["status"] == "prepared_no_gpu"
    assert request["source"]["artifact_id"] == source.id
    assert request["target"]["expected_megapixels"] > 6
    assert request["human_review_required"] is True
