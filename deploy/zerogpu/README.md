---
# Hugging Face Space configuration
sdk: gradio
sdk_version: 6.25.0
python_version: "3.12"
app_file: app.py
hardware: zerogpu
---

# StockForge ZeroGPU Runtime

Experimental GPU execution layer for StockForge V5.

## Purpose

This Space is deliberately separate from the StockForge control plane. The
Android/Termux client remains responsible for prompt preparation and job
orchestration; this Space performs image generation only while a ZeroGPU
allocation is active.

## Current model path

The first benchmark uses the official Z-Image-Turbo pipeline configuration
from `Tongyi-MAI/Z-Image-Turbo`, while replacing the diffusion transformer and
VAE with the StockForge FP8/AE files from `ibank31/stockforge-models`.

The StockForge Qwen FP8 file is retained as the canonical model artifact, but
is not manually injected into Transformers in this first runtime revision.
This avoids an unsafe ad-hoc state-dict loader and lets us validate the GPU
execution path first.

## Quota strategy

- ZeroGPU `large` only. `xlarge` costs 2x quota.
- GPU decorator uses a per-request duration estimator.
- Default generation is 1024x1024 and 8 steps, matching the Turbo workflow.
- Prompt validation and seed generation happen outside the GPU function.
- No model download occurs inside the generation function.
- No `torch.compile`; ZeroGPU does not support it. AOT compilation can be
  added after the baseline benchmark succeeds.

## Benchmark goal

Measure actual GPU seconds per 1024x1024 / 8-step image. The first successful
run becomes the baseline for optimizing duration, AOT, and batching.

## Important

Do not merge this branch into `main` until the Space has produced one real
image and the measured GPU duration has been recorded.
