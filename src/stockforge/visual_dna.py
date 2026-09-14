"""Deterministic Visual DNA descriptors for StockForge V2.

Visual DNA describes measurable visual structure. It intentionally does not
pretend to infer semantic subject matter, demand, or marketplace performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .reference_intelligence import ReferenceProfile


@dataclass(frozen=True, slots=True)
class VisualDNA:
    composition_signature: tuple[str, ...]
    palette_family: str
    texture_profile: str
    visual_density: str
    format_role: str
    confidence: tuple[tuple[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "composition_signature": list(self.composition_signature),
            "palette_family": self.palette_family,
            "texture_profile": self.texture_profile,
            "visual_density": self.visual_density,
            "format_role": self.format_role,
            "confidence": {key: value for key, value in self.confidence},
            "semantic_claims": "not inferred by this deterministic layer",
        }


def _palette_family(mean_rgb: tuple[int, int, int], colors: tuple[str, ...]) -> str:
    red, green, blue = mean_rgb
    brightness = (red + green + blue) / 3
    spread = max(mean_rgb) - min(mean_rgb)
    if brightness < 65:
        return "dark"
    if brightness > 205 and spread < 35:
        return "light-neutral"
    if blue > red * 1.15 and blue > green * 1.05:
        return "cool-blue"
    if red > blue * 1.18 and red > green * 1.05:
        return "warm-red"
    if green > red * 1.12 and green > blue * 0.9:
        return "green-natural"
    if spread < 30:
        return "neutral"
    if len(colors) >= 4:
        return "multicolor"
    return "mixed"


def _texture_profile(edge_density: float, color_variation: float) -> str:
    if edge_density >= 0.18 or color_variation >= 3500:
        return "high-texture"
    if edge_density >= 0.08 or color_variation >= 1200:
        return "moderate-texture"
    return "low-texture"


def _density(edge_density: float) -> str:
    if edge_density >= 0.20:
        return "dense"
    if edge_density >= 0.09:
        return "moderate"
    return "minimal"


def _format_role(profile: ReferenceProfile) -> str:
    if profile.visual.has_alpha:
        return "transparent-or-isolated-reference"
    if profile.visual.orientation == "landscape":
        return "scene-background-or-banner-reference"
    if profile.visual.orientation == "portrait":
        return "portrait-or-editorial-reference"
    return "square-asset-reference"


def extract_visual_dna(profile: ReferenceProfile) -> VisualDNA:
    """Derive reproducible visual structure from the current reference profile."""
    visual = profile.visual
    composition: list[str] = [visual.orientation]
    if visual.aspect_ratio >= 1.6:
        composition.append("wide-horizontal-framing")
    elif visual.aspect_ratio <= 0.7:
        composition.append("tall-vertical-framing")
    else:
        composition.append("balanced-framing")
    if visual.has_alpha:
        composition.append("alpha-isolation-present")
    else:
        composition.append("opaque-background")

    confidence = (
        ("composition", "high"),
        ("palette", "high"),
        ("texture", "medium"),
        ("semantic", "not-verified"),
        ("commercial_intent", "not-verified"),
    )
    return VisualDNA(
        composition_signature=tuple(composition),
        palette_family=_palette_family(visual.mean_rgb, visual.dominant_colors),
        texture_profile=_texture_profile(visual.edge_density, visual.color_variation),
        visual_density=_density(visual.edge_density),
        format_role=_format_role(profile),
        confidence=confidence,
    )
