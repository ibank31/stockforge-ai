# Development Status

**Date:** 2026-08-21  
**Branch:** `feat/zerogpu-runtime`

## Current milestone

**v0.2 Multi-Provider Generation Runtime → Model Registry → Adobe Stock Readiness**

StockForge has a verified remote generation provider on Hugging Face ZeroGPU and a verified Kaggle GPU worker. The next architectural step is to separate model management from compute-provider execution and add provider routing/failover.

Generation success is still not the same thing as a marketplace-ready asset.

## Completed

### Core foundation

- CLI entry point
- `stockforge version`
- `stockforge init`
- `stockforge doctor`
- SQLite initialization
- Project creation and listing
- Project workspace layout
- Versioned project manifest
- Atomic manifest writes
- Project creation rollback handling
- Initial pytest coverage
- GitHub Actions CI

### Asset registry

- Persistent asset registry
- Asset UUID and project ownership
- Asset lifecycle status contract
- File path validation
- MIME type and file-size support
- SHA-256 checksum support
- Artifact lineage contract

### Persistent job queue

- Persistent job model
- Durable SQLite-backed queue
- Priority ordering
- Atomic worker claiming
- Attempt counting
- Bounded retries
- Job completion/failure/cancellation
- Job CLI create/list/claim/complete/fail/cancel commands

### Plugin and pipeline architecture

- Vendor-neutral plugin descriptor/API contract
- Plugin registry with deterministic lookup
- Capability-based plugin discovery
- Plugin API version validation
- Plugin trust-boundary documentation
- Versioned pipeline definition
- Deterministic sequential pipeline runner
- Pipeline capability validation
- Pipeline execution error boundary

### Provenance / lineage

- Versioned provenance record contract
- Explicit artifact lineage contract
- Durable SQLite provenance records
- Durable SQLite artifact lineage records
- Provenance/lineage round-trip and validation tests

### Hugging Face ZeroGPU — VERIFIED

- Space: `ibank31/stockforge-zerogpu`
- `zero-a10g` runtime
- Termux-triggered generation
- Public `/generate` endpoint
- Z-Image Turbo
- Qwen3 FP8 mixed text encoder path
- 1024×1024 / 8-step benchmark
- Successful image result
- 44.238 seconds measured GPU-function time in the recorded benchmark

### Kaggle GPU worker — VERIFIED INFRASTRUCTURE

- Public worker: `iqbalteguh/stockforge-worker-public`
- CUDA available
- 2 × Tesla T4 observed
- ~14.56 GiB VRAM per GPU observed
- PyTorch CUDA matmul test passed
- Remote worker job/result contract passed

### Kaggle Qwen-Image feasibility — NOT COMPLETE

Verified:

- DiffSynth-Studio installation from the official GitHub repository succeeds.
- Qwen-Image pipeline reaches model download/loading.
- DiffSynth's low-VRAM FP8 + disk-offload configuration is compatible with the intended test path.

Failure observed:

- `OSError: [Errno 28] No space left on device`

Therefore Kaggle **must not** be marked as a completed Qwen-Image generator yet.

## Research re-baseline — 2026-08-21

New evidence and decisions are recorded in:

- `docs/RESEARCH_GAPS_2026-08-21.md`
- `docs/MODEL_PROVIDER_ARCHITECTURE.md`

Key decisions:

1. Qwen-Image remains a **top candidate**, not a proven universal best model.
2. Hugging Face and Kaggle are **compute providers**, not the core model abstraction.
3. A **Model Registry** is required before scaling the provider count.
4. Provider capability, health, quota, VRAM, RAM, disk, and model compatibility must be measured and schedulable.
5. Model preparation/cache must be separated from GPU inference where provider capabilities permit.
6. Provider failure should trigger policy-driven retry/failover rather than changing the logical generation job.
7. Model licenses and marketplace rights must be recorded as evidence, not inferred from the word "open-source".

## Current gaps — highest priority

### P0 — Architecture

1. Model Registry contract and implementation.
2. Unified Generation Job/Result contract.
3. Provider Capability/Health contract.
4. Provider Router with quota/health/capability-aware selection.
5. Provider failover and idempotent execution.
6. Model cache/delivery abstraction.

### P1 — Runtime

7. Kaggle storage-aware preflight.
8. Kaggle Qwen-Image end-to-end generation test.
9. Runtime heartbeat/progress and structured failure diagnostics.
10. Model benchmark harness comparing candidate generators.

### P1 — Asset quality and marketplace readiness

11. JPEG + sRGB finalization.
12. Technical image QA.
13. Anatomy/hand/face/object consistency QA.
14. OCR/logo/trademark/watermark QA.
15. Perceptual deduplication and similarity/spam gate.
16. AI disclosure + people/property/release metadata.
17. Commercial-value scoring.
18. Stock title/keyword/category metadata engine.
19. Human review/submission package.

### P2 — Intelligence and feedback

20. Market opportunity engine.
21. Commercial concept planner.
22. Prompt compliance firewall.
23. Prompt/variation engine.
24. Controlled batch generation.
25. Portfolio diversity scoring.
26. Acceptance/sales feedback loop.

## Important current constraint

Do not optimize the system around unlimited free GPU availability. Kaggle documents notebook session limits and storage constraints; Hugging Face ZeroGPU also has daily quotas. Free compute is a pool of opportunistic capacity that the router must schedule around.

## Documentation source of truth

- Product vision/context: `docs/PROJECT_CONTINUATION.md`
- Current architecture: `docs/ARCHITECTURE.md`
- Model/provider design: `docs/MODEL_PROVIDER_ARCHITECTURE.md`
- Research and gap map: `docs/RESEARCH_GAPS_2026-08-21.md`
- Feature state: `docs/FEATURE_ROADMAP.md`
- Adobe readiness: `docs/ADOBE_STOCK_READINESS.md`
- Dated history: `docs/CHANGELOG.md`
- Core status: this file

## Completion rule

A feature is complete only when implementation, verification, and repository state are correct. External-provider claims require live evidence. A model is not considered production-ready until generation, quality, licensing/policy, resource footprint, and marketplace suitability have all been evaluated.
