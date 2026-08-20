import os
import time

import gradio as gr
import spaces
import torch
from diffusers import AutoencoderKL, DiffusionPipeline, ZImageTransformer2DModel
from huggingface_hub import hf_hub_download, snapshot_download
from transformers import AutoTokenizer, Qwen3ForCausalLM

MODEL_REPO = "ibank31/stockforge-models"
PIPELINE_ID = "Tongyi-MAI/Z-Image-Turbo"
DTYPE = torch.bfloat16
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")


def _download_model(filename):
    print(f"[StockForge] Downloading {filename} from {MODEL_REPO}...")
    return hf_hub_download(repo_id=MODEL_REPO, filename=filename, revision="main", token=HF_TOKEN)


def _download_pipeline_configs():
    print("[StockForge] Downloading Z-Image configs/tokenizer...")
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
    print("[StockForge] Resolving model files...")
    z_image_path = _download_model("z_image_turbo_fp8_e4m3fn.safetensors")
    ae_path = _download_model("ae.safetensors")
    qwen_path = _download_model("qwen_3_4b_fp8_mixed.safetensors")
    pipeline_dir = _download_pipeline_configs()

    transformer_config = os.path.join(pipeline_dir, "transformer")
    vae_config = os.path.join(pipeline_dir, "vae")
    text_encoder_dir = os.path.join(pipeline_dir, "text_encoder")
    tokenizer_dir = os.path.join(pipeline_dir, "tokenizer")

    print("[StockForge] Loading Z-Image transformer...")
    transformer = ZImageTransformer2DModel.from_single_file(z_image_path, config=transformer_config, torch_dtype=DTYPE)

    print("[StockForge] Loading AE...")
    vae = AutoencoderKL.from_single_file(ae_path, config=vae_config, torch_dtype=DTYPE)

    print("[StockForge] Loading local Qwen3 text encoder...")
    text_encoder = Qwen3ForCausalLM.from_pretrained(
        text_encoder_dir,
        state_dict=None,
        torch_dtype=DTYPE,
        local_files_only=True,
    )

    # Replace the expected checkpoint with the StockForge safetensors file.
    # Diffusers/Transformers can consume a single-file checkpoint when passed explicitly.
    from safetensors.torch import load_file
    qwen_state = load_file(qwen_path, device="cpu")
    missing, unexpected = text_encoder.load_state_dict(qwen_state, strict=False)
    print(f"[StockForge] Qwen loaded. missing={len(missing)} unexpected={len(unexpected)}")

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, local_files_only=True)

    print("[StockForge] Loading pipeline components...")
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
    image = PIPE(prompt=str(prompt).strip(), height=int(height), width=int(width), num_inference_steps=int(steps), guidance_scale=0.0, generator=generator).images[0]
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
