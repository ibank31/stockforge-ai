import os
import time
from pathlib import Path

import gradio as gr
import spaces
import torch
from huggingface_hub import hf_hub_download

# ComfyUI's quantization-aware runtime is required for qwen_3_4b_fp8_mixed.safetensors.
# Do not load this checkpoint with Transformers load_state_dict().
from comfy_diffusion import check_runtime, vae_decode
from comfy_diffusion.conditioning import encode_prompt
from comfy_diffusion.models import ModelManager
from comfy_diffusion.nodes import run_node
from comfy_diffusion.sampling import sample

from reality_engine import compile_prompt, reality_preflight

MODEL_REPO = "ibank31/stockforge-models"
ROOT = Path(os.getenv("STOCKFORGE_MODEL_DIR", "/tmp/stockforge-models"))
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
Z_IMAGE_FILE = "z_image_turbo_fp8_e4m3fn.safetensors"
QWEN_FILE = "qwen_3_4b_fp8_mixed.safetensors"
AE_FILE = "ae.safetensors"
REALITY_WORKFLOW = "wall_moisture_inspection"


def _prepare_models():
    for folder in ("diffusion_models", "text_encoders", "vae"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    files = {
        Z_IMAGE_FILE: "diffusion_models",
        QWEN_FILE: "text_encoders",
        AE_FILE: "vae",
    }
    for filename, folder in files.items():
        target = ROOT / folder / filename
        if target.exists() and target.stat().st_size > 0:
            print(f"[StockForge] Cached: {folder}/{filename}")
            continue
        print(f"[StockForge] Downloading {filename}...")
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=filename,
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
    print("[StockForge] Loading FP8 Z-Image model through Comfy runtime...")
    model = run_node(
        "UNETLoader",
        unet_name=Z_IMAGE_FILE,
        weight_dtype="default",
    )[0]
    print("[StockForge] Loading Qwen3 FP8 mixed text encoder through Comfy runtime...")
    clip = run_node(
        "CLIPLoader",
        clip_name=QWEN_FILE,
        type="lumina2",
        device="default",
    )[0]
    print("[StockForge] Loading AE VAE...")
    vae = manager.load_vae(AE_FILE)
    print("[StockForge] Models ready")
    return model, clip, vae


MODEL_CACHE = None


def _get_models():
    global MODEL_CACHE
    if MODEL_CACHE is None:
        MODEL_CACHE = _load_runtime_models()
    return MODEL_CACHE


def estimate_duration(prompt, width, height, steps, seed, randomize_seed):
    return min(55, max(20, 8 + int(steps) * 4))


@spaces.GPU(duration=estimate_duration, size="large")
def generate_gpu(prompt, width, height, steps, seed, randomize_seed):
    started = time.perf_counter()
    model, clip, vae = _get_models()
    if randomize_seed:
        seed = int.from_bytes(os.urandom(8), "little") & 0xFFFFFFFFFFFFFFFF
    seed = int(seed)

    positive = encode_prompt(clip, str(prompt).strip())
    negative = encode_prompt(clip, "")

    latent = {"samples": torch.zeros((1, 16, int(height) // 8, int(width) // 8), dtype=torch.float32)}
    model = run_node("ModelSamplingAuraFlow", model=model, shift=3.0)[0]
    denoised = sample(
        model,
        positive,
        negative,
        latent,
        steps=int(steps),
        cfg=1.0,
        sampler_name="res_multistep",
        scheduler="simple",
        seed=seed,
    )
    image = vae_decode(vae, denoised)
    elapsed = round(time.perf_counter() - started, 3)
    return image, seed, elapsed



@spaces.GPU(duration=8, size="large")
def gpu_probe():
    """Read actual GPU capabilities without loading StockForge models."""
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

    # Reality preflight and compilation happen before the GPU function is called.
    # This keeps contradictory professional scenes out of the paid/free GPU window.
    reality_preflight(REALITY_WORKFLOW)
    compiled_prompt = compile_prompt(prompt, task_id=REALITY_WORKFLOW)
    print(f"[StockForge] Reality workflow: {REALITY_WORKFLOW}")
    print(f"[StockForge] Compiled prompt length: {len(compiled_prompt)}")

    return generate_gpu(compiled_prompt, int(width), int(height), int(steps), int(seed), bool(randomize_seed))


# ============================================================
# EXPERIMENTAL: NATIVE QWEN IMAGE
# ============================================================

QWEN_MODEL_REPO = "Comfy-Org/Qwen-Image_ComfyUI"

QWEN_UNET_FILE = "qwen_image_fp8_e4m3fn.safetensors"
QWEN_CLIP_FILE = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
QWEN_VAE_FILE = "qwen_image_vae.safetensors"

QWEN_CACHE = None


def _prepare_qwen_models():
    for folder in ("diffusion_models", "text_encoders", "vae"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)

    files = {
        QWEN_UNET_FILE: (
            "diffusion_models",
            "split_files/diffusion_models/qwen_image_fp8_e4m3fn.safetensors",
        ),
        QWEN_CLIP_FILE: (
            "text_encoders",
            "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        ),
        QWEN_VAE_FILE: (
            "vae",
            "split_files/vae/qwen_image_vae.safetensors",
        ),
    }

    for filename, (folder, remote_filename) in files.items():
        target = ROOT / folder / filename

        if target.exists() and target.stat().st_size > 0:
            print(f"[StockForge Qwen] Cached: {folder}/{filename}")
            continue

        print(f"[StockForge Qwen] Downloading: {remote_filename}")

        hf_hub_download(
            repo_id=QWEN_MODEL_REPO,
            filename=remote_filename,
            revision="main",
            token=HF_TOKEN,
            local_dir=str(ROOT),
        )


def _load_qwen_runtime_models():
    global QWEN_CACHE

    if QWEN_CACHE is not None:
        return QWEN_CACHE

    runtime = check_runtime()
    if isinstance(runtime, dict) and runtime.get("error"):
        raise RuntimeError(runtime["error"])

    _prepare_qwen_models()

    from comfy_diffusion.models import ModelManager
    from comfy_diffusion.nodes import run_node

    manager = ModelManager(models_dir=ROOT)

    print("[StockForge Qwen] Loading diffusion model...")
    model = run_node(
        "UNETLoader",
        unet_name=QWEN_UNET_FILE,
        weight_dtype="default",
    )[0]

    print("[StockForge Qwen] Loading Qwen VL text encoder...")
    clip = run_node(
        "CLIPLoader",
        clip_name=QWEN_CLIP_FILE,
        type="qwen_image",
        device="default",
    )[0]

    print("[StockForge Qwen] Loading VAE...")
    vae = manager.load_vae(str(ROOT / "vae" / QWEN_VAE_FILE))

    QWEN_CACHE = (model, clip, vae)

    print("[StockForge Qwen] Native Qwen models ready")

    return QWEN_CACHE


@spaces.GPU(duration=60, size="large")
def qwen_generate_gpu(prompt, steps, seed, randomize_seed):
    started = time.perf_counter()

    model, clip, vae = _load_qwen_runtime_models()

    if randomize_seed:
        seed = int.from_bytes(os.urandom(8), "little") & 0xFFFFFFFFFFFFFFFF

    seed = int(seed)

    positive = encode_prompt(clip, str(prompt).strip())
    negative = encode_prompt(clip, "")

    latent = {
        "samples": torch.zeros(
            (1, 16, 128, 128),
            dtype=torch.float32,
        )
    }

    denoised = sample(
        model,
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


def qwen_generate(
    prompt,
    steps=4,
    seed=0,
    randomize_seed=True,
):
    prompt = str(prompt or "").strip()

    if not prompt:
        raise gr.Error("Prompt is required.")

    if not 1 <= int(steps) <= 12:
        raise gr.Error("Steps must be between 1 and 12.")

    return qwen_generate_gpu(
        prompt,
        int(steps),
        int(seed),
        bool(randomize_seed),
    )

def reality_health():
    """Non-GPU health proof for the active reality compiler."""
    workflow = reality_preflight(REALITY_WORKFLOW)
    probe = compile_prompt("professional construction inspection photograph", REALITY_WORKFLOW)
    return {
        "status": "ok",
        "reality_engine": "active",
        "compiler": "active",
        "workflow": REALITY_WORKFLOW,
        "tool": workflow.tool,
        "target": workflow.target,
        "human_action": workflow.action,
        "compiled_prompt_length": len(probe),
        "gpu_used": False,
    }


with gr.Blocks(title="StockForge V5 ZeroGPU") as demo:
    gr.Markdown("# StockForge V5 · ZeroGPU\nFP8-aware Z-Image Turbo runtime + Reality Knowledge Layer.")
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

    health_button = gr.Button("Reality Health Check")
    health_output = gr.JSON(label="Reality Engine Status")
    health_button.click(reality_health, outputs=health_output, api_name="reality_health")


    gpu_probe_button = gr.Button("GPU Capability Probe")
    gpu_probe_output = gr.JSON(label="GPU Runtime Capability")
    gpu_probe_button.click(
        gpu_probe,
        outputs=gpu_probe_output,
        api_name="gpu_probe",
    )



# Experimental native Qwen API endpoint.
qwen_prompt_api = gr.Textbox(visible=False)
qwen_steps_api = gr.Number(value=4, visible=False)
qwen_seed_api = gr.Number(value=0, visible=False)
qwen_randomize_api = gr.Checkbox(value=True, visible=False)
qwen_button_api = gr.Button(visible=False)
qwen_output_api = gr.Image(visible=False, type="pil")
qwen_output_seed_api = gr.Number(visible=False)
qwen_gpu_seconds_api = gr.Number(visible=False)

qwen_button_api.click(
    qwen_generate,
    [qwen_prompt_api, qwen_steps_api, qwen_seed_api, qwen_randomize_api],
    [qwen_output_api, qwen_output_seed_api, qwen_gpu_seconds_api],
    api_name="qwen_generate",
)

if __name__ == "__main__":
    demo.queue(max_size=32).launch()
