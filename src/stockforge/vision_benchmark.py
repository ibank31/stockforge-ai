"""Offline benchmark harness for StockForge vision providers.

The harness compares provider outputs against human-labeled reference records.
It never downloads models and does not make marketplace-acceptance claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class LabeledImage:
    image_id: str
    labels: Mapping[str, bool]


@dataclass(frozen=True, slots=True)
class ProviderMetrics:
    provider: str
    evaluated: int
    accuracy: float
    false_positive_rate: float
    false_negative_rate: float


def _binary(value: float | bool | None, threshold: float = 0.5) -> bool | None:
    if value is None:
        return None
    return value if isinstance(value, bool) else value >= threshold


def score_provider(
    provider: str,
    references: Iterable[LabeledImage],
    predictions: Mapping[str, Mapping[str, float | bool | None]],
    signal: str,
    *,
    threshold: float = 0.5,
) -> ProviderMetrics:
    tp = tn = fp = fn = 0
    for item in references:
        expected = item.labels.get(signal)
        predicted = _binary(predictions.get(item.image_id, {}).get(signal), threshold)
        if expected is None or predicted is None:
            continue
        if expected and predicted:
            tp += 1
        elif not expected and not predicted:
            tn += 1
        elif predicted:
            fp += 1
        else:
            fn += 1
    total = tp + tn + fp + fn
    if total == 0:
        return ProviderMetrics(provider, 0, 0.0, 0.0, 0.0)
    return ProviderMetrics(
        provider=provider,
        evaluated=total,
        accuracy=round((tp + tn) / total, 4),
        false_positive_rate=round(fp / (fp + tn), 4) if fp + tn else 0.0,
        false_negative_rate=round(fn / (fn + tp), 4) if fn + tp else 0.0,
    )


def rank_providers(metrics: Iterable[ProviderMetrics]) -> list[ProviderMetrics]:
    """Rank by accuracy first, then lower false negatives/positives."""
    return sorted(
        metrics,
        key=lambda m: (m.accuracy, -m.false_negative_rate, -m.false_positive_rate),
        reverse=True,
    )
