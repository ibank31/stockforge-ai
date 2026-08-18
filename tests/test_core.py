from pathlib import Path

import pytest
from typer.testing import CliRunner

from stockforge.cli import app
from stockforge.manifest import ManifestError, ProjectManifest


def test_init_and_project_create(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    runner = CliRunner()

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output

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
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
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
