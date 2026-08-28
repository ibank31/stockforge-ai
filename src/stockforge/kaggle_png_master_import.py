"""Import and verify one isolated Kaggle BiRefNet PNG master."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .adobe_png_gate import AdobePngTechnicalReport, inspect_transparent_png
from .artifact import sha256_file
from .upscaler import UpscaleReport


class KagglePngMasterImportError(RuntimeError):
    """Raised when a PNG finalizer result fails its immutable contract."""


def _read_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise KagglePngMasterImportError(f"{label} file is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KagglePngMasterImportError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise KagglePngMasterImportError(f"{label} must be a JSON object")
    return value


@dataclass(frozen=True, slots=True)
class PngFinalizationReport:
    source_path: str
    master_path: str
    intermediate_path: str
    upscale: UpscaleReport
    png: AdobePngTechnicalReport
    minimum_megapixels: float
    quality_state: str = "visual_review_required"

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "master_path": self.master_path,
            "intermediate_path": self.intermediate_path,
            "upscale": self.upscale.to_dict(),
            "png": self.png.to_dict(),
            "minimum_megapixels": self.minimum_megapixels,
            "quality_state": self.quality_state,
            "notice": "Technical PNG output passed deterministic checks only; 100% visual edge review remains required.",
        }


def import_kaggle_png_master(*, request_path: str | Path, result_dir: str | Path, project_root: str | Path) -> PngFinalizationReport:
    request_file = Path(request_path).expanduser().resolve()
    result_root = Path(result_dir).expanduser().resolve()
    root = Path(project_root).expanduser().resolve()
    request = _read_object(request_file, "PNG finalizer request")
    result = _read_object(result_root / "result.json", "Kaggle PNG finalizer result")
    if request.get("kind") != "stockforge.png_finalizer_request":
        raise KagglePngMasterImportError("Unexpected PNG finalizer request kind")
    if result.get("kind") not in {"stockforge.kaggle_png_finalizer_result", "stockforge.kaggle_finalizer_result"}:
        raise KagglePngMasterImportError("Unexpected PNG finalizer result kind")
    if result.get("status") != "visual_review_required":
        raise KagglePngMasterImportError("PNG finalizer result has not reached visual_review_required")
    for field in ("request_id", "source", "target"):
        if result.get(field) != request.get(field):
            raise KagglePngMasterImportError(f"PNG finalizer result {field} does not match request")

    master = result.get("master")
    if not isinstance(master, dict) or not isinstance(master.get("file"), str) or Path(master["file"]).name != master["file"]:
        raise KagglePngMasterImportError("PNG finalizer master filename is unsafe or missing")
    remote_master = result_root / master["file"]
    if not remote_master.is_file():
        raise KagglePngMasterImportError("PNG finalizer master output is missing")
    if sha256_file(remote_master) != master.get("sha256"):
        raise KagglePngMasterImportError("PNG finalizer master checksum does not match manifest")

    destination_relative = request.get("destination")
    if not isinstance(destination_relative, str) or destination_relative.startswith("/") or not destination_relative.casefold().endswith(".png"):
        raise KagglePngMasterImportError("PNG finalizer destination is invalid")
    destination = (root / destination_relative).resolve()
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise KagglePngMasterImportError("PNG finalizer destination escapes project root") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        shutil.copyfile(remote_master, temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)

    technical = inspect_transparent_png(destination)
    target = request.get("target")
    if not isinstance(target, dict):
        destination.unlink(missing_ok=True)
        raise KagglePngMasterImportError("PNG request target is missing")
    expected_size = (int(target["expected_width"]), int(target["expected_height"]))
    if not technical.ready or (technical.width, technical.height) != expected_size or technical.color_mode != "RGBA":
        destination.unlink(missing_ok=True)
        raise KagglePngMasterImportError("Imported master failed PNG/RGBA/true-alpha/sRGB technical gate")
    minimum = float(target.get("minimum_megapixels", 6.0))
    if technical.megapixels is None or technical.megapixels < minimum:
        destination.unlink(missing_ok=True)
        raise KagglePngMasterImportError("Imported PNG master is below requested megapixel target")

    source_data = request.get("source")
    if not isinstance(source_data, dict) or not isinstance(source_data.get("relative_path"), str):
        raise KagglePngMasterImportError("PNG request source path is invalid")
    source_path = (root / source_data["relative_path"]).resolve()
    try:
        source_path.relative_to(root)
    except ValueError as exc:
        raise KagglePngMasterImportError("PNG source path escapes project root") from exc
    if not source_path.is_file():
        raise KagglePngMasterImportError("Original PNG preview is missing")

    upscale = UpscaleReport(
        source_path=str(source_path), output_path=str(remote_master), provider_id=str(result.get("provider", "kaggle-birefnet-alpha")),
        model_id=str(result.get("model_id", "birefnet")), scale=int(target.get("scale", 4)),
        source_width=int(source_data["width"]), source_height=int(source_data["height"]),
        output_width=int(technical.width), output_height=int(technical.height),
    )
    return PngFinalizationReport(str(source_path), str(destination), str(remote_master), upscale, technical, minimum)
