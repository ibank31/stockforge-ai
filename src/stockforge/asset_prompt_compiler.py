"""Compile provider-neutral AssetSpec objects into canonical prompt packages."""

from __future__ import annotations

from .asset_spec import AssetSpec
from .prompt_compiler import PromptPackage


_BASE_NEGATIVE = (
    "multiple objects when one object is required",
    "collage, scene, environment, frame, border, unnecessary props",
    "people, hands, fingers, faces, bodies, tools, measuring devices, meters, screens, phones, computers, cables",
    "readable text, fake typography, letters, numbers, labels, logos, trademarks, watermarks, signatures, stamps, postmarks",
    "recognizable copyrighted artwork or characters, celebrity likenesses",
    "deformed geometry, malformed object structure, duplicated elements",
    "plastic texture, CGI appearance, generic AI aesthetic",
    "oversaturated colors, excessive HDR, glow, cinematic effects",
    "dirty background, gray background, background contamination",
    "blur, compression artifacts, oversharpening, chromatic aberration",
    "white halo, colored fringe, broken extraction edges",
)

_SCENE_NEGATIVE = (
    "multiple unrelated subjects, crowded composition, accidental background people, "
    "unrelated props, cluttered set dressing",
    "deformed anatomy, extra fingers, fused limbs, malformed faces, duplicated subjects, unnatural proportions",
    "readable text, fake typography, letters, numbers, labels, logos, trademarks, watermarks, signatures, stamps, postmarks",
    "recognizable copyrighted artwork or characters, celebrity likenesses",
    "deformed geometry, malformed object structure, duplicated elements",
    "plastic texture, CGI appearance, generic AI aesthetic",
    "oversaturated colors, excessive HDR, glow, cinematic effects",
    "dirty background, gray background, background contamination",
    "blur, compression artifacts, oversharpening, chromatic aberration",
    "white halo, colored fringe, broken extraction edges",
)

_LEGAL_CONSTRAINTS = (
    "Avoid brands, trademarks, logos, copyrighted characters, and celebrity or public-figure likenesses.",
    "Do not imply endorsement by a real company or person.",
    "Use only the approved fictional or rights-cleared subject matter; prompt constraints are not legal clearance.",
    "Final submission still requires human rights and compliance review.",
)


def compile_asset_prompt(spec: AssetSpec) -> PromptPackage:
    """Compile an AssetSpec without adding market facts or provider syntax."""
    isolation = {
        "isolated": "single standalone asset, fully visible, no overlap with other objects",
        "cluster": "small controlled cluster of related objects with clear separation",
        "scene": "coherent scene with realistic environmental context",
    }[spec.isolation_policy]
    background = {
        "white": "solid clean white background, extraction-friendly",
        "transparent": "transparent-background intent with clean object edges",
        "neutral": "minimal neutral studio background",
        "scene": "contextual background appropriate to the subject",
    }[spec.background_policy]
    text = {
        "none": "no readable text or typography",
        "abstract": "only non-readable abstract marks if visually necessary",
        "controlled": "only controlled, intentional text with no brand implication",
        "required": "text is a deliberate part of the approved asset specification",
    }[spec.text_policy]

    layout_instruction = {
        "hero_landscape": "Preserve deliberate directional copy-safe space because this product is a hero or background asset.",
        "square": "Use tight square product framing; do not reserve empty copy space unless it is explicitly part of the subject.",
        "portrait": "Use a complete vertical composition without decorative empty side fields.",
    }[spec.layout_mode]
    format_instruction = {
        "jpeg": "Deliverable intent: high-quality raster JPEG composition.",
        "png": "Deliverable intent: true transparent PNG cutout with clean alpha-ready edges and no white backdrop.",
        "svg": "Deliverable intent: editable native SVG geometry, not a raster image trace.",
    }[spec.delivery_format]
    palette = ", ".join(spec.palette) if spec.palette else "restrained commercially coherent color palette"
    levers = ", ".join(spec.originality_levers)
    mechanism = next(
        (item.removeprefix("Visual mechanism:").strip() for item in spec.extra_constraints
         if item.startswith("Visual mechanism:")),
        "one clear visual mechanism that is legible at thumbnail size",
    )
    extras = " ".join(item for item in spec.extra_constraints if not item.startswith("Visual mechanism:"))

    # Keep buyer/use-case language out of the image-facing instruction.  Terms
    # such as developer, dashboard, packaging, or SaaS can pull a model toward
    # literal devices, labels, or fake interfaces even when the asset contract
    # forbids them.  Buyer context remains frozen in metadata and provenance.
    prompt = (
        f"Premium commercial stock {spec.asset_type} asset. "
        f"Primary subject, one complete object or fused controlled system only: {spec.subject}. "
        f"Visual mechanism: {mechanism}. "
        f"Material behavior: {spec.medium}; surfaces must be physically believable and cleanly resolved. "
        f"Composition contract: {spec.composition}. Negative-space contract: {spec.negative_space}. "
        f"{layout_instruction} {format_instruction} "
        f"{isolation}. {background}. Palette: {palette}. {text}. "
        f"Distinctness levers: {levers}. Visual language: {spec.visual_language}. "
        "Prioritize a complete readable silhouette, clean geometry, credible material behavior, "
        "controlled shadow, professional art direction, and a thumbnail-readable focal idea. "
        "Do not add a literal device, interface, business prop, product label, or decorative element unless it is the approved primary subject. "
        "Do not turn the asset into a generic decorative image. "
        f"{extras}"
    ).strip()

    quality = (
        "clear primary subject and immediate thumbnail recognition",
        "physically or visually coherent object geometry",
        "believable material and medium characteristics",
        "clean extraction-friendly silhouette where isolation is required",
        "format-appropriate framing and canvas use",
        "restrained professional color treatment",
        "no accidental text, branding, or watermark",
        *spec.quality_gates,
    )
    metadata = (
        spec.asset_family,
        spec.asset_type,
        spec.micro_niche,
        spec.buyer_segment,
        spec.buyer_job,
        spec.channel,
        *spec.commercial_use_cases,
        *spec.originality_levers,
        *spec.metadata_hints,
    )
    negative_terms = _SCENE_NEGATIVE if spec.delivery_format == "jpeg" and spec.isolation_policy == "scene" else _BASE_NEGATIVE
    return PromptPackage(
        prompt=prompt,
        negative_prompt="; ".join(negative_terms),
        quality_constraints=quality,
        legal_constraints=_LEGAL_CONSTRAINTS,
        metadata_hints=metadata,
    )
