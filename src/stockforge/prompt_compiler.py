"""Commercial prompt compiler for StockForge concept variants.

The compiler is deterministic. It does not invent market evidence, brands,
public figures, or product claims. Its job is to translate an approved
ConceptVariant into a production prompt plus safety/quality constraints.
"""

from __future__ import annotations

from dataclasses import dataclass

from .concept_engine import ConceptVariant


@dataclass(frozen=True, slots=True)
class PromptPackage:
    prompt: str
    negative_prompt: str
    quality_constraints: tuple[str, ...]
    legal_constraints: tuple[str, ...]
    metadata_hints: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "quality_constraints": self.quality_constraints,
            "legal_constraints": self.legal_constraints,
            "metadata_hints": self.metadata_hints,
        }


_BASE_QUALITY = (
    "photorealistic commercial stock photography",
    "natural human anatomy and believable hands",
    "physically plausible objects and perspective",
    "realistic lighting, materials, skin texture, and depth",
    "clean professional composition with useful negative space",
    "authentic rather than staged corporate behavior",
    "no visible text required for the concept",
)

_BASE_NEGATIVE = (
    "text, letters, logos, trademarks, brand marks, watermarks, signatures",
    "celebrity likeness, public figure likeness, recognizable copyrighted character",
    "deformed hands, extra fingers, missing fingers, duplicated limbs",
    "warped tools, malformed equipment, impossible architecture",
    "plastic skin, excessive smoothing, uncanny faces, CGI look",
    "oversaturated colors, extreme HDR, artificial glow, generic holograms",
    "random UI text, fake readable screens, illegible typography",
    "low resolution, blur, compression artifacts, oversharpening, noise",
)


def _angle_instruction(concept: ConceptVariant) -> str:
    if concept.angle == "hero":
        return "Create a strong wide hero image; keep the primary subject clearly separated and reserve intentional clean copy space."
    if concept.angle == "workflow":
        return "Prioritize the sequence of human work and environmental context; make the action understandable without captions."
    if concept.angle == "detail":
        return "Use a controlled close operational detail; preserve realistic material texture and enough context to identify the work."
    return "Capture a credible decision moment; show the human consequence of the workflow rather than an abstract technology metaphor."


def compile_prompt(concept: ConceptVariant) -> PromptPackage:
    """Compile a concept into a generation-ready commercial prompt."""
    if not concept.subject.strip() or not concept.visual_problem.strip():
        raise ValueError("Concept must contain subject and visual problem.")
    if not concept.uniqueness_levers:
        raise ValueError("Concept must contain at least one uniqueness lever.")

    levers = ", ".join(concept.uniqueness_levers)
    prompt = (
        f"Commercial stock photograph for {concept.buyer_job}. "
        f"Show {concept.visual_problem}. "
        f"Primary subject: {concept.subject}. "
        f"Action: {concept.action}. "
        f"Environment: {concept.environment}. "
        f"Visual angle: {concept.angle}; {concept.composition}. "
        f"Copy space: {concept.copy_space}. "
        f"Differentiate through {levers}. "
        f"The scene must communicate the business use case visually without text or branding. "
        f"{_angle_instruction(concept)} "
        "Natural documentary-commercial photography, believable real-world detail, subtle depth of field, "
        "restrained color treatment, editorially useful framing."
    )

    legal = (
        "Avoid identifiable brands, trademarks, logos, copyrighted characters, celebrities, and public figures.",
        "Do not imply endorsement by a real company or person.",
        "Keep interfaces generic and non-readable; do not recreate proprietary software screens.",
        "Final submission still requires human rights/compliance review; prompt constraints are not legal clearance.",
    )
    metadata = (
        concept.buyer_job,
        concept.channel,
        concept.angle,
        *concept.uniqueness_levers,
    )
    return PromptPackage(
        prompt=prompt,
        negative_prompt="; ".join(_BASE_NEGATIVE),
        quality_constraints=_BASE_QUALITY,
        legal_constraints=legal,
        metadata_hints=metadata,
    )
