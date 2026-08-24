"""StockForge command line interface."""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import typer

from . import __version__
from .adobe_finalize import AdobeFinalizationError, finalize_image
from .adobe_upload_bundle import AdobeUploadBundleError, prepare_adobe_upload_bundle
from .adobe_gate import inspect_image
from .asset import ASSET_TYPES, AssetError
from .asset_manager import AssetManager
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .generation import GenerationRequest
from .job import JobError
from .job_database import JobDatabase
from .job_manager import JobManager
from .kaggle_worker import KaggleWorkerError, doctor as kaggle_doctor, list_kernels, push as kaggle_push, quota as kaggle_quota, remote as kaggle_remote, validate_local
from .kaggle_finalizer import doctor as kaggle_finalizer_doctor, remote as kaggle_finalizer_remote, submit as kaggle_finalizer_submit, validate_local as validate_kaggle_finalizer
from .project import ProjectManager
from .provider_config import ProviderConfigError
from .provider_orchestration import ProviderRoutingError
from .portfolio import PortfolioError, lane_for, list_lanes, metadata_from_dict, plan_manifest
from .portfolio_io import PortfolioPlanError, load_project_plan, portfolio_snapshot, select_brief
from .artifact import sha256_file
from .master_finalizer import MasterFinalizationError, MasterTarget
from .master_registry import MasterRegistryError, register_master_candidate
from .kaggle_master_import import KaggleMasterImportError, import_kaggle_master
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
kaggle_finalizer_app = typer.Typer(help="Control the private Kaggle AI-upscale finalizer without a browser.")
provider_app = typer.Typer(help="Configure remote GPU workers for Termux-controlled generation.")
portfolio_app = typer.Typer(help="Plan evidence-aligned, human-review-required portfolio batches.")
app.add_typer(project_app, name="project")
app.add_typer(asset_app, name="asset")
app.add_typer(job_app, name="job")
app.add_typer(adobe_app, name="adobe")
app.add_typer(kaggle_app, name="kaggle")
app.add_typer(kaggle_finalizer_app, name="kaggle-finalizer")
app.add_typer(provider_app, name="provider")
app.add_typer(portfolio_app, name="portfolio")


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
    profile: str = typer.Option("z-image-turbo", "--profile"),
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


@portfolio_app.command("lanes")
def portfolio_lanes(json_output: bool = typer.Option(False, "--json")) -> None:
    """List evidence-aligned lanes and their initial safe batch caps."""
    lanes = list_lanes()
    if json_output:
        typer.echo(json.dumps([
            {
                "key": lane.key,
                "name": lane.name,
                "tier": lane.tier,
                "evidence_confidence": lane.evidence_confidence,
                "opportunity_id": lane.opportunity_id,
                "test_cap": lane.test_cap,
                "seed_concepts": len(lane.concepts),
                "notes": lane.notes,
            }
            for lane in lanes
        ], indent=2))
        return
    for lane in lanes:
        typer.echo(
            f"{lane.key}\t{lane.tier}\tcap={lane.test_cap}\t"
            f"seed_concepts={len(lane.concepts)}\t{lane.name}"
        )


@portfolio_app.command("plan")
def portfolio_plan(
    lane: str = typer.Option(..., "--lane"),
    count: int = typer.Option(1, "--count", min=1),
    json_output: bool = typer.Option(True, "--json/--text"),
) -> None:
    """Preview bounded, generation-ready brief cards without calling a remote worker."""
    try:
        manifest = plan_manifest(lane, count)
    except PortfolioError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if json_output:
        typer.echo(json.dumps(manifest, indent=2))
        return
    lane_info = manifest["lane"]
    typer.echo(f"Lane: {lane_info['name']} ({lane_info['tier']})")
    typer.echo(f"Status: {manifest['status']}; human review required: yes")
    for brief in manifest["briefs"]:
        typer.echo("")
        typer.echo(f"Brief: {brief['brief_id']}")
        typer.echo(f"Title draft: {brief['metadata']['title']}")
        typer.echo(f"Prompt: {brief['prompt_package']['prompt']}")
        typer.echo(f"Negative prompt: {brief['prompt_package']['negative_prompt']}")


def _portfolio_project(project: str) -> tuple[object, Path]:
    manager = ConfigManager()
    config = manager.initialize()
    database = JobDatabase(config.database)
    database.initialize()
    projects = [item for item in database.list_projects() if item["name"] == project]
    if not projects:
        raise PortfolioError(f"Project not found: {project}")
    record = projects[0]
    return record, Path(record["path"]).resolve()


