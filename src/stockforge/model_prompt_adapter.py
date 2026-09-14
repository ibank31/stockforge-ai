"""Model-specific prompt adapters for StockForge V2.

GenerationBrief is provider-neutral. Adapters render provider-specific prompt
packages without changing the underlying creative intent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .generation_brief import GenerationBrief


@dataclass(frozen=True, slots=True)
class RenderedPrompt:
    model_id: str
    prompt: str
    negative_prompt: str
    parameters: dict[str, object]


class PromptAdapter(Protocol):
    model_id: str
    def render(self, brief: GenerationBrief) -> RenderedPrompt: ...


class ZImageTurboAdapter:
    model_id = "z-image-turbo"

    def render(self, brief: GenerationBrief) -> RenderedPrompt:
        prompt = (
            f"{brief.subject}. {brief.composition}. {brief.viewpoint}. "
            f"{brief.color_direction}. {brief.context}. "
            f"Commercial use: {brief.use_case}. Market intent: {brief.market_intent}. "
            "Create an original visual interpretation, not a reproduction of the reference. "
            f"Differentiation: {'; '.join(brief.differentiation_rationale)}."
        )
        return RenderedPrompt(
            model_id=self.model_id,
            prompt=prompt,
            negative_prompt="duplicate composition, copied reference, watermark, text, logo, people, hands, fingers, face, body",
            parameters={"reference_mode": "intent_only"},
        )


class FluxAdapter:
    model_id = "flux"

    def render(self, brief: GenerationBrief) -> RenderedPrompt:
        prompt = (
            f"Original commercial stock asset of {brief.subject}, "
            f"{brief.composition}, viewed from {brief.viewpoint}, "
            f"{brief.color_direction}, {brief.context}. "
            f"Designed for {brief.use_case}. "
            f"Must substantially differ from source reference across: {', '.join(brief.changed_dimensions)}."
        )
        return RenderedPrompt(
            model_id=self.model_id,
            prompt=prompt,
            negative_prompt="reference duplication, watermark, logo, text",
            parameters={"guidance": "provider_default", "reference_mode": "intent_only"},
        )


class GeminiImageAdapter:
    model_id = "gemini-image"

    def render(self, brief: GenerationBrief) -> RenderedPrompt:
        prompt = (
            "Generate a commercially useful, clearly original image.\n"
            f"Subject: {brief.subject}\n"
            f"Composition: {brief.composition}\n"
            f"Viewpoint: {brief.viewpoint}\n"
            f"Color direction: {brief.color_direction}\n"
            f"Context: {brief.context}\n"
            f"Use case: {brief.use_case}\n"
            f"Originality constraints: change {', '.join(brief.changed_dimensions)} relative to the reference intent."
        )
        return RenderedPrompt(
            model_id=self.model_id,
            prompt=prompt,
            negative_prompt="Do not recreate or closely imitate the reference image.",
            parameters={"reference_mode": "intent_only", "safety": "commercial_originality"},
        )


_ADAPTERS: dict[str, PromptAdapter] = {
    "z-image-turbo": ZImageTurboAdapter(),
    "flux": FluxAdapter(),
    "gemini-image": GeminiImageAdapter(),
}


def render_generation_prompt(brief: GenerationBrief, model_id: str) -> RenderedPrompt:
    try:
        adapter = _ADAPTERS[model_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported model adapter: {model_id}") from exc
    return adapter.render(brief)
