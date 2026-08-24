import os
import time
from pathlib import Path

import gradio as gr
import spaces
from huggingface_hub import hf_hub_download

from comfy_diffusion import check_runtime, vae_decode
from comfy_diffusion.conditioning import encode_prompt
from comfy_diffusion.models import ModelManager
from comfy_diffusion.nodes import run_node
from comfy_diffusion.sampling import sample

# Official ComfyUI Qwen Image T2I assets.
MODEL_REPO = "Comfy-Org/Qwen-Image_ComfyUI"
LORA_REPO = "lightx2v/Qwen-Image-Lightning"
ROOT = Path(os.getenv("STOCKFORGE_MODEL_DIR", "/tmp/stockforge-models"))
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
QWEN_IMAGE_FILE = "qwen_image_fp8_e4m3fn.safetensors"
QWEN_CLIP_FILE = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
QWEN_VAE_FILE = "qwen_image_vae.safetensors"
QWEN_LORA_FILE = "Qwen-Image-Lightning-8steps-V1.0.safetensors"


def _prepare_models():
    for folder in ("diffusion_models", "text_encoders", "vae", "loras"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)

    files = {
        QWEN_IMAGE_FILE: (MODEL_REPO, "split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors", "diffusion_models"),
        QWEN_CLIP_FILE: (MODEL_REPO, "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors", "text_encoders"),
        QWEN_VAE_FILE: (MODEL_REPO, "split_files/vae/qwen_image_vae.safetensors", "vae"),
        QWEN_LORA_FILE: (LORA_REPO, QWEN_LORA_FILE, "loras"),
    }

    for filename, (repo_id, hf_filename, folder) in files.items():
        target = ROOT / folder / filename
        if target.exists() and target.stat().st_size > 0:
            print(f"[StockForge] Cached: {folder}/{filename}")
            continue
        print(f"[StockForge] Downloading {repo_id}:{hf_filename}...")
        hf_hub_download(
            repo_id=repo_id,
            filename=hf_filename,
            revision="main",
            token=HF_TOKEN,
            local_dir=str(ROOT / folder),
            local_dir_use_symlinks=False,
        )


def _load_runtime_models():
    runtime = check_runtime()
    if isinstance(runtime, dict) and runtime.get("error"):
        raise RuntimeError(runtime["error"])

    _prepare_models()
    manager = ModelManager(models_dir=ROOT)

    print("[StockForge] Loading official Qwen Image FP8 diffusion model...")
    model = run_node(
        "UNETLoader",
        unet_name=QWEN_IMAGE_FILE,
        weight_dtype="default",
    )[0]

    print("[StockForge] Loading Qwen 2.5 VL FP8 text encoder...")
    clip = run_node(
        "CLIPLoader",
        clip_name=QWEN_CLIP_FILE,
        type="qwen_image",
        device="default",
    )[0]

    print("[StockForge] Loading Qwen Image VAE...")
    vae = manager.load_vae(QWEN_VAE_FILE)

    print("[StockForge] Loading official 8-step Lightning LoRA...")
    lora_model = run_node(
        "LoraLoaderModelOnly",
        model=model,
        lora_name=QWEN_LORA_FILE,
        strength_model=1.0,
    )[0]

    print("[StockForge] Models ready")
    return model, lora_model, clip, vae


MODEL_CACHE = None


def _get_models():
    global MODEL_CACHE
    if MODEL_CACHE is None:
        MODEL_CACHE = _load_runtime_models()
    return MODEL_CACHE


def estimate_duration(prompt, width, height, steps, seed, randomize_seed):
    return min(55, max(25, 12 + int(steps) * 4))


@spaces.GPU(duration=estimate_duration, size="large")
def generate_gpu(prompt, width, height, steps, seed, randomize_seed):
    started = time.perf_counter()
    base_model, lora_model, clip, vae = _get_models()

    if randomize_seed:
        seed = int.from_bytes(os.urandom(8), "little") & 0xFFFFFFFFFFFFFFFF
    seed = int(seed)

    # Mirrors the official Qwen Image workflow:
    # CLIPTextEncode -> EmptySD3LatentImage -> ModelSamplingAuraFlow -> KSampler -> VAEDecode.
    positive, negative = encode_prompt(clip, str(prompt).strip(), "")

    latent = run_node(
        "EmptySD3LatentImage",
        width=int(width),
        height=int(height),
        batch_size=1,
    )[0]

    # Official Qwen Image workflow uses shift=3.1.
    sampled_model = run_node(
        "ModelSamplingAuraFlow",
        model=lora_model,
        shift=3.1,
    )[0]

    denoised = sample(
        sampled_model,
        positive,
        negative,
        latent,
        steps=int(steps),
        cfg=1.0,
        sampler_name="euler",
        scheduler="simple",
        seed=seed,
    )

    image = vae_decode(vae, denoised)
    elapsed = round(time.perf_counter() - started, 3)
    return image, seed, elapsed


