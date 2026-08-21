# StockForge Model Registry

## Purpose

The model registry is the control-plane source of truth for models that StockForge may use in generation. It stores **metadata and immutable model references, not model weights**.

## Storage boundary

```text
GitHub repository
  models/registry.json
        |
        | metadata + repository + revision + integrity data
        v
Hugging Face Hub
  model weights
        |
        | ephemeral download/cache
        v
GPU worker
  RAM / VRAM / temporary disk
        |
        v
  generation
```

Model weights must not be committed to Git, copied into the Android project, or treated as permanent files on an ephemeral GPU worker.

## Required model metadata

Each registered model declares:

- stable model id and version
- generation kind
- commercial-use eligibility
- capabilities
- minimum VRAM/RAM/disk requirements
- remote artifact repository and revision
- allowed production providers
- deterministic priority
- licensing/runtime validation notes

## Current candidates

### SDXL-Lightning 4-step

`sdxl-lightning` remains the primary **research-selected** constrained-GPU candidate. It is not production-enabled in the registry yet. The current Hugging Face model card identifies the repository as `openrail++` but also states that the released models are for research purposes only. Therefore StockForge must not treat it as commercially cleared for Adobe Stock production until that rights question is resolved.

### Qwen-Image 20B

`qwen-image` is registered as a specialist candidate. The official Hugging Face repository identifies it as Apache 2.0, but the unquantized model is 20B/BF16 and too large for the target free-worker budget. The Nunchaku/SVDQuant INT4 artifact and its exact provider path must be validated before enabling it.

## Routing rule

A model is eligible only when it is enabled, commercially eligible, supports the requested capability, and the worker/provider reports sufficient resources. Provider quota and health remain runtime constraints and are checked before GPU reservation/execution.

A licensing uncertainty is a hard stop, not a warning. Free GPU time is scarce enough without spending it generating assets we later discover cannot be sold.
