"""Configuration and workspace management for StockForge."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(slots=True)
class StockForgeConfig:
    """Persistent StockForge control-plane and project storage configuration."""

    workspace: Path
    database: Path
    project_root: Path | None = None

    def __post_init__(self) -> None:
        if self.project_root is None:
            self.project_root = self.workspace / "projects"

    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        return {key: str(value) for key, value in data.items()}


class ConfigManager:
    """Resolve and persist the global StockForge workspace and project storage."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or os.environ.get("STOCKFORGE_HOME", Path.home() / ".stockforge")).expanduser()
        self.config_file = self.root / "config.json"

    def load(self) -> StockForgeConfig:
        if not self.config_file.exists():
            workspace = self.root / "workspace"
            project_root = Path(
                os.environ.get("STOCKFORGE_PROJECT_ROOT", workspace / "projects")
            ).expanduser()
            return StockForgeConfig(
                workspace=workspace,
                database=self.root / "stockforge.db",
                project_root=project_root,
            )
        data = json.loads(self.config_file.read_text(encoding="utf-8"))
        workspace = Path(data["workspace"]).expanduser()
        project_root = Path(
            data.get("project_root", os.environ.get("STOCKFORGE_PROJECT_ROOT", workspace / "projects"))
        ).expanduser()
        return StockForgeConfig(
            workspace=workspace,
            database=Path(data["database"]).expanduser(),
            project_root=project_root,
        )

    def initialize(self) -> StockForgeConfig:
        config = self.load()
        self.root.mkdir(parents=True, exist_ok=True)
        config.workspace.mkdir(parents=True, exist_ok=True)
        config.project_root.mkdir(parents=True, exist_ok=True)
        (config.workspace / "assets").mkdir(parents=True, exist_ok=True)
        (config.workspace / "output").mkdir(parents=True, exist_ok=True)
        (config.workspace / "cache").mkdir(parents=True, exist_ok=True)
        (config.workspace / "logs").mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(config.to_dict(), indent=2) + "\n", encoding="utf-8")
        return config