@spaces.GPU(duration=8, size="large")
def gpu_probe():
    """Read actual GPU capabilities without loading StockForge models."""
    import torch

    if not torch.cuda.is_available():
        return {
            "status": "error",
            "cuda_available": False,
            "error": "CUDA unavailable",
        }

    free_bytes, total_bytes = torch.cuda.mem_get_info(0)
    props = torch.cuda.get_device_properties(0)

    return {
        "status": "ok",
        "cuda_available": True,
        "device_name": torch.cuda.get_device_name(0),
        "compute_capability": f"{props.major}.{props.minor}",
        "total_vram_gib": round(total_bytes / 1024**3, 3),
        "free_vram_gib": round(free_bytes / 1024**3, 3),
        "allocated_vram_gib": round(torch.cuda.memory_allocated(0) / 1024**3, 3),
        "reserved_vram_gib": round(torch.cuda.memory_reserved(0) / 1024**3, 3),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "models_loaded": False,
        "image_generated": False,
    }


def generate(prompt, width=1024, height=1024, steps=8, seed=0, randomize_seed=True):
    prompt = str(prompt or "").strip()
    if not prompt:
        raise gr.Error("Prompt is required.")
    if int(width) != 1024 or int(height) != 1024:
        raise gr.Error("Baseline benchmark is fixed at 1024x1024.")
    if not 4 <= int(steps) <= 12:
        raise gr.Error("Steps must be between 4 and 12 for the free-tier benchmark.")

    print(f"[StockForge] Standalone prompt length: {len(prompt)}")
    return generate_gpu(prompt, int(width), int(height), int(steps), int(seed), bool(randomize_seed))


def portfolio_health():
    """Non-GPU health proof for the standalone-asset generation boundary."""
    return {
        "status": "ok",
        "generation_mode": "standalone_portfolio",
        "legacy_reality_compiler": "disabled",
        "default_constraints": [
            "one primary subject",
            "white isolated background",
            "no people, hands, tools, devices, screens, text, numbers, stamps, or unrelated props",
        ],
        "gpu_used": False,
    }


with gr.Blocks(title="StockForge V5 ZeroGPU") as demo:
    gr.Markdown("# StockForge V5 · ZeroGPU\nStandalone Asset Portfolio · Qwen Image FP8 + 8-step Lightning.")
    prompt = gr.Textbox(label="Prompt", lines=4)
    with gr.Row():
        width = gr.Number(value=1024, label="Width", precision=0)
        height = gr.Number(value=1024, label="Height", precision=0)
        steps = gr.Slider(4, 12, value=8, step=1, label="Steps")
    with gr.Row():
        seed = gr.Number(value=0, label="Seed", precision=0)
        randomize = gr.Checkbox(value=True, label="Random seed")
    generate_button = gr.Button("Generate", variant="primary")
    output = gr.Image(label="Generated image", type="pil")
    output_seed = gr.Number(label="Used seed", precision=0)
    gpu_seconds = gr.Number(label="Measured GPU-function seconds", precision=3)
    generate_button.click(generate, [prompt, width, height, steps, seed, randomize], [output, output_seed, gpu_seconds], api_name="generate")

    health_button = gr.Button("Standalone Portfolio Health Check")
    health_output = gr.JSON(label="Standalone Portfolio Status")
    health_button.click(portfolio_health, outputs=health_output, api_name="portfolio_health")

    gpu_probe_button = gr.Button("GPU Capability Probe")
    gpu_probe_output = gr.JSON(label="GPU Runtime Capability")
    gpu_probe_button.click(gpu_probe, outputs=gpu_probe_output, api_name="gpu_probe")


if __name__ == "__main__":
    demo.queue(max_size=32).launch()
