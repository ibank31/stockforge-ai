"""Dependency-free semantic-ish visual QA heuristics for stock assets.

Stage 13 deliberately avoids a heavyweight CV stack. It provides deterministic
signals that can be used as a production gate now, while leaving a clean seam
for a future CV provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .image_qa import ImageQAReport, inspect_image

VISUAL_QA_SCHEMA_VERSION = 1
VISUAL_STATUSES = frozenset({"pass", "warn", "fail"})


class VisualQAError(ValueError):
    """Raised when visual QA input is invalid."""


@dataclass(frozen=True, slots=True)
class VisualQAPolicy:
    """Deterministic production heuristics layered on structural QA."""

    max_aspect_ratio: float = 4.0
    min_aspect_ratio: float = 0.25
    max_filename_length: int = 180

    def __post_init__(self) -> None:
        if self.min_aspect_ratio <= 0 or self.max_aspect_ratio <= 0:
            raise VisualQAError("aspect ratio limits must be positive")
        if self.min_aspect_ratio >= self.max_aspect_ratio:
            raise VisualQAError("min_aspect_ratio must be lower than max_aspect_ratio")
        if self.max_filename_length < 1:
            raise VisualQAError("max_filename_length must be positive")


@dataclass(frozen=True, slots=True)
class VisualQAReport:
    """Stable result of deterministic visual sanity checks."""

    status: Literal["pass", "warn", "fail"]
    path: str
    structural_status: Literal["pass", "warn", "fail"]
    aspect_ratio: float | None
    checks: dict[str, str]
    schema_version: int = VISUAL_QA_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.status not in VISUAL_STATUSES:
            raise VisualQAError(f"Unsupported visual QA status: {self.status}")
        if self.schema_version != VISUAL_QA_SCHEMA_VERSION:
            raise VisualQAError(f"Unsupported visual QA schema: {self.schema_version}")


def inspect_visual(
    path: Path,
    *,
    structural: ImageQAReport | None = None,
    policy: VisualQAPolicy | None = None,
) -> VisualQAReport:
    """Run structural QA plus deterministic visual sanity checks."""
    policy = policy or VisualQAPolicy()
    image_path = Path(path)
    report = structural or inspect_image(image_path)
    checks = {"structural": report.status}

    aspect_ratio: float | None = None
    if report.width and report.height:
        aspect_ratio = report.width / report.height
        checks["aspect_ratio"] = (
            "pass" if policy.min_aspect_ratio <= aspect_ratio <= policy.max_aspect_ratio else "fail"
        )
    else:
        checks["aspect_ratio"] = "fail"

    checks["filename"] = "pass" if len(image_path.name) <= policy.max_filename_length else "warn"

    if "fail" in checks.values():
        status: Literal["pass", "warn", "fail"] = "fail"
    elif "warn" in checks.values():
        status = "warn"
    else:
        status = "pass"

    return VisualQAReport(status, str(image_path), report.status, aspect_ratio, checks)
