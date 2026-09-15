from __future__ import annotations

import time
import urllib.request
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import spaces
import torch

WEIGHTS_DIR = Path("/tmp/stockforge-realesrgan")
WEIGHTS_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"


def _ensure_basicsr_compat() -> None:
    import sys
    import types
    import torchvision.transforms.functional as functional

    module_name = "torchvision.transforms.functional_tensor"
    if module_name in sys.modules:
        return
    compatibility = types.ModuleType(module_name)
    compatibility.rgb_to_grayscale = functional.rgb_to_grayscale
    sys.modules[module_name] = compatibility


def _upscaler():
    _ensure_basicsr_compat()
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    weights = WEIGHTS_DIR / "RealESRGAN_x4plus.pth"
    if not weights.is_file():
        WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
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


@spaces.GPU(duration=55, size="large")
def upscale_remote(source_url: str, stockforge_job_id: str, scale: int = 4):
    job_id = str(stockforge_job_id or "").strip()
    if not job_id:
        raise ValueError("stockforge_job_id is required")
    if int(scale) != 4:
        raise ValueError("Only 4x upscaling is supported in the free production lane")

    started = time.perf_counter()
    request = urllib.request.Request(str(source_url), method="GET")
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()
    source = Image.open(BytesIO(payload))
    source.load()
    source = source.convert("RGB")
    array = np.asarray(source)
    output, _ = _upscaler().enhance(cv2.cvtColor(array, cv2.COLOR_RGB2BGR), outscale=4)
    rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb, mode="RGB")
    elapsed = round(time.perf_counter() - started, 3)
    print(f"[StockForge] upscale job={job_id} source={source.size} output={image.size} seconds={elapsed}")
    return image, 4, int(image.width), int(image.height), elapsed
