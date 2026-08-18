"""Vendor-neutral image generation contracts.

The core deliberately knows nothing about HTTP, ComfyUI, Diffusers, or any
other provider. Adapters translate this contract at the execution boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

GENERATION_SCHEMA_VERSION = 1
GENERATION_STATUSES = frozenset({"succeeded", "failed"})


class GenerationError(ValueError):
    """Raised when a generation request or result violates the contract."""


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Provider-neutral description of one controlled generation operation."""

    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    steps: int = 30
    guidance_scale: float = 7.0
    seed: int | None = None
    batch_size: int = 1
    model_id: str | None = None
    model_version: str | None = None
    workflow_hash: str | None = None
    input_artifact_ids: tuple[str, ...] = ()
    parameters: dict[str, Any] = field(default_factory=dict)
    schema_version: int = GENERATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != GENERATION_SCHEMA_VERSION:
            raise GenerationError(f"Unsupported generation schema: {self.schema_version}")
        if not self.prompt.strip():
            raise GenerationError("prompt must be non-empty")
        if self.width < 1 or self.height < 1:
            raise GenerationError("width and height must be positive")
        if self.steps < 1:
            raise GenerationError("steps must be positive")
        if self.guidance_scale < 0:
            raise GenerationError("guidance_scale must be non-negative")
        if self.seed is not None and (self.seed < 0 or isinstance(self.seed, bool)):
            raise GenerationError("seed must be a non-negative integer or null")
        if not 1 <= self.batch_size <= 100:
            raise GenerationError("batch_size must be between 1 and 100")
        if not all(isinstance(item, str) and item for item in self.input_artifact_ids):
            raise GenerationError("input_artifact_ids must contain non-empty strings")
        if not isinstance(self.parameters, dict):
            raise GenerationError("parameters must be an object")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "guidance_scale": self.guidance_scale,
            "seed": self.seed,
            "batch_size": self.batch_size,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "workflow_hash": self.workflow_hash,
            "input_artifact_ids": list(self.input_artifact_ids),
            "parameters": self.parameters,
        }


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Provider-neutral outcome returned by a generator adapter."""

    status: Literal["succeeded", "failed"]
    artifact_ids: tuple[str, ...] = ()
    provider_job_id: str | None = None
    model_id: str | None = None
    model_version: str | None = None
    workflow_hash: str | None = None
    seed: int | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    schema_version: int = GENERATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != GENERATION_SCHEMA_VERSION:
            raise GenerationError(f"Unsupported generation schema: {self.schema_version}")
        if self.status not in GENERATION_STATUSES:
            raise GenerationError(f"Unsupported generation status: {self.status}")
        if not all(isinstance(item, str) and item for item in self.artifact_ids):
            raise GenerationError("artifact_ids must contain non-empty strings")
        if self.seed is not None and (self.seed < 0 or isinstance(self.seed, bool)):
            raise GenerationError("seed must be a non-negative integer or null")
        if not isinstance(self.parameters, dict):
            raise GenerationError("parameters must be an object")
        if self.status == "succeeded":
            if not self.artifact_ids:
                raise GenerationError("successful generation must return at least one artifact")
            if self.error_code is not None or self.error_message is not None:
                raise GenerationError("successful generation cannot contain an error")
        elif not self.error_code or not self.error_message:
            raise GenerationError("failed generation requires error_code and error_message")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status,
            "artifact_ids": list(self.artifact_ids),
            "provider_job_id": self.provider_job_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "workflow_hash": self.workflow_hash,
            "seed": self.seed,
            "parameters": self.parameters,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


class ImageGenerator:
    """Structural generator interface implemented by provider adapters."""

    def generate(self, request: GenerationRequest) -> GenerationResult:  # pragma: no cover - interface
        raise NotImplementedError
