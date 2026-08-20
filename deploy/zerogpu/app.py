import os
import time

import gradio as gr
import spaces
import torch
from diffusers import AutoencoderKL, DiffusionPipeline, ZImageTransformer2DModel
from huggingface_hub import hf_hub_download, snapshot_download

MODEL_REPO = "ibank31/stockforge-models"
PIPELINE_ID = "Tongyi-MAI/Z-Image-Turbo"
DTYPE = torch.bfloat16
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")


def _download_model(filename):
    print(f"[StockForge] Downloading {filename} from {MODEL_REPO}...")
    return hf_hub_download(
        repo_id=MODEL_REPO,
        filename=filename,
        revision="main",
        token=HF_TOKEN,
    )


def _download_pipeline_configs():
    print("[StockForge] Downloading Z-Image pipeline configs...")
    return snapshot_download(
        repo_id=PIPELINE_ID,
        revision="main",
        allow_patterns=[
            "model_index.json",
            "transformer/config.json",
            "vae/config.json",
            "scheduler/scheduler_config.json",
            "text_encoder/config.json",
            "tokenizer/*",
        ],
        token=HF_TOKEN,
    )


def _build_pipeline():
    print("[StockForge] Resolving StockForge model files...")
    z_image_path = _download_model("z_image_turbo_fp8_e4m3fn.safetensors")
    ae_path = _download_model("ae.safetensors")
    pipeline_dir = _download_pipeline_configs()

    transformer_config = os.path.join(pipeline_dir, "transformer")
    vae_config = os.path.join(pipeline_dir, "vae")

    print("[StockForge] Loading Z-Image FP8 transformer...")
    transformer = ZImageTransformer2DModel.from_single_file(
        z_image_path,
        config=transformer_config,
        torch_dtype=DTYPE,
    )

    print("[StockForge] Loading AE...")
    vae = AutoencoderKL.from_single_file(
        ae_path,
        config=vae_config,
        torch_dtype=DTYPE,
    )

    print("[StockForge] Loading pipeline components...")
    pipe = DiffusionPipeline.from_pretrained(
        pipeline_dir,
        transformer=transformer,
        vae=vae,
        torch_dtype=DTYPE,
        low_cpu_mem_usage=False,
    )
    pipe.to("cuda")
    return pipe


PIPE = _build_pipeline()
print("[StockForge] Pipeline ready")


def estimate_duration(prompt, width, height, steps, seed, randomize_seed):
    steps = int(steps)
    return min(55, max(20, 8 + steps * 4))


@spaces.GPU(duration=estimate_duration, size="large")
def generate_gpu(prompt, width, height, steps, seed, randomize_seed):
    started = time.perf_counter()
    if randomize_seed:
        seed = int(torch.randint(0, 2**32 - 1, (1,), device="cuda").item())
    seed = int(seed)

    generator = torch.Generator(device="cuda").manual_seed(seed)
    image = PIPE(
        prompt=str(prompt).strip(),
        height=int(height),
        width=int(width),
        num_inference_steps=int(steps),
        guidance_scale=0.0,
        generator=generator,
    ).images[0]

    elapsed = time.perf_counter() - started
    return image, seed, round(elapsed, 3)


def generate(prompt, width=1024, height=1024, steps=8, seed=0, randomize_seed=True):
    prompt = str(prompt or "").strip()
    if not prompt:
        raise gr.Error("Prompt is required.")

    width = int(width)
    height = int(height)
    steps = int(steps)

    if width != 1024 or height != 1024:
        raise gr.Error("Baseline benchmark is fixed at 1024x1024.")
    if not 4 <= steps <= 12:
        raise gr.Error("Steps must be between 4 and 12 for the free-tier benchmark.")

    return generate_gpu(prompt, width, height, steps, int(seed), bool(randomize_seed))


with gr.Blocks(title="StockForge V5 ZeroGPU") as demo:
    gr.Markdown(
        "# StockForge V5 · ZeroGPU\n"
        "Quota-aware Z-Image Turbo benchmark runtime."
    )
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

    generate_button.click(
        generate,
        inputs=[prompt, width, height, steps, seed, randomize],
        outputs=[output, output_seed, gpu_seconds],
        api_name="generate",
    )

if __name__ == "__main__":
    demo.queue(max_size=32).launch()
