"""Reference-image intelligence for controlled microstock differentiation.

This module intentionally performs only deterministic visual decomposition.
It does not identify copyrighted works, infer ownership, or claim semantic
understanding. Its purpose is to turn measurable layout/color/light signals
into explicit variation instructions before a new asset is planned.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


class ReferenceIntelligenceError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ReferenceAnalysis:
    path: str
    width: int
    height: int
    orientation: Literal["square", "landscape", "portrait"]
    brightness: float
    saturation: float
    edge_density: float
    visual_balance: tuple[float, float, float, float]
    dominant_palette: tuple[str, ...]
    notice: str = (
        "Deterministic pixel analysis only. No semantic, copyright, ownership, "
        "or marketplace-similarity conclusion is made."
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class VariationPlan:
    composition_change: str
    palette_change: str
    lighting_change: str
    density_change: str
    negative_space_change: str
    distinctness_constraints: tuple[str, ...]
    notice: str = (
        "This plan requests materially different visual decisions. It does not "
        "guarantee legal clearance, originality, or marketplace acceptance."
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _require_pillow():
    try:
        from PIL import Image, ImageFilter, ImageStat
    except ImportError as exc:
        raise ReferenceIntelligenceError("Pillow is required for reference analysis") from exc
    return Image, ImageFilter, ImageStat


def _hex(color: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*color)


def analyze_reference(path: Path) -> ReferenceAnalysis:
    image_path = Path(path)
    if not image_path.is_file():
        raise ReferenceIntelligenceError(f"Reference image does not exist: {image_path}")
    Image, ImageFilter, ImageStat = _require_pillow()
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
            width, height = image.size
            sample = image.resize((64, 64))
            hsv = sample.convert("HSV")
            brightness = ImageStat.Stat(hsv.getchannel("V")).mean[0] / 255.0
            saturation = ImageStat.Stat(hsv.getchannel("S")).mean[0] / 255.0
            edges = sample.convert("L").filter(ImageFilter.FIND_EDGES)
            edge_density = sum(1 for value in edges.getdata() if value >= 48) / (64 * 64)

            quadrants: list[float] = []
            for box in ((0, 0, 32, 32), (32, 0, 64, 32), (0, 32, 32, 64), (32, 32, 64, 64)):
                quadrants.append(ImageStat.Stat(edges.crop(box)).mean[0] / 255.0)
            total = sum(quadrants) or 1.0
            balance = tuple(round(value / total, 4) for value in quadrants)

            palette_image = sample.quantize(colors=5, method=Image.Quantize.MEDIANCUT).convert("RGB")
            colors = palette_image.getcolors(64 * 64) or []
            palette = tuple(
                _hex(color)
                for _, color in sorted(colors, reverse=True)[:5]
            )
    except Exception as exc:
        raise ReferenceIntelligenceError(f"Unable to analyze reference image: {image_path}") from exc

    orientation: Literal["square", "landscape", "portrait"]
    if width == height:
        orientation = "square"
    elif width > height:
        orientation = "landscape"
    else:
        orientation = "portrait"
    return ReferenceAnalysis(
        str(image_path.resolve()), width, height, orientation,
        round(brightness, 4), round(saturation, 4), round(edge_density, 4),
        balance, palette,
    )


def build_variation_plan(
    analysis: ReferenceAnalysis,
    *,
    target_layout: Literal["square", "landscape", "portrait"] | None = None,
) -> VariationPlan:
    """Create explicit measurable changes instead of requesting a vague 'different image'."""
    layout = target_layout or {
        "square": "landscape",
        "landscape": "portrait",
        "portrait": "square",
    }[analysis.orientation]
    composition_change = (
        f"Change from reference {analysis.orientation} balance to a {layout} composition; "
        "move the primary focal mass to a different grid region and alter the subject scale."
    )
    palette_change = (
        "Use a materially different palette family and dominant hue relationship; "
        "do not preserve the reference palette as the main color identity."
    )
    lighting_change = (
        "Change the primary light direction and contrast structure rather than merely "
        "changing exposure."
    )
    density_change = (
        "Increase structural separation and change visual density by adding or removing "
        "meaningful approved elements, not decorative noise."
    )
    negative_space_change = (
        "Relocate negative space to a different side or region and change its proportion "
        "relative to the focal subject."
    )
    return VariationPlan(
        composition_change, palette_change, lighting_change, density_change,
        negative_space_change,
        (
            "Do not reproduce the same subject silhouette or object arrangement.",
            "Do not preserve the same dominant palette plus layout together.",
            "Change at least composition, palette, lighting, and focal hierarchy.",
            "Treat the result as a new concept, not a crop, recolor, seed, or style-only variation.",
        ),
    )


def analyze_and_plan(path: Path, *, target_layout: str | None = None) -> dict[str, object]:
    analysis = analyze_reference(path)
    if target_layout is not None and target_layout not in {"square", "landscape", "portrait"}:
        raise ReferenceIntelligenceError("target_layout must be square, landscape, or portrait")
    plan = build_variation_plan(analysis, target_layout=target_layout)
    return {"reference": analysis.to_dict(), "variation_plan": plan.to_dict()}
