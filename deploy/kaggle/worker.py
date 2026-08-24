"""Kaggle-compatible StockForge GPU worker.

This is the same model/runtime boundary as the HF worker, but without the
Hugging Face `spaces.GPU` decorator. It exposes the same Gradio
`generate_remote` endpoint so the core uses one provider adapter for either
compute location.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import gradio as gr
import torch
from huggingface_hub import hf_hub_download

from comfy_diffusion import check_runtime, vae_decode  # noqa: E402
from comfy_diffusion.conditioning import encode_prompt  # noqa: E402
from comfy_diffusion.models import ModelManager  # noqa: E402
from comfy_diffusion.nodes import run_node  # noqa: E402
from comfy_diffusion.sampling import sample  # noqa: E402

MODEL_REPO = os.getenv("STOCKFORGE_MODEL_REPO", "ibank31/stockforge-models")
ROOT = Path(os.getenv("STOCKFORGE_MODEL_DIR", "/kaggle/working/stockforge-models"))
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
Z_IMAGE_FILE = "z_image_turbo_fp8_e4m3fn.safetensors"
QWEN_FILE = "qwen_3_4b_fp8_mixed.safetensors"
AE_FILE = "ae.safetensors"
MODEL_CACHE = None
JOB_CACHE = {}


def prepare_models():
    for folder in ("diffusion_models", "text_encoders", "vae"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    for filename, folder in {
        Z_IMAGE_FILE: "diffusion_models",
        QWEN_FILE: "text_encoders",
        AE_FILE: "vae",
    }.items():
        target = ROOT / folder / filename
        if target.exists() and target.stat().st_size > 0:
            continue
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=filename,
            revision="main",
            token=HF_TOKEN,
            local_dir=str(ROOT / folder),
            local_dir_use_symlinks=False,
        )


def load_models():
    runtime = check_runtime()
    if isinstance(runtime, dict) and runtime.get("error"):
        raise RuntimeError(runtime["error"])
    prepare_models()
    manager = ModelManager(models_dir=ROOT)
    model = run_node("UNETLoader", unet_name=Z_IMAGE_FILE, weight_dtype="default")[0]
    clip = run_node("CLIPLoader", clip_name=QWEN_FILE, type="lumina2", device="default")[0]
    vae = manager.load_vae(AE_FILE)
    return model, clip, vae


def get_models():
    global MODEL_CACHE
    if MODEL_CACHE is None:
        MODEL_CACHE = load_models()
    return MODEL_CACHE


def generate(prompt, width=1024, height=1024, steps=8, seed=0, randomize_seed=True):
    prompt = str(prompt or "").strip()
    if not prompt:
        raise gr.Error("Prompt is required")
    if int(width) != 1024 or int(height) != 1024:
        raise gr.Error("Baseline worker is fixed at 1024x1024")
    if not 4 <= int(steps) <= 12:
        raise gr.Error("Steps must be between 4 and 12")
    started = time.perf_counter()
    model, clip, vae = get_models()
    if randomize_seed:
        seed = int.from_bytes(os.urandom(8), "little") & 0xFFFFFFFFFFFFFFFF
    seed = int(seed)
    positive = encode_prompt(clip, prompt)
    negative = encode_prompt(clip, "")
    latent = {"samples": torch.zeros((1, 16, int(height) // 8, int(width) // 8), dtype=torch.float32)}
    sampled_model = run_node("ModelSamplingAuraFlow", model=model, shift=3.0)[0]
    denoised = sample(
        sampled_model,
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
    return image, seed, round(time.perf_counter() - started, 3)


def generate_remote(prompt, width=1024, height=1024, steps=8, seed=0, randomize_seed=True, stockforge_job_id=""):
    job_id = str(stockforge_job_id or "").strip()
    if not job_id:
        raise gr.Error("stockforge_job_id is required")
    if job_id in JOB_CACHE:
        return JOB_CACHE[job_id]
    result = generate(prompt, width, height, steps, seed, randomize_seed)
    JOB_CACHE[job_id] = result
    return result


with gr.Blocks(title="StockForge Kaggle Worker") as demo:
    gr.Markdown("# StockForge GPU Worker · Kaggle")
    prompt = gr.Textbox(label="Prompt", lines=4)
    width = gr.Number(value=1024, visible=False)
    height = gr.Number(value=1024, visible=False)
    steps = gr.Number(value=8, visible=False)
    seed = gr.Number(value=0, visible=False)
    randomize = gr.Checkbox(value=True, visible=False)
    job_id = gr.Textbox(label="StockForge Job ID")
    button = gr.Button("Generate")
    output = gr.Image(type="pil")
    output_seed = gr.Number()
    gpu_seconds = gr.Number()
    button.click(
        generate_remote,
        [prompt, width, height, steps, seed, randomize, job_id],
        [output, output_seed, gpu_seconds],
        api_name="generate_remote",
    )


if __name__ == "__main__":
    demo.queue(max_size=16).launch(share=True)
