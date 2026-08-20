"""Deterministic finalization of raster images for Adobe Stock submission.

This stage converts a raster candidate into a JPEG with an embedded sRGB ICC
profile. It intentionally does not upscale, sharpen, remove artifacts, or
perform legal/visual moderation. Those are separate pipeline stages.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms, ImageOps, UnidentifiedImageError

from .adobe_gate import MAX_FILE_BYTES, MAX_MEGA_PIXELS, MIN_MEGA_PIXELS, inspect_image


class AdobeFinalizationError(ValueError):
    """Raised when a candidate cannot be safely finalized."""


@dataclass(frozen=True, slots=True)
class FinalizationReport:
    source_path: str
    output_path: str
    source_mode: str
    source_profile: str | None
    assumed_srgb: bool
    width: int
    height: int
    megapixels: float
    jpeg_quality: int
    subsampling: str
    output_size_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "output_path": self.output_path,
            "source_mode": self.source_mode,
            "source_profile": self.source_profile,
            "assumed_srgb": self.assumed_srgb,
            "width": self.width,
            "height": self.height,
            "megapixels": self.megapixels,
            "jpeg_quality": self.jpeg_quality,
            "subsampling": self.subsampling,
            "output_size_bytes": self.output_size_bytes,
        }


def _srgb_profile() -> ImageCms.ImageCmsProfile:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))


def _profile_description(raw: bytes) -> str:
    profile = ImageCms.ImageCmsProfile(raw)
    return ImageCms.getProfileDescription(profile).strip()


def _has_transparency(image: Image.Image) -> bool:
    if "A" not in image.getbands():
        return False
    alpha = image.getchannel("A")
    extrema = alpha.getextrema()
    return extrema[0] < 255


def _prepare_rgb(
    image: Image.Image,
    *,
    assume_srgb: bool,
) -> tuple[Image.Image, str | None, bool]:
    """Return RGB pixels and the source profile description.

    Missing ICC metadata is not silently treated as proof of sRGB. The caller
    must explicitly opt into the documented sRGB assumption for unprofiled
    source pixels, which is appropriate for pipelines whose generator contract
    guarantees sRGB-like 8-bit output.
    """
    image = ImageOps.exif_transpose(image)
    if _has_transparency(image):
        raise AdobeFinalizationError(
            "Input contains non-opaque transparency; flattening it automatically "
            "could change the intended stock asset. Remove transparency explicitly "
            "before finalization."
        )

    raw_profile = image.info.get("icc_profile")
    description: str | None = None
    if raw_profile:
        try:
            description = _profile_description(raw_profile)
            source_profile = ImageCms.ImageCmsProfile(raw_profile)
        except Exception as exc:
            raise AdobeFinalizationError(f"Invalid embedded ICC profile: {exc}") from exc
    else:
        source_profile = None
        if not assume_srgb:
            raise AdobeFinalizationError(
                "Input has no embedded ICC profile. Refusing to assume sRGB; "
                "rerun with assume_srgb=True after confirming the generator's color contract."
            )

    target_profile = _srgb_profile()

    if source_profile is not None:
        try:
            # ICC transforms require a mode supported by the source profile.
            if image.mode in {"RGB", "CMYK", "LAB", "XYZ"}:
                converted = ImageCms.profileToProfile(
                    image,
                    source_profile,
                    target_profile,
                    renderingIntent=ImageCms.Intent.PERCEPTUAL,
                    outputMode="RGB",
                )
                if converted is None:
                    raise AdobeFinalizationError("ICC conversion returned no image.")
                image = converted
            elif image.mode == "L":
                image = image.convert("RGB")
            else:
                image = image.convert("RGB")
        except Exception as exc:
            raise AdobeFinalizationError(f"Could not convert source profile to sRGB: {exc}") from exc
    else:
        image = image.convert("RGB")

    return image, description, source_profile is None


def _encode_jpeg(image: Image.Image, quality: int, subsampling: str) -> bytes:
    buffer = BytesIO()
    image.save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
        subsampling=subsampling,
        icc_profile=_srgb_profile().tobytes(),
    )
    return buffer.getvalue()


def _choose_encoding(image: Image.Image) -> tuple[bytes, int, str]:
    """Choose the highest tested JPEG quality that stays under 45 MB."""
    for subsampling in ("4:4:4", "4:2:0"):
        for quality in range(95, 84, -1):
            data = _encode_jpeg(image, quality, subsampling)
            if len(data) <= MAX_FILE_BYTES:
                return data, quality, subsampling
    raise AdobeFinalizationError(
        "The image remains larger than 45 MB at the conservative JPEG quality floor. "
        "Do not keep lowering quality automatically; resize or use a dedicated "
        "enhancement/final-size policy instead."
    )


def finalize_image(
    source: str | Path,
    destination: str | Path,
    *,
    assume_srgb: bool = False,
) -> FinalizationReport:
    """Finalize a raster candidate as an Adobe-oriented JPEG/sRGB artifact.

    The function preserves pixel dimensions. It therefore rejects candidates
    outside Adobe's 4-100 MP range instead of silently upscaling or downscaling.
    """
    source_path = Path(source).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve()

    if not source_path.is_file():
        raise AdobeFinalizationError(f"Source file does not exist: {source_path}")
    if source_path == destination_path:
        raise AdobeFinalizationError("Source and destination must be different files.")

    try:
        with Image.open(source_path) as opened:
            opened.load()
            source_mode = opened.mode
            width, height = opened.size
            megapixels = (width * height) / 1_000_000
            if not MIN_MEGA_PIXELS <= megapixels <= MAX_MEGA_PIXELS:
                raise AdobeFinalizationError(
                    f"Source is {width}x{height} ({megapixels:.2f} MP); "
                    f"final candidates must be {MIN_MEGA_PIXELS:g}-{MAX_MEGA_PIXELS:g} MP. "
                    "Upscaling/downscaling belongs to a separate pipeline stage."
                )

            image, source_profile, assumed = _prepare_rgb(opened, assume_srgb=assume_srgb)
            data, quality, subsampling = _choose_encoding(image)
    except (UnidentifiedImageError, OSError) as exc:
        raise AdobeFinalizationError(f"Source image could not be decoded: {exc}") from exc

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_path.with_suffix(destination_path.suffix + ".tmp")
    try:
        temporary.write_bytes(data)
        temporary.replace(destination_path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise AdobeFinalizationError(f"Could not write final JPEG: {exc}") from exc

    report = inspect_image(destination_path)
    if not report.ready:
        try:
            destination_path.unlink(missing_ok=True)
        except OSError:
            pass
        details = "; ".join(f"{item.name}: {item.detail}" for item in report.checks if item.status != "PASS")
        raise AdobeFinalizationError(f"Finalized artifact failed its own technical gate: {details}")

    return FinalizationReport(
        source_path=str(source_path),
        output_path=str(destination_path),
        source_mode=source_mode,
        source_profile=source_profile,
        assumed_srgb=assumed,
        width=width,
        height=height,
        megapixels=megapixels,
        jpeg_quality=quality,
        subsampling=subsampling,
        output_size_bytes=len(data),
    )
