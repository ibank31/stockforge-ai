"""Deterministic technical gate for Adobe-oriented transparent PNG assets.

This gate verifies file facts only.  It cannot decide whether an object is
commercially useful or whether an alpha edge looks natural at 100% zoom; those
remain human review tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms, UnidentifiedImageError

from .adobe_gate import MAX_FILE_BYTES, MAX_MEGA_PIXELS, MIN_MEGA_PIXELS, GateCheck


@dataclass(frozen=True, slots=True)
class AdobePngTechnicalReport:
    path: str
    width: int | None
    height: int | None
    megapixels: float | None
    file_size_bytes: int
    color_mode: str | None
    transparent_fraction: float | None
    subject_bbox: tuple[int, int, int, int] | None
    checks: tuple[GateCheck, ...]

    @property
    def ready(self) -> bool:
        return all(item.status == "PASS" for item in self.checks)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "format": "PNG",
            "width": self.width,
            "height": self.height,
            "megapixels": self.megapixels,
            "file_size_bytes": self.file_size_bytes,
            "color_mode": self.color_mode,
            "transparent_fraction": self.transparent_fraction,
            "subject_bbox": list(self.subject_bbox) if self.subject_bbox else None,
            "ready": self.ready,
            "checks": [
                {"name": item.name, "status": item.status, "detail": item.detail}
                for item in self.checks
            ],
        }


def _srgb_check(image: Image.Image) -> GateCheck:
    raw = image.info.get("icc_profile")
    if not raw:
        return GateCheck("color_space", "REVIEW", "No embedded ICC profile; final PNG must explicitly normalize to sRGB.")
    try:
        profile = ImageCms.ImageCmsProfile(BytesIO(raw))
        description = ImageCms.getProfileDescription(profile).strip()
    except Exception as exc:
        return GateCheck("color_space", "FAIL", f"Embedded ICC profile could not be parsed: {exc}.")
    if "srgb" in description.casefold():
        return GateCheck("color_space", "PASS", f"Embedded ICC profile: {description}.")
    return GateCheck("color_space", "FAIL", f"Embedded ICC profile is not sRGB: {description or 'unknown' }.")


def inspect_transparent_png(path: str | Path) -> AdobePngTechnicalReport:
    """Verify a PNG with real alpha, not a white-background PNG conversion."""
    file_path = Path(path).expanduser().resolve()
    size = file_path.stat().st_size if file_path.is_file() else 0
    checks: list[GateCheck] = []
    if not file_path.is_file():
        checks.append(GateCheck("file_exists", "FAIL", f"File does not exist: {file_path}"))
        return AdobePngTechnicalReport(str(file_path), None, None, None, 0, None, None, None, tuple(checks))
    checks.append(GateCheck("file_size", "PASS" if size <= MAX_FILE_BYTES else "FAIL", f"{size} bytes; maximum is {MAX_FILE_BYTES} bytes."))
    try:
        with Image.open(file_path) as image:
            image_format = image.format
            width, height = image.size
            mode = image.mode
            checks.append(GateCheck("format", "PASS" if image_format == "PNG" else "FAIL", f"Detected format: {image_format or 'unknown'}; required PNG."))
            megapixels = (width * height) / 1_000_000
            checks.append(GateCheck(
                "resolution",
                "PASS" if MIN_MEGA_PIXELS <= megapixels <= MAX_MEGA_PIXELS else "FAIL",
                f"{width}x{height} = {megapixels:.2f} MP; required range is {MIN_MEGA_PIXELS:g}-{MAX_MEGA_PIXELS:g} MP.",
            ))
            if "A" not in image.getbands():
                checks.append(GateCheck("true_alpha", "FAIL", "PNG has no alpha channel; a white background is not transparent delivery."))
                checks.append(_srgb_check(image))
                return AdobePngTechnicalReport(str(file_path), width, height, megapixels, size, mode, None, None, tuple(checks))
            alpha = image.getchannel("A")
            extrema = alpha.getextrema()
            histogram = alpha.histogram()
            transparent_pixels = sum(histogram[:255])
            transparent_fraction = transparent_pixels / (width * height)
            bbox = alpha.getbbox()
            if extrema[0] != 0:
                checks.append(GateCheck("true_alpha", "FAIL", "Alpha channel contains no fully transparent pixels; this is not a transparent-background PNG."))
            elif bbox is None:
                checks.append(GateCheck("true_alpha", "FAIL", "PNG is fully transparent and has no visible subject."))
            else:
                checks.append(GateCheck("true_alpha", "PASS", f"True alpha is present; {transparent_fraction:.1%} of pixels are not fully opaque."))
            if mode not in {"RGBA", "LA"}:
                checks.append(GateCheck("color_mode", "FAIL", f"Pixel mode is {mode}; transparent PNG must preserve alpha."))
            else:
                checks.append(GateCheck("color_mode", "PASS", f"Pixel mode is {mode}."))
            checks.append(_srgb_check(image))
        # Pillow requires verify() before pixel access, so structural validation is
        # performed in a fresh open after alpha inspection.
        with Image.open(file_path) as verified:
            verified.verify()
        with Image.open(file_path) as image:
            image.load()
            checks.append(GateCheck("decodability", "PASS", "Image structure and pixel data decoded successfully."))
        return AdobePngTechnicalReport(str(file_path), width, height, megapixels, size, mode, transparent_fraction, bbox, tuple(checks))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        checks.append(GateCheck("decodability", "FAIL", f"Image could not be decoded safely: {exc}"))
        return AdobePngTechnicalReport(str(file_path), None, None, None, size, None, None, None, tuple(checks))
