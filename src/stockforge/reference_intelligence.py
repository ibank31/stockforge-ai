"""Reference Intelligence foundation for StockForge V2.

This module deliberately separates measurable image facts from semantic claims.
Pillow can reliably inspect pixels, dimensions, alpha and coarse visual structure;
it cannot honestly infer "what sells" or the commercial meaning of an image.

Semantic/commercial fields therefore remain explicit inputs until a real vision
provider is wired into the production path.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter, ImageStat, UnidentifiedImageError


class ReferenceIntelligenceError(ValueError):
    """Raised when a reference cannot be safely profiled."""


@dataclass(frozen=True, slots=True)
class ReferenceVisualFacts:
    sha256: str
    detected_format: str
    width: int
    height: int
    mode: str
    has_alpha: bool
    aspect_ratio: float
    orientation: str
    dominant_colors: tuple[str, ...]
    mean_rgb: tuple[int, int, int]
    color_variation: float
    edge_density: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "sha256": self.sha256,
            "detected_format": self.detected_format,
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "has_alpha": self.has_alpha,
            "aspect_ratio": self.aspect_ratio,
            "orientation": self.orientation,
            "dominant_colors": list(self.dominant_colors),
            "mean_rgb": list(self.mean_rgb),
            "color_variation": self.color_variation,
            "edge_density": self.edge_density,
        }


@dataclass(frozen=True, slots=True)
class ReferenceProfile:
    visual: ReferenceVisualFacts
    subject: str | None = None
    category: str | None = None
    commercial_intent: str | None = None
    buyer_relevance: str | None = None

    @property
    def semantic_status(self) -> str:
        values = (self.subject, self.category, self.commercial_intent, self.buyer_relevance)
        return "user_supplied" if any(value for value in values) else "not_verified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "visual": self.visual.to_dict(),
            "semantic": {
                "subject": self.subject,
                "category": self.category,
                "commercial_intent": self.commercial_intent,
                "buyer_relevance": self.buyer_relevance,
                "status": self.semantic_status,
            },
        }


@dataclass(frozen=True, slots=True)
class CreativeDistancePlan:
    """Explicit dimensions that must change before a new asset is generated."""

    change_subject: bool = True
    change_composition: bool = True
    change_viewpoint: bool = True
    change_color_direction: bool = True
    change_context: bool = True
    change_use_case: bool = True

    def to_dict(self) -> dict[str, bool]:
        return {
            "change_subject": self.change_subject,
            "change_composition": self.change_composition,
            "change_viewpoint": self.change_viewpoint,
            "change_color_direction": self.change_color_direction,
            "change_context": self.change_context,
            "change_use_case": self.change_use_case,
        }

    def validate(self) -> None:
        if sum(self.to_dict().values()) < 3:
            raise ReferenceIntelligenceError(
                "Creative distance requires at least three independent changes; "
                "a reference must not be treated as a reproduction template."
            )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _orientation(width: int, height: int) -> str:
    ratio = width / height
    if math.isclose(ratio, 1.0, abs_tol=0.02):
        return "square"
    return "landscape" if ratio > 1 else "portrait"


def _hex(color: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*color)


def _dominant_colors(image: Image.Image, limit: int = 5) -> tuple[str, ...]:
    reduced = image.convert("RGB").resize((64, 64))
    palette = reduced.quantize(colors=limit, method=Image.Quantize.MEDIANCUT)
    counts = sorted(palette.getcolors(), reverse=True)
    palette_values = palette.getpalette() or []
    colors: list[str] = []
    for _count, index in counts[:limit]:
        base = index * 3
        rgb = tuple(palette_values[base:base + 3])
        if len(rgb) == 3:
            colors.append(_hex((int(rgb[0]), int(rgb[1]), int(rgb[2]))))
    return tuple(colors)


def _edge_density(image: Image.Image) -> float:
    gray = image.convert("L").resize((256, 256))
    edges = gray.filter(ImageFilter.FIND_EDGES)
    values = list(edges.getdata())
    return round(sum(value >= 40 for value in values) / len(values), 6)


def profile_reference_image(
    source: Path,
    *,
    subject: str | None = None,
    category: str | None = None,
    commercial_intent: str | None = None,
    buyer_relevance: str | None = None,
) -> ReferenceProfile:
    """Create a reproducible V2 reference profile without semantic overclaiming."""

    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ReferenceIntelligenceError(f"Reference does not exist: {source}")

    try:
        with Image.open(source) as probe:
            probe.verify()
        with Image.open(source) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise ReferenceIntelligenceError("Animated references are not supported.")
            image.load()
            width, height = image.size
            if width < 1 or height < 1:
                raise ReferenceIntelligenceError("Reference has invalid dimensions.")
            rgb = image.convert("RGB")
            stat = ImageStat.Stat(rgb)
            mean = tuple(int(round(value)) for value in stat.mean[:3])
            variation = round(sum(stat.var[:3]) / 3, 6)
            facts = ReferenceVisualFacts(
                sha256=_sha256(source),
                detected_format=image.format or "UNKNOWN",
                width=width,
                height=height,
                mode=image.mode,
                has_alpha="A" in image.getbands(),
                aspect_ratio=round(width / height, 6),
                orientation=_orientation(width, height),
                dominant_colors=_dominant_colors(image),
                mean_rgb=(mean[0], mean[1], mean[2]),
                color_variation=variation,
                edge_density=_edge_density(image),
            )
    except ReferenceIntelligenceError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, RuntimeError) as exc:
        raise ReferenceIntelligenceError(
            f"Reference is not a safely decodable image: {exc}"
        ) from exc

    return ReferenceProfile(
        visual=facts,
        subject=subject,
        category=category,
        commercial_intent=commercial_intent,
        buyer_relevance=buyer_relevance,
    )
