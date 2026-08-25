"""Minimal Android-facing export for StockForge review and approved-upload files.

This module intentionally copies only the user-facing asset.  Provenance, logs,
ZIP packages, CSV, and review records remain inside the project workspace.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path


class AndroidExportError(ValueError):
    """Raised when a user-facing mobile export would be unsafe or ambiguous."""


USER_VISIBLE_ROOT = "MACHINE STOCKFORGE"
PREVIEW_BRANCH = "PREVIEW_TO_MANUS"
UPLOAD_BRANCH = "READY_UPLOAD_ADOBE"
_ALLOWED_PREVIEW_SUFFIXES = frozenset({".webp", ".jpg", ".jpeg", ".png"})
_ALLOWED_UPLOAD_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".svg"})
_SLUG = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class AndroidExport:
    source: Path
    destination: Path
    branch: str

    def to_dict(self) -> dict[str, str]:
        return {"source": str(self.source), "destination": str(self.destination), "branch": self.branch}


def default_downloads_root() -> Path | None:
    """Return an existing Android Download mount, or None outside Termux."""
    candidates = (
        Path("/storage/emulated/0/Download"),
        Path.home() / "storage" / "downloads",
    )
    for candidate in candidates:
        try:
            if candidate.is_dir():
                return candidate.resolve()
        except OSError:
            continue
    return None


def machine_root(downloads_root: str | Path) -> Path:
    return Path(downloads_root).expanduser().resolve() / USER_VISIBLE_ROOT


def _name(value: str) -> str:
    normalized = _SLUG.sub("-", value.casefold()).strip("-")
    if not normalized:
        raise AndroidExportError("A non-empty asset name is required for Android export.")
    return normalized


def export_preview(*, source: str | Path, downloads_root: str | Path, asset_name: str) -> AndroidExport:
    """Copy one review image into the only user-visible preview branch."""
    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise AndroidExportError(f"Preview source does not exist: {source_path}")
    if source_path.suffix.casefold() not in _ALLOWED_PREVIEW_SUFFIXES:
        raise AndroidExportError("Preview export requires WEBP, JPEG, or PNG image input.")
    destination = machine_root(downloads_root) / PREVIEW_BRANCH / f"{_name(asset_name)}__preview{source_path.suffix.casefold()}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return AndroidExport(source_path, destination, PREVIEW_BRANCH)


def export_ready_upload(*, source: str | Path, downloads_root: str | Path, asset_name: str) -> AndroidExport:
    """Copy one approved final file into the only Android upload branch.

    This function does not assert that a marketplace will accept the asset; the
    caller must pass a format-specific technical gate and obtain user approval
    before using it.
    """
    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise AndroidExportError(f"Final source does not exist: {source_path}")
    if source_path.suffix.casefold() not in _ALLOWED_UPLOAD_SUFFIXES:
        raise AndroidExportError("Ready-upload export requires JPEG, PNG, or SVG input.")
    destination = machine_root(downloads_root) / UPLOAD_BRANCH / f"{_name(asset_name)}__adobe{source_path.suffix.casefold()}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return AndroidExport(source_path, destination, UPLOAD_BRANCH)
