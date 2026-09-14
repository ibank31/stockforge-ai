"""Deterministic screenshot auto-crop support for StockForge V2.

The cropper does not claim semantic object detection. It ranks visually rich
rectangles so screenshots containing UI, text and a featured asset can be
reduced to reviewable crop candidates. Human confirmation remains mandatory.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat, UnidentifiedImageError


class AutoCropError(ValueError):
    """Raised when a source cannot safely produce crop candidates."""


@dataclass(frozen=True, slots=True)
class CropBox:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def to_dict(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
            "width": self.width,
            "height": self.height,
        }


@dataclass(frozen=True, slots=True)
class CropCandidate:
    rank: int
    box: CropBox
    score: float
    aspect_ratio: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "box": self.box.to_dict(),
            "score": self.score,
            "aspect_ratio": self.aspect_ratio,
            "reasons": list(self.reasons),
        }


def _load(source: Path) -> Image.Image:
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise AutoCropError(f"Reference does not exist: {source}")
    try:
        with Image.open(source) as probe:
            probe.verify()
        with Image.open(source) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise AutoCropError("Animated references are not supported.")
            image.load()
            return image.convert("RGB")
    except AutoCropError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, RuntimeError) as exc:
        raise AutoCropError(f"Reference is not a safely decodable image: {exc}") from exc


def _resize_for_scan(image: Image.Image, max_side: int = 192) -> tuple[Image.Image, float, float]:
    width, height = image.size
    scale = min(1.0, max_side / max(width, height))
    if scale == 1.0:
        return image, 1.0, 1.0
    small = image.resize((max(1, round(width * scale)), max(1, round(height * scale))))
    return small, width / small.width, height / small.height


def _region_score(image: Image.Image, box: tuple[int, int, int, int], global_mean: float) -> float:
    region = image.crop(box)
    stat = ImageStat.Stat(region)
    rgb_mean = sum(stat.mean[:3]) / 3
    rgb_var = sum(stat.var[:3]) / 3
    width, height = region.size
    pixels = max(1, width * height)
    # Texture/variation helps suppress flat UI backgrounds. Difference from the
    # whole screenshot helps surface featured media without pretending semantics.
    variation = min(math.sqrt(max(rgb_var, 0.0)) / 64.0, 1.5)
    contrast = min(abs(rgb_mean - global_mean) / 96.0, 1.0)
    area = math.sqrt(pixels / max(1, image.width * image.height))
    return variation * 1.7 + contrast * 0.7 + area * 0.35


def _iou(a: CropBox, b: CropBox) -> float:
    left = max(a.left, b.left)
    top = max(a.top, b.top)
    right = min(a.right, b.right)
    bottom = min(a.bottom, b.bottom)
    overlap = max(0, right - left) * max(0, bottom - top)
    union = a.width * a.height + b.width * b.height - overlap
    return overlap / union if union else 0.0


def _scan_boxes(image: Image.Image) -> list[tuple[float, CropBox, tuple[str, ...]]]:
    ratios = (1.0, 4 / 3, 3 / 2, 16 / 9, 2.0, 3 / 4)
    fractions = (0.30, 0.42, 0.56, 0.70, 0.84)
    global_mean = sum(ImageStat.Stat(image).mean[:3]) / 3
    results: list[tuple[float, CropBox, tuple[str, ...]]] = []

    for fraction in fractions:
        target_area = image.width * image.height * fraction
        for ratio in ratios:
            width = int(round(math.sqrt(target_area * ratio)))
            height = int(round(width / ratio))
            if width < 8 or height < 8 or width > image.width or height > image.height:
                continue
            step_x = max(1, width // 5)
            step_y = max(1, height // 5)
            xs = list(range(0, image.width - width + 1, step_x))
            ys = list(range(0, image.height - height + 1, step_y))
            if xs[-1] != image.width - width:
                xs.append(image.width - width)
            if ys[-1] != image.height - height:
                ys.append(image.height - height)
            for left in xs:
                for top in ys:
                    box = (left, top, left + width, top + height)
                    score = _region_score(image, box, global_mean)
                    center_x = (left + width / 2) / image.width
                    center_y = (top + height / 2) / image.height
                    center_bonus = max(0.0, 1.0 - math.hypot(center_x - 0.5, center_y - 0.5) * 1.5) * 0.12
                    results.append(
                        (
                            score + center_bonus,
                            CropBox(*box),
                            ("visually rich region", "screen layout candidate"),
                        )
                    )
    return results


def suggest_crop_candidates(source: Path, *, limit: int = 5) -> tuple[CropCandidate, ...]:
    """Return distinct auto-crop candidates. Never mutates the source image."""

    if limit < 1 or limit > 10:
        raise AutoCropError("Crop candidate limit must be between 1 and 10.")

    original = _load(source)
    scan, scale_x, scale_y = _resize_for_scan(original)
    selected: list[tuple[float, CropBox, tuple[str, ...]]] = []
    for score, box, reasons in sorted(_scan_boxes(scan), key=lambda item: item[0], reverse=True):
        scaled = CropBox(
            left=max(0, round(box.left * scale_x)),
            top=max(0, round(box.top * scale_y)),
            right=min(original.width, round(box.right * scale_x)),
            bottom=min(original.height, round(box.bottom * scale_y)),
        )
        if scaled.width < 2 or scaled.height < 2:
            continue
        if any(_iou(scaled, existing) > 0.82 for _score, existing, _reasons in selected):
            continue
        selected.append((score, scaled, reasons))
        if len(selected) >= limit:
            break

    if not selected:
        raise AutoCropError("No usable crop candidates were found.")

    return tuple(
        CropCandidate(
            rank=index,
            box=box,
            score=round(score, 6),
            aspect_ratio=round(box.width / box.height, 6),
            reasons=reasons,
        )
        for index, (score, box, reasons) in enumerate(selected, start=1)
    )


def crop_reference(
    source: Path,
    destination: Path,
    box: CropBox,
) -> Path:
    """Apply a human-confirmed crop and preserve the source unchanged."""

    image = _load(source)
    if not (0 <= box.left < box.right <= image.width and 0 <= box.top < box.bottom <= image.height):
        raise AutoCropError("Crop box is outside the source image bounds.")

    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    cropped = image.crop((box.left, box.top, box.right, box.bottom))
    try:
        cropped.save(destination)
    except OSError as exc:
        raise AutoCropError(f"Could not save cropped reference: {exc}") from exc
    return destination
