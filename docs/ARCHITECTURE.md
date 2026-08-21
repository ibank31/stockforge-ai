# StockForge AI Architecture

StockForge is a lightweight orchestration core with replaceable plugins and interchangeable compute providers.

```text
                         Termux / Control Plane
                                  |
              +-------------------+-------------------+
              |                   |                   |
        Project/Config        Model Registry       Job Queue
        Database/Artifacts    License/Policy       Persistent Jobs
              |                   |                   |
              +-------------------+-------------------+
                                  |
                           Provider Router
                                  |
             +--------------------+--------------------+
             |                    |                    |
             v                    v                    v
       HF ZeroGPU            Kaggle GPU          Other Provider
          Adapter              Adapter               Adapter
             |                    |                    |
             +--------------------+--------------------+
                                  |
                         Generator Plugin
                                  |
                       Artifact + Provenance
                                  |
              +-------------------+-------------------+
              |                   |                   |
             QA              Enhancement          Metadata
              |                   |                   |
              +-------------------+-------------------+
                                  |
                         Compliance Gate
                                  |
                          Submission Package
                                  |
                           Human Approval
```

## Core rule

The core must not import vendor-specific AI engines directly. External engines such as ComfyUI, Diffusers, and DiffSynth-Studio are integrated through adapters/plugins.

## Model vs provider

A **model** is a managed resource with a stable ID, revision, license/policy evidence, resource requirements, and compatibility metadata.

A **provider** is a compute backend. It may be Hugging Face ZeroGPU, Kaggle, a local GPU, or another API/service. Providers are interchangeable as long as they satisfy the provider contract.

A provider still needs access to model weights during inference. The system therefore uses a canonical model registry plus provider-local cache/access rather than assuming that a remote GPU can execute a model that never reaches the provider runtime.

## Control plane

The Termux device is the control plane. It owns job creation, routing policy, persistence, provenance, and provider orchestration. Heavy inference runs on workers where resources permit.

## Scheduling constraints

Provider selection must consider measured:

- accelerator type/count
- VRAM
- RAM
- disk availability
- model compatibility
- backend/runtime compatibility
- quota/session limits
- queue depth
- preparation/download cost
- latency and cost
- privacy/data constraints

Free quota is a capacity signal, not a guaranteed service level.

## Provider failure isolation

A provider failure must not invalidate the logical generation job. The router may retry or fail over to another compatible provider according to policy. Provider-specific execution IDs and errors belong in execution records, not in the model-independent job contract.

## Current verified runtime state

- Hugging Face ZeroGPU: live generation provider verified on `feat/zerogpu-runtime`.
- Kaggle: GPU/CUDA worker verified; Qwen-Image installation and model-download stages verified; end-to-end Qwen-Image generation remains unverified because the experiment exhausted runtime disk.

See `docs/MODEL_PROVIDER_ARCHITECTURE.md` and `docs/RESEARCH_GAPS_2026-08-21.md` for the current provider/model design and evidence.
