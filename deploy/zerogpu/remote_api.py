"""Machine-to-machine API layer for the StockForge ZeroGPU worker.

The normal UI remains in app.py. This module adds a stable `generate_remote`
endpoint with the StockForge request shape so the core can call the Space or a
compatible Gradio worker without knowing the model implementation.
"""

from __future__ import annotations

from typing import Any

import gradio as gr

from app import demo, generate

_CACHE: dict[str, tuple[Any, int, float]] = {}


def generate_remote(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 8,
    seed: int = 0,
    randomize_seed: bool = True,
    stockforge_job_id: str = "",
):
    """Generate an image and reuse a completed result for the same job ID."""
    job_id = str(stockforge_job_id or "").strip()
    if not job_id:
        raise gr.Error("stockforge_job_id is required")
    if job_id in _CACHE:
        return _CACHE[job_id]
    result = generate(prompt, width, height, steps, seed, randomize_seed)
    _CACHE[job_id] = result
    return result


with demo:
    remote_prompt = gr.Textbox(visible=False)
    remote_width = gr.Number(value=1024, visible=False)
    remote_height = gr.Number(value=1024, visible=False)
    remote_steps = gr.Number(value=8, visible=False)
    remote_seed = gr.Number(value=0, visible=False)
    remote_randomize = gr.Checkbox(value=True, visible=False)
    remote_job_id = gr.Textbox(visible=False)
    remote_button = gr.Button(visible=False)
    remote_output = gr.Image(visible=False, type="pil")
    remote_output_seed = gr.Number(visible=False)
    remote_gpu_seconds = gr.Number(visible=False)
    remote_button.click(
        generate_remote,
        [remote_prompt, remote_width, remote_height, remote_steps, remote_seed, remote_randomize, remote_job_id],
        [remote_output, remote_output_seed, remote_gpu_seconds],
        api_name="generate_remote",
    )


if __name__ == "__main__":
    demo.queue(max_size=32).launch()
