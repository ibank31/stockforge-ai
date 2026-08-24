"""Deterministic asset-type selection before prompt or generation.

The selector is intentionally conservative. It chooses a product lane and
explains missing gates; it does not silently fall back to JPEG and it never
calls a provider.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


class AssetSelectionError(ValueError):
    """Raised when the requested asset type is not registered."""


@dataclass(frozen=True, slots=True)
class AssetTypePolicy:
    key: str
    label: str
    product_kind: str
    delivery_format: str
    execution_mode: str
    readiness: str
    candidate_niches: tuple[str, ...]
    blockers: tuple[str, ...]
    next_step: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["candidate_niches"] = list(self.candidate_niches)
        data["blockers"] = list(self.blockers)
        return data


ASSET_TYPE_POLICIES: tuple[AssetTypePolicy, ...] = (
    AssetTypePolicy(
        key="scene",
        label="Conceptual or commercial scene",
        product_kind="raster_illustration",
        delivery_format="jpeg",
        execution_mode="remote_raster_generation",
        readiness="READY_FOR_TRIAL",
        candidate_niches=("surreal conceptual scene", "seasonal commercial scene", "tactile material scene"),
        blockers=("full-size visual review is required after generation", "final marketplace acceptance is not automatic"),
        next_step="Select one evidence-backed scene brief, run preflight, then allow one controlled JPEG trial.",
    ),
    AssetTypePolicy(
        key="native_object",
        label="Editable isolated object",
        product_kind="native_vector",
        delivery_format="svg",
        execution_mode="local_native_vector_build",
        readiness="READY_FOR_TRIAL",
        candidate_niches=("geometric object", "modular icon element", "technical design component"),
        blockers=("current builder is limited to controlled geometric presets", "portal upload validation is still pending"),
        next_step="Choose a supported geometric preset, build locally, inspect SVG structure, then perform one manual upload validation.",
    ),
    AssetTypePolicy(
        key="technical_icon",
        label="Technical icon or clip-art element",
        product_kind="native_vector",
        delivery_format="svg",
        execution_mode="local_native_vector_build",
        readiness="REVIEW_REQUIRED",
        candidate_niches=("technical component", "food or produce icon", "badge or simple symbol"),
        blockers=("dedicated technical/icon presets are not complete", "visual utility and editability require a human review"),
        next_step="Expand and test the deterministic SVG preset family before a trial is authorized.",
    ),
    AssetTypePolicy(
        key="seamless_pattern",
        label="Seamless pattern or repeat background",
        product_kind="native_vector",
        delivery_format="svg",
        execution_mode="local_native_vector_build",
        readiness="REVIEW_REQUIRED",
        candidate_niches=("geometric repeat", "decorative background", "pattern element"),
        blockers=("edge gate exists but a dedicated tile builder is not complete", "a square preview is not proof of seamlessness"),
        next_step="Build a tile-aware preset, run horizontal and vertical seam checks, then review the repeated result.",
    ),
    AssetTypePolicy(
        key="transparent_cutout",
        label="Transparent cutout, overlay, or sticker",
        product_kind="transparent_cutout",
        delivery_format="png",
        execution_mode="remote_raster_then_alpha_finalize",
        readiness="BLOCKED",
        candidate_niches=("isolated object overlay", "sticker-like element", "transparent decorative asset"),
        blockers=("true alpha producer is not connected", "anti-fringe and trim gates are not complete", "portal validation is pending"),
        next_step="Implement and test the real alpha pipeline; no PNG production trial is authorized before the blockers clear.",
    ),
)


_POLICY_BY_KEY = {policy.key: policy for policy in ASSET_TYPE_POLICIES}


def list_asset_type_policies() -> tuple[AssetTypePolicy, ...]:
    return ASSET_TYPE_POLICIES


def select_asset_type(asset_type: str) -> AssetTypePolicy:
    key = asset_type.strip().casefold()
    if key not in _POLICY_BY_KEY:
        supported = ", ".join(policy.key for policy in ASSET_TYPE_POLICIES)
        raise AssetSelectionError(f"Unsupported asset type {asset_type!r}. Choose one of: {supported}.")
    return _POLICY_BY_KEY[key]
