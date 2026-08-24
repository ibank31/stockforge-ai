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
from .android_export import AndroidExportError, default_downloads_root, export_preview, export_ready_upload
from .adobe_upload_bundle import AdobeUploadBundleError, latest_finalized_master_execution_id, prepare_adobe_upload_bundle
from .asset_selector import AssetSelectionError, list_asset_type_policies, select_asset_type
from .adobe_gate import inspect_image
from .adobe_png_gate import inspect_transparent_png
from .asset import ASSET_TYPES, AssetError
from .asset_manager import AssetManager
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .generation import GenerationRequest
from .generation_evaluation import EvaluationError, append_evaluation, new_evaluation, summarize_evaluations
from .job import JobError
from .job_database import JobDatabase
from .job_manager import JobManager
from .kaggle_worker import KaggleWorkerError, doctor as kaggle_doctor, list_kernels, push as kaggle_push, quota as kaggle_quota, remote as kaggle_remote, validate_local
from .kaggle_finalizer import doctor as kaggle_finalizer_doctor, remote as kaggle_finalizer_remote, submit as kaggle_finalizer_submit, validate_local as validate_kaggle_finalizer
from .project import ProjectManager
from .provider_config import ProviderConfigError
from .provider_orchestration import ProviderRoutingError
from .portfolio import PortfolioError, build_brief, lane_for, list_lanes, metadata_from_dict, plan_manifest
from .portfolio_io import PortfolioPlanError, jpeg_metadata_preflight, load_project_plan, portfolio_snapshot, preview_preflight, select_brief
from .format_router import FormatRoutingError, route_from_dict
from .local_vector_build import LocalVectorBuildError, build_local_native_vector
from .artifact import sha256_file
from .master_finalizer import MasterFinalizationError, MasterTarget
from .master_registry import MasterRegistryError, register_master_candidate
from .kaggle_master_import import KaggleMasterImportError, import_kaggle_master
from .model_catalog import list_image_models
from .recovery_orchestrator import RecoveryGenerationOrchestrator
from .release_package import build_release_package
from .trial_gate import TrialGateError, assess_trial_readiness
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


@provider_app.command("models")
def provider_models(json_output: bool = typer.Option(False, "--json")) -> None:
    """List evidence-backed image models without configuring or calling a provider."""
    records = [record.to_dict() for record in list_image_models()]
    if json_output:
        typer.echo(json.dumps(records, indent=2))
        return
    for record in records:
        typer.echo(
            f"{record['profile']}\t{record['readiness']}\t{record['license_id']}\t{record['primary_use']}"
        )


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


@portfolio_app.command("trial-readiness")
def portfolio_trial_readiness(
    asset_type: str = typer.Option(..., "--asset-type", "-t"),
    hypothesis: str = typer.Option(..., "--hypothesis"),
    purpose: str = typer.Option(..., "--purpose"),
) -> None:
    """Check whether one controlled trial may be considered; never calls a provider."""
    try:
        readiness = assess_trial_readiness(asset_type=asset_type, hypothesis=hypothesis, purpose=purpose)
    except (TrialGateError, AssetSelectionError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(readiness.to_dict(), indent=2))


@portfolio_app.command("asset-types")
def portfolio_asset_types(
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """List supported asset types and their conservative format routes without generation."""
    policies = [item.to_dict() for item in list_asset_type_policies()]
    if json_output:
        typer.echo(json.dumps(policies, indent=2))
        return
    for item in policies:
        typer.echo(f"{item['key']}\t{item['delivery_format']}\t{item['readiness']}\t{item['label']}")


@portfolio_app.command("readiness")
def portfolio_readiness(
    asset_type: str = typer.Option("all", "--asset-type", "-t"),
) -> None:
    """Explain whether an asset type is ready for a trial; never calls a provider."""
    try:
        if asset_type.strip().casefold() == "all":
            output = [item.to_dict() for item in list_asset_type_policies()]
        else:
            output = select_asset_type(asset_type).to_dict()
    except AssetSelectionError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(output, indent=2))


