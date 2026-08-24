"""Master-candidate finalization after an explicit visual upscale step.

This module intentionally separates three concerns:

1. An :class:`~stockforge.upscaler.Upscaler` performs the visual/GPU change.
2. This module validates the output size and exports an Adobe-oriented JPEG/sRGB
   candidate through ``adobe_finalize``.
3. The caller persists lineage and requires human visual/legal review.

A technically valid master is *not* marketplace-approved.  No function in this
module labels an asset ``submission_ready``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .adobe_finalize import AdobeFinalizationError, FinalizationReport, finalize_image
from .adobe_gate import MAX_MEGA_PIXELS, inspect_image
from .upscaler import UpscaleReport, UpscaleRequest, Upscaler, UpscalerError


class MasterFinalizationError(RuntimeError):
    """Raised when a master candidate cannot safely be prepared."""


@dataclass(frozen=True, slots=True)
class MasterTarget:
    """A deliberately conservative cross-market raster target."""

    minimum_megapixels: float = 6.0
    scale: int = 4

    def __post_init__(self) -> None:
        if self.minimum_megapixels < 4.0 or self.minimum_megapixels > MAX_MEGA_PIXELS:
            raise MasterFinalizationError(
                f"minimum_megapixels must be between 4 and {MAX_MEGA_PIXELS:g}."
            )
        if self.scale not in {2, 4}:
            raise MasterFinalizationError("scale must be 2 or 4 for an AI upscale provider.")


@dataclass(frozen=True, slots=True)
class MasterFinalizationReport:
    """Traceable result of visual upscale plus deterministic JPEG finalization."""

    source_path: str
    master_path: str
    intermediate_path: str
    upscale: UpscaleReport
    jpeg: FinalizationReport
    minimum_megapixels: float
    quality_state: str = "visual_review_required"

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "master_path": self.master_path,
            "intermediate_path": self.intermediate_path,
            "upscale": self.upscale.to_dict(),
            "jpeg": self.jpeg.to_dict(),
            "minimum_megapixels": self.minimum_megapixels,
            "quality_state": self.quality_state,
            "notice": (
                "Technical output passed deterministic checks only. Full-resolution visual, "
                "rights, policy, metadata, distinctness, and marketplace-specific review remain required."
            ),
        }


def _source_dimensions(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            image.load()
            return image.size
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise MasterFinalizationError(f"Source image could not be decoded: {exc}") from exc


def finalize_master_candidate(
    *,
    source: str | Path,
    destination: str | Path,
    upscaler: Upscaler,
    target: MasterTarget = MasterTarget(),
    assume_srgb_after_upscale: bool = True,
) -> MasterFinalizationReport:
    """Create one JPEG/sRGB master candidate from one selected preview.

    The upscaler is expected to be an actual visual/GPU provider.  This function
    does not silently resize with Pillow or treat a changed file extension as an
    upscale.  The intermediate result is retained next to the master so a human
    reviewer can inspect the exact visual transform before the delivery package
    is built.
    """

    source_path = Path(source).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve()
    if not source_path.is_file():
        raise MasterFinalizationError(f"Source image does not exist: {source_path}")
    if source_path == destination_path:
        raise MasterFinalizationError("Source and destination must be different files.")
    if destination_path.suffix.lower() not in {".jpg", ".jpeg"}:
        raise MasterFinalizationError("Master destination must use a .jpg or .jpeg extension.")

    source_width, source_height = _source_dimensions(source_path)
    expected_width = source_width * target.scale
    expected_height = source_height * target.scale
    expected_megapixels = (expected_width * expected_height) / 1_000_000
    if expected_megapixels > MAX_MEGA_PIXELS:
        raise MasterFinalizationError(
            f"{target.scale}x upscale would create {expected_megapixels:.2f} MP, "
            f"above the {MAX_MEGA_PIXELS:g} MP technical ceiling. Use a smaller source or scale."
        )
    if expected_megapixels < target.minimum_megapixels:
        raise MasterFinalizationError(
            f"{target.scale}x upscale would create only {expected_megapixels:.2f} MP, "
            f"below the {target.minimum_megapixels:.2f} MP master target."
        )

    intermediate = destination_path.with_suffix(".upscaled.png")
    try:
        upscale = upscaler.upscale(
            UpscaleRequest(source=source_path, destination=intermediate, scale=target.scale)
        )
    except UpscalerError as exc:
        raise MasterFinalizationError(str(exc)) from exc

    if Path(upscale.output_path).resolve() != intermediate.resolve():
        raise MasterFinalizationError("Upscaler returned an unexpected intermediate output path.")
    if (upscale.output_width, upscale.output_height) != (expected_width, expected_height):
        raise MasterFinalizationError(
            "Upscaler dimensions do not match the requested scale: "
            f"{upscale.output_width}x{upscale.output_height} vs {expected_width}x{expected_height}."
        )

    try:
        jpeg = finalize_image(
            intermediate,
            destination_path,
            assume_srgb=assume_srgb_after_upscale,
        )
    except AdobeFinalizationError as exc:
        raise MasterFinalizationError(str(exc)) from exc

    technical = inspect_image(destination_path)
    if not technical.ready or technical.megapixels is None:
        raise MasterFinalizationError("Master JPEG did not pass its deterministic technical gate.")
    if technical.megapixels < target.minimum_megapixels:
        raise MasterFinalizationError(
            f"Master is {technical.megapixels:.2f} MP, below target {target.minimum_megapixels:.2f} MP."
        )

    return MasterFinalizationReport(
        source_path=str(source_path),
        master_path=str(destination_path),
        intermediate_path=str(intermediate),
        upscale=upscale,
        jpeg=jpeg,
        minimum_megapixels=target.minimum_megapixels,
    )
