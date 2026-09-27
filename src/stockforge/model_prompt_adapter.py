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


class QwenImage2512Adapter:
    """Prompt adapter for the production ZeroGPU lane.

    Qwen-Image-2512 is driven by a Qwen2.5-VL text encoder, so it responds
    best to fluent, detailed natural-language descriptions rather than
    comma-separated tag soup. The worker applies its own commercial framing
    and negative prompt, so this adapter focuses on carrying the brief's
    creative intent, market context, and anti-similarity constraints.
    """

    def __init__(self, model_id: str = "qwen-image-2512") -> None:
        self.model_id = model_id

    def render(self, brief: GenerationBrief) -> RenderedPrompt:
        changed = ", ".join(brief.changed_dimensions)
        rationale = "; ".join(brief.differentiation_rationale)
        prompt = (
            f"A premium commercial stock asset of {brief.subject}, "
            f"{brief.composition}, viewed from {brief.viewpoint}. "
            f"{brief.color_direction}. Setting: {brief.context}. "
            f"Designed for {brief.use_case}; market intent: {brief.market_intent}. "
            f"This must be an original interpretation that differs substantially "
            f"from any reference across: {changed}. "
            f"Creative differentiation: {rationale}. "
            "Photorealistic detail, natural materials, clean professional lighting, "
            "sharp focus, balanced composition with copy space where appropriate."
        )
        return RenderedPrompt(
            model_id=self.model_id,
            prompt=prompt,
            negative_prompt=(
                "watermark, logo, text overlay, signature, border, decorative frame, "
                "user interface, screenshot, deformed hands, distorted fingers, "
                "warped anatomy, blurry, low quality, jpeg artifacts, "
                "exact copy of reference composition"
            ),
            parameters={
                "reference_mode": "intent_only",
                "lane": "zerogpu-qwen-2512-lightning-4step",
                "prompt_style": "descriptive-sentences",
            },
        )


_ADAPTERS: dict[str, PromptAdapter] = {
    "z-image-turbo": ZImageTurboAdapter(),
    "flux": FluxAdapter(),
    "gemini-image": GeminiImageAdapter(),
    "qwen-image-2512": QwenImage2512Adapter("qwen-image-2512"),
    # Alias matching the model catalog profile name for the same production lane.
    "qwen-image": QwenImage2512Adapter("qwen-image"),
}


def render_generation_prompt(brief: GenerationBrief, model_id: str) -> RenderedPrompt:
    try:
        adapter = _ADAPTERS[model_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported model adapter: {model_id}") from exc
    return adapter.render(brief)
