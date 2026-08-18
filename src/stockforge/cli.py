"""StockForge command line interface."""

from __future__ import annotations

import typer

from . import __version__
from .asset import ASSET_TYPES, AssetError
from .asset_manager import AssetManager
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .project import ProjectManager

app = typer.Typer(help="StockForge AI — digital asset production automation.")
project_app = typer.Typer(help="Manage StockForge projects.")
asset_app = typer.Typer(help="Register and inspect project assets.")
app.add_typer(project_app, name="project")
app.add_typer(asset_app, name="asset")


def _initialized() -> tuple[ConfigManager, object, Database, ProjectManager]:
    manager = ConfigManager()
    config = manager.load()
    database = Database(config.database)
    database.initialize()
    return manager, config, database, ProjectManager(config, database)


def _asset_manager() -> AssetManager:
    manager = ConfigManager()
    config = manager.load()
    database = Database(config.database)
    database.initialize()
    return AssetManager(config, database)


@app.command()
def version() -> None:
    """Show StockForge version."""
    typer.echo(f"StockForge AI {__version__}")


@app.command()
def init() -> None:
    """Initialize the global StockForge workspace."""
    manager = ConfigManager()
    config = manager.initialize()
    Database(config.database).initialize()
    typer.echo(f"Initialized StockForge workspace: {manager.root}")


@app.command()
def doctor() -> None:
    """Check the local environment."""
    checks = run_doctor()
    for check in checks:
        icon = "OK" if check.ok else "FAIL"
        typer.echo(f"[{icon}] {check.name}: {check.detail}")
    raise typer.Exit(code=0 if all(check.ok for check in checks) else 1)


@project_app.command("create")
def project_create(name: str) -> None:
    """Create a new project."""
    try:
        _, _, _, projects = _initialized()
        project = projects.create(name)
    except (ValueError, FileExistsError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Created project: {project['name']}")
    typer.echo(f"Path: {project['path']}")


@project_app.command("list")
def project_list() -> None:
    """List projects."""
    _, _, _, projects = _initialized()
    items = projects.list()
    if not items:
        typer.echo("No projects.")
        raise typer.Exit()
    for item in items:
        typer.echo(f"{item['name']}\t{item['status']}\t{item['path']}")


@asset_app.command("create")
def asset_create(
    project: str = typer.Option(..., "--project", "-p", help="Project name."),
    name: str = typer.Option(..., "--name", "-n", help="Asset name."),
    asset_type: str = typer.Option("image", "--type", help="Asset type."),
    path: str | None = typer.Option(None, "--path", help="Path relative to the project root."),
    source: str = typer.Option("manual", "--source", help="Asset source identifier."),
) -> None:
    """Register an asset in the project registry."""
    if asset_type not in ASSET_TYPES:
        raise typer.BadParameter(f"Unsupported asset type: {asset_type}")
    try:
        asset = _asset_manager().create(
            project_name=project,
            name=name,
            asset_type=asset_type,
            relative_path=path,
            source=source,
        )
    except AssetError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Registered asset: {asset.id}")
    typer.echo(f"Project: {project}")
    typer.echo(f"Status: {asset.status}")
    if asset.relative_path:
        typer.echo(f"Path: {asset.relative_path}")
    if asset.checksum_sha256:
        typer.echo(f"SHA-256: {asset.checksum_sha256}")


@asset_app.command("list")
def asset_list(
    project: str | None = typer.Option(None, "--project", "-p", help="Filter by project name."),
) -> None:
    """List registered assets."""
    try:
        assets = _asset_manager().list(project)
    except AssetError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not assets:
        typer.echo("No assets.")
        raise typer.Exit()
    for asset in assets:
        path = asset.relative_path or "-"
        typer.echo(f"{asset.id}\t{asset.name}\t{asset.asset_type}\t{asset.status}\t{path}")


if __name__ == "__main__":
    app()
