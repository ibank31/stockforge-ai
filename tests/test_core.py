from pathlib import Path

import pytest
from typer.testing import CliRunner

from stockforge.asset import Asset, AssetError, checksum_file, validate_relative_path
from stockforge.asset_manager import AssetManager
from stockforge.cli import app
from stockforge.config import ConfigManager
from stockforge.database import Database
from stockforge.manifest import ManifestError, ProjectManifest


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
    project_id = "1c4d2f42-9b13-4d57-bf7d-8b5f0b0f1a10"
    project_path = config.workspace / "projects" / "demo"
    project_path.mkdir(parents=True)
    database.create_project(project_id, "demo", project_path)
    source = project_path / "assets" / "sample.txt"
    source.parent.mkdir()
    source.write_bytes(b"stockforge")

    asset = Asset.from_file(
        asset_id="f0d3c2b1-a4e5-4f67-8a90-123456789abc",
        project_id=project_id,
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
    assert database.list_assets(project_id)[0].id == saved.id


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
    project_id = "1c4d2f42-9b13-4d57-bf7d-8b5f0b0f1a11"
    project_path = config.workspace / "projects" / "demo"
    project_path.mkdir(parents=True)
    database.create_project(project_id, "demo", project_path)
    assets = AssetManager(config, database)
    assets.create("demo", "same-name")
    with pytest.raises(AssetError, match="same name or relative path"):
        assets.create("demo", "same-name")
