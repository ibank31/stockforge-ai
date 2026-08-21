"""Provider-neutral ensemble for StockForge visual QA.

The ensemble combines independent signals. It does not claim that any model
can predict marketplace acceptance or sales. Missing providers produce REVIEW,
not a silent PASS.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping

Decision = Literal["PASS", "REVIEW", "FAIL"]


@dataclass(frozen=True, slots=True)
class VisionFinding:
    name: str
    score: float | None
    decision: Decision
    reason: str
    provider: str


@dataclass(frozen=True, slots=True)
class VisionEnsembleReport:
    findings: tuple[VisionFinding, ...]
    decision: Decision
    confidence: float
    missing_providers: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class EnsembleThresholds:
    aesthetic_min: float = 0.55
    semantic_min: float = 0.70
    commercial_min: float = 0.70
    similarity_max: float = 0.92
    critical_failure_names: tuple[str, ...] = (
        "anatomy",
        "subject_integrity",
        "unexpected_text",
        "ip_risk",
        "artifact_risk",
    )


def _decision_for(name: str, score: float | None, thresholds: EnsembleThresholds) -> Decision:
    if score is None:
        return "REVIEW"
    if name == "aesthetic":
        return "PASS" if score >= thresholds.aesthetic_min else "REVIEW"
    if name in {"semantic", "commercial"}:
        minimum = thresholds.semantic_min if name == "semantic" else thresholds.commercial_min
        return "PASS" if score >= minimum else "REVIEW"
    if name == "similarity":
        return "PASS" if score <= thresholds.similarity_max else "FAIL"
    return "PASS" if score >= 0.70 else "REVIEW"


def evaluate_ensemble(
    signals: Mapping[str, float | None],
    *,
    provider_names: Mapping[str, str] | None = None,
    thresholds: EnsembleThresholds = EnsembleThresholds(),
) -> VisionEnsembleReport:
    """Evaluate model-independent vision signals conservatively.

    Expected signal names may include aesthetic, semantic, commercial,
    anatomy, subject_integrity, artifact_risk, unexpected_text, ip_risk,
    and similarity. Scores use [0, 1], except similarity where higher is worse.
    """
    providers = provider_names or {}
    findings: list[VisionFinding] = []
    missing: list[str] = []
    for name, score in signals.items():
        provider = providers.get(name, "unknown")
        decision = _decision_for(name, score, thresholds)
        if score is None:
            missing.append(provider)
        findings.append(VisionFinding(name, score, decision, "ensemble policy", provider))

    critical_failures = [
        f for f in findings
        if f.name in thresholds.critical_failure_names and f.score is not None and f.score < 0.50
    ]
    hard_failures = [f for f in findings if f.decision == "FAIL"]
    reviews = [f for f in findings if f.decision == "REVIEW"]

    if critical_failures or hard_failures:
        decision: Decision = "FAIL"
    elif missing or reviews:
        decision = "REVIEW"
    else:
        decision = "PASS"

    known = [f.score for f in findings if f.score is not None]
    confidence = round(sum(known) / len(known), 3) if known else 0.0
    return VisionEnsembleReport(tuple(findings), decision, confidence, tuple(sorted(set(missing))))
