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
from .adobe_png_upload_bundle import AdobePngUploadBundleError, prepare_adobe_png_upload_bundle
from .asset_selector import AssetSelectionError, list_asset_type_policies, select_asset_type
from .adobe_gate import inspect_image
from .adobe_png_gate import inspect_transparent_png
from .png_metadata import PngMetadataError, embed_png_metadata, read_embedded_png_metadata
from .asset import ASSET_TYPES, AssetError
from .asset_manager import AssetManager
from .config import ConfigManager
from .database import Database
from .doctor import run_doctor
from .generation import GenerationRequest
from .generation_evaluation import EvaluationError, append_evaluation, new_evaluation, summarize_evaluations
from .niche_learning import summarize_niche_learning
from .job import JobError
from .job_database import JobDatabase
from .job_manager import JobManager
from .kaggle_worker import KaggleWorkerError, doctor as kaggle_doctor, list_kernels, push as kaggle_push, quota as kaggle_quota, remote as kaggle_remote, validate_local
from .kaggle_finalizer import doctor as kaggle_finalizer_doctor, remote as kaggle_finalizer_remote, submit as kaggle_finalizer_submit, validate_local as validate_kaggle_finalizer
from .kaggle_png_finalizer import doctor as kaggle_png_finalizer_doctor, prepare_request as prepare_kaggle_png_request, remote as kaggle_png_finalizer_remote, submit as kaggle_png_finalizer_submit, validate_local as validate_kaggle_png_finalizer
from .kaggle_vector_worker import KaggleVectorWorkerError, doctor as kaggle_vector_doctor, remote as kaggle_vector_remote, submit as kaggle_vector_submit, validate_local as validate_kaggle_vector
from .project import ProjectManager
from .provider_config import ProviderConfigError
from .provider_orchestration import ProviderRoutingError
from .portfolio import PortfolioError, build_brief, lane_for, list_lanes, metadata_from_dict, plan_manifest
from .portfolio_io import PortfolioPlanError, jpeg_metadata_preflight, load_project_plan, normalize_historical_plan_reference, portfolio_snapshot, preview_preflight, select_brief
from .format_router import FormatRoutingError, route_from_dict
from .local_vector_build import LocalVectorBuildError, build_local_native_vector
from .learning_loop import critique_image, save_critique, summarize_learning_memory
from .artifact import sha256_file
from .external_import import ExternalImportError, import_external_image
from .external_finalizer_prep import ExternalFinalizerPreparationError, prepare_external_finalizer
from .master_finalizer import MasterFinalizationError, MasterTarget
from .master_registry import MasterRegistryError, register_master_candidate
from .kaggle_master_import import KaggleMasterImportError, import_kaggle_master
from .kaggle_png_master_import import KagglePngMasterImportError, import_kaggle_png_master
from .workflow import WorkflowError, attest_keep, load_workflow, mark_finalizer_ready, mark_master_ready, start_external, start_internal
from .model_catalog import list_image_models
from .recovery_orchestrator import RecoveryGenerationOrchestrator
from .release_package import build_release_package
from .trial_gate import TrialGateError, assess_trial_readiness
from .v2_cli import app as v2_app
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
kaggle_png_finalizer_app = typer.Typer(help="Control the isolated private Kaggle PNG alpha finalizer without a browser.")
kaggle_vector_app = typer.Typer(help="Control the isolated Kaggle StarVector SVG worker without a browser.")
provider_app = typer.Typer(help="Configure remote GPU workers for Termux-controlled generation.")
portfolio_app = typer.Typer(help="Plan evidence-aligned, human-review-required portfolio batches.")
app.add_typer(project_app, name="project")
app.add_typer(asset_app, name="asset")
app.add_typer(job_app, name="job")
app.add_typer(adobe_app, name="adobe")
app.add_typer(kaggle_app, name="kaggle")
app.add_typer(kaggle_finalizer_app, name="kaggle-finalizer")
app.add_typer(kaggle_png_finalizer_app, name="kaggle-png-finalizer")
app.add_typer(kaggle_vector_app, name="kaggle-vector")
app.add_typer(provider_app, name="provider")
app.add_typer(portfolio_app, name="portfolio")
app.add_typer(v2_app, name="v2")


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
