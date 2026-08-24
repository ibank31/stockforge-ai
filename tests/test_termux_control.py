from pathlib import Path
from uuid import uuid4

import pytest
from typer.testing import CliRunner

from stockforge.cli import app
from stockforge.generation import GenerationRequest
from stockforge.job_database import JobDatabase
from stockforge.job_manager import JobManager
from stockforge.provider_orchestration import ProviderRoutingError
from stockforge.termux_control import (
    TermuxControlError,
    canvas_dimensions,
    configure_remote_provider,
    profile_for,
    route_remote_generation,
)


runner = CliRunner()


def test_z_image_profile_is_bounded_for_free_worker():
    request = profile_for("z-image-turbo").request("single translucent resin pebble", seed=42)

    assert request.model_id == "z-image-turbo"
    assert (request.width, request.height, request.steps, request.batch_size) == (1024, 1024, 8, 1)
    assert request.guidance_scale == 0.0
    assert request.parameters["quota_policy"] == "single-candidate"
    assert request.parameters["asset_policy"] == "standalone_single_subject_v1"
    assert "single translucent resin pebble" in request.prompt
    assert "No people, hands" in request.prompt
    assert "measuring instruments" in request.prompt
    assert "stamp, postmark" in request.prompt


def test_compiled_portfolio_prompt_preserves_directional_layout_contract():
    compiled = "Primary subject: one clear modular tower on the left third. Negative-space contract: one third clean white copy space on the right."

    request = profile_for("z-image-turbo").request(
        compiled,
        seed=42,
        canvas="hero-landscape",
        apply_standalone_policy=False,
    )

    assert request.prompt == compiled
    assert "centered and clearly separated" not in request.prompt
    assert request.parameters["asset_policy"] == "portfolio_compiled_contract_v2"
    assert request.parameters["prompt_mode"] == "portfolio_compiled"


def test_conditional_model_profile_is_blocked_before_worker_routing():
    with pytest.raises(TermuxControlError, match="not an active free production profile"):
        profile_for("qwen-image")


def test_provider_model_catalog_is_local_and_exposes_readiness():
    result = runner.invoke(app, ["provider", "models", "--json"])

    assert result.exit_code == 0, result.output
    records = __import__("json").loads(result.output)
    assert records[0]["profile"] == "z-image-turbo"
    assert records[0]["readiness"] == "verified_free"
    assert any(item["profile"] == "qwen-image" and item["readiness"] == "conditional" for item in records)


def test_hero_landscape_canvas_preserves_pixel_budget_and_provenance():
    request = profile_for("z-image-turbo").request(
        "thick recycled-fiber paper arch",
        seed=137,
        canvas="hero-landscape",
    )

    assert (request.width, request.height) == (1344, 768)
    assert request.parameters["canvas"] == "hero-landscape"
    assert request.width * request.height <= 1024 * 1024


def test_canvas_rejects_arbitrary_dimensions():
    with pytest.raises(TermuxControlError, match="Unsupported canvas"):
        canvas_dimensions("2048x1024")


def test_configured_worker_routes_only_supported_profile(tmp_path: Path):
    config = configure_remote_provider(
        workspace=tmp_path,
        provider_id="zerogpu",
        endpoint="https://example.invalid",
        profile_names=("z-image-turbo",),
        score=10,
    )
    request = profile_for("z-image-turbo").request("single translucent resin pebble")

    selected = route_remote_generation(
        workspace=tmp_path,
        request=request,
        output_dir=tmp_path / "provider-output",
    )

    assert selected.capabilities.provider_id == "zerogpu"
    assert selected.provider.descriptor.id == config.provider_id


def test_route_rejects_unsupported_model(tmp_path: Path):
    configure_remote_provider(
        workspace=tmp_path,
        provider_id="zerogpu",
        endpoint="https://example.invalid",
        profile_names=("z-image-turbo",),
    )
    request = GenerationRequest(prompt="text asset", model_id="qwen-image", width=1024, height=1024, steps=8)

    with pytest.raises(ProviderRoutingError):
        route_remote_generation(
            workspace=tmp_path,
            request=request,
            output_dir=tmp_path / "provider-output",
        )


def test_provider_configuration_rejects_non_http_endpoint(tmp_path: Path):
    with pytest.raises(TermuxControlError, match="absolute http"):
        configure_remote_provider(
            workspace=tmp_path,
            provider_id="invalid",
            endpoint="not-a-url",
        )


def test_claiming_known_job_does_not_take_other_queued_job(tmp_path: Path):
    database = JobDatabase(tmp_path / "stockforge.db")
    database.initialize()
    project_id = str(uuid4())
    database.create_project(project_id, "demo", tmp_path / "project")
    jobs = JobManager(database)
    first = jobs.create(project_id=project_id, job_type="image.generate")
    second = jobs.create(project_id=project_id, job_type="image.generate")

    claimed = jobs.claim(second.id, "termux-test")

    assert claimed.id == second.id
    assert claimed.status == "running"
    assert database.get_job(first.id).status == "queued"


def test_termux_generate_dry_run_is_provider_profiled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))

    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0
    configured = runner.invoke(
        app,
        [
            "provider", "configure", "--id", "zerogpu", "--endpoint", "https://example.invalid",
            "--profile", "z-image-turbo",
        ],
    )
    assert configured.exit_code == 0, configured.output

    result = runner.invoke(
        app,
        [
            "generate", "--project", "demo", "--prompt", "isolated botanical asset",
            "--provider", "zerogpu", "--profile", "z-image-turbo", "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert '"dry_run": true' in result.output
    assert '"steps": 8' in result.output
    assert '"batch_size": 1' in result.output
    assert '"canvas": "square"' in result.output


def test_termux_generate_dry_run_accepts_hero_landscape_canvas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))

    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0
    configured = runner.invoke(
        app,
        [
            "provider", "configure", "--id", "zerogpu", "--endpoint", "https://example.invalid",
            "--profile", "z-image-turbo",
        ],
    )
    assert configured.exit_code == 0, configured.output

    result = runner.invoke(
        app,
        [
            "generate", "--project", "demo", "--prompt", "isolated material arch",
            "--provider", "zerogpu", "--profile", "z-image-turbo",
            "--canvas", "hero-landscape", "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert '"canvas": "hero-landscape"' in result.output
    assert '"width": 1344' in result.output
    assert '"height": 768' in result.output


def test_kaggle_controller_validates_checked_in_worker(monkeypatch: pytest.MonkeyPatch):
    from stockforge.kaggle_worker import validate_local

    monkeypatch.delenv("STOCKFORGE_KAGGLE_DIR", raising=False)
    info = validate_local()

    assert info["metadata"]["code_file"] == "worker.py"
    assert info["code_file"].endswith("deploy/kaggle/worker.py")
