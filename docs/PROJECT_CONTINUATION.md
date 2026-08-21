# StockForge AI — Project Continuation Brief

**Last re-baselined:** 2026-08-21  
**Active branch:** `feat/zerogpu-runtime`

This is the canonical handoff document. Future sessions must inspect actual repository/provider state before assuming any milestone is complete.

## 1. What we are building

StockForge AI is a **free-first, Termux-first, plugin-based AI stock asset factory**. The first production target is high-quality commercial stock photography for marketplaces such as Adobe Stock.

It is not merely an image generator. The intended closed loop is:

`market signal → opportunity → concept → compliant prompt → generation → technical/visual QA → enhancement → deduplication → provenance/compliance → metadata → human review → marketplace → acceptance/sales feedback`

The long-term advantage is controlled commercial production and learning, not raw image volume.

## 2. Non-negotiable principles

- Commercial usefulness over novelty.
- Quality and differentiation over volume.
- Free/open-source first, but never assume free means unlimited or commercially unrestricted.
- Vendor-neutral core.
- Model and compute-provider independence.
- Full provenance and reproducibility where technically possible.
- Marketplace compliance as a first-class gate.
- Termux/Android as the control plane.
- Heavy inference delegated to interchangeable workers.
- Human approval remains the final marketplace submission gate.
- No feature is DONE without implementation + verification + correct repository state.

## 3. Current architecture

```text
Termux / Control Plane
        |
        +-- Project + Config + SQLite
        +-- Model Registry
        +-- Persistent Job Queue
        +-- Provider Router
        +-- Pipeline Runner
        |
        +--> Hugging Face ZeroGPU adapter
        +--> Kaggle GPU adapter
        +--> future provider adapters
                    |
                    v
              Model preparation/cache
                    |
                 GPU inference
                    |
              Artifact + Provenance
                    |
          QA → Enhancement → Dedup
                    |
          Compliance → Metadata
                    |
              Human Approval
                    |
                Marketplace
```

**Model** and **provider** are separate abstractions. A model has identity, revision, license/policy evidence, resource requirements, and compatibility metadata. A provider supplies compute and execution.

A provider still needs model weights locally or through a runtime-supported mounted/streamed mechanism during inference. The practical goal is therefore **central model registry + provider-local cache/access**, not an impossible zero-transfer model.

## 4. Verified runtime state

### Hugging Face ZeroGPU — VERIFIED

Space: `ibank31/stockforge-zerogpu`

Recorded live benchmark:

- hardware: `zero-a10g`
- request: 1024×1024
- steps: 8
- successful image returned
- Z-Image Turbo + Qwen3 FP8 mixed text encoder path
- measured GPU-function time: 44.238 seconds
- Termux-triggered HTTP generation succeeded

This is a working remote generation provider adapter.

### Kaggle GPU — VERIFIED INFRASTRUCTURE

Worker: `iqbalteguh/stockforge-worker-public`

Verified:

- CUDA available
- 2 × Tesla T4
- ~14.56 GiB VRAM per GPU
- PyTorch CUDA matmul succeeded
- structured worker result succeeded

### Kaggle Qwen-Image — NOT YET VERIFIED END-TO-END

The feasibility worker reached:

- official DiffSynth-Studio installation
- Qwen-Image pipeline loading
- model download from ModelScope
- FP8 + disk-offload configuration

The experiment then failed with:

`OSError: [Errno 28] No space left on device`

Therefore the repository must **not** claim that Kaggle currently generates Qwen-Image successfully. The next test must be storage-aware and must produce an actual image before the provider is marked complete.

## 5. Model strategy

Qwen-Image is currently a **top candidate**, not a permanently declared best model.

Current evidence:

- Qwen/Qwen-Image is listed as Apache-2.0 on Hugging Face.
- The model is 20B parameters and the current Hub repository is roughly 57.7 GB.
- Official DiffSynth documentation provides a VRAM-managed path and a low-VRAM FP8/disk-offload example.
- DiffSynth documents approximately 40 GB VRAM for an unmanaged 20B DiT inference, while its managed Qwen-Image path is documented as runnable from 8 GB VRAM.

StockForge still needs an internal benchmark before declaring any model "best". The benchmark must include photorealism, prompt adherence, anatomy/object consistency, artifact rate, commercial usefulness, latency, resource footprint, licensing/policy, and reproducibility.

## 6. Model registry requirements

Every approved model should record:

- model ID
- exact revision
- source repository
- backend/runtime
- precision/weight format
- code license
- weight license
- commercial-use assessment
- marketplace-policy assessment
- expected disk/RAM/VRAM footprint
- supported resolutions
- provider compatibility
- integrity/hash data where available
- approval/deprecation state

