import pytest

from stockforge.comfyui import ComfyUIProvider, extract_output_refs, workflow_hash
from stockforge.generation import GenerationRequest
from stockforge.provider import ProviderConfig
from stockforge.provider_runtime import ProviderError


class FakeComfyUI:
    def __init__(self, histories=None):
        self.queued = []
        self.interrupted = []
        self.histories = histories or {}

    def queue_prompt(self, workflow, *, client_id):
        self.queued.append((workflow, client_id))
        return {"prompt_id": "prompt-123"}

    def get_history(self, prompt_id):
        return self.histories.get(prompt_id, {})

    def interrupt(self, prompt_id):
        self.interrupted.append(prompt_id)


def workflow():
    return {"1": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024}}}


def request():
    wf = workflow()
    return GenerationRequest(
        prompt="commercial stock photo",
        workflow_hash=workflow_hash(wf),
        parameters={"comfyui_workflow": wf},
    )


def test_workflow_hash_is_deterministic():
    first = {"b": 2, "a": 1}
    second = {"a": 1, "b": 2}
    assert workflow_hash(first) == workflow_hash(second)


def test_submit_returns_provider_job_without_fake_artifact_ids():
    fake = FakeComfyUI()
    provider = ComfyUIProvider(
        ProviderConfig(id="comfyui.local", kind="image-generator"),
        client=fake,
        client_id="client-1",
    )
    job = provider.submit(request())
    assert job.provider_job_id == "prompt-123"
    assert job.state == "submitted"
    assert fake.queued == [(workflow(), "client-1")]


def test_completed_provider_job_waits_for_artifact_ingestion():
    history = {
        "prompt-123": {
            "status": {"status_str": "success", "completed": True},
            "outputs": {"9": {"images": [{"filename": "hero.png", "subfolder": "", "type": "output"}]}},
        }
    }
    provider = ComfyUIProvider(
        ProviderConfig(id="comfyui.local", kind="image-generator"),
        client=FakeComfyUI(history),
    )
    job = provider.status("prompt-123")
    assert job.state == "completed"
    refs = provider.output_refs("prompt-123")
    assert refs == ({"node_id": "9", "filename": "hero.png", "subfolder": "", "type": "output"},)


def test_failure_is_structured():
    history = {"prompt-123": {"status": {"status_str": "error", "completed": True}}}
    provider = ComfyUIProvider(
        ProviderConfig(id="comfyui.local", kind="image-generator"),
        client=FakeComfyUI(history),
    )
    job = provider.status("prompt-123")
    assert job.state == "failed"
    assert job.error_code == "COMFYUI_EXECUTION_FAILED"


def test_cancel_is_targeted():
    fake = FakeComfyUI()
    provider = ComfyUIProvider(
        ProviderConfig(id="comfyui.local", kind="image-generator"),
        client=fake,
    )
    job = provider.cancel("prompt-123")
    assert job.state == "cancelled"
    assert fake.interrupted == ["prompt-123"]


def test_workflow_hash_mismatch_is_rejected():
    wf = workflow()
    bad = GenerationRequest(
        prompt="commercial stock photo",
        workflow_hash="not-the-real-hash",
        parameters={"comfyui_workflow": wf},
    )
    provider = ComfyUIProvider(
        ProviderConfig(id="comfyui.local", kind="image-generator"),
        client=FakeComfyUI(),
    )
    with pytest.raises(ProviderError, match="workflow_hash"):
        provider.submit(bad)


def test_missing_workflow_is_rejected():
    provider = ComfyUIProvider(
        ProviderConfig(id="comfyui.local", kind="image-generator"),
        client=FakeComfyUI(),
    )
    with pytest.raises(ProviderError, match="comfyui_workflow"):
        provider.submit(GenerationRequest(prompt="commercial stock photo"))


def test_output_refs_ignore_non_image_outputs():
    history = {
        "p": {
            "outputs": {
                "1": {"text": "not an image"},
                "2": {"images": [{"filename": "a.png"}]},
            }
        }
    }
    assert extract_output_refs(history, "p") == (
        {"node_id": "2", "filename": "a.png", "subfolder": "", "type": "output"},
    )
