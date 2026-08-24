from pathlib import Path

from stockforge.generation import GenerationRequest
from stockforge.generation_provider import ProviderJob
from stockforge.remote_gradio import RemoteGradioProvider


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
        'event: heartbeat\ndata: null\n\n'
        'event: complete\n'
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


def test_remote_provider_uses_live_v2_named_generate_contract(tmp_path: Path, monkeypatch):
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
    job = provider.submit(GenerationRequest(prompt="commercial botanical asset", seed=42), provider_job_id="job-123")

    assert job.provider_job_id == "job-123"
    assert captured == {
        "method": "POST",
        "path": "/gradio_api/call/v2/generate",
        "payload": {
            "prompt": "commercial botanical asset",
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "seed": 42,
            "randomize_seed": False,
        },
    }


def test_remote_provider_wait_returns_completed_job(tmp_path: Path, monkeypatch):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    completed = ProviderJob("job-123", "completed")
    monkeypatch.setattr(provider, "status", lambda _: completed)

    assert provider.wait("job-123", timeout_seconds=0.1) == completed
