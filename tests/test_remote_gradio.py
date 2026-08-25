from pathlib import Path

from io import BytesIO
from urllib.error import HTTPError

import pytest

from stockforge.generation import GenerationRequest, GenerationResult
from stockforge.generation_provider import ProviderJob
from stockforge.remote_gradio import RemoteGradioError, RemoteGradioProvider


def test_remote_provider_uses_deterministic_stockforge_job_id(tmp_path: Path):
    request = GenerationRequest(prompt="commercial stock photo")
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    first = provider._new_job_id(request)
    second = provider._new_job_id(request)
    assert first == second
    assert first.startswith("sf-")


def test_remote_provider_parses_last_complete_sse_event(tmp_path: Path):
    provider = RemoteGradioProvider(
        provider_id="kaggle-worker",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    event, data = provider._last_sse_event(
        "event: heartbeat\ndata: null\n\n"
        "event: complete\n"
        'data: [{"path":"/tmp/result.png","url":"https://example/result.png"}, 42, 1.2]\n'
    )
    assert event == "complete"
    assert '"url":"https://example/result.png"' in data


def test_remote_provider_creates_missing_output_directory(tmp_path: Path):
    output_dir = tmp_path / "missing" / "provider-output"
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=output_dir,
    )
    assert provider.output_dir == output_dir.resolve()
    assert output_dir.is_dir()


def test_remote_provider_uses_live_generate_remote_contract(
    tmp_path: Path, monkeypatch
):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    captured = {}

    def fake_request(method, path, payload):
        captured.update({"method": method, "path": path, "payload": payload})
        return {"event_id": "event-123"}

    monkeypatch.setattr(provider, "_request_json", fake_request)
    job = provider.submit(
        GenerationRequest(prompt="commercial botanical asset", seed=42),
        provider_job_id="job-123",
    )

    assert job.provider_job_id == "job-123"
    assert captured == {
        "method": "POST",
        "path": "/gradio_api/call/generate_remote",
        "payload": {
            "data": [
                "commercial botanical asset",
                1024,
                1024,
                30,
                42,
                False,
                "job-123",
            ]
        },
    }


def test_active_zerogpu_app_registers_generate_remote_endpoint():
    app_source = Path("deploy/zerogpu/app.py").read_text(encoding="utf-8")

    assert "def generate_remote(" in app_source
    assert 'api_name="generate_remote"' in app_source
    assert "remote_job_id" in app_source


def test_remote_provider_surfaces_http_error_body(tmp_path: Path, monkeypatch):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )

    def fail(*_args, **_kwargs):
        raise HTTPError(
            "https://example.invalid/gradio_api/call/generate_remote",
            500,
            "Internal Server Error",
            hdrs=None,
            fp=BytesIO(b"worker model load failed"),
        )

    monkeypatch.setattr("urllib.request.urlopen", fail)

    with pytest.raises(RemoteGradioError, match="HTTP 500.*worker model load failed"):
        provider._request_json("POST", "/gradio_api/call/generate_remote", {"data": []})


def test_remote_provider_wait_returns_completed_job(tmp_path: Path, monkeypatch):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    result = GenerationResult(
        status="succeeded",
        artifact_ids=("provider:job-123:0",),
        provider_job_id="job-123",
    )
    completed = ProviderJob("job-123", "completed", result=result)
    monkeypatch.setattr(provider, "status", lambda _: completed)

    assert provider.wait("job-123", timeout_seconds=0.1) == completed


def test_remote_provider_advertises_single_image_batch_limit(tmp_path: Path):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    capabilities = provider.capabilities()
    assert capabilities.provider_id == "huggingface-zerogpu"
    assert capabilities.max_batch_size == 1


def test_remote_provider_rejects_non_positive_timeout(tmp_path: Path):
    with pytest.raises(RemoteGradioError, match="timeout_seconds must be positive"):
        RemoteGradioProvider(
            provider_id="huggingface-zerogpu",
            base_url="https://example.invalid",
            output_dir=tmp_path,
            timeout_seconds=0,
        )