Model storage is separate from provider cache.

## 7. Provider requirements

Every provider adapter should eventually support:

```text
capabilities()
health()
submit(job)
status(execution_id)
result(execution_id)
cancel(execution_id)  # if provider supports it
```

Runtime capability data should include accelerator, VRAM, RAM, disk, model/backend compatibility, queue state, and quota/session information.

The router should select providers using measured capability and policy rather than a hard-coded preference.

Provider failure should be isolated from the logical job so compatible jobs can fail over without changing their model-independent contract.

## 8. Stock marketplace reality

Adobe Stock currently accepts generative AI content when it meets its requirements. Current Adobe guidance requires appropriate submission rights, generative-AI labeling, accurate asset type/metadata, releases where applicable, and technically/visually sound content. Adobe also restricts prohibited prompt/title/keyword references and warns against excessive similar submissions.

Therefore StockForge must implement:

- prompt/IP compliance firewall
- technical QA
- anatomy/face/hand/object checks
- OCR/logo/trademark/watermark detection
- similarity/deduplication gate
- commercial-value scoring
- AI disclosure and release metadata
- marketplace-specific submission packaging
- human approval

## 9. Major gaps discovered

### P0 architecture

1. Model Registry implementation.
2. Unified Generation Job/Result contract.
3. Provider capability/health/quota contract.
4. Provider router.
5. Failover/idempotency.
6. Model cache/delivery abstraction.

### P1 runtime

7. Kaggle storage-aware preflight.
8. Kaggle Qwen-Image end-to-end test.
9. Worker heartbeat/progress diagnostics.
10. Internal model benchmark harness.

### P1 asset factory

11. JPEG + sRGB finalization.
12. Technical QA.
13. Visual/anatomy QA.
14. OCR/logo/trademark/watermark QA.
15. Perceptual deduplication.
16. Commercial-value scoring.
17. Metadata engine.
18. Human review/submission package.

### P2 intelligence

19. Market opportunity engine.
20. Commercial concept planner.
21. Prompt/variation engine.
22. Controlled batch generation.
23. Portfolio diversity scoring.
24. Acceptance/sales feedback loop.

## 10. Immediate implementation sequence

1. Implement Model Registry contract.
2. Implement Provider Capability/Health contract.
3. Implement unified Generation Job/Result contract.
4. Implement Provider Router and failover policy.
5. Implement model cache/delivery abstraction.
6. Add Kaggle storage preflight and fail-fast diagnostics.
7. Re-test Qwen-Image on Kaggle only after preflight passes.
8. Build internal model benchmark harness.
9. Build technical/visual QA gates.
10. Build commercial-value and deduplication gates.
11. Build Adobe metadata/compliance package.
12. Build human approval/submission package.

## 11. Repository documentation map

- `docs/ARCHITECTURE.md` — current system architecture.
- `docs/MODEL_PROVIDER_ARCHITECTURE.md` — model registry, provider, routing, and cache design.
- `docs/RESEARCH_GAPS_2026-08-21.md` — evidence-backed research and gap map.
- `docs/STATUS.md` — current implementation state and priorities.
- `docs/FEATURE_ROADMAP.md` — feature ledger.
- `docs/ADOBE_STOCK_READINESS.md` — marketplace requirements.
- `docs/CHANGELOG.md` — dated implementation history.

## 12. Evidence sources

- Qwen-Image: https://huggingface.co/Qwen/Qwen-Image
- DiffSynth Qwen-Image guide: https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/Qwen-Image.md
- DiffSynth low-VRAM example: https://github.com/modelscope/DiffSynth-Studio/blob/main/examples/qwen_image/model_inference_low_vram/Qwen-Image.py
- DiffSynth VRAM management: https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Developer_Guide/Enabling_VRAM_management.md
- Kaggle notebook resources: https://www.kaggle.com/docs/notebooks
- Hugging Face ZeroGPU: https://huggingface.co/docs/hub/main/spaces-zerogpu
- Hugging Face Space storage: https://huggingface.co/docs/hub/en/spaces-storage
- Adobe Stock generative AI guidelines: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html
- Adobe Stock generative AI FAQ: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/adobe-stock-generative-ai-faq.html

## Product definition

> StockForge AI is a free-first, Termux-first, plugin-based AI stock asset factory. Its first and most important output is high-quality commercial stock photography. It transforms market opportunities into generation jobs, uses interchangeable compute providers, automatically rejects technical/commercial failures, preserves provenance, creates compliant metadata, prevents duplicate/spam submissions, and produces human-reviewable marketplace packages. Its long-term advantage is the closed loop from market demand to asset performance and future production decisions.
