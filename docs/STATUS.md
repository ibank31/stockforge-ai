# Development Status

**Date:** 2026-08-20  
**Branch:** `feat/zerogpu-runtime`

## Current milestone

**v0.2 Live ZeroGPU Generation Runtime → Adobe Stock Readiness Pipeline Specification**

StockForge has crossed the first major runtime milestone: a real Termux-triggered generation job now runs on Hugging Face ZeroGPU and returns an image using the Z-Image Turbo + Qwen3 FP8 mixed stack.

The generator is now considered a **working provider adapter**, not a submission-ready asset factory.

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
- Asset CLI create/list commands
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

### ZeroGPU generation runtime — LIVE

- Hugging Face Space: `ibank31/stockforge-zerogpu`
- ZeroGPU hardware: `zero-a10g`
- Python 3.12 runtime
- Gradio 6.25-compatible runtime
- Comfy-compatible FP8 loading path
- Z-Image Turbo integration
- Qwen3 FP8 mixed text encoder integration
- AE/VAE loading
- Public Gradio `/generate` endpoint
- Termux HTTP generation workflow
- Runtime health check
- End-to-end generation benchmark

### Verified live benchmark

- Date: 2026-08-20
- Resolution: 1024×1024 generation request
- Steps: 8
- Seed: `2157290427964887587`
- GPU-function seconds: `44.238`
- Result: successful image returned
- Concept: construction project planning meeting
- Assessment: commercially promising, **not yet Adobe submission-ready**

### Adobe Stock readiness documentation — DONE

Added:

- `docs/ADOBE_STOCK_READINESS.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/CHANGELOG.md`

These documents define the complete downstream asset-factory requirements and provide a permanent feature/completion ledger.

## Important architectural decisions

1. **Do not return to raw `Qwen3ForCausalLM.load_state_dict()` for the FP8 mixed checkpoint.**
2. **Keep ZeroGPU generation as a provider/adapter.** Adobe compliance belongs downstream in the core pipeline.
3. **Generation success does not equal submission readiness.** Every asset must pass technical, visual, compliance, metadata, deduplication, and human-approval gates.
4. **Do not optimize for raw volume.** Optimize for differentiated commercial utility.
5. **Every completed feature must be recorded in `docs/CHANGELOG.md` and reflected in `docs/FEATURE_ROADMAP.md`.**
6. **Do not mark a feature DONE without verification evidence.**

## Current gaps

### Highest priority

1. Adobe technical submission gate
2. JPEG + sRGB finalization
3. AI upscaling to submission resolution
4. Technical image QA
5. Anatomy/hand/face QA
6. OCR and logo/trademark/watermark QA
7. AI disclosure + people/property/release metadata
8. Provenance population for live generation
9. Perceptual deduplication
10. Commercial-value scoring
11. Stock title/keyword/category metadata engine
12. Human review/submission package

### Next strategic layer

13. Market opportunity engine
14. Commercial concept planner
15. Prompt compliance firewall
16. Prompt/variation engine
17. Controlled batch generation
18. Portfolio diversity scoring
19. Acceptance/sales feedback loop

## Next implementation sequence

### Phase A — Submission Gate

Build the deterministic finalization and hard-fail checks first:

- resolution
- JPEG export
- sRGB
- file size
- corruption/integrity
- basic sharpness/noise/color checks

### Phase B — AI Visual QA

Add:

- face detection
- hand/anatomy analysis
- object consistency
- OCR
- logo/trademark detection
- watermark detection
- persisted QA report

### Phase C — Commercial Selection

Add:

- buyer/use-case classification
- copy-space analysis
- commercial-value score
- perceptual deduplication
- portfolio diversity

### Phase D — Production Factory

Add:

- market intelligence
- concept planner
- prompt engine
- controlled variations
- batch queueing
- automatic best-of-batch selection
- metadata
- submission package
- human approval

## Documentation source of truth

- Product architecture and long-term vision: `docs/PROJECT_CONTINUATION.md`
- Feature state: `docs/FEATURE_ROADMAP.md`
- Adobe readiness specification: `docs/ADOBE_STOCK_READINESS.md`
- Dated implementation history: `docs/CHANGELOG.md`
- Core development status: this file

## Completion rule

A feature is complete only when implementation, verification, and repository state are all correct. A live benchmark or integration result must be recorded when the feature depends on an external runtime/provider.
