"""StockForge command line interface."""

from __future__ import annotations

import json
import socket
from pathlib import Path

import typer

from . import __version__
from .adobe_finalize import AdobeFinalizationError, finalize_image
from .adobe_gate import inspect_image
from .asset import ASSET_TYPES, AssetError
from .asset_manager import AssetManager
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .job import JobError
from .job_database import JobDatabase
from .job_manager import JobManager
from .kaggle_worker import KaggleWorkerError, doctor as kaggle_doctor, list_kernels, push as kaggle_push, quota as kaggle_quota, remote as kaggle_remote, validate_local
from .project import ProjectManager
from .provider_config import ProviderConfigError
from .provider_orchestration import ProviderRoutingError
from .recovery_orchestrator import RecoveryGenerationOrchestrator
from .release_package import build_release_package
from .termux_control import (
    TermuxControlError,
    configure_remote_provider,
    profile_for,
    provider_names,
    route_remote_generation,
)

app = typer.Typer(help="StockForge AI — digital asset production automation.")
project_app = typer.Typer(help="Manage StockForge projects.")
asset_app = typer.Typer(help="Register and inspect project assets.")
job_app = typer.Typer(help="Create and operate persistent jobs.")
adobe_app = typer.Typer(help="Adobe Stock readiness checks.")
kaggle_app = typer.Typer(help="Control the Kaggle GPU worker without a browser.")
provider_app = typer.Typer(help="Configure remote GPU workers for Termux-controlled generation.")
app.add_typer(project_app, name="project")
app.add_typer(asset_app, name="asset")
app.add_typer(job_app, name="job")
app.add_typer(adobe_app, name="adobe")
app.add_typer(kaggle_app, name="kaggle")
app.add_typer(provider_app, name="provider")


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


