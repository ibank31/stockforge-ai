# StockForge AI — Research Findings & Gap Map

**Date:** 2026-08-21  
**Purpose:** Re-baseline the project from verified evidence after the first live Hugging Face runtime and Kaggle Qwen-Image experiments.

## 1. Product objective, stated precisely

StockForge AI is a **free-first, Termux-first AI stock asset factory**. The goal is not simply to generate images. The machine should turn commercial opportunity into controlled, auditable stock assets:

`market signal → concept → compliant prompt → generation → technical QA → visual/commercial QA → enhancement → deduplication → provenance → metadata → human review → marketplace submission → acceptance/sales feedback`

The first production target remains **commercial stock photography**, with Adobe Stock as the first concrete marketplace target. The system must remain marketplace-neutral at its core.

## 2. Critical architectural clarification: model vs compute provider

A model and a GPU provider are separate concerns.

- **Model registry/storage:** canonical model identifiers, revisions, license/policy records, hashes, compatibility requirements, and optional cached artifacts.
- **Compute providers:** Hugging Face Spaces/ZeroGPU, Kaggle, local GPU, or future providers. Providers are interchangeable execution backends.
- **Orchestrator:** selects a provider based on capability, availability, quota/cost, model compatibility, expected latency, and job policy.
- **Worker:** prepares or accesses the required model locally, loads it into accelerator memory, performs inference, writes artifacts, and returns structured results.

A remote GPU cannot infer from weights that exist only in a remote model repository without obtaining the required model data. Therefore the practical architecture is **central model registry + provider-local cache/access**, not "GPU only with zero model transfer".

## 3. Verified runtime evidence

### Hugging Face ZeroGPU

The repository's `feat/zerogpu-runtime` branch records a live Termux-triggered generation benchmark on `ibank31/stockforge-zerogpu` using `zero-a10g`, with successful 1024×1024 generation in 8 steps and measured GPU-function time of 44.238 seconds. This establishes that the provider-adapter architecture works for at least one real remote runtime.

### Kaggle

The Kaggle worker was verified independently:

- CUDA available.
- 2 × Tesla T4 reported.
- ~14.56 GiB VRAM per T4.
- PyTorch CUDA matmul test succeeded.
- DiffSynth-Studio installed successfully from its GitHub repository in the later Qwen-Image test.
- Qwen-Image pipeline initialization reached the model-download stage.
- A manual run ultimately failed with `OSError: [Errno 28] No space left on device`.

This means **Kaggle GPU compatibility is demonstrated, but Qwen-Image end-to-end generation is not yet proven on Kaggle**.

Do not document Kaggle as a completed Qwen-Image generator until an actual image-generation PASS is recorded.

## 4. Qwen-Image findings

The current Qwen/Qwen-Image model card reports:

- Apache-2.0 license.
- 20B parameters.
- ~57.7 GB repository size at the time of this research snapshot.
- Official Diffusers support.
- Kaggle and other notebook usage references.

DiffSynth-Studio's current Qwen-Image documentation states that its VRAM-managed path can run with a minimum of 8 GB VRAM and provides a disk-offload + FP8 configuration. The same project's developer documentation notes that an unmanaged 20B DiT inference can require about 40 GB VRAM.

**Conclusion:** Qwen-Image is a technically credible candidate for low-VRAM remote workers, but the project has not established that it is the single "best" stock-photography model. Model selection must be benchmark-driven against StockForge's own commercial criteria.

Required benchmark dimensions:

1. photorealism
2. prompt adherence
3. anatomy and object consistency
4. lighting/material realism
5. text/logo contamination risk
6. commercial usefulness
7. acceptance-risk signals
8. generation latency/cost
9. license and output rights
10. reproducibility

## 5. Kaggle storage lesson

Kaggle's current notebook documentation lists 20 GB of auto-saved `/kaggle/working` storage plus additional scratch disk. The Qwen-Image run downloaded multiple large model components and used DiffSynth disk offload. The observed `No space left on device` failure demonstrates that **model delivery + disk-offload storage is a first-class provider constraint**.

The solution should not be to blindly increase retries. The provider contract must expose:

- free disk
- model footprint estimate
- cache location
- scratch/working distinction
- VRAM
- RAM
- accelerator type/count
- provider session/time/quota limits
- model availability/cache state

Workers should fail fast when storage requirements cannot be satisfied.

## 6. Hugging Face findings

Hugging Face currently documents ZeroGPU as shared dynamic infrastructure with daily GPU quotas. It also documents model/dataset repository volumes and persistent storage buckets for Spaces. ZeroGPU therefore remains useful as a compute provider, but it is not a universal free unlimited GPU service.

The architecture should treat HF quota as a schedulable resource, not as an assumption of availability.

## 7. Adobe Stock requirements that materially change the architecture

Adobe's current generative-AI guidance (updated June 2026) confirms:

- AI-generated content is accepted when requirements are met.
- Contributors must have the necessary rights to submit the generated content for commercial licensing.
- AI-generated content must be labeled as such.
- Fictional people/property require the appropriate fictional checkbox; identifiable real people/property can require releases.
- Prompts, titles, and keywords must not use prohibited artist/person/character/copyrighted-work/government-agency/third-party-IP references.
- Content must be technically and visually sound, including accurate anatomy and no unintended anomalies.
- Similar-asset spam is restricted; Adobe's current FAQ says a maximum of three iterations of similar assets may be submitted.

