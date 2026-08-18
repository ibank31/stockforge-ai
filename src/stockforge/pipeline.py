"""Vendor-neutral pipeline definition and deterministic execution contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

PIPELINE_SCHEMA_VERSION = 1


class PipelineError(ValueError):
    """Raised when a pipeline definition or execution is invalid."""


@dataclass(frozen=True, slots=True)
class PipelineStep:
    """One executable step in a linear pipeline."""

    id: str
    plugin_id: str
    capability: str
    input_key: str = "input"
    output_key: str = "output"
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name, value in (("id", self.id), ("plugin_id", self.plugin_id), ("capability", self.capability)):
            if not value or len(value) > 128:
                raise PipelineError(f"{field_name} must be between 1 and 128 characters.")
        if not self.input_key or not self.output_key:
            raise PipelineError("input_key and output_key must be non-empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "plugin_id": self.plugin_id,
            "capability": self.capability,
            "input_key": self.input_key,
            "output_key": self.output_key,
            "parameters": dict(self.parameters),
        }


@dataclass(frozen=True, slots=True)
class PipelineDefinition:
    """Serializable pipeline contract independent of any provider."""

    id: str
    version: int
    steps: tuple[PipelineStep, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = PIPELINE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.id or len(self.id) > 128:
            raise PipelineError("Pipeline id must be between 1 and 128 characters.")
        if self.schema_version != PIPELINE_SCHEMA_VERSION:
            raise PipelineError("Unsupported pipeline schema version.")
        if self.version < 1:
            raise PipelineError("Pipeline version must be >= 1.")
        if not self.steps:
            raise PipelineError("Pipeline must contain at least one step.")
        ids = [step.id for step in self.steps]
        if len(ids) != len(set(ids)):
            raise PipelineError("Pipeline step ids must be unique.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "version": self.version,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class PipelineResult:
    outputs: Mapping[str, Any]
    completed_steps: tuple[str, ...]


class PipelineRunner:
    """Execute registered plugins sequentially without provider coupling."""

    def __init__(self, registry: Any) -> None:
        self.registry = registry

    def run(self, definition: PipelineDefinition, initial_input: Mapping[str, Any]) -> PipelineResult:
        state: dict[str, Any] = dict(initial_input)
        completed: list[str] = []
        for step in definition.steps:
            plugin = self.registry.get(step.plugin_id)
            if step.capability not in plugin.descriptor.capabilities:
                raise PipelineError(f"Plugin '{step.plugin_id}' does not provide capability '{step.capability}'.")
            raw_input = state.get(step.input_key, {})
            if not isinstance(raw_input, dict):
                raise PipelineError(f"Pipeline input '{step.input_key}' must be an object.")
            payload = dict(raw_input)
            payload["parameters"] = dict(step.parameters)
            try:
                result = plugin.execute(payload)
            except Exception as exc:
                raise PipelineError(f"Pipeline step '{step.id}' failed: {exc}") from exc
            if not isinstance(result, dict):
                raise PipelineError(f"Pipeline step '{step.id}' returned a non-object result.")
            state[step.output_key] = result
            completed.append(step.id)
        return PipelineResult(outputs=state, completed_steps=tuple(completed))
