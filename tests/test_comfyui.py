import pytest

from stockforge.comfyui import ComfyUIProvider, extract_output_refs, workflow_hash
from stockforge.generation import GenerationRequest
from stockforge.generation_provider import ProviderRuntimeError
from stockforge.provider import ProviderConfig


class FakeComfyUI:
    def __init__(self, histories=None):
        self.queued = []
        self.interrupted = []
        self.histories = histories or {}

    def queue_prompt(self, workflow, *, client_id, prompt_id=None):
        self.queued.append((workflow, client_id, prompt_id))
        return {"prompt_id": prompt_id or "prompt-123"}

    def get_history(self, prompt_id):
        return self.histories.get(prompt_id, {})

    def interrupt(self, prompt_id):
        self.interrupted.append(prompt_id)


def workflow():
    return {"1": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024}}}


def request():
    wf = workflow()
    return GenerationRequest(prompt="commercial stock photo", workflow_hash=workflow_hash(wf), parameters={"comfyui_workflow": wf})


def provider(fake):
    return ComfyUIProvider(ProviderConfig(id="comfyui.local", kind="comfyui"), client=fake, client_id="client-1")


def test_workflow_hash_is_deterministic():
    assert workflow_hash({"b": 2, "a": 1}) == workflow_hash({"a": 1, "b": 2})


def test_submit_returns_provider_job_without_artifact_ids():
    fake = FakeComfyUI()
    job = provider(fake).submit(request())
    assert job.provider_job_id == "prompt-123"
    assert job.state == "submitted"
    assert fake.queued == [(workflow(), "client-1", None)]


def test_submit_can_reuse_durable_provider_identity():
    fake = FakeComfyUI()
    job = provider(fake).submit(request(), provider_job_id="execution-123")
    assert job.provider_job_id == "execution-123"
    assert fake.queued[-1] == (workflow(), "client-1", "execution-123")


def test_durable_identity_mismatch_is_rejected():
    class Mismatch(FakeComfyUI):
        def queue_prompt(self, workflow, *, client_id, prompt_id=None):
            return {"prompt_id": "different-id"}

    with pytest.raises(ProviderRuntimeError, match="different prompt_id"):
        provider(Mismatch()).submit(request(), provider_job_id="execution-123")


def test_completed_provider_job_waits_for_artifact_ingestion():
    history = {"prompt-123": {"status": {"status_str": "success", "completed": True}, "outputs": {"9": {"images": [{"filename": "hero.png", "subfolder": "", "type": "output"}]}}}}
    fake = FakeComfyUI(history)
    comfy = provider(fake)
    assert comfy.status("prompt-123").state == "completed"
    assert comfy.output_refs("prompt-123") == ({"node_id": "9", "filename": "hero.png", "subfolder": "", "type": "output"},)


def test_failure_is_structured():
    fake = FakeComfyUI({"prompt-123": {"status": {"status_str": "error", "completed": True}}})
    job = provider(fake).status("prompt-123")
    assert job.state == "failed"
    assert job.error_code == "COMFYUI_EXECUTION_FAILED"


def test_cancel_is_targeted():
    fake = FakeComfyUI()
    job = provider(fake).cancel("prompt-123")
    assert job.state == "cancelled"
    assert fake.interrupted == ["prompt-123"]


def test_workflow_hash_mismatch_is_rejected():
    wf = workflow()
    bad = GenerationRequest(prompt="commercial stock photo", workflow_hash="not-the-real-hash", parameters={"comfyui_workflow": wf})
    with pytest.raises(ProviderRuntimeError, match="workflow_hash"):
        provider(FakeComfyUI()).submit(bad)


def test_missing_workflow_is_rejected():
    with pytest.raises(ProviderRuntimeError, match="comfyui_workflow"):
        provider(FakeComfyUI()).submit(GenerationRequest(prompt="commercial stock photo"))


def test_output_refs_ignore_non_image_outputs():
    history = {"p": {"outputs": {"1": {"text": "not an image"}, "2": {"images": [{"filename": "a.png"}]}}}}
    assert extract_output_refs(history, "p") == ({"node_id": "2", "filename": "a.png", "subfolder": "", "type": "output"},)
