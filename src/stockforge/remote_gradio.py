"""Provider adapter for remote Gradio/Spaces generation workers."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

from .generation import GenerationRequest, GenerationResult
from .generation_provider import GenerationProvider, ProviderJob, ProviderRuntimeError
from .plugin import PluginDescriptor


class RemoteGradioError(ProviderRuntimeError):
    """Raised when a remote Gradio worker cannot complete a generation."""


class RemoteGradioProvider(GenerationProvider):
    """Call a Gradio worker using POST -> event_id -> SSE completion."""

    def __init__(self, *, provider_id: str, base_url: str, output_dir: Path, token: str | None = None, api_name: str = "generate_remote", timeout_seconds: float = 300.0, capabilities: frozenset[str] | None = None) -> None:
        self.provider_id = provider_id
        self.base_url = base_url.rstrip("/")
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.token = token
        self.api_name = api_name.strip("/")
        self.timeout_seconds = timeout_seconds
        self._jobs: dict[str, ProviderJob] = {}
        self._events: dict[str, str] = {}
        self._outputs: dict[str, tuple[dict[str, Any], ...]] = {}
        self._capabilities = capabilities or frozenset({"image.generate", "image.generate.remote"})

    @property
    def descriptor(self) -> PluginDescriptor:
        return PluginDescriptor(id=self.provider_id, name=f"Remote Gradio ({self.provider_id})", version="1.0.0", api_version="1", kind="generator", capabilities=self._capabilities)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        job = self.submit(request)
        terminal = self.wait(job.provider_job_id)
        if terminal.state not in {"completed", "succeeded"} or terminal.result is None:
            raise RemoteGradioError(terminal.error_message or "Remote generation failed")
        return terminal.result

    def submit(self, request: GenerationRequest, *, provider_job_id: str | None = None) -> ProviderJob:
        durable_id = provider_job_id or self._new_job_id(request)
        existing = self._jobs.get(durable_id)
        if existing is not None:
            return existing
        payload = {"data": [request.prompt, request.width, request.height, request.steps, request.seed or 0, request.seed is None, durable_id]}
        event = self._request_json("POST", f"/gradio_api/call/{self.api_name}", payload)
        event_id = str(event.get("event_id") or "")
        if not event_id:
            raise RemoteGradioError("Remote worker did not return event_id")
        self._events[durable_id] = event_id
        job = ProviderJob(durable_id, "submitted")
        self._jobs[durable_id] = job
        return job

    def status(self, provider_job_id: str) -> ProviderJob:
        cached = self._jobs.get(provider_job_id)
        if cached is None:
            raise RemoteGradioError(f"Unknown provider job: {provider_job_id}")
        if cached.state in {"succeeded", "failed", "cancelled"}:
            return cached
        return self._poll(provider_job_id)

    def wait(self, provider_job_id: str) -> ProviderJob:
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            current = self.status(provider_job_id)
            if current.state in {"succeeded", "failed", "cancelled"}:
                return current
            time.sleep(1.0)
        failed = ProviderJob(provider_job_id, "failed", error_code="provider_timeout", error_message="Remote generation timed out")
        self._jobs[provider_job_id] = failed
        return failed

    def cancel(self, provider_job_id: str) -> ProviderJob:
        raise RemoteGradioError("Generic Gradio workers do not expose a portable cancellation contract")

    def output_refs(self, provider_job_id: str) -> tuple[dict[str, Any], ...]:
        return self._outputs.get(provider_job_id, ())

    def _poll(self, durable_id: str) -> ProviderJob:
        event_id = self._events.get(durable_id)
        if not event_id:
            raise RemoteGradioError(f"No remote event identity for job: {durable_id}")
        response = self._request_text("GET", f"/gradio_api/call/{self.api_name}/{event_id}")
        event, data = self._last_sse_event(response)
        if event == "complete":
            values = json.loads(data)
            if not isinstance(values, list) or not values:
                raise RemoteGradioError("Gradio completed without output data")
            refs = self._materialize_outputs(values[0], durable_id)
            self._outputs[durable_id] = refs
            result = GenerationResult(status="succeeded", artifact_ids=(f"provider:{durable_id}:0",), provider_job_id=durable_id, seed=int(values[1]) if len(values) > 1 and values[1] is not None else None, parameters={"remote_provider": self.provider_id, "gpu_seconds": values[2] if len(values) > 2 else None})
            job = ProviderJob(durable_id, "completed", result=result)
        elif event in {"error", "exception"}:
            job = ProviderJob(durable_id, "failed", error_code="remote_generation_failed", error_message=data or event)
        else:
            job = ProviderJob(durable_id, "running")
        self._jobs[durable_id] = job
        return job

    def _materialize_outputs(self, output: Any, job_id: str) -> tuple[dict[str, Any], ...]:
        items = output if isinstance(output, list) else [output]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        refs: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict) or not item.get("url"):
                raise RemoteGradioError("Remote output is not a downloadable Gradio FileData object")
            suffix = Path(str(item.get("orig_name") or "output.png")).suffix or ".png"
            filename = f"{job_id}-{index}{suffix}"
            self._download(str(item["url"]), self.output_dir / filename)
            refs.append({"filename": filename, "subfolder": "", "type": "output"})
        return tuple(refs)

    def _download(self, url: str, target: Path) -> None:
        request = urllib.request.Request(url, method="GET")
        self._add_auth(request)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response, target.open("wb") as handle:
            handle.write(response.read())

    def _request_json(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(self.base_url + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method=method)
        self._add_auth(request)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            value = json.loads(response.read().decode("utf-8"))
        if not isinstance(value, dict):
            raise RemoteGradioError("Remote worker returned a non-object response")
        return value

    def _request_text(self, method: str, path: str) -> str:
        request = urllib.request.Request(self.base_url + path, method=method)
        self._add_auth(request)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return response.read().decode("utf-8")

    def _add_auth(self, request: urllib.request.Request) -> None:
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")

    @staticmethod
    def _last_sse_event(text: str) -> tuple[str, str]:
        events: list[tuple[str, str]] = []
        current_event = "message"
        current_data: list[str] = []
        for line in text.splitlines():
            if line.startswith("event:"):
                if current_data:
                    events.append((current_event, "\n".join(current_data)))
                current_event = line[6:].strip()
                current_data = []
            elif line.startswith("data:"):
                current_data.append(line[5:].lstrip())
        if current_data:
            events.append((current_event, "\n".join(current_data)))
        if not events:
            raise RemoteGradioError("Remote worker returned no SSE events")
        return events[-1]

    @staticmethod
    def _new_job_id(request: GenerationRequest) -> str:
        raw = json.dumps(request.to_dict(), sort_keys=True, separators=(",", ":"))
        return "sf-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
