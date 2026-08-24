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

    palette = ", ".join(spec.palette) if spec.palette else "restrained commercially coherent color palette"
    levers = ", ".join(spec.originality_levers)
    uses = ", ".join(spec.commercial_use_cases) if spec.commercial_use_cases else "commercial design use"
    extras = " ".join(spec.extra_constraints)

    prompt = (
        f"Premium commercial stock {spec.asset_type} asset for {spec.buyer_job}. "
        f"Asset family: {spec.asset_family}. Micro-niche: {spec.micro_niche}. "
        f"Primary subject: {spec.subject}. Visual language: {spec.visual_language}. "
        f"Medium/material: {spec.medium}. Composition: {spec.composition}. "
        f"Negative space: {spec.negative_space}. {isolation}. {background}. "
        f"Palette: {palette}. Branding policy: {spec.branding_policy}. {text}. "
        f"Differentiate through: {levers}. "
        f"Commercial use cases: {uses}. "
        "Prioritize practical design utility, thumbnail readability, believable material behavior, "
        "clean geometry, professional art direction, and marketplace-ready finish. "
        "Do not turn the asset into a generic decorative image. "
        f"{extras}"
    ).strip()

    quality = (
        "clear primary subject and immediate thumbnail recognition",
        "physically or visually coherent object geometry",
        "believable material and medium characteristics",
        "clean extraction-friendly silhouette where isolation is required",
        "commercially useful negative space",
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
    return PromptPackage(
        prompt=prompt,
        negative_prompt="; ".join(_BASE_NEGATIVE),
        quality_constraints=quality,
        legal_constraints=_LEGAL_CONSTRAINTS,
        metadata_hints=metadata,
    )
