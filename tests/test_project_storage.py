from pathlib import Path

from stockforge.config import ConfigManager
from stockforge.database import Database
from stockforge.project import ProjectManager


def test_project_root_defaults_to_workspace_projects(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / ".stockforge"))
    config = ConfigManager().initialize()
    assert config.project_root == config.workspace / "projects"


def test_project_root_can_be_configured_for_android_shared_storage(tmp_path: Path, monkeypatch):
    home = tmp_path / ".stockforge"
    project_root = tmp_path / "shared" / "StockForge" / "projects"
    monkeypatch.setenv("STOCKFORGE_HOME", str(home))
    monkeypatch.setenv("STOCKFORGE_PROJECT_ROOT", str(project_root))

    manager = ConfigManager()
    config = manager.initialize()
    database = Database(config.database)
    database.initialize()

    project = ProjectManager(config, database).create("commercial-stock")
    assert Path(project["path"]) == project_root / "commercial-stock"
    assert (project_root / "commercial-stock" / "project.json").exists()
    assert (project_root / "commercial-stock" / "assets").is_dir()
    assert (project_root / "commercial-stock" / "output").is_dir()


def test_project_root_persists_in_config(tmp_path: Path, monkeypatch):
    home = tmp_path / ".stockforge"
    project_root = tmp_path / "shared" / "StockForge" / "projects"
    monkeypatch.setenv("STOCKFORGE_HOME", str(home))
    monkeypatch.setenv("STOCKFORGE_PROJECT_ROOT", str(project_root))

    first = ConfigManager()
    config = first.initialize()
    assert config.project_root == project_root

    monkeypatch.delenv("STOCKFORGE_PROJECT_ROOT")
    loaded = ConfigManager(home).load()
    assert loaded.project_root == project_root
