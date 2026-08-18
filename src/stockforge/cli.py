"""StockForge command line interface."""

from __future__ import annotations

import json

import typer

from . import __version__
from .asset import ASSET_TYPES, AssetError
from .asset_manager import AssetManager
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .job import JobError
from .job_database import JobDatabase
from .job_manager import JobManager
from .project import ProjectManager

app = typer.Typer(help="StockForge AI — digital asset production automation.")
project_app = typer.Typer(help="Manage StockForge projects.")
asset_app = typer.Typer(help="Register and inspect project assets.")
job_app = typer.Typer(help="Create and operate persistent jobs.")
app.add_typer(project_app, name="project")
app.add_typer(asset_app, name="asset")
app.add_typer(job_app, name="job")


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


def _job_manager() -> tuple[ConfigManager, object, JobManager]:
    manager = ConfigManager()
    config = manager.load()
    database = JobDatabase(config.database)
    database.initialize()
    return manager, config, JobManager(database)


def _project_id(project_name: str) -> str:
    _, _, database, _ = _initialized()
    projects = [item for item in database.list_projects() if item["name"] == project_name]
    if not projects:
        raise JobError(f"Project not found: {project_name}")
    return projects[0]["id"]


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


@job_app.command("create")
def job_create(
    project: str = typer.Option(..., "--project", "-p", help="Project name."),
    job_type: str = typer.Option(..., "--type", help="Job type identifier."),
    payload: str = typer.Option("{}", "--payload", help="JSON object payload."),
    priority: int = typer.Option(0, "--priority"),
    max_attempts: int = typer.Option(3, "--max-attempts"),
) -> None:
    """Enqueue a persistent job."""
    try:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise JobError("payload must be a JSON object.")
        job = _job_manager()[2].create(
            project_id=_project_id(project),
            job_type=job_type,
            payload=data,
            priority=priority,
            max_attempts=max_attempts,
        )
    except (json.JSONDecodeError, JobError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Created job: {job.id}")
    typer.echo(f"Status: {job.status}")
    typer.echo(f"Priority: {job.priority}")


@job_app.command("list")
def job_list(
    project: str | None = typer.Option(None, "--project", "-p", help="Filter by project."),
    status: str | None = typer.Option(None, "--status", help="Filter by status."),
) -> None:
    """List persistent jobs."""
    try:
        project_id = _project_id(project) if project else None
        jobs = _job_manager()[2].list(project_id=project_id, status=status)
    except JobError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not jobs:
        typer.echo("No jobs.")
        raise typer.Exit()
    for job in jobs:
        typer.echo(f"{job.id}\t{job.job_type}\t{job.status}\tp{job.priority}\tattempts={job.attempts}/{job.max_attempts}")


@job_app.command("claim")
def job_claim(
    worker: str = typer.Option(..., "--worker", help="Worker identifier."),
) -> None:
    """Atomically claim the highest-priority available job."""
    try:
        job = _job_manager()[2].claim_next(worker)
    except JobError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if job is None:
        typer.echo("No queued jobs available.")
        raise typer.Exit()
    typer.echo(f"Claimed job: {job.id}")
    typer.echo(f"Type: {job.job_type}")
    typer.echo(f"Attempt: {job.attempts}/{job.max_attempts}")


@job_app.command("complete")
def job_complete(
    job_id: str = typer.Argument(...),
    result: str = typer.Option("{}", "--result", help="JSON object result."),
) -> None:
    """Mark a running job as succeeded."""
    try:
        data = json.loads(result)
        if not isinstance(data, dict):
            raise JobError("result must be a JSON object.")
        job = _job_manager()[2].complete(job_id, data)
    except (json.JSONDecodeError, JobError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Completed job: {job.id}")


@job_app.command("fail")
def job_fail(
    job_id: str = typer.Argument(...),
    error: str = typer.Option(..., "--error"),
    retry_delay: int = typer.Option(0, "--retry-delay", min=0),
) -> None:
    """Fail a running job and retry while attempts remain."""
    try:
        job = _job_manager()[2].fail(job_id, error, retry_delay)
    except JobError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Job {job.id}: {job.status} ({job.attempts}/{job.max_attempts})")


@job_app.command("cancel")
def job_cancel(job_id: str = typer.Argument(...)) -> None:
    """Cancel a queued or running job."""
    try:
        job = _job_manager()[2].cancel(job_id)
    except JobError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Cancelled job: {job.id}")


if __name__ == "__main__":
    app()
