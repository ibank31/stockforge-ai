"""Deterministic edge checks for raster seamless-pattern candidates.

The check is intentionally narrow: it verifies that the opposite edge strips
match closely enough to avoid an obvious boundary when a tile is repeated. It
does not claim that a pattern is commercially useful or that the full image is
free of defects; those remain separate review gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageStat, UnidentifiedImageError


class SeamlessPatternError(ValueError):
    """Raised when a seamless-pattern inspection cannot be performed."""


@dataclass(frozen=True, slots=True)
class SeamCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True, slots=True)
class SeamlessPatternReport:
    path: str
    width: int
    height: int
    edge_width: int
    tolerance: float
    horizontal_error: float | None
    vertical_error: float | None
    ready: bool
    checks: tuple[SeamCheck, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "edge_width": self.edge_width,
            "tolerance": self.tolerance,
            "horizontal_error": self.horizontal_error,
            "vertical_error": self.vertical_error,
            "ready": self.ready,
            "checks": [
                {"name": item.name, "status": item.status, "detail": item.detail}
                for item in self.checks
            ],
        }


def _compare_edges(first: Image.Image, last: Image.Image) -> float:
    difference = ImageChops.difference(first, last)
    return max(ImageStat.Stat(difference).mean)


def inspect_seamless_raster(
    path: str | Path,
    *,
    edge_width: int = 1,
    tolerance: float = 0.0,
) -> SeamlessPatternReport:
    """Check whether opposite raster edges match within a bounded tolerance.

    The left/right and top/bottom strips are compared in the same order. This
    models the boundary created when the image is placed next to an identical
    copy. The function never modifies the source file.
    """
    file_path = Path(path).expanduser().resolve()
    checks: list[SeamCheck] = []

    if not file_path.is_file():
        return SeamlessPatternReport(
            str(file_path), 0, 0, edge_width, tolerance, None, None, False,
            (SeamCheck("file_exists", "FAIL", "Pattern file does not exist."),),
        )
    if edge_width < 1:
        raise SeamlessPatternError("edge_width must be positive")
    if tolerance < 0:
        raise SeamlessPatternError("tolerance must be non-negative")

    try:
        with Image.open(file_path) as source:
            image = source.convert("RGBA")
            width, height = image.size
            image.load()
    except (UnidentifiedImageError, OSError) as exc:
        return SeamlessPatternReport(
            str(file_path), 0, 0, edge_width, tolerance, None, None, False,
            (SeamCheck("decodable", "FAIL", f"Raster could not be decoded: {exc}."),),
        )

    if width < 2 or height < 2:
        return SeamlessPatternReport(
            str(file_path), width, height, edge_width, tolerance, None, None, False,
            (SeamCheck("dimensions", "FAIL", "Seamless check requires at least 2x2 pixels."),),
        )
    if edge_width > min(width, height) // 2:
        raise SeamlessPatternError("edge_width must not exceed half of the image dimensions")

    left = image.crop((0, 0, edge_width, height))
    right = image.crop((width - edge_width, 0, width, height))
    top = image.crop((0, 0, width, edge_width))
    bottom = image.crop((0, height - edge_width, width, height))
    horizontal_error = _compare_edges(left, right)
    vertical_error = _compare_edges(top, bottom)

    checks.append(
        SeamCheck(
            "horizontal_boundary",
            "PASS" if horizontal_error <= tolerance else "FAIL",
            f"left/right mean channel difference={horizontal_error:.3f}; tolerance={tolerance:.3f}.",
        )
    )
    checks.append(
        SeamCheck(
            "vertical_boundary",
            "PASS" if vertical_error <= tolerance else "FAIL",
            f"top/bottom mean channel difference={vertical_error:.3f}; tolerance={tolerance:.3f}.",
        )
    )
    checks.append(
        SeamCheck(
            "scope",
            "REVIEW",
            "Edge continuity only; visual quality, composition, and commercial utility require separate review.",
        )
    )
    ready = horizontal_error <= tolerance and vertical_error <= tolerance
    return SeamlessPatternReport(
        str(file_path),
        width,
        height,
        edge_width,
        tolerance,
        horizontal_error,
        vertical_error,
        ready,
        tuple(checks),
    )
