"""Structured commercial asset specification for the StockForge factory."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import re
from typing import Any

ASSET_FAMILIES = frozenset({
    "material_atmosphere", "ui_3d_metaphor", "surreal_concept",
    "retro_tech_nostalgia", "craft_element", "organic_motif", "technical_component_illustration", "generic",
})
ASSET_TYPES = frozenset({"photo", "illustration", "ephemera", "3d", "icon", "icon_set", "texture", "graphic"})
BACKGROUND_POLICIES = frozenset({"white", "transparent", "neutral", "scene"})
ISOLATION_POLICIES = frozenset({"isolated", "cluster", "scene"})
TEXT_POLICIES = frozenset({"none", "abstract", "controlled", "required"})
PRODUCT_KINDS = frozenset({"raster_illustration", "transparent_cutout", "native_vector"})
DELIVERY_FORMATS = frozenset({"jpeg", "png", "svg"})
LAYOUT_MODES = frozenset({"square", "hero_landscape", "portrait"})
_FORMATS_BY_PRODUCT = {
    "raster_illustration": frozenset({"jpeg"}),
    "transparent_cutout": frozenset({"png"}),
    "native_vector": frozenset({"svg"}),
}
_CAPABILITY_PREFERENCE = re.compile(r"^[a-z][a-z0-9_]*\s*(?:=|>=|<=)\s*[a-z0-9_.]+$")


class AssetSpecError(ValueError):
    """Raised when a commercial asset specification is invalid."""


@dataclass(frozen=True, slots=True)
class AssetSpec:
    """Provider-neutral commercial specification for one asset candidate."""

    asset_id: str
    market_opportunity_id: str
    buyer_segment: str
    buyer_job: str
    channel: str
    asset_family: str
    asset_type: str
    micro_niche: str
    subject: str
    visual_language: str
    medium: str
    product_kind: str = "raster_illustration"
    delivery_format: str = "jpeg"
    layout_mode: str = "square"
    palette: tuple[str, ...] = ()
    composition: str = ""
    negative_space: str = ""
    background_policy: str = "white"
    isolation_policy: str = "isolated"
    text_policy: str = "none"
    branding_policy: str = "no_branding"
    originality_levers: tuple[str, ...] = ()
    variation_policy: str = "genuinely_different"
    commercial_use_cases: tuple[str, ...] = ()
    quality_gates: tuple[str, ...] = ()
    model_preferences: tuple[str, ...] = ()
    metadata_hints: tuple[str, ...] = ()
    extra_constraints: tuple[str, ...] = ()
    tags: tuple[str, ...] = field(default_factory=tuple)
    identity_signature: str = ""
    identity_lighting: str = ""
    identity_framing: str = ""
    identity_context: str = ""
    identity_distinctness: tuple[str, ...] = ()
    identity_prohibited_shorthand: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        required = {
            "asset_id": self.asset_id,
            "market_opportunity_id": self.market_opportunity_id,
            "buyer_segment": self.buyer_segment,
            "buyer_job": self.buyer_job,
            "channel": self.channel,
            "asset_family": self.asset_family,
            "asset_type": self.asset_type,
            "micro_niche": self.micro_niche,
            "subject": self.subject,
            "visual_language": self.visual_language,
            "medium": self.medium,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise AssetSpecError(f"Required fields are empty: {', '.join(missing)}")
        if self.asset_family not in ASSET_FAMILIES:
            raise AssetSpecError(f"Unsupported asset family: {self.asset_family}")
        if self.asset_type not in ASSET_TYPES:
            raise AssetSpecError(f"Unsupported asset type: {self.asset_type}")
        if self.background_policy not in BACKGROUND_POLICIES:
            raise AssetSpecError(f"Unsupported background policy: {self.background_policy}")
        if self.isolation_policy not in ISOLATION_POLICIES:
            raise AssetSpecError(f"Unsupported isolation policy: {self.isolation_policy}")
        if self.text_policy not in TEXT_POLICIES:
            raise AssetSpecError(f"Unsupported text policy: {self.text_policy}")
        if self.product_kind not in PRODUCT_KINDS:
            raise AssetSpecError(f"Unsupported product kind: {self.product_kind}")
        if self.delivery_format not in DELIVERY_FORMATS:
            raise AssetSpecError(f"Unsupported delivery format: {self.delivery_format}")
        if self.delivery_format not in _FORMATS_BY_PRODUCT[self.product_kind]:
            allowed = ", ".join(sorted(_FORMATS_BY_PRODUCT[self.product_kind]))
            raise AssetSpecError(
                f"Product kind {self.product_kind!r} requires one of: {allowed}; "
                f"received {self.delivery_format!r}."
            )
        if self.layout_mode not in LAYOUT_MODES:
            raise AssetSpecError(f"Unsupported layout mode: {self.layout_mode}")
        if self.product_kind == "transparent_cutout":
            if self.background_policy != "transparent" or self.isolation_policy != "isolated":
                raise AssetSpecError("Transparent cutouts require isolated placement on a transparent background.")
            if self.layout_mode != "square":
                raise AssetSpecError("Transparent cutouts require tight square framing; do not sell copy space as part of the file.")
        if self.product_kind == "native_vector" and self.isolation_policy == "scene":
            raise AssetSpecError("Native vectors must be an editable object, pattern, icon set, or controlled cluster; scenes are not supported.")
        if not self.originality_levers:
            raise AssetSpecError("At least one originality lever is required.")
        if any(not _CAPABILITY_PREFERENCE.fullmatch(preference) for preference in self.model_preferences):
            raise AssetSpecError(
                "Model preferences must be provider-neutral capability expressions, "
                "such as 'realism=high' or 'resolution>=1024'."
            )
        if self.isolation_policy == "isolated" and self.background_policy == "scene":
            raise AssetSpecError("An isolated asset cannot require a scene background.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def standalone_asset_spec(
    *,
    asset_id: str,
    market_opportunity_id: str,
    buyer_segment: str,
    buyer_job: str,
    channel: str,
    asset_family: str,
    asset_type: str,
    micro_niche: str,
    subject: str,
    visual_language: str,
    medium: str,
    originality_levers: tuple[str, ...],
    commercial_use_cases: tuple[str, ...] = (),
    product_kind: str = "raster_illustration",
    delivery_format: str = "jpeg",
    layout_mode: str = "square",
    background_policy: str = "white",
    isolation_policy: str = "isolated",
    text_policy: str = "none",
    branding_policy: str = "no_branding",
    palette: tuple[str, ...] = (),
    model_preferences: tuple[str, ...] = (),
    metadata_hints: tuple[str, ...] = (),
    extra_constraints: tuple[str, ...] = (),
) -> AssetSpec:
    """Build the common isolated-asset policy for the first factory lane."""
    spec = AssetSpec(
        asset_id=asset_id,
        market_opportunity_id=market_opportunity_id,
        buyer_segment=buyer_segment,
        buyer_job=buyer_job,
        channel=channel,
        asset_family=asset_family,
        asset_type=asset_type,
        micro_niche=micro_niche,
        subject=subject,
        visual_language=visual_language,
        medium=medium,
        product_kind=product_kind,
        delivery_format=delivery_format,
        layout_mode=layout_mode,
        palette=palette,
        composition="single standalone object, fully visible, extraction-friendly silhouette",
        negative_space="substantial clean negative space around the asset",
        background_policy=background_policy,
        isolation_policy=isolation_policy,
        text_policy=text_policy,
        branding_policy=branding_policy,
        originality_levers=originality_levers,
        variation_policy="retain only commercially distinct variants; crop/color/seed-only changes are insufficient",
        commercial_use_cases=commercial_use_cases,
        quality_gates=(
            "thumbnail readability",
            "clean silhouette",
            "no accidental text, letters, numbers, labels, or typography",
            "no logos, trademarks, stamps, postmarks, or watermarks",
            "no people, hands, faces, bodies, tools, devices, screens, or unrelated props",
            "no obvious AI artifacts",
            "commercial design utility",
        ),
        model_preferences=model_preferences,
        metadata_hints=metadata_hints,
        extra_constraints=extra_constraints,
    )
    if (
        spec.background_policy != "white"
        or spec.isolation_policy != "isolated"
        or spec.text_policy != "none"
        or spec.branding_policy != "no_branding"
    ):
        raise AssetSpecError(
            "Standalone assets require white background, isolated placement, "
            "no text, and no branding."
        )
    return spec
