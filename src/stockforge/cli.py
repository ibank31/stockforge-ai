"""StockForge command line interface."""

from __future__ import annotations

import typer

from . import __version__
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .project import ProjectManager

app = typer.Typer(help="StockForge AI — digital asset production automation.")
project_app = typer.Typer(help="Manage StockForge projects.")
app.add_typer(project_app, name="project")


def _initialized() -> tuple[ConfigManager, object, Database, ProjectManager]:
    manager = ConfigManager()
    config = manager.load()
    database = Database(config.database)
    database.initialize()
    return manager, config, database, ProjectManager(config, database)


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


if __name__ == "__main__":
    app()
