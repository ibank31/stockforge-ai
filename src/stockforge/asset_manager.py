"""Asset registry service."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from .asset import Asset, AssetError
from .config import StockForgeConfig
from .database import Database


class AssetManager:
    """Coordinates asset validation, filesystem inspection, and persistence."""

    def __init__(self, config: StockForgeConfig, database: Database) -> None:
        self.config = config
        self.database = database

    def create(
        self,
        project_name: str,
        name: str,
        asset_type: str = "image",
        relative_path: str | None = None,
        source: str = "manual",
    ) -> Asset:
        projects = [item for item in self.database.list_projects() if item["name"] == project_name]
        if not projects:
            raise AssetError(f"Project not found: {project_name}")
        project = projects[0]
        project_root = Path(project["path"]).resolve()

        asset_id = str(uuid4())
        if relative_path:
            asset = Asset.from_file(
                asset_id=asset_id,
                project_id=project["id"],
                name=name,
                project_root=project_root,
                file_path=project_root / relative_path,
                asset_type=asset_type,
                source=source,
            )
        else:
            asset = Asset(
                id=asset_id,
                project_id=project["id"],
                name=name,
                asset_type=asset_type,
                source=source,
            )

        try:
            return self.database.create_asset(asset)
        except sqlite3.IntegrityError as exc:
            raise AssetError(
                "An asset with the same name or relative path already exists in this project."
            ) from exc

    def list(self, project_name: str | None = None) -> list[Asset]:
        if project_name is None:
            return self.database.list_assets()
        projects = [item for item in self.database.list_projects() if item["name"] == project_name]
        if not projects:
            raise AssetError(f"Project not found: {project_name}")
        return self.database.list_assets(projects[0]["id"])