Therefore compliance cannot be a final manual afterthought. StockForge needs a **prompt firewall, asset QA, deduplication, metadata policy engine, and submission gate**.

## 8. Gaps discovered during development

### A. Provider orchestration gap — HIGH

The core has provider-neutral contracts, but the project still needs a real scheduler/router that can select among multiple compute providers and retry/fail over without changing the generation job contract.

Needed:
- provider capability registry
- provider health/status
- quota/availability state
- model compatibility matrix
- cost/latency policy
- queue routing
- idempotent submission
- retry/failover rules
- result normalization

### B. Model registry/cache gap — HIGH

Model identity is not yet a first-class operational object. We need:
- model ID + revision
- source repository
- license/policy record
- expected disk footprint
- expected VRAM/RAM footprint
- runtime/backend compatibility
- provider availability
- cache key
- integrity/hash
- approved/rejected status

### C. Worker capability/handshake gap — HIGH

A worker must advertise what it can actually run before receiving a job.

Example capability record:

```json
{
  "provider": "kaggle",
  "gpu": "Tesla T4",
  "vram_gib": 14.56,
  "models": ["Qwen/Qwen-Image"],
  "backends": ["diffsynth"],
  "disk_free_gib": 42.1,
  "status": "ready"
}
```

The values must be measured at runtime, never assumed.

### D. Model delivery/cache gap — HIGH

The current Qwen worker downloads model data during a GPU session. This wastes accelerator session time and creates disk failures. Model preparation should be separated from inference where provider capabilities permit it.

### E. Generation contract gap — HIGH

A single provider-neutral generation request/response schema is needed. It should include model revision, dimensions, steps, seed, prompt data, input artifacts, provider execution identity, timings, warnings, and output artifact references.

### F. QA gap — HIGH

The existing QA direction is good but not yet a complete enforceable gate. The production gate must reject technical and visual failures before marketplace packaging.

### G. Commercial-value gap — HIGH

The system can eventually generate images, but generation alone does not answer whether an asset is worth submitting. We need demand/use-case scoring, copy-space detection, diversity, saturation signals, and portfolio coverage.

### H. Compliance gap — HIGH

License evidence and marketplace policy need to be attached to model/provider records and generation provenance. "Open source" is not a sufficient compliance assertion.

### I. Submission automation gap — MEDIUM

The system still needs marketplace-specific export packages and a human approval boundary. Automatic submission should not be treated as the immediate MVP goal.

### J. Feedback-loop gap — MEDIUM

Acceptance/rejection/sales data is not yet feeding back into concept and model selection.

## 9. Decisions from this research

1. **Keep Qwen-Image as a top candidate, not a permanent winner.** Benchmark it against alternatives.
2. **Keep Hugging Face and Kaggle as compute-provider adapters.** Neither should own the core generation contract.
3. **Introduce a Model Registry before adding many more providers.**
4. **Introduce Provider Capability + Health + Quota state before automatic routing.**
5. **Separate model preparation/cache from inference whenever possible.**
6. **Treat provider disk, VRAM, RAM, network, and quota as first-class scheduling constraints.**
7. **Do not claim Kaggle Qwen-Image generation is complete yet.** It has only reached model loading/download and encountered storage exhaustion.
8. **Do not call Qwen-Image "best" without an internal benchmark.**
9. **Keep Adobe compliance downstream and marketplace-specific while storing universal provenance in core.**
10. **Do not optimize for raw generation volume.** Adobe's current similarity/spam rules make controlled diversity essential.

## 10. Immediate implementation order

1. Model Registry contract.
2. Provider Capability/Health contract.
3. Unified Generation Job/Result contract.
4. Provider router with failover policy.
5. Model cache/delivery abstraction.
6. Kaggle worker storage-aware preflight.
7. Kaggle Qwen-Image end-to-end test only after preflight passes.
8. Internal model benchmark harness.
9. Technical/visual QA gates.
10. Commercial-value scoring.
11. Adobe metadata/compliance package.
12. Human approval and submission package.

## 11. Evidence sources

- Qwen-Image model card: https://huggingface.co/Qwen/Qwen-Image
- Qwen-Image files/size: https://huggingface.co/Qwen/Qwen-Image/tree/main
- DiffSynth Qwen-Image guide: https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/Qwen-Image.md
- DiffSynth low-VRAM example: https://github.com/modelscope/DiffSynth-Studio/blob/main/examples/qwen_image/model_inference_low_vram/Qwen-Image.py
- DiffSynth VRAM management: https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Developer_Guide/Enabling_VRAM_management.md
- Kaggle notebook resources: https://www.kaggle.com/docs/notebooks
- Hugging Face ZeroGPU: https://huggingface.co/docs/hub/main/spaces-zerogpu
- Hugging Face Space storage: https://huggingface.co/docs/hub/en/spaces-storage
- Adobe Stock generative AI guidelines: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html
- Adobe Stock generative AI FAQ: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/adobe-stock-generative-ai-faq.html
- Adobe Stock AI photo guidelines: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-photo-submission-guidelines.html
