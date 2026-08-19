"""ComfyUI provider adapter.

The adapter owns ComfyUI's HTTP payloads and history shape. StockForge core only
sees ProviderJob and GenerationRequest contracts. Network I/O is injectable so
unit tests never require a running ComfyUI instance.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any, Protocol

from .generation import GenerationRequest, GenerationResult
from .generation_provider import GenerationProvider, ProviderJob, ProviderRuntimeError
from .plugin import PluginDescriptor
from .provider import ProviderConfig, ProviderConfigError

COMFYUI_PROVIDER_KIND = "comfyui"
COMFYUI_WORKFLOW_PARAMETER = "comfyui_workflow"
ProviderError = ProviderRuntimeError


class ComfyUIClient(Protocol):
    """Minimal transport contract used by the adapter."""

    def queue_prompt(self, workflow: dict[str, Any], *, client_id: str) -> dict[str, Any]: ...
    def get_history(self, prompt_id: str) -> dict[str, Any]: ...
    def interrupt(self, prompt_id: str) -> None: ...


class ComfyUIHTTPError(ProviderError):
    """Raised for transport or non-success HTTP responses."""


class ComfyUIHttpClient:
    """Small dependency-free HTTP client for the native ComfyUI API."""

    def __init__(self, endpoint: str, *, api_key: str | None = None, timeout: float = 60.0) -> None:
        if not endpoint or not isinstance(endpoint, str):
            raise ProviderError("ComfyUI endpoint must be a non-empty string")
        if timeout <= 0:
            raise ProviderError("ComfyUI timeout must be positive")
        self._base_url = endpoint.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    def _request(self, path: str, *, method: str, payload: dict[str, Any] | None = None) -> Any:
        url = urllib.parse.urljoin(self._base_url + "/", path.lstrip("/"))
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            raise ComfyUIHTTPError(f"ComfyUI HTTP error: {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ComfyUIHTTPError("ComfyUI transport failure") from exc
        if not body:
            return None
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ComfyUIHTTPError("ComfyUI returned invalid JSON") from exc

    def queue_prompt(self, workflow: dict[str, Any], *, client_id: str) -> dict[str, Any]:
        response = self._request("/prompt", method="POST", payload={"prompt": workflow, "client_id": client_id})
        if not isinstance(response, dict):
            raise ComfyUIHTTPError("ComfyUI /prompt returned an invalid response")
        return response

    def get_history(self, prompt_id: str) -> dict[str, Any]:
        response = self._request(f"/history/{urllib.parse.quote(prompt_id, safe='')}", method="GET")
        if not isinstance(response, dict):
            raise ComfyUIHTTPError("ComfyUI /history returned an invalid response")
        return response

    def interrupt(self, prompt_id: str) -> None:
        self._request("/interrupt", method="POST", payload={"prompt_id": prompt_id})


def workflow_hash(workflow: dict[str, Any]) -> str:
    """Return a deterministic SHA-256 hash of an API-format workflow."""
    if not isinstance(workflow, dict) or not workflow:
        raise ProviderError("ComfyUI workflow must be a non-empty object")
    canonical = json.dumps(workflow, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _history_entry(history: dict[str, Any], prompt_id: str) -> dict[str, Any] | None:
    """Normalize both /history/{id} and test-double history shapes."""
    if not isinstance(history, dict):
        return None
    direct = history.get(prompt_id)
    if isinstance(direct, dict):
        return direct
    if "status" in history or "outputs" in history:
        return history
    return None


def extract_output_refs(history: dict[str, Any], prompt_id: str) -> tuple[dict[str, str], ...]:
    """Extract provider output references without pretending they are artifacts."""
    entry = _history_entry(history, prompt_id)
    if entry is None:
        return ()
    outputs = entry.get("outputs", {})
    if not isinstance(outputs, dict):
        return ()
    refs: list[dict[str, str]] = []
    for node_id, node_output in outputs.items():
        if not isinstance(node_output, dict):
            continue
        images = node_output.get("images", [])
        if not isinstance(images, list):
            continue
        for image in images:
            if not isinstance(image, dict) or not image.get("filename"):
                continue
            refs.append(
                {
                    "node_id": str(node_id),
                    "filename": str(image["filename"]),
                    "subfolder": str(image.get("subfolder", "")),
                    "type": str(image.get("type", "output")),
                }
            )
    return tuple(refs)


class ComfyUIProvider(GenerationProvider):
    """Asynchronous ComfyUI adapter using the native /prompt + /history API."""

    def __init__(self, config: ProviderConfig, *, client: ComfyUIClient | None = None, client_id: str | None = None) -> None:
        if not config.enabled:
            raise ProviderError(f"Provider {config.id!r} is disabled")
        timeout = float(config.options.get("timeout_seconds", 60))
        self.config = config
        self._client_id = client_id or str(uuid.uuid4())
        if client is None:
            if not config.endpoint:
                raise ProviderConfigError("ComfyUI provider requires an endpoint")
            api_key = config.resolve_secret()
            self._client = ComfyUIHttpClient(config.endpoint, api_key=api_key, timeout=timeout)
        else:
            self._client = client
        self._poll_interval = float(config.options.get("poll_interval_seconds", 1.0))
        if self._poll_interval <= 0:
            raise ProviderError("poll_interval_seconds must be positive")

    @property
    def descriptor(self) -> PluginDescriptor:
        return PluginDescriptor(
            id=self.config.id,
            name="ComfyUI",
            version="native-api-v1",
            kind="generator",
            capabilities=frozenset({"image.generate", "generation.async", "generation.cancel"}),
            description="Native ComfyUI asynchronous image generation adapter.",
        )

    def _workflow(self, request: GenerationRequest) -> dict[str, Any]:
        workflow = request.parameters.get(COMFYUI_WORKFLOW_PARAMETER)
        if not isinstance(workflow, dict) or not workflow:
            raise ProviderError(f"Generation request requires parameters[{COMFYUI_WORKFLOW_PARAMETER!r}]")
        calculated_hash = workflow_hash(workflow)
        if request.workflow_hash is not None and request.workflow_hash != calculated_hash:
            raise ProviderError("Generation workflow_hash does not match the supplied ComfyUI workflow")
        return workflow

    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise ProviderError("ComfyUI provider is asynchronous; use submit/status")

    def submit(self, request: GenerationRequest) -> ProviderJob:
        workflow = self._workflow(request)
        response = self._client.queue_prompt(workflow, client_id=self._client_id)
        prompt_id = response.get("prompt_id") if isinstance(response, dict) else None
        if not isinstance(prompt_id, str) or not prompt_id:
            if isinstance(response, dict) and response.get("error"):
                raise ProviderError("ComfyUI rejected workflow validation")
            raise ProviderError("ComfyUI /prompt response did not contain prompt_id")
        return ProviderJob(provider_job_id=prompt_id, state="submitted")

    def status(self, provider_job_id: str) -> ProviderJob:
        if not provider_job_id:
            raise ProviderError("provider_job_id must be non-empty")
        history = self._client.get_history(provider_job_id)
        entry = _history_entry(history, provider_job_id)
        if entry is None:
            return ProviderJob(provider_job_id=provider_job_id, state="running")
        status = entry.get("status")
        status_str = status.get("status_str") if isinstance(status, dict) else None
        if status_str in {"error", "failed"}:
            return ProviderJob(provider_job_id=provider_job_id, state="failed", error_code="COMFYUI_EXECUTION_FAILED", error_message="ComfyUI reported workflow execution failure")
        if status_str in {"interrupted", "cancelled"}:
            return ProviderJob(provider_job_id=provider_job_id, state="cancelled")
        if isinstance(status, dict) and status.get("completed") is True:
            return ProviderJob(provider_job_id=provider_job_id, state="completed")
        return ProviderJob(provider_job_id=provider_job_id, state="running")

    def cancel(self, provider_job_id: str) -> ProviderJob:
        if not provider_job_id:
            raise ProviderError("provider_job_id must be non-empty")
        self._client.interrupt(provider_job_id)
        return ProviderJob(provider_job_id=provider_job_id, state="cancelled")

    def output_refs(self, provider_job_id: str) -> tuple[dict[str, str], ...]:
        history = self._client.get_history(provider_job_id)
        return extract_output_refs(history, provider_job_id)

    def wait(self, provider_job_id: str, *, timeout_seconds: float = 600.0) -> ProviderJob:
        """Poll until a provider terminal state, without creating StockForge artifacts."""
        if timeout_seconds <= 0:
            raise ProviderError("timeout_seconds must be positive")
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            job = self.status(provider_job_id)
            if job.state in {"completed", "failed", "cancelled"}:
                return job
            time.sleep(self._poll_interval)
        raise ProviderError("ComfyUI provider polling timed out")
