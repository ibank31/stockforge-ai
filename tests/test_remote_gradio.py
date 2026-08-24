from pathlib import Path

from stockforge.generation import GenerationRequest
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
