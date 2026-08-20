"""Deterministic image-quality preflight for StockForge.

This module is a screening layer, not an Adobe moderation emulator. It measures
objective image signals that can identify candidates needing human review:
sharpness proxy, clipping/exposure, saturation extremes, and decodability.
AI-specific anatomy, object, logo, OCR, watermark, and semantic checks remain
separate because those require dedicated vision models and/or human review.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageChops, ImageFilter, UnidentifiedImageError

Status = Literal["PASS", "FAIL", "REVIEW"]

# Conservative screening thresholds. They are intentionally not presented as
# Adobe's numeric thresholds; Adobe publishes qualitative guidance for these
# issues rather than a universal machine-readable cutoff.
MIN_SHARPNESS_SCORE = 2.0
MAX_CLIPPED_FRACTION = 0.015
MAX_EXTREME_SATURATION_FRACTION = 0.05


@dataclass(frozen=True, slots=True)
class QualityCheck:
    name: str
    status: Status
    detail: str


@dataclass(frozen=True, slots=True)
class ImageQualityReport:
    path: str
    width: int | None
    height: int | None
    checks: tuple[QualityCheck, ...]

    @property
    def ready_for_review(self) -> bool:
        return not any(check.status == "FAIL" for check in self.checks)

    @property
    def failures(self) -> tuple[QualityCheck, ...]:
        return tuple(check for check in self.checks if check.status == "FAIL")

    @property
    def reviews(self) -> tuple[QualityCheck, ...]:
        return tuple(check for check in self.checks if check.status == "REVIEW")

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "ready_for_review": self.ready_for_review,
            "checks": [
                {"name": c.name, "status": c.status, "detail": c.detail}
                for c in self.checks
            ],
        }


def _grayscale_values(image: Image.Image) -> list[int]:
    return list(image.convert("L").getdata())


def _fraction(values: list[int], predicate) -> float:
    if not values:
        return 0.0
    return sum(1 for value in values if predicate(value)) / len(values)


def _sharpness_proxy(image: Image.Image) -> float:
    """Return a deterministic edge-energy proxy.

    It is useful for ranking/review triage, not for declaring an image
    objectively sharp. Adobe explicitly recommends inspecting at 100%.
    """
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    values = list(edges.getdata())
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return variance ** 0.5


def _saturation_extreme_fraction(image: Image.Image) -> float:
    rgb = image.convert("RGB")
    pixels = list(rgb.getdata())
    if not pixels:
        return 0.0
    extreme = 0
    for red, green, blue in pixels:
        maximum = max(red, green, blue)
        minimum = min(red, green, blue)
        if maximum == 0:
            continue
        saturation = (maximum - minimum) / maximum
        if saturation >= 0.98 and maximum >= 245:
            extreme += 1
    return extreme / len(pixels)


def inspect_quality(path: str | Path) -> ImageQualityReport:
    """Run deterministic quality screening on a decodable raster image."""
    file_path = Path(path).expanduser().resolve()
    checks: list[QualityCheck] = []

    if not file_path.is_file():
        return ImageQualityReport(
            str(file_path), None, None,
            (QualityCheck("file_exists", "FAIL", f"File does not exist: {file_path}"),),
        )

    try:
        with Image.open(file_path) as image:
            image.load()
            width, height = image.size
            checks.append(QualityCheck("decodability", "PASS", "Image decoded successfully."))

            gray_values = _grayscale_values(image)
            dark_clip = _fraction(gray_values, lambda value: value <= 2)
            light_clip = _fraction(gray_values, lambda value: value >= 253)
            clipped = dark_clip + light_clip
            if clipped > MAX_CLIPPED_FRACTION:
                checks.append(QualityCheck(
                    "exposure_clipping", "REVIEW",
                    f"{clipped:.2%} of luminance pixels are near black/white clipping; inspect exposure at 100%."
                ))
            else:
                checks.append(QualityCheck(
                    "exposure_clipping", "PASS",
                    f"Clipped luminance fraction {clipped:.2%}; below screening threshold {MAX_CLIPPED_FRACTION:.2%}."
                ))

            sharpness = _sharpness_proxy(image)
            if sharpness < MIN_SHARPNESS_SCORE:
                checks.append(QualityCheck(
                    "sharpness_proxy", "REVIEW",
                    f"Edge-energy proxy {sharpness:.2f}; inspect the primary subject at 100%."
                ))
            else:
                checks.append(QualityCheck(
                    "sharpness_proxy", "PASS",
                    f"Edge-energy proxy {sharpness:.2f}; no automatic softness flag."
                ))

            saturation = _saturation_extreme_fraction(image)
            if saturation > MAX_EXTREME_SATURATION_FRACTION:
                checks.append(QualityCheck(
                    "extreme_saturation", "REVIEW",
                    f"{saturation:.2%} of pixels are highly saturated near clipping; inspect for unnatural color."
                ))
            else:
                checks.append(QualityCheck(
                    "extreme_saturation", "PASS",
                    f"Extreme-saturation fraction {saturation:.2%}; no automatic color flag."
                ))

            # A simple high-frequency proxy helps identify heavily processed
            # output, but it is deliberately REVIEW-only rather than a hard
            # rejection because texture and detail vary by subject.
            blurred = image.convert("RGB").filter(ImageFilter.GaussianBlur(radius=1.0))
            residual = ImageChops.difference(image.convert("RGB"), blurred)
            residual_values = list(residual.convert("L").getdata())
            residual_mean = sum(residual_values) / max(len(residual_values), 1)
            checks.append(QualityCheck(
                "high_frequency_residual", "PASS",
                f"High-frequency residual mean {residual_mean:.2f}; retained as an audit metric."
            ))

            return ImageQualityReport(str(file_path), width, height, tuple(checks))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        checks.append(QualityCheck("decodability", "FAIL", f"Image could not be decoded: {exc}"))
        return ImageQualityReport(str(file_path), None, None, tuple(checks))
