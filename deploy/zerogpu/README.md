---
# Hugging Face Space configuration
sdk: gradio
sdk_version: 6.25.0
python_version: "3.12"
app_file: remote_api.py
hardware: zerogpu
---

# StockForge ZeroGPU Runtime

Remote GPU generation worker for the StockForge V2 production call graph.

## Role

The Space is deliberately separate from the StockForge control plane. The
browser and page.dev front door do not call this Space directly. The StockForge
control plane calls the stable Gradio `generate_remote` endpoint and records the
provider/event identity in its durable job flow.

Termux is not required for this worker to execute. It is an optional operator
surface only.

## Remote contract

The machine-to-machine endpoint is:

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

The request carries seven values:

```text
prompt
width
height
steps
seed
randomize_seed
stockforge_job_id
```

`stockforge_job_id` is the durable StockForge execution identity. The worker
uses it for idempotent caching of completed results.

## Current model path

The first runtime uses the Z-Image-Turbo pipeline configuration from
`Tongyi-MAI/Z-Image-Turbo`, with the StockForge FP8/AE files from
`ibank31/stockforge-models` where configured by the model manifest.

## Quota strategy

- ZeroGPU `large` is the intended free-first runtime.
- Default generation is 1024×1024 at 8 steps.
- Prompt validation and seed handling happen outside the GPU function where applicable.
- Model loading is kept outside the generation call when the runtime permits it.
- `torch.compile` is not required by the baseline runtime.

ZeroGPU quota is limited. The control plane must therefore retain durable job
state and may use another explicitly configured provider when the production
routing policy selects it.

## Production rule

This directory defines the remote GPU boundary. It is not a local executor
instruction and must not reintroduce a Termux dependency into the production
call graph.
