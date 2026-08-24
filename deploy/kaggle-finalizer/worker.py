"""One-shot Kaggle GPU finalizer for a staged StockForge master request.

The input request and source preview are staged locally by StockForge before a
private Kaggle kernel is pushed. This worker has no public API and processes one
request into one JPEG master plus a manifest for the Termux control plane.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

REQUEST_PATH = Path(os.getenv("STOCKFORGE_FINALIZER_REQUEST", "request.json"))
OUTPUT_DIR = Path("/kaggle/working/stockforge-finalizer-output")
WEIGHTS_DIR = Path("/kaggle/working/stockforge-realesrgan")
WEIGHTS_URL = (
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.0/"
    "RealESRGAN_x4plus.pth"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def srgb_bytes() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def load_request() -> dict:
    if not REQUEST_PATH.is_file():
        raise RuntimeError(f"Finalizer request is missing: {REQUEST_PATH}")
    data = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    if data.get("kind") != "stockforge.master_finalizer_request":
        raise RuntimeError("Invalid finalizer request kind")
    if data.get("status") != "prepared_no_gpu":
        raise RuntimeError("Finalizer request must have prepared_no_gpu status")
    source = data.get("source")
    target = data.get("target")
    if not isinstance(source, dict) or not isinstance(target, dict):
        raise RuntimeError("Finalizer request lacks source/target object")
    if target.get("mode") != "ai_upscale" or target.get("scale") != 4:
        raise RuntimeError("This worker only supports 4x ai_upscale requests")
    if target.get("format") != "jpeg" or target.get("color_space") != "sRGB":
        raise RuntimeError("Finalizer target must be JPEG/sRGB")
    return data


def source_file(data: dict) -> Path:
    source = data["source"]
    basename = Path(str(source["relative_path"])).name
    staged = Path("input") / basename
    if not staged.is_file():
        raise RuntimeError(f"Staged source image is missing: {staged}")
    if sha256_file(staged) != source["sha256"]:
        raise RuntimeError("Staged source SHA-256 does not match finalizer request")
    return staged


def build_upscaler():
    try:
        import torch
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
    except ImportError:
        import subprocess
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "realesrgan==0.3.0",
                "basicsr==1.4.2",
                "opencv-python-headless>=4.8,<5.0",
            ]
        )
        import torch
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
    weights = WEIGHTS_DIR / "RealESRGAN_x4plus.pth"
    if not weights.is_file():
        WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        import urllib.request
        urllib.request.urlretrieve(WEIGHTS_URL, weights)
    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=4,
    )
    return RealESRGANer(
        scale=4,
        model_path=str(weights),
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=torch.cuda.is_available(),
    )


def finalize(data: dict, source_path: Path) -> dict:
    import cv2
    import numpy as np

    target = data["target"]
    with Image.open(source_path) as source:
        source.load()
        source = ImageOps.exif_transpose(source).convert("RGB")
        width, height = source.size
        array = np.asarray(source)
    if (width, height) != (data["source"]["width"], data["source"]["height"]):
        raise RuntimeError("Staged source dimensions do not match finalizer request")

    output, _ = build_upscaler().enhance(cv2.cvtColor(array, cv2.COLOR_RGB2BGR), outscale=4)
    rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    master = Image.fromarray(rgb, mode="RGB")
    expected = (int(target["expected_width"]), int(target["expected_height"]))
    if master.size != expected:
        raise RuntimeError(f"Unexpected upscale size {master.size}; expected {expected}")
    megapixels = (master.width * master.height) / 1_000_000
    if megapixels < float(target["minimum_megapixels"]):
        raise RuntimeError("Upscaled image is below requested megapixel target")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    intermediate = OUTPUT_DIR / "master.upscaled.png"
    master.save(intermediate, format="PNG")
    destination = OUTPUT_DIR / "master.jpg"
    buffer = BytesIO()
    master.save(
        buffer,
        format="JPEG",
        quality=95,
        optimize=True,
        progressive=True,
        subsampling="4:4:4",
        icc_profile=srgb_bytes(),
    )
    destination.write_bytes(buffer.getvalue())
    with Image.open(destination) as check:
        check.load()
        if check.format != "JPEG" or check.mode != "RGB" or check.size != expected:
            raise RuntimeError("Final JPEG verification failed")

    return {
        "schema_version": 1,
        "kind": "stockforge.kaggle_finalizer_result",
        "status": "visual_review_required",
        "request_id": data["request_id"],
        "source": data["source"],
        "target": target,
        "provider": "kaggle-realesrgan",
        "model_id": "RealESRGAN_x4plus",
        "scale": 4,
        "master": {
            "file": destination.name,
            "sha256": sha256_file(destination),
            "width": master.width,
            "height": master.height,
            "megapixels": round(megapixels, 4),
            "icc_profile": "sRGB",
            "jpeg_quality": 95,
            "subsampling": "4:4:4",
            "size_bytes": destination.stat().st_size,
        },
        "intermediate": {"file": intermediate.name, "sha256": sha256_file(intermediate)},
        "human_review_required": True,
        "notice": "AI upscale finished. Inspect at 100% for invented detail, haloing, blur, texture damage, object drift, pseudo-text, IP risk, and metadata accuracy before importing or submission.",
    }


def main() -> None:
    data = load_request()
    result = finalize(data, source_file(data))
    (OUTPUT_DIR / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "error.json").write_text(json.dumps({"status": "failed", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"STOCKFORGE FINALIZER FAILED: {exc}", file=sys.stderr)
        raise
