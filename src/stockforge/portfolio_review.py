"""Deterministic post-generation screening for StockForge assets."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

from .artifact import Artifact
from .dedupe_pipeline import DedupePipelineError, compare_images
from .image_quality import inspect_quality
from .similarity_risk import analyze_similarity_risk

ReviewDecision = Literal["REJECT", "REVIEW"]


@dataclass(frozen=True, slots=True)
class SimilarityFinding:
    artifact_id: str
    relative_path: str
    classification: str
    similarity: float | None
    detail: str


@dataclass(frozen=True, slots=True)
class PortfolioReviewReport:
    decision: ReviewDecision
    quality: dict[str, object]
    similarities: tuple[SimilarityFinding, ...]
    reasons: tuple[str, ...]
    notice: str = "Deterministic screening only. Human visual, IP, metadata, and marketplace review remain required."

    def to_dict(self) -> dict[str, object]:
        return {"decision": self.decision, "quality": self.quality,
                "similarities": [asdict(item) for item in self.similarities],
                "reasons": list(self.reasons), "notice": self.notice}


def evaluate_portfolio_candidate(source: Path, *, project_root: Path,
                                 current_artifact_id: str,
                                 project_artifacts: Iterable[Artifact]) -> PortfolioReviewReport:
    """Screen quality, exact/perceptual duplicates, and V2 similarity risk."""
    candidate, root = Path(source).resolve(), Path(project_root).resolve()
    quality = inspect_quality(candidate)
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
            similarity = result.comparison.similarity if result.comparison else 1.0
            risk = analyze_similarity_risk(comparison_path, candidate)
        except (DedupePipelineError, OSError, ValueError) as exc:
            findings.append(SimilarityFinding(artifact.id, artifact.relative_path, "unavailable", None,
                f"Similarity screen unavailable: {type(exc).__name__}"))
            continue

        classification = result.classification
        detail = (
            f"AHash={similarity:.4f}; V2 risk={risk.score:.2f}/100 ({risk.level}). "
            f"{risk.recommendation}"
        )
        findings.append(SimilarityFinding(artifact.id, artifact.relative_path, classification,
                                          round(similarity, 4), detail))
        if classification in {"exact_duplicate", "duplicate"}:
            reasons.append(f"duplicate of existing project artifact {artifact.id}")
        elif risk.level == "blocked":
            reasons.append(f"V2 similarity risk blocked against existing project artifact {artifact.id}")
        elif risk.level == "high":
            reasons.append(f"high V2 similarity risk against existing project artifact {artifact.id}; regenerate with stronger transformation")
        elif classification == "similar":
            reasons.append(f"similar to existing project artifact {artifact.id}; hold for human distinctness review")

    decision: ReviewDecision = "REJECT" if any(
        reason.startswith(("deterministic image-quality", "duplicate", "V2 similarity risk blocked"))
        for reason in reasons
    ) else "REVIEW"
    if not reasons:
        reasons.append("technical and V2 similarity screens completed; semantic and commercial review still required")
    return PortfolioReviewReport(decision, quality.to_dict(), tuple(findings), tuple(reasons))
