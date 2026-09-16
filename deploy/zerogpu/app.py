import json
import os
import random
import shutil
import sys
import time
import urllib.request
from pathlib import Path

import gradio as gr
import spaces
import torch
from huggingface_hub import hf_hub_download
from PIL import Image

# Comfy Diffusion supplies the actual Qwen-Image model/node runtime.
from comfy_diffusion import check_runtime, vae_decode
from comfy_diffusion.nodes import run_node


ROOT = Path(os.getenv("STOCKFORGE_MODEL_DIR", "/tmp/stockforge-models"))
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")

# Official ComfyUI-compatible Qwen-Image-2512 components.
QWEN_REPO = "Comfy-Org/Qwen-Image_ComfyUI"
QWEN_DIFFUSION_REMOTE = "split_files/diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors"
QWEN_CLIP_REMOTE = "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"
QWEN_VAE_REMOTE = "split_files/vae/qwen_image_vae.safetensors"
QWEN_LORA_REPO = "lightx2v/Qwen-Image-2512-Lightning"
QWEN_LORA_REMOTE = "Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors"

QWEN_DIFFUSION_FILE = "qwen_image_2512_fp8_e4m3fn.safetensors"
QWEN_CLIP_FILE = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
QWEN_VAE_FILE = "qwen_image_vae.safetensors"
QWEN_LORA_FILE = "Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors"

# Qwen-Image-2512 documented native canvases.
CANVASES = {
    (1328, 1328),
    (1664, 928),
    (928, 1664),
    (1472, 1104),
    (1104, 1472),
    (1584, 1056),
    (1056, 1584),
}

# Official Real-ESRGAN x4 general-image checkpoint.
ESRGAN_URL = (
    "https://github.com/xinntao/Real-ESRGAN/releases/download/"
    "v0.1.0/RealESRGAN_x4plus.pth"
)
ESRGAN_PATH = ROOT / "weights" / "RealESRGAN_x4plus.pth"

QWEN_CACHE = None
ESRGAN_CACHE = None


def _prepare_dirs():
    for folder in ("diffusion_models", "text_encoders", "vae", "loras", "weights"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)


