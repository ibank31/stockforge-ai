import os
import time

import gradio as gr
import spaces
import torch
from diffusers import AutoencoderKL, DiffusionPipeline, ZImageTransformer2DModel
from huggingface_hub import hf_hub_download, snapshot_download
from safetensors.torch import load_file
from transformers import AutoTokenizer, Qwen3ForCausalLM

MODEL_REPO = "ibank31/stockforge-models"
PIPELINE_ID = "Tongyi-MAI/Z-Image-Turbo"
DTYPE = torch.bfloat16
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")


def _download_model(filename):
    return hf_hub_download(repo_id=MODEL_REPO, filename=filename, revision="main", token=HF_TOKEN)


def _download_pipeline_configs():
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


def _build_qwen(config_dir, checkpoint):
    config_path = os.path.join(config_dir, "config.json")
    config = Qwen3ForCausalLM.config_class.from_pretrained(config_path)
    model = Qwen3ForCausalLM._from_config(config, torch_dtype=DTYPE)
    state = load_file(checkpoint, device="cpu")
    result = model.load_state_dict(state, strict=False)
    print(f"[StockForge] Qwen checkpoint: missing={len(result.missing_keys)} unexpected={len(result.unexpected_keys)}")
    if result.missing_keys:
        print("[StockForge] Missing:", result.missing_keys[:8])
    if result.unexpected_keys:
        print("[StockForge] Unexpected:", result.unexpected_keys[:8])
    if len(result.missing_keys) > 20:
        raise RuntimeError("Qwen checkpoint is not structurally compatible with the official Z-Image Qwen3 config")
    return model


def _build_pipeline():
    print("[StockForge] Downloading StockForge models...")
    z_image_path = _download_model("z_image_turbo_fp8_e4m3fn.safetensors")
    ae_path = _download_model("ae.safetensors")
    qwen_path = _download_model("qwen_3_4b_fp8_mixed.safetensors")
    pipeline_dir = _download_pipeline_configs()

    transformer = ZImageTransformer2DModel.from_single_file(
        z_image_path,
        config=os.path.join(pipeline_dir, "transformer"),
        torch_dtype=DTYPE,
    )
    vae = AutoencoderKL.from_single_file(
        ae_path,
        config=os.path.join(pipeline_dir, "vae"),
        torch_dtype=DTYPE,
    )
    text_encoder = _build_qwen(os.path.join(pipeline_dir, "text_encoder"), qwen_path)
    tokenizer = AutoTokenizer.from_pretrained(
        os.path.join(pipeline_dir, "tokenizer"), local_files_only=True
    )

    pipe = DiffusionPipeline.from_pretrained(
        pipeline_dir,
        transformer=transformer,
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        torch_dtype=DTYPE,
        low_cpu_mem_usage=False,
    )
    pipe.to("cuda")
    return pipe


PIPE = _build_pipeline()
print("[StockForge] Pipeline ready")


def estimate_duration(prompt, width, height, steps, seed, randomize_seed):
    return min(55, max(20, 8 + int(steps) * 4))


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
    return image, seed, round(time.perf_counter() - started, 3)


def generate(prompt, width=1024, height=1024, steps=8, seed=0, randomize_seed=True):
    prompt = str(prompt or "").strip()
    if not prompt:
        raise gr.Error("Prompt is required.")
    if int(width) != 1024 or int(height) != 1024:
        raise gr.Error("Baseline benchmark is fixed at 1024x1024.")
    if not 4 <= int(steps) <= 12:
        raise gr.Error("Steps must be between 4 and 12 for the free-tier benchmark.")
    return generate_gpu(prompt, int(width), int(height), int(steps), int(seed), bool(randomize_seed))


with gr.Blocks(title="StockForge V5 ZeroGPU") as demo:
    gr.Markdown("# StockForge V5 · ZeroGPU\nQuota-aware Z-Image Turbo benchmark runtime.")
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

if __name__ == "__main__":
    demo.queue(max_size=32).launch()
