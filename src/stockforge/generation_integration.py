"""Generation integration boundary for StockForge V2.

This layer connects a provider-neutral GenerationBrief to the existing generation
transport while preserving anti-similarity intent and traceability.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .generation_brief import GenerationBrief
from .model_prompt_adapter import RenderedPrompt, render_generation_prompt


class GenerationTransport(Protocol):
    def generate(self, prompt: str, *, negative_prompt: str, parameters: dict[str, object]) -> str: ...


@dataclass(frozen=True, slots=True)
class GenerationResult:
    model_id: str
    brief_id: str
    reference_sha256: str
    artifact_path: str
    changed_dimensions: tuple[str, ...]


def execute_generation(
    brief: GenerationBrief,
    *,
    model_id: str,
    transport: GenerationTransport,
) -> GenerationResult:
    """Render a model prompt and execute it through an injected transport.

    The transport is intentionally injected so existing providers can be adapted
    without coupling V2 decision logic to one remote implementation.
    """
    rendered: RenderedPrompt = render_generation_prompt(brief, model_id)
    artifact_path = transport.generate(
        rendered.prompt,
        negative_prompt=rendered.negative_prompt,
        parameters={
            **rendered.parameters,
            "stockforge_v2_brief_id": brief.brief_id,
            "stockforge_v2_reference_sha256": brief.reference_sha256,
            "stockforge_v2_changed_dimensions": list(brief.changed_dimensions),
        },
    )
    if not artifact_path:
        raise RuntimeError("Generation transport returned no artifact path")
    return GenerationResult(
        model_id=model_id,
        brief_id=brief.brief_id,
        reference_sha256=brief.reference_sha256,
        artifact_path=artifact_path,
        changed_dimensions=brief.changed_dimensions,
    )
