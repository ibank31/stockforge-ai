"""Post-generation verification for StockForge V2.

This is a deterministic risk gate, not a claim of semantic originality or legal
clearance. It compares the generated candidate with the user reference after
generation and can block highly similar output from finalization.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .similarity_risk import SimilarityRisk, analyze_similarity_risk

Decision = Literal["BLOCK", "REVIEW"]


@dataclass(frozen=True, slots=True)
class PostGenerationVerification:
    reference_path: str
    candidate_path: str
    decision: Decision
    similarity: SimilarityRisk
    rationale: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_path": self.reference_path,
            "candidate_path": self.candidate_path,
            "decision": self.decision,
            "similarity": {
                "score": self.similarity.score,
                "level": self.similarity.level,
                "perceptual_similarity": self.similarity.perceptual_similarity,
                "composition_similarity": self.similarity.composition_similarity,
                "color_similarity": self.similarity.color_similarity,
                "recommendation": self.similarity.recommendation,
            },
            "rationale": list(self.rationale),
        }


def verify_generated_candidate(reference: Path, candidate: Path) -> PostGenerationVerification:
    """Compare generated output against its source reference.

    Scores at the existing blocked threshold cannot proceed as final output.
    Lower scores remain human-review signals, matching StockForge's existing
    no-auto-approve policy.
    """
    reference = Path(reference)
    candidate = Path(candidate)
    risk = analyze_similarity_risk(reference, candidate)
    if risk.level == "blocked":
        decision: Decision = "BLOCK"
        rationale = (
            "Generated output is too visually similar to the supplied reference.",
            "Regenerate with stronger changes to subject, composition, palette, or structure.",
        )
    else:
        decision = "REVIEW"
        rationale = (
            "No automatic approval is issued.",
            "Continue through technical checks and human review before finalization.",
        )
    return PostGenerationVerification(
        reference_path=str(reference),
        candidate_path=str(candidate),
        decision=decision,
        similarity=risk,
        rationale=rationale,
    )


def require_post_generation_distance(reference: Path, candidate: Path) -> PostGenerationVerification:
    verification = verify_generated_candidate(reference, candidate)
    if verification.decision == "BLOCK":
        raise ValueError(
            "Generated candidate blocked by post-generation similarity verification."
        )
    return verification
