"""Private Kaggle PNG alpha finalizer; never touches the JPEG finalizer."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms, ImageFilter, ImageOps

INPUT_ROOT = Path("/kaggle/input")
WORK_ROOT = Path("/kaggle/working/stockforge-png-finalizer")
OUTPUT_DIR = WORK_ROOT / "output"
REQUEST_PATH = WORK_ROOT / "request.json"
TARGET_SIZE = 4096
MAX_FILE_BYTES = 45 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def srgb_bytes() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def materialize_staged_input() -> None:
    try:
        request_b64 = globals()["REQUEST_B64"]
        source_b64 = globals()["SOURCE_B64"]
        source_name = globals()["SOURCE_NAME"]
    except KeyError:
        raise RuntimeError("PNG worker requires transient embedded request and source input")
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    REQUEST_PATH.write_bytes(base64.b64decode(request_b64))
    source_path = WORK_ROOT / Path(str(source_name)).name
    source_path.write_bytes(base64.b64decode(source_b64))


def load_request() -> dict:
    if not REQUEST_PATH.is_file():
        raise RuntimeError(f"PNG request missing: {REQUEST_PATH}")
    data = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    if data.get("kind") != "stockforge.png_finalizer_request":
        raise RuntimeError("Invalid PNG finalizer request kind")
    if data.get("status") != "prepared_no_gpu":
        raise RuntimeError("PNG finalizer request must be prepared_no_gpu")
    source = data.get("source")
    target = data.get("target")
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise RuntimeError("PNG request lacks source/target objects")
    if target.get("format") != "png" or target.get("mode") != "alpha_finalize":
        raise RuntimeError("PNG target must use alpha_finalize mode and PNG format")
    if int(target.get("scale", 0)) != 4:
        raise RuntimeError("PNG worker supports only 4x alpha-aware resize")
    return data


def source_file(data: dict) -> Path:
    source_path = WORK_ROOT / Path(str(data["source"]["relative_path"])).name
    if not source_path.is_file():
        raise RuntimeError(f"Staged PNG source missing: {source_path}")
    expected = str(data["source"].get("sha256") or "")
    if expected and sha256_file(source_path) != expected:
        raise RuntimeError("Staged PNG source SHA-256 does not match request")
    return source_path


def _find_one(name: str) -> Path:
    matches = sorted(path for path in INPUT_ROOT.rglob(name) if path.is_file())
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one cached {name}, found {len(matches)}")
    return matches[0]


def _find_model_root() -> Path:
    configs = sorted(path.parent for path in INPUT_ROOT.rglob("config.json") if (path.parent / "model.safetensors").is_file())
    if len(configs) != 1:
        raise RuntimeError(f"Expected one BiRefNet model root, found {len(configs)}")
    return configs[0]


def _install_offline_dependencies() -> None:
    from importlib.metadata import PackageNotFoundError, version

    try:
        transformers_version = version("transformers")
        safetensors_version = version("safetensors")
        if transformers_version == "4.48.3" and safetensors_version == "0.4.5":
            return
    except PackageNotFoundError:
        pass
    wheels = sorted(path for path in INPUT_ROOT.rglob("*.whl") if path.is_file())
    if not wheels:
        raise RuntimeError("Offline wheelhouse is missing; refusing network installation")
    wheel_dir = wheels[0].parent
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--no-index", "--force-reinstall", "--no-deps",
        "--find-links", str(wheel_dir), "transformers==4.48.3", "safetensors==0.4.5",
        "tokenizers==0.21.0", "huggingface-hub==0.27.1", "Pillow==11.1.0", "numpy==2.0.2",
    ])


def load_birefnet():
    _install_offline_dependencies()
    import torch
    from transformers import AutoModelForImageSegmentation

    model_root = _find_model_root()
    device_note = "cpu_no_cuda"
    if torch.cuda.is_available():
        capability = torch.cuda.get_device_capability(0)
        if capability >= (7, 0):
            device = "cuda"
            device_note = f"cuda_sm_{capability[0]}{capability[1]}"
        else:
            device = "cpu"
            device_note = f"cpu_cuda_sm_{capability[0]}{capability[1]}_unsupported_by_torch"
    else:
        device = "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForImageSegmentation.from_pretrained(
        str(model_root),
        trust_remote_code=True,
        local_files_only=True,
        torch_dtype=dtype,
    )
    model.to(device)
    model.eval()
    return model, device, dtype, device_note


def predict_mask(model, device: str, dtype, image: Image.Image) -> Image.Image:
    import torch
    from torchvision import transforms

    transform = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    tensor = transform(image.convert("RGB")).unsqueeze(0).to(device=device, dtype=dtype)
    with torch.inference_mode():
        prediction = model(tensor)[-1].sigmoid().float().cpu()[0, 0]
    mask = transforms.ToPILImage()(prediction).resize(image.size, Image.Resampling.LANCZOS)
    # A tiny blur removes single-pixel mask stair steps without erasing the silhouette.
    return mask.filter(ImageFilter.GaussianBlur(radius=0.35))


def decontaminate_white_background(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Remove white backdrop color from soft alpha edges; preserve real RGB content."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    alpha = np.asarray(mask, dtype=np.float32) / 255.0
    safe = np.maximum(alpha[..., None], 0.04)
    foreground = (rgb - (1.0 - alpha[..., None]) * 255.0) / safe
    foreground = np.clip(foreground, 0.0, 255.0)
    foreground[alpha < 0.02] = 0.0
    result = np.dstack([foreground.astype(np.uint8), np.asarray(mask, dtype=np.uint8)])
    return Image.fromarray(result, mode="RGBA")


def alpha_report(image: Image.Image) -> dict[str, object]:
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("Alpha output is fully transparent")
    if alpha.min() != 0:
        raise RuntimeError("Alpha output has no fully transparent background pixels")
    if bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] >= image.width or bbox[3] >= image.height:
        raise RuntimeError(f"Subject touches output border: bbox={bbox}, size={image.size}")
    partial = ((alpha > 0) & (alpha < 255)).mean()
    if partial > 0.35:
        raise RuntimeError(f"Alpha edge coverage is suspiciously broad: {partial:.1%}")
    return {
        "subject_bbox": list(bbox),
        "transparent_fraction": float((alpha == 0).mean()),
        "partial_alpha_fraction": float(partial),
        "edge_review_required": True,
    }


def finalize(data: dict, source_path: Path) -> dict:
    with Image.open(source_path) as opened:
        opened.load()
        source = ImageOps.exif_transpose(opened).convert("RGB")
    model, device, dtype, device_note = load_birefnet()
    mask = predict_mask(model, device, dtype, source)
    cutout = decontaminate_white_background(source, mask)
    cutout = cutout.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.LANCZOS)
    quality = alpha_report(cutout)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / "master.png"
    cutout.save(destination, format="PNG", optimize=True, compress_level=9, icc_profile=srgb_bytes())
    if destination.stat().st_size > MAX_FILE_BYTES:
        raise RuntimeError(f"PNG exceeds 45 MB technical limit: {destination.stat().st_size} bytes")
    with Image.open(destination) as check:
        check.load()
        if check.format != "PNG" or check.mode != "RGBA" or check.size != (TARGET_SIZE, TARGET_SIZE):
            raise RuntimeError("Final RGBA PNG verification failed")
    return {
        "schema_version": 1,
        "kind": "stockforge.kaggle_png_finalizer_result",
        "status": "visual_review_required",
        "request_id": data["request_id"],
        "source": data["source"],
        "target": data["target"],
        "provider": "kaggle-birefnet-alpha",
        "model_id": "ZhengPeng7/BiRefNet",
        "inference_device": device,
        "inference_device_note": device_note,
        "master": {
            "file": destination.name,
            "sha256": sha256_file(destination),
            "width": TARGET_SIZE,
            "height": TARGET_SIZE,
            "megapixels": round((TARGET_SIZE * TARGET_SIZE) / 1_000_000, 4),
            "color_mode": "RGBA",
            "icc_profile": "sRGB",
            "size_bytes": destination.stat().st_size,
        },
        "alpha_quality": quality,
        "human_review_required": True,
        "jpeg_pipeline_touched": False,
        "notice": "Inspect the cutout at 100% for halos, missing details, false holes, edge clipping, and unwanted shadows before any upload consideration.",
    }


def main() -> None:
    materialize_staged_input()
    data = load_request()
    result = finalize(data, source_file(data))
    (OUTPUT_DIR / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail closed and preserve concise error evidence
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "error.json").write_text(json.dumps({"status": "failed", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"STOCKFORGE PNG FINALIZER FAILED: {exc}", file=sys.stderr)
        raise
