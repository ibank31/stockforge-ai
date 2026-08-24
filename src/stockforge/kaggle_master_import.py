"""Import a one-shot Kaggle finalizer result into StockForge safely."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from .adobe_finalize import FinalizationReport
from .adobe_gate import inspect_image
from .artifact import sha256_file
from .master_finalizer import MasterFinalizationReport
from .upscaler import UpscaleReport


class KaggleMasterImportError(RuntimeError):
    """Raised when a Kaggle finalizer result fails lineage or technical checks."""


def _read_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise KaggleMasterImportError(f"{label} file is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KaggleMasterImportError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise KaggleMasterImportError(f"{label} must be a JSON object")
    return value


def import_kaggle_master(
    *,
    request_path: str | Path,
    result_dir: str | Path,
    project_root: str | Path,
) -> MasterFinalizationReport:
    """Verify/copy a Kaggle finalizer output and return an auditable report.

    This function does not register database rows itself.  The caller must pair
    the returned report with the original preview artifact/execution through
    ``register_master_candidate``.
    """

    request_file = Path(request_path).expanduser().resolve()
    result_root = Path(result_dir).expanduser().resolve()
    root = Path(project_root).expanduser().resolve()
    request = _read_object(request_file, "Finalizer request")
    result = _read_object(result_root / "result.json", "Kaggle finalizer result")
    if request.get("kind") != "stockforge.master_finalizer_request":
        raise KaggleMasterImportError("Unexpected finalizer request kind")
    if result.get("kind") != "stockforge.kaggle_finalizer_result":
        raise KaggleMasterImportError("Unexpected finalizer result kind")
    if result.get("status") != "visual_review_required":
        raise KaggleMasterImportError("Finalizer result has not reached visual_review_required")
    if result.get("request_id") != request.get("request_id"):
        raise KaggleMasterImportError("Finalizer result request_id does not match request")
    if result.get("source") != request.get("source"):
        raise KaggleMasterImportError("Finalizer result source does not match the original request")
    if result.get("target") != request.get("target"):
        raise KaggleMasterImportError("Finalizer result target does not match the original request")

    master = result.get("master")
    intermediate = result.get("intermediate")
    if not isinstance(master, dict) or not isinstance(intermediate, dict):
        raise KaggleMasterImportError("Finalizer result lacks master/intermediate details")
    master_name = master.get("file")
    intermediate_name = intermediate.get("file")
    if not isinstance(master_name, str) or Path(master_name).name != master_name:
        raise KaggleMasterImportError("Finalizer master filename is unsafe")
    if not isinstance(intermediate_name, str) or Path(intermediate_name).name != intermediate_name:
        raise KaggleMasterImportError("Finalizer intermediate filename is unsafe")
    remote_master = result_root / master_name
    remote_intermediate = result_root / intermediate_name
    if not remote_master.is_file() or not remote_intermediate.is_file():
        raise KaggleMasterImportError("Finalizer output files are incomplete")
    if sha256_file(remote_master) != master.get("sha256"):
        raise KaggleMasterImportError("Finalizer master checksum does not match manifest")
    if sha256_file(remote_intermediate) != intermediate.get("sha256"):
        raise KaggleMasterImportError("Finalizer intermediate checksum does not match manifest")

    destination_relative = request.get("destination")
    if not isinstance(destination_relative, str) or destination_relative.startswith("/"):
        raise KaggleMasterImportError("Finalizer request destination is invalid")
    destination = (root / destination_relative).resolve()
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise KaggleMasterImportError("Finalizer destination escapes project root") from exc
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        shutil.copyfile(remote_master, temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)

    report = inspect_image(destination)
    target = request["target"]
    expected_size = (int(target["expected_width"]), int(target["expected_height"]))
    if not report.ready or report.format != "JPEG" or report.color_mode != "RGB":
        destination.unlink(missing_ok=True)
        raise KaggleMasterImportError("Imported master did not pass JPEG/RGB/sRGB technical gate")
    if (report.width, report.height) != expected_size:
        destination.unlink(missing_ok=True)
        raise KaggleMasterImportError("Imported master dimensions do not match finalizer target")
    if report.megapixels is None or report.megapixels < float(target["minimum_megapixels"]):
        destination.unlink(missing_ok=True)
        raise KaggleMasterImportError("Imported master is below requested megapixel target")

    source_relative = request["source"].get("relative_path")
    if not isinstance(source_relative, str):
        raise KaggleMasterImportError("Finalizer request source path is invalid")
    source_path = (root / source_relative).resolve()
    try:
        source_path.relative_to(root)
    except ValueError as exc:
        raise KaggleMasterImportError("Finalizer source path escapes project root") from exc
    try:
        with Image.open(source_path) as source_image:
            source_image.load()
            source_mode = source_image.mode
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise KaggleMasterImportError(f"Original preview could not be decoded: {exc}") from exc

    upscale = UpscaleReport(
        source_path=str(source_path),
        output_path=str(remote_intermediate),
        provider_id=str(result.get("provider")),
        model_id=str(result.get("model_id")),
        scale=int(result.get("scale")),
        source_width=int(request["source"]["width"]),
        source_height=int(request["source"]["height"]),
        output_width=int(report.width),
        output_height=int(report.height),
    )
    jpeg = FinalizationReport(
        source_path=str(remote_intermediate),
        output_path=str(destination),
        source_mode=source_mode,
        source_profile=None,
        assumed_srgb=True,
        width=int(report.width),
        height=int(report.height),
        megapixels=float(report.megapixels),
        jpeg_quality=int(master.get("jpeg_quality", 0)),
        subsampling=str(master.get("subsampling", "unknown")),
        output_size_bytes=destination.stat().st_size,
    )
    return MasterFinalizationReport(
        source_path=str(source_path),
        master_path=str(destination),
        intermediate_path=str(remote_intermediate),
        upscale=upscale,
        jpeg=jpeg,
        minimum_megapixels=float(target["minimum_megapixels"]),
    )
