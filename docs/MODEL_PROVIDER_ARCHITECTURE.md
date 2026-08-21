# Model Registry & Multi-Provider Architecture

## Purpose

StockForge separates **what model is used** from **where inference runs**.

The model is a managed asset with identity, revision, license/policy evidence, resource requirements, and compatibility metadata. A compute provider is an interchangeable execution backend.

## Target architecture

```text
                         STOCKFORGE CONTROL PLANE
                                  |
                    +-------------+-------------+
                    |                           |
              Model Registry              Job Queue
                    |                           |
                    +-------------+-------------+
                                  |
                           Provider Router
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
        Hugging Face          Kaggle             Provider N
        ZeroGPU/Space        GPU Worker            GPU/API
              |                   |                   |
              +-------------------+-------------------+
                                  |
                             Generation
                                  |
                           Artifact Registry
```

## Model Registry

Every production model should have a registry record containing at least:

- stable model ID
- source repository
- exact revision/commit when available
- backend/runtime
- weight format/precision
- model license
- code/backend license
- commercial-use assessment
- marketplace policy assessment
- expected disk footprint
- expected RAM/VRAM footprint
- supported resolutions and constraints
- provider compatibility
- integrity/hash information where available
- approval state: `candidate`, `approved`, `blocked`, `deprecated`

A model repository is not the same thing as a provider cache.

## Provider contract

A provider adapter should expose a common lifecycle:

```text
capabilities()
health()
submit(job)
status(execution_id)
result(execution_id)
cancel(execution_id)   # when supported
```

Provider-specific details remain behind the adapter.

## Capability handshake

Before scheduling a job, a provider must report measured runtime capabilities where possible:

```json
{
  "provider": "kaggle",
  "accelerator": "Tesla T4",
  "gpu_count": 2,
  "vram_gib": 14.56,
  "ram_gib": 30,
  "disk_free_gib": 42.1,
  "models": ["Qwen/Qwen-Image"],
  "backends": ["diffsynth"],
  "status": "ready"
}
```

Values such as free disk and available quota must be runtime observations, not hard-coded assumptions.

## Scheduling policy

The router should consider:

1. model compatibility
2. provider health
3. available quota/session budget
4. VRAM/RAM/disk requirements
5. expected model preparation time
6. generation latency
7. cost
8. queue depth
9. retry/failover policy
10. data/privacy constraints

The router should not select a provider merely because it is configured.

## Model delivery

The desired pattern is:

```text
Canonical model repository
        |
        +--> provider-local cache/access
        |         |
        |         +--> model preparation
        |         +--> inference
        |
        +--> another provider-local cache/access
```

A provider still needs the model weights locally or through a runtime-supported mounted/streamed mechanism during inference. The architecture therefore optimizes for **reuse and caching**, not an impossible zero-transfer model.

For ephemeral GPU providers, model preparation should be separated from GPU-intensive inference whenever possible. If a provider cannot persist a cache, the scheduler should account for the preparation cost before allocating accelerator time.

## Generation contract

A provider-neutral generation request should include:

- job ID
- model ID + revision
- prompt/negative prompt references
- seed
- width/height
- inference steps
- guidance/sampling parameters
- input artifact references
- output policy
- QA policy
- timeout/deadline

A generation result should include:

- execution ID
- provider ID
- runtime identity
- model ID + revision
- backend/version
- generation parameters
- timing breakdown
- resource observations
- warnings/errors
- output artifact references
- reproducibility/provenance information

## Current provider evidence

### Hugging Face ZeroGPU

Verified on the active development branch with a live Termux-triggered generation benchmark. This is a working provider adapter.

### Kaggle

GPU boot and CUDA tests are successful. Qwen-Image reached DiffSynth installation and model-download stages, but the current end-to-end experiment hit disk exhaustion before a generation PASS. Kaggle therefore remains a **verified GPU provider, not yet a verified Qwen-Image production provider**.

## Non-goals

- Do not hard-code one model into the core.
- Do not hard-code one provider into the pipeline.
- Do not put provider credentials in generation jobs.
- Do not treat free quota as guaranteed capacity.
- Do not claim model quality from infrastructure tests alone.