@portfolio_app.command("plan-type")
def portfolio_plan_type(
    asset_type: str = typer.Option(..., "--asset-type", "-t"),
    concept: str | None = typer.Option(None, "--concept", help="Optional registered concept override."),
) -> None:
    """Turn one asset-type choice into a reviewable brief without generation."""
    try:
        policy = select_asset_type(asset_type)
        if not policy.recommended_lane_keys or not policy.recommended_concept_keys:
            raise PortfolioError("This asset type has no approved brief lane yet; follow its readiness blockers.")
        lane_key = policy.recommended_lane_keys[0]
        concept_key = concept or policy.recommended_concept_keys[0]
        brief = build_brief(lane_key, concept_key).to_dict()
        route = route_from_dict(brief["asset_spec"])
    except (AssetSelectionError, PortfolioError, FormatRoutingError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps({
        "kind": "stockforge.asset_type_plan",
        "status": "planned_no_generation",
        "selector": policy.to_dict(),
        "lane_key": lane_key,
        "concept_key": concept_key,
        "format_route": route.to_dict(),
        "brief": brief,
        "notice": "No provider or GPU was called. Human review is required before any trial.",
    }, indent=2))


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
        base_request = profile_for(profile).request(
            prompt,
            seed=seed,
            canvas=canvas,
            apply_standalone_policy=portfolio_context is None,
        )
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
            "pre_gpu_gate": portfolio_context.get("pre_gpu_gate"),
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
        android_preview_export = _export_preview_to_android(
            database=database,
            project_root=project_root,
            artifact_ids=result.execution.artifact_ids,
            asset_name=str((portfolio_context or {}).get("brief_id", result.execution.id[:12])),
        )
        jobs.complete(
            claimed.id,
            {
                "execution_id": result.execution.id,
                "artifact_ids": list(result.execution.artifact_ids),
                "provider": candidate.capabilities.provider_id,
                "release_package": package.to_dict(),
                "android_preview_export": android_preview_export,
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
        "android_preview_export": android_preview_export,
        "status": "review_ready",
    }


def _export_ready_uploads_to_android(bundle: object) -> dict[str, object]:
    """Copy only approved JPEG upload masters into the Android upload folder."""
    downloads_root = default_downloads_root()
    if downloads_root is None:
        return {"status": "not_available", "notice": "No Android Download mount was detected; upload bundle remains in the project workspace."}
    asset_dirs = getattr(bundle, "asset_dirs", ())
    exports: list[dict[str, object]] = []
    try:
        for asset_dir in asset_dirs:
            candidates = sorted(Path(asset_dir).glob("*.jpg")) + sorted(Path(asset_dir).glob("*.jpeg"))
            if len(candidates) != 1:
                raise AndroidExportError("Each approved upload folder must contain exactly one JPEG master.")
            exported = export_ready_upload(
                source=candidates[0],
                downloads_root=downloads_root,
                asset_name=Path(asset_dir).name,
            )
            exports.append(exported.to_dict())
    except (AndroidExportError, OSError, ValueError) as exc:
        return {"status": "failed", "error": str(exc), "exports": exports}
    return {"status": "exported", "exports": exports}


def _export_preview_to_android(*, database: JobDatabase, project_root: Path, artifact_ids: tuple[str, ...], asset_name: str) -> dict[str, object]:
    """Export only the first generated visual when an Android Download mount exists."""
    downloads_root = default_downloads_root()
    if downloads_root is None:
        return {"status": "not_available", "notice": "No Android Download mount was detected; project package remains available."}
    if not artifact_ids:
        return {"status": "failed", "error": "Generation returned no artifact IDs."}
    artifact = database.get_artifact(artifact_ids[0])
    if artifact is None:
        return {"status": "failed", "error": "Generated artifact was not found for Android export."}
    source = (project_root / artifact.relative_path).resolve()
    try:
        source.relative_to(project_root.resolve())
        exported = export_preview(source=source, downloads_root=downloads_root, asset_name=asset_name)
    except (AndroidExportError, OSError, ValueError) as exc:
        return {"status": "failed", "error": str(exc)}
    return {"status": "exported", **exported.to_dict()}


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


@portfolio_app.command("metadata-preflight")
def portfolio_metadata_preflight(
    project: str = typer.Option(..., "--project", "-p"),
    plan: str = typer.Option(..., "--plan"),
    brief: str = typer.Option(..., "--brief"),
    category: str | None = typer.Option(None, "--category", help="Optional human-reviewed category label for validation only; never selected or uploaded automatically."),
) -> None:
    """Validate reviewed JPEG metadata across marketplaces without uploading."""
    try:
        _record, project_root = _portfolio_project(project)
        plan_path, data = load_project_plan(project_root, plan)
        selected = select_brief(data, brief)
        asset_spec = selected.get("asset_spec")
        if not isinstance(asset_spec, dict) or asset_spec.get("delivery_format") != "jpeg":
            raise PortfolioError("Metadata preflight is currently limited to JPEG briefs.")
        report = jpeg_metadata_preflight(data, selected, category=category)
        report.update({"project": project, "plan": plan_path.name, "brief": brief})
        typer.echo(json.dumps(report, indent=2))
    except (PortfolioPlanError, PortfolioError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc


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
    execution: list[str] = typer.Option([], "--execution", "-e", help="Finalized-master execution ID; repeat for a batch."),
    latest_master: bool = typer.Option(False, "--latest-master", help="Use the newest finalized master in this project."),
    approved: bool = typer.Option(False, "--approved", help="Explicitly attest that each selected master passed human visual review."),
    category: int | None = typer.Option(None, "--category", help="Reviewed Adobe category number (1-21) when no safe lane mapping exists."),
    destination: str | None = typer.Option(None, "--destination", "-d", help="Final Adobe batch folder; defaults to Android Download/AdobeStock/READY_TO_UPLOAD when available."),
) -> None:
    """Create an Adobe portal batch with JPEGs, official-schema CSV, and no submit action."""
    try:
        record, project_root = _portfolio_project(project)
        database = JobDatabase(ConfigManager().initialize().database)
        database.initialize()
        if latest_master:
            if execution:
                raise PortfolioError("Use either --latest-master or one or more --execution values, not both.")
            execution_ids = (latest_finalized_master_execution_id(database=database, project_id=record["id"]),)
        else:
            execution_ids = tuple(execution)
        if destination is not None:
            destination_root = Path(destination).expanduser().resolve()
        elif str(project_root).startswith("/storage/emulated/0/"):
            destination_root = Path("/storage/emulated/0/Download/AdobeStock/READY_TO_UPLOAD")
        else:
            destination_root = project_root / "adobe-upload-bundles"
        bundle = prepare_adobe_upload_bundle(
            database=database,
            project_id=record["id"],
            project_root=project_root,
            execution_ids=execution_ids,
            approved_by_user=approved,
            category=category,
            destination_root=destination_root,
        )
        android_ready_upload_exports = _export_ready_uploads_to_android(bundle)
        output = bundle.to_dict()
        output["android_ready_upload_exports"] = android_ready_upload_exports
        typer.echo(json.dumps(output, indent=2))
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


@portfolio_app.command("evaluate")
def portfolio_evaluate(
    project: str = typer.Option(..., "--project", "-p"),
    execution: str = typer.Option(..., "--execution"),
    artifact: str | None = typer.Option(None, "--artifact"),
    decision: str = typer.Option(..., "--decision", help="Human decision: accept, reject, or review."),
    visual_quality: int = typer.Option(..., "--visual-quality", min=0, max=5),
    technical_quality: int = typer.Option(..., "--technical-quality", min=0, max=5),
    buyer_fit: int = typer.Option(..., "--buyer-fit", min=0, max=5),
    metadata_accuracy: int = typer.Option(..., "--metadata-accuracy", min=0, max=5),
    rejection_reason: list[str] = typer.Option([], "--rejection-reason"),
    marketplace: str = typer.Option("adobe_stock", "--marketplace"),
    marketplace_outcome: str = typer.Option("not_submitted", "--marketplace-outcome"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Record a human review; this never generates, uploads, or changes an asset."""
    try:
        record, project_root = _portfolio_project(project)
        database = JobDatabase(ConfigManager().initialize().database)
        database.initialize()
        execution_record = database.get_execution(execution)
        if execution_record is None or execution_record.project_id != record["id"]:
            raise PortfolioError("Execution does not belong to the requested project.")
        if execution_record.state != "succeeded" or not execution_record.artifact_ids:
            raise PortfolioError("Only a succeeded execution with an artifact can be evaluated.")
        artifact_id = artifact or execution_record.artifact_ids[0]
        if artifact_id not in execution_record.artifact_ids:
            raise PortfolioError("Selected artifact is not an output of the supplied execution.")
        portfolio = execution_record.parameters.get("portfolio")
        if not isinstance(portfolio, dict):
            raise PortfolioError("Evaluation requires a portfolio context with buyer job and format data.")
        asset_spec = portfolio.get("asset_spec")
        if not isinstance(asset_spec, dict):
            raise PortfolioError("Portfolio context has no immutable asset specification.")
        route = portfolio.get("format_route")
        if not isinstance(route, dict):
            route = {}
        evaluation = new_evaluation(
            execution_id=execution_record.id,
            artifact_id=artifact_id,
            lane_key=str(portfolio.get("lane_key", "")),
            buyer_job=str(portfolio.get("buyer_job", asset_spec.get("buyer_job", ""))),
            product_kind=str(asset_spec.get("product_kind", "")),
            delivery_format=str(asset_spec.get("delivery_format", route.get("delivery_format", ""))),
            provider_id=str(execution_record.provider_id or "local"),
            model_id=str(execution_record.model_id or "deterministic"),
            workflow_hash=str(execution_record.workflow_hash or "unknown"),
            decision=decision,
            visual_quality=visual_quality,
            technical_quality=technical_quality,
            buyer_fit=buyer_fit,
            metadata_accuracy=metadata_accuracy,
            rejection_reasons=tuple(rejection_reason),
            marketplace=marketplace,
            marketplace_outcome=marketplace_outcome,
            notes=notes,
        )
        ledger = append_evaluation(project_root, evaluation)
    except (EvaluationError, PortfolioError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps({"path": str(ledger), "evaluation": evaluation.to_dict()}, indent=2))


@portfolio_app.command("evaluation-summary")
def portfolio_evaluation_summary(
    project: str = typer.Option(..., "--project", "-p"),
) -> None:
    """Summarize reviewed outcomes without predicting sales or triggering work."""
    try:
        _record, project_root = _portfolio_project(project)
        summary = summarize_evaluations(project_root)
    except (EvaluationError, PortfolioError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(summary, indent=2))


@portfolio_app.command("build-vector")
def portfolio_build_vector(
    project: str = typer.Option(..., "--project", "-p"),
    plan: str = typer.Option(..., "--plan"),
    brief: str = typer.Option(..., "--brief"),
) -> None:
    """Build one native SVG asset locally; this never calls a GPU provider."""
    try:
        record, project_root = _portfolio_project(project)
        plan_path, data = load_project_plan(project_root, plan)
        selected = select_brief(data, brief)
        asset_spec = selected.get("asset_spec")
        if not isinstance(asset_spec, dict):
            raise PortfolioError("Portfolio brief has no valid asset specification.")
        route = route_from_dict(asset_spec)
        if route.execution_mode != "local_native_vector_build":
            raise PortfolioError("This brief is not a native-vector product; do not use build-vector.")
        database = JobDatabase(ConfigManager().initialize().database)
        database.initialize()
        context = portfolio_snapshot(data, selected, plan_path)
        context["format_route"] = route.to_dict()
        from .asset_spec import AssetSpec
        spec = AssetSpec(**asset_spec)
        result = build_local_native_vector(
            database=database,
            project_id=record["id"],
            project_root=project_root,
            spec=spec,
            portfolio_context=context,
        )
        package = build_release_package(
            database=database,
            project_id=record["id"],
            project_root=project_root,
            execution_id=result.execution_id,
        )
    except (PortfolioError, PortfolioPlanError, FormatRoutingError, LocalVectorBuildError, OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps({
        **result.to_dict(),
        "release_package": package.to_dict(),
        "notice": "Native SVG was built locally. No remote provider, GPU, Kaggle, XMP, Adobe upload, or submission was called.",
    }, indent=2))


@portfolio_app.command("generate")
def portfolio_generate(
    project: str = typer.Option(..., "--project", "-p"),
    plan: str = typer.Option(..., "--plan"),
    brief: str = typer.Option(..., "--brief"),
    provider: str | None = typer.Option(None, "--provider"),
    profile: str = typer.Option("z-image-turbo", "--profile"),
    seed: int | None = typer.Option(None, "--seed", min=0),
    canvas: str | None = typer.Option(None, "--canvas", help="Optional override: square or hero-landscape. Defaults to the brief's layout recommendation."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Generate exactly one selected saved brief with immutable portfolio lineage."""
    try:
        _record, project_root = _portfolio_project(project)
        plan_path, data = load_project_plan(project_root, plan)
        selected = select_brief(data, brief)
        preflight = preview_preflight(data, selected)
        if not preflight["gpu_eligible"]:
            raise PortfolioError(
                "Pre-GPU gate blocked this brief without calling a remote worker: "
                + "; ".join(preflight["blockers"])
            )
        context = portfolio_snapshot(data, selected, plan_path)
        context["pre_gpu_gate"] = preflight
        selected_canvas = canvas or str(preflight["recommended_canvas"])
        output = _run_one_generation(
            project=project,
            prompt=selected["prompt_package"]["prompt"],
            provider=provider,
            profile=profile,
            seed=seed,
            canvas=selected_canvas,
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


@adobe_app.command("check-png")
def adobe_check_png(path: str = typer.Argument(...), json_output: bool = typer.Option(False, "--json")) -> None:
    """Check a transparent PNG against deterministic alpha and Adobe technical requirements."""
    try:
        report = inspect_transparent_png(path)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc
    if json_output:
        typer.echo(json.dumps(report.to_dict(), indent=2))
    else:
        typer.echo(json.dumps(report.to_dict(), indent=2))
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
