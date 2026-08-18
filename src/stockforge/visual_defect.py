"""Lightweight pixel-level visual defect signals for stock assets."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageStat

from .visual_qa import VisualQAReport, inspect_visual

DEFECT_QA_SCHEMA_VERSION = 1
DEFECT_STATUSES = frozenset({"pass", "warn", "fail"})

class VisualDefectError(ValueError):
    """Raised when visual defect inspection cannot be performed."""

@dataclass(frozen=True, slots=True)
class VisualDefectPolicy:
    min_luma_stddev: float = 3.0
    max_dark_clip_ratio: float = 0.08
    max_bright_clip_ratio: float = 0.08
    flat_image_stddev: float = 1.0
    warn_luma_stddev: float = 8.0

    def __post_init__(self) -> None:
        if self.min_luma_stddev < 0 or self.flat_image_stddev < 0 or self.warn_luma_stddev < 0:
            raise VisualDefectError("luminance thresholds must be non-negative")
        if not 0 <= self.max_dark_clip_ratio <= 1 or not 0 <= self.max_bright_clip_ratio <= 1:
            raise VisualDefectError("clip ratios must be between 0 and 1")
        if self.flat_image_stddev > self.min_luma_stddev:
            raise VisualDefectError("flat_image_stddev must not exceed min_luma_stddev")

@dataclass(frozen=True, slots=True)
class VisualDefectReport:
    status: Literal["pass", "warn", "fail"]
    path: str
    structural_status: Literal["pass", "warn", "fail"]
    visual_status: Literal["pass", "warn", "fail"]
    luminance_mean: float | None
    luminance_stddev: float | None
    dark_clip_ratio: float | None
    bright_clip_ratio: float | None
    checks: dict[str, str]
    schema_version: int = DEFECT_QA_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.status not in DEFECT_STATUSES:
            raise VisualDefectError(f"Unsupported defect status: {self.status}")
        if self.schema_version != DEFECT_QA_SCHEMA_VERSION:
            raise VisualDefectError(f"Unsupported defect schema: {self.schema_version}")

def _pixel_ratios(gray: Image.Image) -> tuple[float, float]:
    histogram = gray.histogram()
    total = gray.width * gray.height
    if total == 0:
        raise VisualDefectError("image contains no pixels")
    return sum(histogram[:3]) / total, sum(histogram[253:]) / total

def inspect_visual_defects(path: Path, *, visual: VisualQAReport | None = None, policy: VisualDefectPolicy | None = None) -> VisualDefectReport:
    policy = policy or VisualDefectPolicy()
    image_path = Path(path)
    if not image_path.is_file():
        raise VisualDefectError(f"Image file does not exist: {image_path}")
    visual_report = visual or inspect_visual(image_path)
    checks = {"structural": visual_report.structural_status, "visual_sanity": visual_report.status}
    try:
        with Image.open(image_path) as image:
            image.load()
            gray = image.convert("L")
            stats = ImageStat.Stat(gray)
            mean = float(stats.mean[0])
            stddev = float(stats.stddev[0])
            dark_ratio, bright_ratio = _pixel_ratios(gray)
    except Exception as exc:
        raise VisualDefectError(f"Unable to decode image pixels: {image_path}") from exc
    checks["flat_image"] = "fail" if stddev <= policy.flat_image_stddev else "pass"
    checks["luminance_variation"] = "fail" if stddev < policy.min_luma_stddev else ("warn" if stddev < policy.warn_luma_stddev else "pass")
    checks["dark_clipping"] = "fail" if dark_ratio > policy.max_dark_clip_ratio else "pass"
    checks["bright_clipping"] = "fail" if bright_ratio > policy.max_bright_clip_ratio else "pass"
    status: Literal["pass", "warn", "fail"] = "fail" if "fail" in checks.values() else ("warn" if "warn" in checks.values() else "pass")
    return VisualDefectReport(status, str(image_path), visual_report.structural_status, visual_report.status, mean, stddev, dark_ratio, bright_ratio, checks)
