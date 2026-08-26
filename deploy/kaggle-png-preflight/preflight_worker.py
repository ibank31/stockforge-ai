"""Offline BiRefNet preflight using a synthetic image only; no user asset or upload."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

INPUT_ROOT = Path("/kaggle/input")
OUTPUT = Path("/kaggle/working/stockforge-png-preflight")


def find_model_root() -> Path:
    matches = sorted(path.parent for path in INPUT_ROOT.rglob("config.json") if (path.parent / "model.safetensors").is_file())
    if len(matches) != 1:
        raise RuntimeError(f"Expected one BiRefNet root, found {len(matches)}")
    return matches[0]


def install_wheels() -> list[str]:
    from importlib.metadata import PackageNotFoundError, version

    missing = []
    try:
        if version("transformers") != "4.48.3":
            missing.append("transformers-version")
        if version("safetensors") != "0.4.5":
            missing.append("safetensors-version")
        if version("tokenizers") != "0.21.0":
            missing.append("tokenizers-version")
    except PackageNotFoundError:
        missing.append("missing-package")
    wheels = sorted(path for path in INPUT_ROOT.rglob("*.whl") if path.is_file())
    if missing and not wheels:
        raise RuntimeError("Offline wheelhouse missing")
    if missing:
        wheel_dir = wheels[0].parent
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-index", "--force-reinstall", "--no-deps", "--find-links", str(wheel_dir), "transformers==4.48.3", "safetensors==0.4.5", "tokenizers==0.21.0", "huggingface-hub==0.27.1", "Pillow==11.1.0", "numpy==2.0.2"])
    return missing


def main() -> None:
    started = time.perf_counter()
    missing_before = install_wheels()
    import torch
    from transformers import AutoModelForImageSegmentation
    from torchvision import transforms

    model_root = find_model_root()
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
    model = AutoModelForImageSegmentation.from_pretrained(str(model_root), trust_remote_code=True, local_files_only=True, torch_dtype=dtype)
    model.to(device).eval()
    synthetic = Image.new("RGB", (1024, 1024), "white")
    draw = ImageDraw.Draw(synthetic)
    draw.rounded_rectangle((230, 170, 794, 854), radius=80, fill=(36, 132, 143), outline=(20, 43, 74), width=18)
    draw.ellipse((360, 320, 664, 624), fill=(242, 184, 75), outline=(20, 43, 74), width=18)
    transform = transforms.Compose([transforms.Resize((1024, 1024)), transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    tensor = transform(synthetic).unsqueeze(0).to(device=device, dtype=dtype)
    with torch.inference_mode():
        prediction = model(tensor)[-1].sigmoid().float().cpu()[0, 0]
    mask = transforms.ToPILImage()(prediction).resize(synthetic.size, Image.Resampling.LANCZOS)
    rgba = synthetic.convert("RGBA")
    rgba.putalpha(mask)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    synthetic.save(OUTPUT / "synthetic_input.png")
    rgba.save(OUTPUT / "synthetic_rgba_output.png")
    free, total = torch.cuda.mem_get_info(0) if torch.cuda.is_available() else (0, 0)
    report = {
        "status": "passed",
        "model": "ZhengPeng7/BiRefNet",
        "model_root": str(model_root),
        "device": device,
        "dtype": str(dtype),
        "device_note": device_note,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "vram_total_gib": round(total / 1024**3, 3),
        "vram_free_after_inference_gib": round(free / 1024**3, 3),
        "synthetic_input_only": True,
        "rgba_output": True,
        "output_size": list(rgba.size),
        "alpha_min": min(mask.getextrema()),
        "alpha_max": max(mask.getextrema()),
        "wheel_install_was_needed": bool(missing_before),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "jpeg_pipeline_touched": False,
        "hf_token_used": False,
        "notice": "This is only an environment/model-load preflight. It is not a commercial asset trial.",
    }
    (OUTPUT / "birefnet_preflight.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