@provider_app.command("configure")
def provider_configure(
    provider_id: str = typer.Option(..., "--id"),
    endpoint: str = typer.Option(..., "--endpoint"),
    profile: str = typer.Option("qwen-image", "--profile"),
    secret_env: str | None = typer.Option(None, "--secret-env"),
    timeout_seconds: int = typer.Option(300, "--timeout-seconds", min=1),
    score: float = typer.Option(0.0, "--score"),
) -> None:
    """Register one remote worker without persisting its secret value."""
    try:
        manager = ConfigManager()
        config = manager.initialize()
        provider = configure_remote_provider(
            workspace=config.workspace,
            provider_id=provider_id,
            endpoint=endpoint,
            secret_env=secret_env,
            timeout_seconds=timeout_seconds,
            profile_names=(profile,),
            score=score,
        )
    except (TermuxControlError, ProviderConfigError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Configured provider: {provider.provider_id}")
    typer.echo(f"Endpoint: {provider.endpoint}")
    typer.echo(f"Profile: {profile}")
    typer.echo(f"Secret environment variable: {provider.secret_env or '-'}")


@provider_app.command("list")
def provider_list() -> None:
    """List configured remote workers without exposing secret values."""
    config = ConfigManager().load()
    names = provider_names(config.workspace)
    if not names:
        typer.echo("No remote providers configured.")
        raise typer.Exit()
    for name in names:
        typer.echo(name)


@app.command("generate")
def generate(
    project: str = typer.Option(..., "--project", "-p"),
    prompt: str = typer.Option(..., "--prompt"),
    provider: str | None = typer.Option(None, "--provider"),
    profile: str = typer.Option("qwen-image", "--profile"),
    seed: int | None = typer.Option(None, "--seed", min=0),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Submit exactly one bounded remote generation from the Termux control plane."""
    manager = ConfigManager()
    config = manager.initialize()
    database = JobDatabase(config.database)
    database.initialize()
    projects = [item for item in database.list_projects() if item["name"] == project]
    if not projects:
        raise typer.BadParameter(f"Project not found: {project}")
    project_record = projects[0]
    project_root = Path(project_record["path"]).resolve()

    try:
        request = profile_for(profile).request(prompt, seed=seed)
        candidate = route_remote_generation(
            workspace=config.workspace,
            request=request,
            output_dir=project_root / ".provider-output" / (provider or "auto"),
            provider_id=provider,
        )
    except (TermuxControlError, ProviderConfigError, ProviderRoutingError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    preview = {
        "project": project,
        "provider": candidate.capabilities.provider_id,
        "profile": profile,
        "model_id": request.model_id,
        "model_version": request.model_version,
        "width": request.width,
        "height": request.height,
        "steps": request.steps,
        "seed": request.seed,
        "batch_size": request.batch_size,
        "estimated_gpu_seconds": request.parameters["estimated_gpu_seconds"],
    }
    if dry_run:
        typer.echo(json.dumps({"dry_run": True, **preview}, indent=2))
        raise typer.Exit()

    jobs = JobManager(database)
    job = jobs.create(
        project_id=project_record["id"],
        job_type="image.generate",
        payload=request.to_dict(),
        max_attempts=1,
    )
    claimed = jobs.claim(job.id, f"termux:{socket.gethostname()}")
    orchestrator = RecoveryGenerationOrchestrator(
        database,
        project_id=project_record["id"],
        project_root=project_root,
        provider_root=candidate.provider.output_dir,
        provider=candidate.provider,
    )
    try:
        result = orchestrator.run(request, job_id=claimed.id)
        package = build_release_package(
            database=database,
            project_id=project_record["id"],
            project_root=project_root,
            execution_id=result.execution.id,
        )
        jobs.complete(
            claimed.id,
            {
                "execution_id": result.execution.id,
                "artifact_ids": list(result.execution.artifact_ids),
                "provider": candidate.capabilities.provider_id,
                "release_package": package.to_dict(),
            },
        )
    except Exception as exc:
        try:
            jobs.fail(claimed.id, str(exc), retry_delay_seconds=0)
        except JobError:
            pass
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(json.dumps({
        **preview,
        "job_id": claimed.id,
        "execution_id": result.execution.id,
        "artifact_ids": list(result.execution.artifact_ids),
        "release_package": package.to_dict(),
        "status": "review_ready",
    }, indent=2))


@adobe_app.command("check")
def adobe_check(path: str = typer.Argument(...), json_output: bool = typer.Option(False, "--json")) -> None:
    """Check a final image against deterministic Adobe technical requirements."""
    try:
        report = inspect_image(path)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc
    if json_output:
        typer.echo(json.dumps(report.to_dict(), indent=2))
    else:
        typer.echo(f"File: {report.path}")
        typer.echo(f"Format: {report.format or '-'}")
        typer.echo(f"Dimensions: {report.width or '-'} x {report.height or '-'}")
        typer.echo(f"Megapixels: {report.megapixels:.2f}" if report.megapixels is not None else "Megapixels: -")
        typer.echo(f"Size: {report.file_size_bytes} bytes")
        typer.echo(f"Mode: {report.color_mode or '-'}")
        typer.echo(f"ICC: {report.icc_profile or '-'}")
        typer.echo("")
        for check in report.checks:
            typer.echo(f"[{check.status}] {check.name}: {check.detail}")
        typer.echo("")
        typer.echo(f"SUBMISSION TECHNICAL GATE: {'PASS' if report.ready else 'NOT READY'}")
    raise typer.Exit(code=0 if report.ready else 1)


@adobe_app.command("finalize")
def adobe_finalize(source: str = typer.Argument(...), destination: str = typer.Argument(...), assume_srgb: bool = typer.Option(False, "--assume-srgb"), json_output: bool = typer.Option(False, "--json")) -> None:
    """Finalize a raster candidate as JPEG with an embedded sRGB profile."""
    try:
        report = finalize_image(source, destination, assume_srgb=assume_srgb)
    except AdobeFinalizationError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if json_output:
        typer.echo(json.dumps(report.to_dict(), indent=2))
    else:
        typer.echo(f"Source: {report.source_path}")
        typer.echo(f"Output: {report.output_path}")
        typer.echo(f"Dimensions: {report.width} x {report.height}")
        typer.echo(f"Megapixels: {report.megapixels:.2f}")
        typer.echo(f"JPEG quality: {report.jpeg_quality}")
        typer.echo(f"Subsampling: {report.subsampling}")
        typer.echo(f"Output size: {report.output_size_bytes} bytes")
        typer.echo(f"Source profile: {report.source_profile or 'none'}")
        typer.echo(f"Assumed sRGB: {'yes' if report.assumed_srgb else 'no'}")
        typer.echo("FINALIZATION: PASS")


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
def asset_create(project: str = typer.Option(..., "--project", "-p"), name: str = typer.Option(..., "--name", "-n"), asset_type: str = typer.Option("image", "--type"), path: str | None = typer.Option(None, "--path"), source: str = typer.Option("manual", "--source")) -> None:
    """Register an asset in the project registry."""
    if asset_type not in ASSET_TYPES:
        raise typer.BadParameter(f"Unsupported asset type: {asset_type}")
    try:
        asset = _asset_manager().create(project_name=project, name=name, asset_type=asset_type, relative_path=path, source=source)
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
def asset_list(project: str | None = typer.Option(None, "--project", "-p")) -> None:
    """List registered assets."""
    try:
        assets = _asset_manager().list(project)
    except AssetError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not assets:
        typer.echo("No assets.")
        raise typer.Exit()
    for asset in assets:
        typer.echo(f"{asset.id}\t{asset.name}\t{asset.asset_type}\t{asset.status}\t{asset.relative_path or '-'}")


@job_app.command("create")
def job_create(project: str = typer.Option(..., "--project", "-p"), job_type: str = typer.Option(..., "--type"), payload: str = typer.Option("{}", "--payload"), priority: int = typer.Option(0, "--priority"), max_attempts: int = typer.Option(3, "--max-attempts")) -> None:
    """Enqueue a persistent job."""
    try:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise JobError("payload must be a JSON object.")
        job = _job_manager()[2].create(project_id=_project_id(project), job_type=job_type, payload=data, priority=priority, max_attempts=max_attempts)
    except (json.JSONDecodeError, JobError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Created job: {job.id}")
    typer.echo(f"Status: {job.status}")
    typer.echo(f"Priority: {job.priority}")


@job_app.command("list")
def job_list(project: str | None = typer.Option(None, "--project", "-p"), status: str | None = typer.Option(None, "--status")) -> None:
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
def job_claim(worker: str = typer.Option(..., "--worker")) -> None:
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
def job_complete(job_id: str = typer.Argument(...), result: str = typer.Option("{}", "--result")) -> None:
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
def job_fail(job_id: str = typer.Argument(...), error: str = typer.Option(..., "--error"), retry_delay: int = typer.Option(0, "--retry-delay", min=0)) -> None:
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


@kaggle_app.command("test")
def kaggle_test() -> None:
    """Validate Kaggle metadata/notebook locally. Never pushes or uses GPU."""
    try:
        info = validate_local()
    except KaggleWorkerError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo("KAGGLE WORKER TEST: PASS")
    typer.echo(f"Worker: {info['worker_dir']}")
    typer.echo(f"Kernel: {info['metadata']['id']}")
    typer.echo(f"Code: {info['code_file']}")
    typer.echo(f"GPU enabled: {info['metadata'].get('enable_gpu', False)}")


@kaggle_app.command("doctor")
def kaggle_doctor_cmd() -> None:
    """Check Kaggle CLI/auth/worker files. Never pushes or uses GPU."""
    checks = kaggle_doctor()
    failed = False
    for name, ok, detail in checks:
        typer.echo(f"[{'OK' if ok else 'FAIL'}] {name}: {detail}")
        failed |= not ok
    raise typer.Exit(code=1 if failed else 0)


@kaggle_app.command("push")
def kaggle_push_cmd(accelerator: str = typer.Option("NvidiaTeslaT4", "--accelerator", "-a"), public: bool = typer.Option(False, "--public")) -> None:
    """Push and run the Kaggle worker from Termux."""
    try:
        code = kaggle_push(accelerator=accelerator, public=True if public else None)
    except KaggleWorkerError as exc:
        raise typer.BadParameter(str(exc)) from exc
    raise typer.Exit(code=code)


@kaggle_app.command("discover")
def kaggle_discover(search: str = typer.Option("stockforge-worker", "--search", "-s")) -> None:
    """Find StockForge kernels using Kaggle's list endpoint."""
    raise typer.Exit(code=list_kernels(search))


@kaggle_app.command("quota")
def kaggle_quota_cmd() -> None:
    """Show Kaggle GPU/TPU quota."""
    raise typer.Exit(code=kaggle_quota())


@kaggle_app.command("status")
def kaggle_status(kernel: str | None = typer.Option(None, "--kernel", "-k")) -> None:
    """Read kernel status through the Kaggle API."""
    raise typer.Exit(code=kaggle_remote("status", kernel))


@kaggle_app.command("logs")
def kaggle_logs(kernel: str | None = typer.Option(None, "--kernel", "-k")) -> None:
    """Read kernel logs through the Kaggle API."""
    raise typer.Exit(code=kaggle_remote("logs", kernel))


@kaggle_app.command("output")
def kaggle_output(kernel: str | None = typer.Option(None, "--kernel", "-k")) -> None:
    """Download the latest kernel output through the Kaggle API."""
    raise typer.Exit(code=kaggle_remote("output", kernel))


if __name__ == "__main__":
    app()
