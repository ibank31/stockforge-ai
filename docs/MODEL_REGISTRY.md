# StockForge Model Registry

## Purpose

The model registry is the control-plane source of truth for models that StockForge may use in production generation. It stores **metadata and immutable model references, not model weights**.

## Storage boundary

```text
GitHub repository
  models/registry.json
        |
        | metadata + repository + revision
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

## Current production baseline

`sdxl-lightning` is the initial production baseline. The registry intentionally does not register a second large model until its exact quantized artifact, license, resource profile, and provider path have been validated end-to-end.

This prevents quota-burning experiments on free GPU providers.

## Routing rule

A model is eligible only when it is enabled, commercially eligible, supports the requested capability, and the worker/provider reports sufficient resources. Provider quota and health remain runtime constraints and are checked by the provider router before reservation/execution.
