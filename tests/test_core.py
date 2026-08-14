from pathlib import Path

from typer.testing import CliRunner

from stockforge.cli import app


def test_init_and_project_create(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    runner = CliRunner()

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(app, ["project", "create", "demo"])
    assert result.exit_code == 0, result.stdout
    assert "Created project: demo" in result.stdout

    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0, result.stdout
    assert "demo" in result.stdout


def test_version():
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "StockForge AI" in result.stdout
