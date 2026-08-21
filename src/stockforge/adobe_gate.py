"""Adobe Stock-oriented technical submission gate.

This module implements only deterministic, machine-verifiable technical checks.
It deliberately does not claim to replace Adobe moderation or visual/legal review.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

from PIL import Image, ImageCms, UnidentifiedImageError


Status = Literal["PASS", "FAIL", "REVIEW"]

MIN_MEGA_PIXELS = 4.0
MAX_MEGA_PIXELS = 100.0
MAX_FILE_BYTES = 45 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class GateCheck:
    name: str
    status: Status
    detail: str


@dataclass(frozen=True, slots=True)
class AdobeTechnicalReport:
    path: str
    format: str | None
    width: int | None
    height: int | None
    megapixels: float | None
    file_size_bytes: int
    color_mode: str | None
    icc_profile: str | None
    checks: tuple[GateCheck, ...]

    @property
    def ready(self) -> bool:
        return all(check.status == "PASS" for check in self.checks)

    @property
    def failures(self) -> tuple[GateCheck, ...]:
        return tuple(check for check in self.checks if check.status == "FAIL")

    @property
    def reviews(self) -> tuple[GateCheck, ...]:
        return tuple(check for check in self.checks if check.status == "REVIEW")

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "format": self.format,
            "width": self.width,
            "height": self.height,
            "megapixels": self.megapixels,
            "file_size_bytes": self.file_size_bytes,
            "color_mode": self.color_mode,
            "icc_profile": self.icc_profile,
            "ready": self.ready,
            "checks": [
                {"name": item.name, "status": item.status, "detail": item.detail}
                for item in self.checks
            ],
        }


def _check_dimensions(width: int, height: int) -> GateCheck:
    megapixels = (width * height) / 1_000_000
    if MIN_MEGA_PIXELS <= megapixels <= MAX_MEGA_PIXELS:
        return GateCheck(
            "resolution",
            "PASS",
            f"{width}x{height} = {megapixels:.2f} MP; within {MIN_MEGA_PIXELS:g}-{MAX_MEGA_PIXELS:g} MP.",
        )
    return GateCheck(
        "resolution",
        "FAIL",
        f"{width}x{height} = {megapixels:.2f} MP; required range is {MIN_MEGA_PIXELS:g}-{MAX_MEGA_PIXELS:g} MP.",
    )


def _icc_description(image: Image.Image) -> tuple[str | None, GateCheck]:
    raw = image.info.get("icc_profile")
    if not raw:
        return None, GateCheck(
            "color_space",
            "REVIEW",
            "No embedded ICC profile; the file's sRGB state cannot be proven from metadata alone. Final export must normalize to sRGB.",
        )
    try:
        profile = ImageCms.ImageCmsProfile(BytesIO(raw))
        description = ImageCms.getProfileDescription(profile).strip()
        normalized = description.lower()
        if "srgb" in normalized:
            return description, GateCheck("color_space", "PASS", f"Embedded ICC profile: {description}.")
        return description, GateCheck(
            "color_space",
            "FAIL",
            f"Embedded ICC profile is not identified as sRGB: {description or 'unknown profile'}.",
        )
    except Exception as exc:
        return "invalid ICC profile", GateCheck(
            "color_space",
            "FAIL",
            f"Embedded ICC profile could not be parsed: {exc}.",
        )


def inspect_image(path: str | Path) -> AdobeTechnicalReport:
    """Inspect a final candidate against deterministic Adobe photo requirements.

    Adobe's published requirements used by this gate are: JPEG, sRGB, 4-100 MP,
    and maximum 45 MB. Missing ICC metadata is reported as REVIEW rather than
    falsely claiming that the pixels are non-sRGB.
    """
    file_path = Path(path).expanduser().resolve()
    size = file_path.stat().st_size if file_path.is_file() else 0
    checks: list[GateCheck] = []

    if not file_path.is_file():
        checks.append(GateCheck("file_exists", "FAIL", f"File does not exist: {file_path}"))
        return AdobeTechnicalReport(str(file_path), None, None, None, None, 0, None, None, tuple(checks))

    checks.append(GateCheck("file_size", "PASS" if size <= MAX_FILE_BYTES else "FAIL", f"{size} bytes; maximum is {MAX_FILE_BYTES} bytes."))

    try:
        with Image.open(file_path) as image:
            image_format = image.format
            width, height = image.size
            mode = image.mode
            checks.append(
                GateCheck("format", "PASS" if image_format == "JPEG" else "FAIL", f"Detected format: {image_format or 'unknown'}; required JPEG.")
            )
            checks.append(_check_dimensions(width, height))

            if mode == "RGB":
                checks.append(GateCheck("color_mode", "PASS", "Pixel mode is RGB."))
            else:
                checks.append(GateCheck("color_mode", "FAIL", f"Pixel mode is {mode}; final photo must be RGB/sRGB."))

            icc_profile, color_check = _icc_description(image)
            checks.append(color_check)

            image.verify()

        # verify() checks structure; reopen/load forces pixel decoding too.
        with Image.open(file_path) as image:
            image.load()
            checks.append(GateCheck("decodability", "PASS", "Image structure and pixel data decoded successfully."))

        megapixels = (width * height) / 1_000_000
        return AdobeTechnicalReport(
            path=str(file_path),
            format=image_format,
            width=width,
            height=height,
            megapixels=megapixels,
            file_size_bytes=size,
            color_mode=mode,
            icc_profile=icc_profile,
            checks=tuple(checks),
        )
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        checks.append(GateCheck("decodability", "FAIL", f"Image could not be decoded safely: {exc}"))
        return AdobeTechnicalReport(str(file_path), None, None, None, None, size, None, None, tuple(checks))
