"""Explicit product-format strategy for StockForge asset briefs.

A file extension is only the delivery detail.  The strategy is selected from
buyer utility and production constraints before a provider is called.  The
engine never claims marketplace approval or demand.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Literal


DeliveryFormat = Literal["jpeg", "png", "svg"]


class FormatStrategyError(ValueError):
    """Raised when a format contract conflicts with its buyer job."""


@dataclass(frozen=True, slots=True)
class FormatDecision:
    """Persistable explanation of why a product format was selected."""

    delivery_format: DeliveryFormat
    product_kind: str
    strategy_key: str
    buyer_utility: str
    background_policy: str
    requires_true_alpha: bool
    requires_remote_gpu: bool
    selection_reason: str
    risk_flags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return data


_COMPOSITING_TERMS = re.compile(
    r"(?:transparent|overlay|composit(?:e|ing)|drop[- ]?in|layer(?:ed|ing)?|sticker|cutout|isolat(?:ed|e))",
    re.IGNORECASE,
)
_EDITABLE_TERMS = re.compile(r"(?:editable|icon(?:s| set)?|vector|svg|paths?)", re.IGNORECASE)
_SCENE_TERMS = re.compile(r"(?:scene|hero|background|editorial composition|copy space|campaign)", re.IGNORECASE)


def recommend_format(
    *,
    asset_type: str,
    buyer_job: str,
    compositing_required: bool = False,
    editable_paths_required: bool = False,
    scene_required: bool = False,
    infer_from_text: bool = True,
) -> FormatDecision:
    """Recommend a product route from user-facing asset intent.

    Explicit compositing requirements win over generic food/illustration labels.
    Editable path requirements route to SVG rather than raster.  A normal
    self-contained scene or illustration routes to JPEG.  The result is a
    recommendation only; a concrete AssetSpec must still be validated.
    """
    text = f"{asset_type} {buyer_job}".strip()
    if editable_paths_required or (infer_from_text and _EDITABLE_TERMS.search(text)):
        return FormatDecision(
            delivery_format="svg",
            product_kind="native_vector",
            strategy_key="editable_vector_utility",
            buyer_utility="editable paths for interface, diagram, or reusable graphic work",
            background_policy="transparent",
            requires_true_alpha=True,
            requires_remote_gpu=False,
            selection_reason="The buyer job requires editable geometry, not a raster export.",
            risk_flags=("visual coherence and editability still require human review",),
        )

    if compositing_required or (infer_from_text and _COMPOSITING_TERMS.search(text)):
        return FormatDecision(
            delivery_format="png",
            product_kind="transparent_cutout",
            strategy_key="transparent_utility_cutout",
            buyer_utility="drop-in isolated object, ingredient, overlay, or sticker for larger compositions",
            background_policy="transparent",
            requires_true_alpha=True,
            requires_remote_gpu=True,
            selection_reason="The buyer job places the asset over other artwork, so true transparency is part of the product.",
            risk_flags=(
                "alpha edge, fringe, shadow, and crop require technical and human review",
                "do not submit the same visual as a duplicate JPEG",
            ),
        )

    if scene_required or (infer_from_text and _SCENE_TERMS.search(text)):
        reason = "The buyer job needs a self-contained composition, tonal scene, or deliberate copy-space layout."
    else:
        reason = "The buyer job is best served by a self-contained raster illustration with a controlled background."
    return FormatDecision(
        delivery_format="jpeg",
        product_kind="raster_illustration",
        strategy_key="self_contained_raster",
        buyer_utility="standalone image for editorial, menu, packaging concept, article, or campaign composition",
        background_policy="white",
        requires_true_alpha=False,
        requires_remote_gpu=True,
        selection_reason=reason,
        risk_flags=("do not also submit an identical transparent PNG",),
    )


def validate_format_decision(
    decision: FormatDecision,
    *,
    delivery_format: str,
    product_kind: str,
    background_policy: str,
    isolation_policy: str,
) -> None:
    """Ensure a persisted decision agrees with the concrete AssetSpec contract."""
    if decision.delivery_format != delivery_format or decision.product_kind != product_kind:
        raise FormatStrategyError(
            "Persisted format decision does not match the AssetSpec product contract."
        )
    if decision.delivery_format == "png":
        if background_policy != "transparent" or isolation_policy != "isolated":
            raise FormatStrategyError("PNG utility assets require isolated placement on a transparent background.")
    elif decision.delivery_format == "jpeg" and background_policy == "transparent":
        raise FormatStrategyError("A transparent buyer job must use PNG, not JPEG.")