@portfolio_app.command("create-batch")
def portfolio_create_batch(
    project: str = typer.Option(..., "--project", "-p"),
    lane: str = typer.Option(..., "--lane"),
    count: int = typer.Option(1, "--count", min=1),
) -> None:
    """Write a project-local, human-review-required batch plan without generating images."""
    try:
        _record, project_root = _portfolio_project(project)
        manifest = plan_manifest(lane, count)
    except PortfolioError as exc:
        raise typer.BadParameter(str(exc)) from exc
    batch_id = f"{lane_for(lane).key}-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    manifest["batch_id"] = batch_id
    manifest["created_at"] = datetime.now(UTC).isoformat()
    destination_dir = project_root / "portfolio-plans"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{batch_id}.json"
    temporary = destination.with_suffix(".json.tmp")
    try:
        temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    typer.echo(json.dumps({
        "batch_id": batch_id,
        "path": str(destination),
        "status": manifest["status"],
        "brief_ids": [item["brief_id"] for item in manifest["briefs"]],
        "notice": "No remote GPU call was made. Each brief remains human_review_required before marketplace submission.",
    }, indent=2))


@portfolio_app.command("list")
def portfolio_list(
    project: str = typer.Option(..., "--project", "-p"),
    status: str | None = typer.Option(None, "--status"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """List project-local portfolio plans; this never claims marketplace acceptance."""
    try:
        _record, project_root = _portfolio_project(project)
    except PortfolioError as exc:
        raise typer.BadParameter(str(exc)) from exc
    plans: list[dict[str, object]] = []
    for path in sorted((project_root / "portfolio-plans").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("kind") != "stockforge.portfolio_batch_plan":
            continue
        if status is not None and data.get("status") != status:
            continue
        plans.append({
            "batch_id": data.get("batch_id", path.stem),
            "lane": data.get("lane", {}).get("key", "-"),
            "status": data.get("status", "-"),
            "brief_count": len(data.get("briefs", [])),
            "path": str(path),
        })
    if json_output:
        typer.echo(json.dumps(plans, indent=2))
        return
    if not plans:
        typer.echo("No matching portfolio plans.")
        return
    for item in plans:
        typer.echo(
            f"{item['batch_id']}\t{item['lane']}\t{item['status']}\t"
            f"briefs={item['brief_count']}\t{item['path']}"
        )


def _run_one_generation(
    *,
    project: str,
    prompt: str,
    provider: str | None,
    profile: str,
    seed: int | None,
    canvas: str,
    dry_run: bool,
    portfolio_context: dict[str, object] | None = None,
) -> dict[str, object]:
    """Run the existing bounded Termux path and optionally freeze portfolio context."""
    manager = ConfigManager()
    config = manager.initialize()
    database = JobDatabase(config.database)
    database.initialize()
    projects = [item for item in database.list_projects() if item["name"] == project]
    if not projects:
        raise PortfolioError(f"Project not found: {project}")
    project_record = projects[0]
    project_root = Path(project_record["path"]).resolve()
    try:
        base_request = profile_for(profile).request(prompt, seed=seed, canvas=canvas)
        parameters = dict(base_request.parameters)
        if portfolio_context is not None:
            parameters["portfolio"] = portfolio_context
        request = GenerationRequest(
            prompt=base_request.prompt,
            negative_prompt=base_request.negative_prompt,
            width=base_request.width,
            height=base_request.height,
            steps=base_request.steps,
            guidance_scale=base_request.guidance_scale,
            seed=base_request.seed,
            batch_size=base_request.batch_size,
            model_id=base_request.model_id,
            model_version=base_request.model_version,
            workflow_hash=base_request.workflow_hash,
            input_artifact_ids=base_request.input_artifact_ids,
            parameters=parameters,
        )
        candidate = route_remote_generation(
            workspace=config.workspace,
            request=request,
            output_dir=project_root / ".provider-output" / (provider or "auto"),
            provider_id=provider,
        )
    except (TermuxControlError, ProviderConfigError, ProviderRoutingError) as exc:
        raise PortfolioError(str(exc)) from exc

    preview: dict[str, object] = {
        "project": project,
        "provider": candidate.capabilities.provider_id,
        "profile": profile,
        "canvas": request.parameters["canvas"],
        "model_id": request.model_id,
        "model_version": request.model_version,
        "width": request.width,
        "height": request.height,
        "steps": request.steps,
        "seed": request.seed,
        "batch_size": request.batch_size,
        "estimated_gpu_seconds": request.parameters["estimated_gpu_seconds"],
    }
    if portfolio_context is not None:
        preview["portfolio"] = {
            "batch_id": portfolio_context["batch_id"],
            "brief_id": portfolio_context["brief_id"],
            "lane_key": portfolio_context["lane_key"],
            "human_review_required": True,
        }
    if dry_run:
        return {"dry_run": True, **preview}

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
        raise PortfolioError(str(exc)) from exc
    return {
        **preview,
        "job_id": claimed.id,
        "execution_id": result.execution.id,
        "artifact_ids": list(result.execution.artifact_ids),
        "release_package": package.to_dict(),
        "status": "review_ready",
    }


@portfolio_app.command("show")
def portfolio_show(
    project: str = typer.Option(..., "--project", "-p"),
    plan: str = typer.Option(..., "--plan"),
    brief: str = typer.Option(..., "--brief"),
) -> None:
    """Display one saved brief without calling a remote worker."""
    try:
        _record, project_root = _portfolio_project(project)
        plan_path, data = load_project_plan(project_root, plan)
        selected = select_brief(data, brief)
    except (PortfolioError, PortfolioPlanError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps({
        "plan": str(plan_path),
        "batch_id": data["batch_id"],
        "brief": selected,
        "notice": "No remote GPU call was made. This brief requires human review before marketplace submission.",
    }, indent=2))


@portfolio_app.command("prepare-master")
def portfolio_prepare_master(
    project: str = typer.Option(..., "--project", "-p"),
    execution: str = typer.Option(..., "--execution"),
    artifact: str | None = typer.Option(None, "--artifact"),
    minimum_megapixels: float = typer.Option(6.0, "--minimum-megapixels", min=4.0, max=100.0),
    scale: int = typer.Option(4, "--scale"),
) -> None:
    """Prepare one lineage-bound master-finalizer request; never calls GPU."""
    try:
        record, project_root = _portfolio_project(project)
        database = JobDatabase(ConfigManager().initialize().database)
        database.initialize()
        source_execution = database.get_execution(execution)
        if source_execution is None or source_execution.project_id != record["id"]:
            raise PortfolioError("Execution does not belong to the requested project.")
        if not source_execution.artifact_ids:
            raise PortfolioError("Execution has no output artifact to finalize.")
        source_id = artifact or source_execution.artifact_ids[0]
        if source_id not in source_execution.artifact_ids:
            raise PortfolioError("Requested artifact is not an output of the supplied execution.")
        source = database.get_artifact(source_id)
        if source is None or source.project_id != record["id"] or source.kind != "generated-image":
            raise PortfolioError("Requested artifact is not an eligible generated preview.")
        source_path = (project_root / source.relative_path).resolve()
        try:
            source_path.relative_to(project_root)
        except ValueError as exc:
            raise PortfolioError("Preview artifact path escapes the project workspace.") from exc
        if not source_path.is_file():
            raise PortfolioError("Preview artifact file is missing from the project workspace.")
        target = MasterTarget(minimum_megapixels=minimum_megapixels, scale=scale)
        from PIL import Image
        with Image.open(source_path) as image:
            image.load()
            width, height = image.size
        expected_width, expected_height = width * target.scale, height * target.scale
        expected_megapixels = (expected_width * expected_height) / 1_000_000
        if expected_megapixels < target.minimum_megapixels:
            raise PortfolioError(
                f"Requested scale produces {expected_megapixels:.2f} MP, below target {target.minimum_megapixels:.2f} MP."
            )
        if expected_megapixels > 100:
            raise PortfolioError(f"Requested scale produces {expected_megapixels:.2f} MP, above 100 MP.")
        portfolio = source_execution.parameters.get("portfolio")
        if portfolio is not None and not isinstance(portfolio, dict):
            raise PortfolioError("Execution portfolio context is invalid.")
        request_id = f"master-{source.id}-{uuid4().hex[:8]}"
        payload = {
            "schema_version": 1,
            "kind": "stockforge.master_finalizer_request",
            "request_id": request_id,
            "status": "prepared_no_gpu",
            "project_id": record["id"],
            "source": {
                "artifact_id": source.id,
                "execution_id": source_execution.id,
                "relative_path": source.relative_path,
                "sha256": sha256_file(source_path),
                "width": width,
                "height": height,
            },
            "target": {
                "mode": "ai_upscale",
                "scale": target.scale,
                "minimum_megapixels": target.minimum_megapixels,
                "expected_width": expected_width,
                "expected_height": expected_height,
                "expected_megapixels": round(expected_megapixels, 4),
                "format": "jpeg",
                "color_space": "sRGB",
            },
            "destination": f"masters/{source.id}-master.jpg",
            "portfolio": portfolio,
            "human_review_required": True,
            "provider_options": ["kaggle-realesrgan", "future-burst-finalizer"],
            "notice": "This request did not call GPU. A finalizer provider must perform visual upscale, then the result requires 100% human review before marketplace submission.",
        }
        destination_dir = project_root / "master-finalizer-requests"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{request_id}.json"
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (PortfolioError, MasterFinalizationError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps({"path": str(destination), **payload}, indent=2))


@portfolio_app.command("prepare-adobe-upload")
def portfolio_prepare_adobe_upload(
    project: str = typer.Option(..., "--project", "-p"),
    execution: list[str] = typer.Option(..., "--execution", "-e", help="Finalized-master execution ID; repeat for a batch."),
    approved: bool = typer.Option(False, "--approved", help="Explicitly attest that each selected master passed human visual review."),
    category: int | None = typer.Option(None, "--category", help="Reviewed Adobe category number (1-21) when no safe lane mapping exists."),
) -> None:
    """Create an Adobe portal batch with JPEGs, official-schema CSV, and no submit action."""
    try:
        record, project_root = _portfolio_project(project)
        database = JobDatabase(ConfigManager().initialize().database)
        database.initialize()
        bundle = prepare_adobe_upload_bundle(
            database=database,
            project_id=record["id"],
            project_root=project_root,
            execution_ids=tuple(execution),
            approved_by_user=approved,
            category=category,
        )
        typer.echo(json.dumps(bundle.to_dict(), indent=2))
    except (AdobeUploadBundleError, PortfolioError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc


@portfolio_app.command("import-kaggle-master")
def portfolio_import_kaggle_master(
    project: str = typer.Option(..., "--project", "-p"),
    request: str = typer.Option(..., "--request"),
    result_dir: str = typer.Option(..., "--result-dir"),
    metadata_review: str | None = typer.Option(None, "--metadata-review", help="Reviewed metadata JSON stored inside the project workspace."),
) -> None:
    """Verify/import one Kaggle finalizer output and build a review package; never calls GPU."""
    try:
        record, project_root = _portfolio_project(project)
        request_path = Path(request).expanduser().resolve()
        try:
            request_path.relative_to(project_root)
        except ValueError as exc:
            raise PortfolioError("Finalizer request must be inside the requested project workspace.") from exc
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        if payload.get("kind") != "stockforge.master_finalizer_request":
            raise PortfolioError("Finalizer request kind is invalid.")
        source_data = payload.get("source")
        if not isinstance(source_data, dict):
            raise PortfolioError("Finalizer request source is invalid.")
        source_artifact_id = source_data.get("artifact_id")
        source_execution_id = source_data.get("execution_id")
        if not isinstance(source_artifact_id, str) or not isinstance(source_execution_id, str):
            raise PortfolioError("Finalizer request lacks source artifact/execution identity.")
        database = JobDatabase(ConfigManager().initialize().database)
        database.initialize()
        source_artifact = database.get_artifact(source_artifact_id)
        source_execution = database.get_execution(source_execution_id)
        if source_artifact is None or source_execution is None:
            raise PortfolioError("Original preview artifact or execution is no longer available.")
        reviewed_metadata = None
        if metadata_review is not None:
            metadata_path = Path(metadata_review).expanduser().resolve()
            try:
                metadata_path.relative_to(project_root)
            except ValueError as exc:
                raise PortfolioError("Reviewed metadata file must remain inside the requested project workspace.") from exc
            try:
                reviewed_metadata = metadata_from_dict(json.loads(metadata_path.read_text(encoding="utf-8"))).to_dict()
            except (OSError, json.JSONDecodeError, PortfolioError) as exc:
                raise PortfolioError(f"Reviewed metadata is invalid: {exc}") from exc
        report = import_kaggle_master(
            request_path=request_path,
            result_dir=result_dir,
            project_root=project_root,
        )
        master, master_execution = register_master_candidate(
            database=database,
            project_id=record["id"],
            project_root=project_root,
            source_artifact=source_artifact,
            source_execution=source_execution,
            report=report,
            reviewed_metadata=reviewed_metadata,
        )
        package = build_release_package(
            database=database,
            project_id=record["id"],
            project_root=project_root,
            execution_id=master_execution.id,
        )
    except (
        PortfolioError,
        KaggleMasterImportError,
        MasterRegistryError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps({
        "status": "review_ready",
        "master_artifact_id": master.id,
        "master_execution_id": master_execution.id,
        "master_finalization": report.to_dict(),
        "release_package": package.to_dict(),
        "notice": "GPU was not called by import. Review the master JPEG at 100% before any marketplace submission.",
    }, indent=2))


@portfolio_app.command("generate")
def portfolio_generate(
    project: str = typer.Option(..., "--project", "-p"),
    plan: str = typer.Option(..., "--plan"),
    brief: str = typer.Option(..., "--brief"),
    provider: str | None = typer.Option(None, "--provider"),
    profile: str = typer.Option("z-image-turbo", "--profile"),
    seed: int | None = typer.Option(None, "--seed", min=0),
    canvas: str = typer.Option("square", "--canvas", help="Pre-approved canvas: square or hero-landscape."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Generate exactly one selected saved brief with immutable portfolio lineage."""
    try:
        _record, project_root = _portfolio_project(project)
        plan_path, data = load_project_plan(project_root, plan)
        selected = select_brief(data, brief)
        context = portfolio_snapshot(data, selected, plan_path)
        output = _run_one_generation(
            project=project,
            prompt=selected["prompt_package"]["prompt"],
            provider=provider,
            profile=profile,
            seed=seed,
            canvas=canvas,
            dry_run=dry_run,
            portfolio_context=context,
        )
    except (PortfolioError, PortfolioPlanError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(output, indent=2))


@app.command("generate")
def generate(
    project: str = typer.Option(..., "--project", "-p"),
    prompt: str = typer.Option(..., "--prompt"),
    provider: str | None = typer.Option(None, "--provider"),
    profile: str = typer.Option("z-image-turbo", "--profile"),
    seed: int | None = typer.Option(None, "--seed", min=0),
    canvas: str = typer.Option("square", "--canvas", help="Pre-approved canvas: square or hero-landscape."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Submit exactly one bounded remote generation from the Termux control plane."""
    try:
        output = _run_one_generation(
            project=project,
            prompt=prompt,
            provider=provider,
            profile=profile,
            seed=seed,
            canvas=canvas,
            dry_run=dry_run,
        )
    except PortfolioError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(output, indent=2))


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


@kaggle_finalizer_app.command("test")
def kaggle_finalizer_test() -> None:
    """Validate finalizer bundle locally. Never pushes or uses GPU."""
    try:
        info = validate_kaggle_finalizer()
    except KaggleWorkerError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo("KAGGLE FINALIZER TEST: PASS")
    typer.echo(f"Worker: {info['worker_dir']}")
    typer.echo(f"Kernel: {info['metadata']['id']}")
    typer.echo("Mode: private one-shot 4x AI upscale")


@kaggle_finalizer_app.command("doctor")
def kaggle_finalizer_doctor_cmd() -> None:
    """Check Kaggle CLI/auth/finalizer files. Never pushes or uses GPU."""
    checks = kaggle_finalizer_doctor()
    failed = False
    for name, ok, detail in checks:
        typer.echo(f"[{'OK' if ok else 'FAIL'}] {name}: {detail}")
        failed |= not ok
    raise typer.Exit(code=1 if failed else 0)


@kaggle_finalizer_app.command("submit")
def kaggle_finalizer_submit_cmd(
    project: str = typer.Option(..., "--project", "-p"),
    request: str = typer.Option(..., "--request"),
    accelerator: str = typer.Option("NvidiaTeslaT4", "--accelerator", "-a"),
) -> None:
    """Push one prepared master request to private Kaggle GPU finalizer."""
    try:
        _record, project_root = _portfolio_project(project)
        code = kaggle_finalizer_submit(request=request, project_root=project_root, accelerator=accelerator)
    except (KaggleWorkerError, PortfolioError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    raise typer.Exit(code=code)


@kaggle_finalizer_app.command("status")
def kaggle_finalizer_status(kernel: str | None = typer.Option(None, "--kernel", "-k")) -> None:
    """Read finalizer kernel status through the Kaggle API."""
    raise typer.Exit(code=kaggle_finalizer_remote("status", kernel))


@kaggle_finalizer_app.command("output")
def kaggle_finalizer_output(
    project: str = typer.Option(..., "--project", "-p"),
    kernel: str | None = typer.Option(None, "--kernel", "-k"),
    destination: str | None = typer.Option(None, "--destination", "-d"),
    force: bool = typer.Option(False, "--force", help="Overwrite local output with the latest completed Kaggle kernel files."),
) -> None:
    """Download finalizer output into the project without using GPU."""
    try:
        _record, project_root = _portfolio_project(project)
        output_dir = Path(destination).expanduser() if destination else project_root / "kaggle-finalizer-output"
        output_dir = output_dir.resolve()
        try:
            output_dir.relative_to(project_root)
        except ValueError as exc:
            raise PortfolioError("Finalizer output destination must remain inside the project workspace.") from exc
        code = kaggle_finalizer_remote("output", kernel, output_dir, force=force)
    except (KaggleWorkerError, PortfolioError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    raise typer.Exit(code=code)


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