def _link_download(repo_id, remote_filename, target):
    target = Path(target)
    if target.exists() and target.stat().st_size > 0:
        return

    cached = hf_hub_download(
        repo_id=repo_id,
        filename=remote_filename,
        revision="main",
        token=HF_TOKEN,
        local_dir=str(ROOT / "_hf_downloads"),
        local_dir_use_symlinks=False,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        target.unlink()
    try:
        target.symlink_to(cached)
    except OSError:
        shutil.copy2(cached, target)


def _prepare_qwen_assets():
    _prepare_dirs()
    _link_download(QWEN_REPO, QWEN_DIFFUSION_REMOTE, ROOT / "diffusion_models" / QWEN_DIFFUSION_FILE)
    _link_download(QWEN_REPO, QWEN_CLIP_REMOTE, ROOT / "text_encoders" / QWEN_CLIP_FILE)
    _link_download(QWEN_REPO, QWEN_VAE_REMOTE, ROOT / "vae" / QWEN_VAE_FILE)
    _link_download(QWEN_LORA_REPO, QWEN_LORA_REMOTE, ROOT / "loras" / QWEN_LORA_FILE)


def _load_qwen():
    global QWEN_CACHE
    if QWEN_CACHE is not None:
        return QWEN_CACHE

    runtime = check_runtime()
    if isinstance(runtime, dict) and runtime.get("error"):
        raise RuntimeError(runtime["error"])

    _prepare_qwen_assets()

    print("[StockForge] Loading Qwen-Image-2512 FP8 diffusion model")
    model = run_node("UNETLoader", unet_name=QWEN_DIFFUSION_FILE, weight_dtype="default")[0]

    print("[StockForge] Loading Qwen 2.5-VL 7B FP8 text encoder")
    clip = run_node("CLIPLoader", clip_name=QWEN_CLIP_FILE, type="qwen_image", device="default")[0]

    print("[StockForge] Loading Qwen image VAE")
    vae = run_node("VAELoader", vae_name=QWEN_VAE_FILE)[0]

    print("[StockForge] Attaching Qwen-Image-2512 Lightning 4-step LoRA")
    model = run_node(
        "LoraLoaderModelOnly",
        model=model,
        lora_name=QWEN_LORA_FILE,
        strength_model=1.0,
    )[0]
    model = run_node("ModelSamplingAuraFlow", model=model, shift=3.1)[0]

    QWEN_CACHE = (model, clip, vae)
    return QWEN_CACHE


def _to_pil(image):
    if isinstance(image, Image.Image):
        return image.convert("RGB")

    if torch.is_tensor(image):
        tensor = image.detach().float().cpu()
        if tensor.ndim == 4:
            tensor = tensor[0]
        if tensor.ndim != 3:
            raise TypeError(f"Unsupported decoded tensor shape: {tuple(tensor.shape)}")
        if tensor.shape[0] in (1, 3, 4):
            tensor = tensor.permute(1, 2, 0)
        tensor = tensor.clamp(0, 1)
        array = (tensor.numpy() * 255.0).round().astype("uint8")
        if array.shape[-1] == 1:
            array = array[..., 0]
        return Image.fromarray(array).convert("RGB")

    raise TypeError(f"Unsupported decoded image type: {type(image).__name__}")


def _canonical_canvas(width, height):
    requested = (int(width), int(height))
    if requested in CANVASES:
        return requested
    aspect = max(0.01, float(width) / max(1, float(height)))
    return min(CANVASES, key=lambda size: abs((size[0] / size[1]) - aspect))


def _commercial_prompt(prompt):
    base = str(prompt or "").strip()
    return (
        "commercial stock asset, production-ready, premium visual quality, "
        "clear subject hierarchy, intentional composition, natural materials, "
        "clean lighting, no watermark, no logo, no brand, no signature, "
        "no UI, no screenshot, no border, no decorative frame, "
        "no accidental text, no copyrighted character, no artist reference, "
        f"{base}"
    )


def _qwen_negative():
    return (
        "低分辨率，低画质，模糊，噪点，肢体畸形，手指畸形，"
        "不一致的光照，蜡像感，过度平滑，混乱构图，"
        "文字模糊，扭曲，logo，水印，签名，边框，UI，截图"
    )


def _generate_with_qwen(prompt, width, height, seed, randomize_seed):
    model, clip, vae = _load_qwen()
    if randomize_seed:
        seed = random.randint(0, 0x7FFFFFFF)
    seed = int(seed)

    positive = run_node("CLIPTextEncode", clip=clip, text=_commercial_prompt(prompt))[0]
    negative = run_node("CLIPTextEncode", clip=clip, text=_qwen_negative())[0]
    latent = run_node("EmptySD3LatentImage", width=int(width), height=int(height), batch_size=1)[0]
    samples = run_node(
        "KSampler",
        model=model,
        positive=positive,
        negative=negative,
        latent_image=latent,
        seed=seed,
        control_after_generate="fixed",
        steps=4,
        cfg=1.0,
        sampler_name="euler",
        scheduler="simple",
        denoise=1.0,
    )[0]
    image = _to_pil(vae_decode(vae, samples))
    return image, seed


# Generation boundary: produce a standalone asset portfolio candidate, not a domain-specific compiler artifact.
@spaces.GPU(duration=120, size="large")
def generate_gpu(prompt, width=1328, height=1328, steps=4, seed=0, randomize_seed=True):
    started = time.perf_counter()
    width, height = _canonical_canvas(width, height)
    image, used_seed = _generate_with_qwen(prompt, width, height, seed, randomize_seed)

    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"generated-{int(time.time() * 1000)}.png"
    image.save(out_path, format="PNG", optimize=True)
    elapsed = round(time.perf_counter() - started, 3)

    try:
        torch.cuda.empty_cache()
    except Exception:
        pass
    return str(out_path), used_seed, elapsed


def _ensure_esrgan():
    global ESRGAN_CACHE
    if ESRGAN_CACHE is not None:
        return ESRGAN_CACHE

    _prepare_dirs()
    if not ESRGAN_PATH.exists() or ESRGAN_PATH.stat().st_size < 50_000_000:
        print("[StockForge] Downloading official RealESRGAN_x4plus checkpoint")
        urllib.request.urlretrieve(ESRGAN_URL, ESRGAN_PATH)

    try:
        import torchvision.transforms.functional as functional
        sys.modules.setdefault("torchvision.transforms.functional_tensor", functional)
    except Exception:
        pass

    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    ESRGAN_CACHE = RealESRGANer(
        scale=4,
        model_path=str(ESRGAN_PATH),
        model=model,
        tile=256,
        tile_pad=20,
        pre_pad=0,
        half=True,
    )
    return ESRGAN_CACHE


def _upscale_image(source_path):
    engine = _ensure_esrgan()
    image = Image.open(source_path).convert("RGB")
    import numpy as np
    bgr = np.asarray(image)[:, :, ::-1].copy()
    output, _ = engine.enhance(bgr, outscale=4)
    return Image.fromarray(output[:, :, ::-1].astype("uint8"), "RGB")


@spaces.GPU(duration=120, size="large")
def upscale_gpu(source_path, job_id=""):
    started = time.perf_counter()
    final_dir = ROOT / "outputs"
    final_dir.mkdir(parents=True, exist_ok=True)
    out_path = final_dir / f"{job_id or 'final'}-4x.jpg"
    image = _upscale_image(source_path)
    image.save(out_path, format="JPEG", quality=97, subsampling=0, optimize=True, progressive=True)
    width, height = image.size
    elapsed = round(time.perf_counter() - started, 3)
    try:
        torch.cuda.empty_cache()
    except Exception:
        pass
    return str(out_path), width, height, 4, elapsed


def generate(prompt, width=1328, height=1328, steps=4, seed=0, randomize_seed=True):
    if not str(prompt or "").strip():
        raise gr.Error("Prompt is required.")
    width, height = _canonical_canvas(width, height)
    return generate_gpu(prompt, width, height, 4, seed, randomize_seed)


def generate_remote(prompt, width=1328, height=1328, steps=4, seed=0, randomize_seed=True, stockforge_job_id=""):
    if not str(stockforge_job_id or "").strip():
        raise gr.Error("stockforge_job_id is required")
    try:
        return generate(prompt, width, height, steps, seed, randomize_seed)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {str(exc)}"[:1000]
        print(f"[StockForge] generation failed: {detail}", flush=True)
        raise gr.Error(detail) from exc


def upscale_remote(source_path, job_id=""):
    source_path = str(source_path or "").strip()
    if not source_path:
        raise gr.Error("Source path is required.")
    local = source_path
    if source_path.startswith(("http://", "https://")):
        cache = ROOT / "inputs"
        cache.mkdir(parents=True, exist_ok=True)
        local = cache / f"{job_id or 'source'}-source.bin"
        urllib.request.urlretrieve(source_path, local)
    try:
        return upscale_gpu(str(local), str(job_id or ""))
    except Exception as exc:
        detail = f"{type(exc).__name__}: {str(exc)}"[:1000]
        print(f"[StockForge] upscale failed: {detail}", flush=True)
        raise gr.Error(detail) from exc


def runtime_health():
    return {
        "status": "ok",
        "generation_provider": "huggingface-zerogpu",
        "generation_model": "Qwen-Image-2512 + Lightning 4-step",
        "upscale_provider": "huggingface-zerogpu",
        "upscale_model": "Real-ESRGAN_x4plus",
        "gpu_used": False,
        "commercial_license_check": {
            "qwen_image_2512": "Apache-2.0",
            "qwen_image_2512_lightning": "Apache-2.0",
        },
        "adobe_target": {
            "native_canvases": sorted([f"{w}x{h}" for w, h in CANVASES]),
            "final_scale": "4x",
            "final_format": "JPEG sRGB",
        },
    }


def runtime_probe():
    runtime = check_runtime()
    return {
        "status": "ok" if not (isinstance(runtime, dict) and runtime.get("error")) else "error",
        "runtime": runtime,
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "gpu_used": False,
        "models_loaded": False,
        "qwen_model_files": [QWEN_DIFFUSION_FILE, QWEN_CLIP_FILE, QWEN_VAE_FILE, QWEN_LORA_FILE],
    }


with gr.Blocks(title="StockForge ZeroGPU") as demo:
    gr.Markdown(
        "# StockForge ZeroGPU\n"
        "Qwen-Image-2512 Lightning + Real-ESRGAN x4, commercial asset generation runtime."
    )

    with gr.Row():
        prompt = gr.Textbox(label="Prompt", lines=5)
    with gr.Row():
        width = gr.Number(value=1328, label="Width", precision=0)
        height = gr.Number(value=1328, label="Height", precision=0)
        steps = gr.Number(value=4, label="Steps", precision=0)
    with gr.Row():
        seed = gr.Number(value=0, label="Seed", precision=0)
        randomize = gr.Checkbox(value=True, label="Random seed")
    generate_button = gr.Button("Generate", variant="primary")
    output = gr.Image(label="Generated image", type="filepath")
    output_seed = gr.Number(label="Used seed", precision=0)
    gpu_seconds = gr.Number(label="Measured GPU seconds", precision=3)
    generate_button.click(
        generate,
        [prompt, width, height, steps, seed, randomize],
        [output, output_seed, gpu_seconds],
        api_name="generate",
    )

    source = gr.File(label="Source image", type="filepath")
    upscale_button = gr.Button("Finalize 4x", variant="primary")
    upscale_output = gr.Image(label="Final master", type="filepath")
    final_width = gr.Number(label="Final width", precision=0)
    final_height = gr.Number(label="Final height", precision=0)
    final_scale = gr.Number(label="Scale", precision=0)
    final_seconds = gr.Number(label="Measured GPU seconds", precision=3)
    upscale_button.click(
        upscale_gpu,
        [source],
        [upscale_output, final_width, final_height, final_scale, final_seconds],
        api_name="upscale",
    )

    remote_prompt = gr.Textbox(visible=False)
    remote_width = gr.Number(value=1328, visible=False)
    remote_height = gr.Number(value=1328, visible=False)
    remote_steps = gr.Number(value=4, visible=False)
    remote_seed = gr.Number(value=0, visible=False)
    remote_randomize = gr.Checkbox(value=True, visible=False)
    remote_job_id = gr.Textbox(visible=False)
    remote_button = gr.Button(visible=False)
    remote_output = gr.Image(visible=False, type="filepath")
    remote_output_seed = gr.Number(visible=False)
    remote_gpu_seconds = gr.Number(visible=False)
    remote_button.click(
        generate_remote,
        [remote_prompt, remote_width, remote_height, remote_steps, remote_seed, remote_randomize, remote_job_id],
        [remote_output, remote_output_seed, remote_gpu_seconds],
        api_name="generate_remote",
    )

    remote_source = gr.Textbox(visible=False)
    remote_job_id_upscale = gr.Textbox(visible=False)
    remote_upscale_button = gr.Button(visible=False)
    remote_upscale_output = gr.Image(visible=False, type="filepath")
    remote_final_width = gr.Number(visible=False)
    remote_final_height = gr.Number(visible=False)
    remote_final_scale = gr.Number(visible=False)
    remote_final_seconds = gr.Number(visible=False)
    remote_upscale_button.click(
        upscale_remote,
        [remote_source, remote_job_id_upscale],
        [remote_upscale_output, remote_final_width, remote_final_height, remote_final_scale, remote_final_seconds],
        api_name="upscale_remote",
    )

    health_button = gr.Button("Runtime Health")
    health_output = gr.JSON(label="Runtime")
    health_button.click(runtime_health, outputs=health_output)
    runtime_button = gr.Button("Runtime Probe")
    runtime_output = gr.JSON(label="Probe")
    runtime_button.click(runtime_probe, outputs=runtime_output)


if __name__ == "__main__":
    demo.queue(max_size=16).launch()
