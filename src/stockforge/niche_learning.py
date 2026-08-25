"""Transparent learning summaries for portfolio niche decisions.

The learning layer consumes only persisted generation reviews. It never treats
sales, ranking, or marketplace approval as observed unless the user explicitly
records that outcome, and it never mutates a brief or triggers generation.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from .generation_evaluation import GenerationEvaluation, SCORE_FIELDS, load_evaluations


@dataclass(frozen=True, slots=True)
class NicheLearningRecord:
    """Aggregated evidence for one lane and buyer-job combination."""

    lane_key: str
    buyer_job: str
    record_count: int
    decision_counts: dict[str, int]
    average_scores: dict[str, float]
    overall_average: float
    rejection_reasons: dict[str, int]
    marketplace_outcome_counts: dict[str, int]
    recommendation: str
    confidence: str
    next_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "lane_key": self.lane_key,
            "buyer_job": self.buyer_job,
            "record_count": self.record_count,
            "decision_counts": dict(self.decision_counts),
            "average_scores": dict(self.average_scores),
            "overall_average": self.overall_average,
            "rejection_reasons": dict(self.rejection_reasons),
            "marketplace_outcome_counts": dict(self.marketplace_outcome_counts),
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "next_action": self.next_action,
        }


def _recommendation(records: list[GenerationEvaluation]) -> tuple[str, str, str]:
    """Return a conservative action, confidence, and explanation."""
    count = len(records)
    averages = {
        field: sum(getattr(item, field) for item in records) / count
        for field in SCORE_FIELDS
    }
    decisions = Counter(item.decision for item in records)
    overall = sum(averages.values()) / len(SCORE_FIELDS)
    if count == 1:
        return (
            "INSUFFICIENT_EVIDENCE",
            "initial",
            "Use this record to refine the next brief; one review cannot establish a niche policy or market demand.",
        )
    if decisions["reject"] > decisions["accept"] and averages["buyer_fit"] < 3:
        return (
            "PAUSE_AND_RESEARCH",
            "emerging",
            "Pause new generation in this lane and revisit the buyer job or product definition before spending another GPU request.",
        )
    weak = [field for field, value in averages.items() if value < 3]
    if weak:
        return (
            "REFINE_BRIEF",
            "emerging",
            "Refine the brief around the weak review dimensions before another materially distinct trial: " + ", ".join(weak) + ".",
        )
    if decisions["accept"] >= decisions["reject"] and overall >= 4:
        return (
            "KEEP_AND_VALIDATE",
            "emerging",
            "Keep the niche hypothesis and validate with a materially distinct concept or a marketplace outcome; do not duplicate the same prompt.",
        )
    return (
        "REVIEW_REQUIRED",
        "emerging",
        "Keep the lane under review and collect a clearer buyer-fit signal before changing the production policy.",
    )


def summarize_niche_records(records: Iterable[GenerationEvaluation]) -> list[NicheLearningRecord]:
    """Aggregate records by lane and buyer job with conservative recommendations."""
    grouped: defaultdict[tuple[str, str], list[GenerationEvaluation]] = defaultdict(list)
    for record in records:
        grouped[(record.lane_key, record.buyer_job)].append(record)

    summaries: list[NicheLearningRecord] = []
    for (lane_key, buyer_job), items in sorted(grouped.items()):
        decision_counts = Counter(item.decision for item in items)
        averages = {
            field: round(sum(getattr(item, field) for item in items) / len(items), 2)
            for field in SCORE_FIELDS
        }
        overall = round(sum(averages.values()) / len(SCORE_FIELDS), 2)
        reasons = Counter(reason for item in items for reason in item.rejection_reasons)
        outcomes = Counter(item.marketplace_outcome for item in items)
        recommendation, confidence, next_action = _recommendation(items)
        summaries.append(
            NicheLearningRecord(
                lane_key=lane_key,
                buyer_job=buyer_job,
                record_count=len(items),
                decision_counts=dict(sorted(decision_counts.items())),
                average_scores=averages,
                overall_average=overall,
                rejection_reasons=dict(sorted(reasons.items())),
                marketplace_outcome_counts=dict(sorted(outcomes.items())),
                recommendation=recommendation,
                confidence=confidence,
                next_action=next_action,
            )
        )
    return summaries


def summarize_niche_learning(project_root: str) -> dict[str, object]:
    """Return a JSON-ready learning report for the portfolio decision layer."""
    records = load_evaluations(project_root)
    summaries = summarize_niche_records(records)
    return {
        "record_count": len(records),
        "niche_count": len(summaries),
        "niches": [item.to_dict() for item in summaries],
        "notice": (
            "Learning summaries describe reviewed generation records only. They are not sales forecasts, ranking predictions, "
            "marketplace approval estimates, or automatic permission to generate."
        ),
    }
