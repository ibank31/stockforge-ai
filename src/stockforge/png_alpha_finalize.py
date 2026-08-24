"""Conservative true-alpha PNG normalization without background guessing.

This module never removes a guessed background. It accepts only a source that
already contains a real alpha channel, preserves the source file, writes a
separate RGBA PNG with an embedded sRGB profile, and leaves alpha-edge quality
as an explicit human-review requirement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageCms

from .adobe_gate import MIN_MEGA_PIXELS
from .adobe_png_gate import AdobePngTechnicalReport, inspect_transparent_png


class PngAlphaFinalizeError(ValueError):
    """Raised when a source cannot safely become a true-alpha PNG."""


@dataclass(frozen=True, slots=True)
class PngAlphaFinalizeReport:
    source_path: str
    output_path: str
    width: int
    height: int
    trimmed: bool
    margin: int
    technical: AdobePngTechnicalReport
    edge_review_required: bool = True

    @property
    def ready(self) -> bool:
        return self.technical.ready and self.edge_review_required

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "output_path": self.output_path,
            "width": self.width,
            "height": self.height,
            "trimmed": self.trimmed,
            "margin": self.margin,
            "edge_review_required": self.edge_review_required,
            "technical": self.technical.to_dict(),
            "ready_for_human_review": self.ready,
        }


def prepare_true_alpha_png(
    source: str | Path,
    destination: str | Path,
    *,
    trim: bool = False,
    margin: int = 16,
) -> PngAlphaFinalizeReport:
    """Normalize an existing alpha source; reject opaque RGB inputs."""
    source_path = Path(source).expanduser().resolve()
    output_path = Path(destination).expanduser().resolve()
    if source_path == output_path:
        raise PngAlphaFinalizeError("Source and destination must be different files.")
    if margin < 0 or margin > 512:
        raise PngAlphaFinalizeError("Margin must be between 0 and 512 pixels.")
    if not source_path.is_file():
        raise PngAlphaFinalizeError(f"Alpha source does not exist: {source_path}")
    if output_path.suffix.casefold() != ".png":
        raise PngAlphaFinalizeError("True-alpha destination must use the .png extension.")

    try:
        with Image.open(source_path) as opened:
            opened.load()
            has_alpha = "A" in opened.getbands() or "transparency" in opened.info
            if not has_alpha:
                raise PngAlphaFinalizeError("Source has no real alpha channel; refusing to guess a background.")
            image = opened.convert("RGBA")
        alpha = image.getchannel("A")
        if alpha.getextrema()[0] != 0 or alpha.getbbox() is None:
            raise PngAlphaFinalizeError("Source alpha must contain both transparent background pixels and visible content.")
        if trim:
            left, top, right, bottom = alpha.getbbox()
            left = max(0, left - margin)
            top = max(0, top - margin)
            right = min(image.width, right + margin)
            bottom = min(image.height, bottom + margin)
            cropped = image.crop((left, top, right, bottom))
        else:
            cropped = image
        if (cropped.width * cropped.height) / 1_000_000 < MIN_MEGA_PIXELS:
            raise PngAlphaFinalizeError(
                f"Normalized PNG is below the {MIN_MEGA_PIXELS:g} MP technical floor; preserve a larger source."
            )
        profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output_path, format="PNG", icc_profile=profile, compress_level=9)
    except PngAlphaFinalizeError:
        output_path.unlink(missing_ok=True)
        raise
    except (OSError, ValueError) as exc:
        output_path.unlink(missing_ok=True)
        raise PngAlphaFinalizeError(f"Could not normalize true-alpha PNG: {exc}") from exc

    technical = inspect_transparent_png(output_path)
    if not technical.ready:
        output_path.unlink(missing_ok=True)
        raise PngAlphaFinalizeError("Normalized PNG failed the technical alpha gate.")
    return PngAlphaFinalizeReport(
        source_path=str(source_path),
        output_path=str(output_path),
        width=technical.width or 0,
        height=technical.height or 0,
        trimmed=trim,
        margin=margin,
        technical=technical,
    )
