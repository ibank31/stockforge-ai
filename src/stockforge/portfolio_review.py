"""Deterministic post-generation screening for StockForge portfolio assets.

This module is intentionally conservative.  It combines local pixel-quality
signals and project-local perceptual similarity into a review decision, but it
never infers marketplace acceptance, legal clearance, or semantic correctness.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

from .artifact import Artifact
from .dedupe_pipeline import DedupePipelineError, compare_images
from .image_quality import inspect_quality
from .microstock_similarity import combine_similarity, compare_composition, composition_fingerprint


ReviewDecision = Literal["REJECT", "REVIEW"]


@dataclass(frozen=True, slots=True)
class SimilarityFinding:
    artifact_id: str
    relative_path: str
    classification: str
    similarity: float | None
    detail: str
    composition_similarity: float | None = None
    composition_classification: str | None = None
    risk: str | None = None


@dataclass(frozen=True, slots=True)
class PortfolioReviewReport:
    decision: ReviewDecision
    quality: dict[str, object]
    similarities: tuple[SimilarityFinding, ...]
    reasons: tuple[str, ...]
    notice: str = (
        "Deterministic screening only. Human visual, IP, metadata, and "
        "marketplace review remain required."
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision,
            "quality": self.quality,
            "similarities": [asdict(item) for item in self.similarities],
            "reasons": list(self.reasons),
            "notice": self.notice,
        }


def evaluate_portfolio_candidate(
    source: Path,
    *,
    project_root: Path,
    current_artifact_id: str,
    project_artifacts: Iterable[Artifact],
) -> PortfolioReviewReport:
    """Screen one generated asset against local quality and existing project files.

    The work is CPU-only.  A hard technical quality failure or an exact/perceptual
    duplicate rejects the candidate.  Everything else remains human review,
    including a visually distinct image: no local screen can certify semantic
    adherence, rights, or marketplace suitability.
    """
    candidate = Path(source).resolve()
    root = Path(project_root).resolve()
    quality = inspect_quality(candidate)
    quality_payload = quality.to_dict()
    reasons: list[str] = []
    if not quality.ready_for_review:
        reasons.append("deterministic image-quality screen failed")

    findings: list[SimilarityFinding] = []
    for artifact in project_artifacts:
        if artifact.id == current_artifact_id or artifact.kind not in {"generated-image", "finalized-master"}:
            continue
        comparison_path = (root / artifact.relative_path).resolve()
        try:
            comparison_path.relative_to(root)
        except ValueError:
            continue
        if not comparison_path.is_file():
            continue
        try:
            result = compare_images(candidate, comparison_path)
        except (DedupePipelineError, OSError, ValueError) as exc:
            findings.append(SimilarityFinding(
                artifact.id,
                artifact.relative_path,
                "unavailable",
                None,
                f"Similarity screen unavailable: {type(exc).__name__}",
            ))
            continue

        similarity = result.comparison.similarity if result.comparison is not None else 1.0
        try:
            composition = compare_composition(
                composition_fingerprint(candidate),
                composition_fingerprint(comparison_path),
            )
            combined = combine_similarity(
                perceptual_similarity=similarity,
                perceptual_classification=result.classification,
                composition=composition,
            )
            composition_similarity = round(composition.similarity, 4)
            composition_classification = composition.classification
            risk = combined.risk
        except (OSError, ValueError):
            composition_similarity = None
            composition_classification = "unavailable"
            risk = "UNKNOWN"
        findings.append(SimilarityFinding(
            artifact.id,
            artifact.relative_path,
            result.classification,
            round(similarity, 4),
            "Perceptual and coarse composition signals; human visual comparison remains required.",
            composition_similarity,
            composition_classification,
            risk,
        ))
        if result.classification in {"exact_duplicate", "duplicate"}:
            reasons.append(f"duplicate of existing project artifact {artifact.id}")
        elif risk == "HIGH":
            reasons.append(f"near-identical composition to existing project artifact {artifact.id}; hold for human distinctness review")
        elif result.classification == "similar" or risk == "MEDIUM":
            reasons.append(f"similar to existing project artifact {artifact.id}; hold for human distinctness review")

    decision: ReviewDecision = "REJECT" if any(
        reason.startswith("deterministic image-quality") or reason.startswith("duplicate")
        for reason in reasons
    ) else "REVIEW"
    if not reasons:
        reasons.append("technical screen completed; semantic and commercial review still required")
    return PortfolioReviewReport(decision, quality_payload, tuple(findings), tuple(reasons))
