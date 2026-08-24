"""Deterministic product-format routing for StockForge assets.

A file extension is not a product strategy.  This module turns an explicit
:class:`AssetSpec` product contract into a bounded route, and refuses routes
that are not yet technically verified.  It never claims marketplace approval.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .asset_spec import AssetSpec


class FormatRoutingError(ValueError):
    """Raised when an asset product contract cannot use a verified route."""


@dataclass(frozen=True, slots=True)
class FormatRoute:
    """One bounded delivery route selected before generation or export."""

    product_kind: str
    delivery_format: str
    layout_mode: str
    canvas: str
    background_policy: str
    execution_mode: str
    requires_remote_gpu: bool
    requires_true_alpha: bool
    verified_for_production: bool
    user_export_branch: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def route_asset_spec(spec: AssetSpec) -> FormatRoute:
    """Return the only valid route for a fully specified commercial product.

    ``transparent_cutout`` remains intentionally unverified until a real alpha
    producer and alpha-quality review are connected.  A model's white backdrop
    is not treated as transparent merely because the prompt requested it.
    """
    if spec.product_kind == "raster_illustration":
        if spec.layout_mode == "portrait":
            raise FormatRoutingError(
                "Portrait raster routing is not verified on the active ZeroGPU worker; "
                "do not spend GPU on an unsupported canvas."
            )
        canvas = "hero-landscape" if spec.layout_mode == "hero_landscape" else "square"
        return FormatRoute(
            product_kind=spec.product_kind,
            delivery_format=spec.delivery_format,
            layout_mode=spec.layout_mode,
            canvas=canvas,
            background_policy=spec.background_policy,
            execution_mode="remote_raster_generation",
            requires_remote_gpu=True,
            requires_true_alpha=False,
            verified_for_production=True,
            user_export_branch="READY_UPLOAD_ADOBE",
            reason="Textured, tonal, material, or compositional artwork is delivered as JPEG raster.",
        )

    if spec.product_kind == "transparent_cutout":
        return FormatRoute(
            product_kind=spec.product_kind,
            delivery_format=spec.delivery_format,
            layout_mode=spec.layout_mode,
            canvas="square",
            background_policy=spec.background_policy,
            execution_mode="remote_raster_then_alpha_finalize",
            requires_remote_gpu=True,
            requires_true_alpha=True,
            verified_for_production=False,
            user_export_branch="READY_UPLOAD_ADOBE",
            reason=(
                "PNG cutouts require a proven alpha producer and alpha-edge review. "
                "The active raster worker can be planned but is blocked from production until that path exists."
            ),
        )

    if spec.product_kind == "native_vector":
        if spec.layout_mode == "portrait":
            raise FormatRoutingError("Portrait native-vector templates are not implemented yet.")
        return FormatRoute(
            product_kind=spec.product_kind,
            delivery_format=spec.delivery_format,
            layout_mode=spec.layout_mode,
            canvas="vector-artboard",
            background_policy=spec.background_policy,
            execution_mode="local_native_vector_build",
            requires_remote_gpu=False,
            requires_true_alpha=spec.background_policy == "transparent",
            verified_for_production=True,
            user_export_branch="READY_UPLOAD_ADOBE",
            reason="Editable SVG paths are built locally; no raster image trace or GPU generation is used.",
        )

    raise FormatRoutingError(f"No route is registered for product kind: {spec.product_kind!r}")


def require_production_route(spec: AssetSpec) -> FormatRoute:
    """Return a route only when it is ready for a real asset operation."""
    route = route_asset_spec(spec)
    if not route.verified_for_production:
        raise FormatRoutingError(route.reason)
    return route


def route_from_dict(value: object) -> FormatRoute:
    """Reconstruct a route after validating a persisted asset-spec dictionary."""
    if not isinstance(value, dict):
        raise FormatRoutingError("Asset specification must be a JSON object.")
    try:
        spec = AssetSpec(
            asset_id=str(value["asset_id"]),
            market_opportunity_id=str(value["market_opportunity_id"]),
            buyer_segment=str(value["buyer_segment"]),
            buyer_job=str(value["buyer_job"]),
            channel=str(value["channel"]),
            asset_family=str(value["asset_family"]),
            asset_type=str(value["asset_type"]),
            micro_niche=str(value["micro_niche"]),
            subject=str(value["subject"]),
            visual_language=str(value["visual_language"]),
            medium=str(value["medium"]),
            product_kind=str(value.get("product_kind", "raster_illustration")),
            delivery_format=str(value.get("delivery_format", "jpeg")),
            layout_mode=str(value.get("layout_mode", "square")),
            palette=tuple(value.get("palette", ())),
            composition=str(value.get("composition", "")),
            negative_space=str(value.get("negative_space", "")),
            background_policy=str(value.get("background_policy", "white")),
            isolation_policy=str(value.get("isolation_policy", "isolated")),
            text_policy=str(value.get("text_policy", "none")),
            branding_policy=str(value.get("branding_policy", "no_branding")),
            originality_levers=tuple(value.get("originality_levers", ())),
            variation_policy=str(value.get("variation_policy", "genuinely_different")),
            commercial_use_cases=tuple(value.get("commercial_use_cases", ())),
            quality_gates=tuple(value.get("quality_gates", ())),
            model_preferences=tuple(value.get("model_preferences", ())),
            metadata_hints=tuple(value.get("metadata_hints", ())),
            extra_constraints=tuple(value.get("extra_constraints", ())),
            tags=tuple(value.get("tags", ())),
            identity_signature=str(value.get("identity_signature", "")),
            identity_lighting=str(value.get("identity_lighting", "")),
            identity_framing=str(value.get("identity_framing", "")),
            identity_context=str(value.get("identity_context", "")),
            identity_distinctness=tuple(value.get("identity_distinctness", ())),
            identity_prohibited_shorthand=tuple(value.get("identity_prohibited_shorthand", ())),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise FormatRoutingError(f"Persisted asset specification is invalid: {exc}") from exc
    return route_asset_spec(spec)
