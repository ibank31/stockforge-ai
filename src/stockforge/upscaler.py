"""Provider-neutral image upscaling contract.

Upscaling is deliberately isolated from Adobe finalization. A provider may use
an AI model, a remote service, or a future local engine, but it must report the
exact scale and model identity used for the artifact lineage.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class UpscalerError(RuntimeError):
    """Raised when an upscaler cannot safely produce an artifact."""


@dataclass(frozen=True, slots=True)
class UpscaleRequest:
    source: Path
    destination: Path
    scale: int = 4

    def __post_init__(self) -> None:
        if self.scale not in {2, 4}:
            raise UpscalerError("Supported AI upscale factors are 2x and 4x.")
        if self.source.resolve() == self.destination.resolve():
            raise UpscalerError("Source and destination must be different files.")


@dataclass(frozen=True, slots=True)
class UpscaleReport:
    source_path: str
    output_path: str
    provider_id: str
    model_id: str
    scale: int
    source_width: int
    source_height: int
    output_width: int
    output_height: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "output_path": self.output_path,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "scale": self.scale,
            "source_width": self.source_width,
            "source_height": self.source_height,
            "output_width": self.output_width,
            "output_height": self.output_height,
        }


class Upscaler(Protocol):
    """Minimal runtime interface for an image upscaler provider."""

    @property
    def provider_id(self) -> str: ...

    @property
    def model_id(self) -> str: ...

    def healthcheck(self) -> bool: ...

    def upscale(self, request: UpscaleRequest) -> UpscaleReport: ...
