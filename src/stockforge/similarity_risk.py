"""Similarity risk analysis for StockForge V2.

This module does not claim semantic understanding. It combines independent,
explainable visual signals so a reference can inform a new asset without being
treated as a template to copy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .dedup import average_hash, compare_fingerprints

RiskLevel = Literal["low", "medium", "high", "blocked"]


@dataclass(frozen=True, slots=True)
class SimilarityRisk:
    score: float
    level: RiskLevel
    perceptual_similarity: float
    composition_similarity: float
    color_similarity: float
    recommendation: str


def _require_pillow():
    try:
        from PIL import Image, ImageStat
    except ImportError as exc:
        raise ValueError("Pillow is required for similarity risk analysis") from exc
    return Image, ImageStat


def _composition_similarity(left: Path, right: Path) -> float:
    Image, _ = _require_pillow()
    with Image.open(left) as a, Image.open(right) as b:
        a = a.convert("L").resize((8, 8))
        b = b.convert("L").resize((8, 8))
        av = list(a.getdata())
        bv = list(b.getdata())
    diff = sum(abs(x - y) for x, y in zip(av, bv)) / (len(av) * 255)
    return max(0.0, 1.0 - diff)


def _color_similarity(left: Path, right: Path) -> float:
    Image, ImageStat = _require_pillow()
    with Image.open(left) as a, Image.open(right) as b:
        a = a.convert("RGB").resize((32, 32))
        b = b.convert("RGB").resize((32, 32))
        ma = ImageStat.Stat(a).mean
        mb = ImageStat.Stat(b).mean
    diff = sum(abs(x - y) for x, y in zip(ma, mb)) / (3 * 255)
    return max(0.0, 1.0 - diff)


def analyze_similarity_risk(reference: Path, candidate: Path) -> SimilarityRisk:
    """Return an explainable risk score from 0 to 100.

    The score intentionally errs toward caution: high visual resemblance is a
    review/block signal, never proof of copyright infringement.
    """
    reference = Path(reference)
    candidate = Path(candidate)
    fp = compare_fingerprints(average_hash(reference), average_hash(candidate))
    composition = _composition_similarity(reference, candidate)
    color = _color_similarity(reference, candidate)
    score = round(100 * (0.50 * fp.similarity + 0.30 * composition + 0.20 * color), 2)

    if score >= 95:
        level: RiskLevel = "blocked"
        recommendation = "DO_NOT_USE_AS_FINAL: regenerate with stronger transformation."
    elif score >= 85:
        level = "high"
        recommendation = "HIGH_RISK: change composition, palette, and visual structure."
    elif score >= 70:
        level = "medium"
        recommendation = "REVIEW: add stronger differentiation before finalization."
    else:
        level = "low"
        recommendation = "LOWER_RISK: continue to technical and human review."

    return SimilarityRisk(
        score=score,
        level=level,
        perceptual_similarity=round(fp.similarity, 4),
        composition_similarity=round(composition, 4),
        color_similarity=round(color, 4),
        recommendation=recommendation,
    )
