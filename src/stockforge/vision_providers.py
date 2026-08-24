"""Lightweight provider interfaces for StockForge vision QA.

Adapters are optional and intentionally do not download models at import time.
This keeps the core package usable on Termux and in the generator runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ProviderResult:
    provider: str
    signals: dict[str, float | None]
    raw: Any = None
    error: str | None = None


class VisionProvider(Protocol):
    name: str

    def inspect(self, image_path: str | Path, context: str = "") -> ProviderResult:
        ...


class UnavailableProvider:
    """Safe placeholder. Missing optional dependencies never become PASS."""

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def inspect(self, image_path: str | Path, context: str = "") -> ProviderResult:
        return ProviderResult(self.name, {}, error=self.reason)


class QwenVLProvider:
    """Optional Transformers adapter for Qwen2.5-VL.

    Model loading is lazy. The model identifier is configurable because model
    licensing and hardware suitability must be reviewed before production use.
    """

    name = "qwen2.5-vl"

    def __init__(self, model_id: str = "Qwen/Qwen2.5-VL-3B-Instruct") -> None:
        self.model_id = model_id
        self._model = None
        self._processor = None

    def _load(self) -> None:
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
        self._processor = AutoProcessor.from_pretrained(self.model_id)
        self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            self.model_id, device_map="auto", torch_dtype="auto"
        )

    def inspect(self, image_path: str | Path, context: str = "") -> ProviderResult:
        try:
            if self._model is None:
                self._load()
            # The semantic prompt is deliberately explicit. Parsing a model's
            # free-form answer into policy scores belongs in a later adapter.
            prompt = (
                "Inspect this stock-photo candidate. Return JSON only with "
                "scores from 0 to 1 for anatomy, subject_integrity, realism, "
                "artifact_risk, unexpected_text, ip_risk, commercial. "
                f"Context: {context}"
            )
            # Keep the actual message assembly isolated until the first
            # benchmark, because Transformers processor APIs vary by release.
            return ProviderResult(self.name, {}, raw={"prompt": prompt, "image": str(image_path)})
        except Exception as exc:
            return ProviderResult(self.name, {}, error=f"{type(exc).__name__}: {exc}")


class PaddleOCRProvider:
    """Optional OCR adapter. No dependency is imported until used."""

    name = "paddleocr"

    def __init__(self, lang: str = "en") -> None:
        self.lang = lang
        self._ocr = None

    def _load(self) -> None:
        from paddleocr import PaddleOCR
        self._ocr = PaddleOCR(lang=self.lang)

    def inspect(self, image_path: str | Path, context: str = "") -> ProviderResult:
        try:
            if self._ocr is None:
                self._load()
            result = self._ocr.predict(str(image_path))
            has_text = bool(result)
            return ProviderResult(
                self.name,
                {"unexpected_text": 0.0 if has_text else 1.0},
                raw=result,
            )
        except Exception as exc:
            return ProviderResult(self.name, {}, error=f"{type(exc).__name__}: {exc}")
