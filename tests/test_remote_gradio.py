from pathlib import Path

from stockforge.generation import GenerationRequest, GenerationResult
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


def test_remote_provider_completed_state_is_terminal(tmp_path: Path):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    result = GenerationResult(status="succeeded", artifact_ids=("provider:job:0",), provider_job_id="job")
    provider._jobs["job"] = ProviderJob("job", "completed", result=result)

    assert provider.status("job").state == "completed"
    assert provider.wait("job", timeout_seconds=0.1).state == "completed"


def test_remote_provider_advertises_single_image_batch_limit(tmp_path: Path):
    provider = RemoteGradioProvider(
        provider_id="huggingface-zerogpu",
        base_url="https://example.invalid",
        output_dir=tmp_path,
    )
    capabilities = provider.capabilities()
    assert capabilities.provider_id == "huggingface-zerogpu"
    assert capabilities.max_batch_size == 1
