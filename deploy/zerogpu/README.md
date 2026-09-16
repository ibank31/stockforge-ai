---
# Hugging Face Space configuration
sdk: gradio
sdk_version: 6.25.0
python_version: "3.12"
app_file: app.py
hardware: zerogpu
---

# StockForge ZeroGPU Runtime

Remote GPU executor for the StockForge V2 production call graph.

## Production boundary

```text
page.dev
   ↓
Cloudflare Pages Functions / Workflow
   ↓
HF ZeroGPU
   ├── generate_remote
   └── upscale_remote
```

The browser never calls this Space directly. Termux is not required for production execution.

## Remote generation contract

```text
POST /gradio_api/call/generate_remote
        ↓
{event_id}
        ↓
GET /gradio_api/call/generate_remote/{event_id}
        ↓
SSE completion
        ↓
Gradio FileData output
```

Arguments:

```text
prompt
width
height
steps
seed
randomize_seed
stockforge_job_id
```

## Remote upscale contract

```text
POST /gradio_api/call/upscale_remote
        ↓
{event_id}
        ↓
GET /gradio_api/call/upscale_remote/{event_id}
        ↓
SSE completion
        ↓
4x RealESRGAN image + dimensions
```

Arguments:

```text
source_url
stockforge_job_id
scale=4
```

The finalizer uses `RealESRGAN_x4plus` and emits RGB raster output. The production target is a 16 MP-or-greater final master for the current raster lane.

## Current generation model

The first production runtime uses the Z-Image-Turbo pipeline configuration from `Tongyi-MAI/Z-Image-Turbo`, with StockForge model assets from `ibank31/stockforge-models` where configured by the model manifest.

## Quota strategy

- ZeroGPU is the free-first production compute lane.
- Generation and upscale share the same Space and therefore the same account quota.
- Default generation is 1024×1024 at 8 steps.
- The control plane tracks job state outside the Space, so closing the browser does not cancel the workflow.

## Commercial boundary

The worker may process commercial output only with models whose licenses and marketplace policy records have been validated by StockForge. Kaggle is not part of this production path.
