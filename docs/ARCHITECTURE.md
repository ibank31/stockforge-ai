# StockForge Active Architecture

**Updated:** 2026-09-15
**Branch:** `main`

StockForge adalah remote-first control plane untuk mengubah reference image dan market intent menjadi asset package yang dapat ditinjau. Browser `stockforge-ai.pages.dev` adalah front door dan operator surface. Termux bukan production executor. GPU generation dan production upscaling dikerjakan oleh Hugging Face ZeroGPU; Cloudflare menyimpan state, artifact, dan workflow orchestration.

## End-to-end production flow

```text
Page.dev upload reference
    ↓
Reference Intelligence
    ↓
Creative Opportunity / Asset Concept
    ↓
Anti-similarity + commercial preflight
    ↓
Durable Cloudflare Workflow
    ↓
HF ZeroGPU generation
    ↓
Raw artifact → R2
    ↓
HF ZeroGPU 4x Super Resolution
    ↓
Final JPEG/sRGB master → R2
    ↓
Exact-duplicate gate + technical QA
    ↓
Metadata / AI disclosure manifest
    ↓
Human visual / rights review
    ↓
READY_UPLOAD_ADOBE
    ↓
Manual Adobe Stock submission
```

## Control-plane boundaries

### Page.dev / Cloudflare

Pages Functions own the browser API, reference upload, Workers AI reference analysis, creative planning, D1 job state, R2 artifact storage, and trigger of the durable pipeline Worker through a service binding.

Cloudflare Workflows own long-running orchestration so the browser does not need to remain open while generation or upscale is running. The page only polls durable state for display.

### HF ZeroGPU

`ibank31/stockforge-zerogpu` is the production GPU worker. It exposes two machine endpoints:

- `generate_remote` — Z-Image Turbo generation.
- `upscale_remote` — 4x RealESRGAN super-resolution.

Both remain behind the same Gradio queue and are invoked remotely by the Cloudflare pipeline. The free lane is quota-limited, not unlimited.

### Kaggle

Kaggle remains an R&D / benchmark / diagnostic provider only. It is not a production commercial Adobe Stock executor because current Kaggle Terms restrict the Services to internal, personal, and non-commercial use. Do not route a revenue-generating asset through the Kaggle finalizer.

### Termux

Termux is optional for maintenance, diagnostics, Git operations, and emergency recovery. A normal production run must work without Termux and without keeping an Android process alive.

## Storage

- D1: references, workflow state, plans, generation jobs, artifact checksums, and review state.
- R2: uploaded references, raw generated artifacts, final masters, and submission manifests.
- Hugging Face model repository `ibank31/stockforge-models`: canonical model source.

## Asset and quality gates

`AssetSpec` remains the provider-neutral contract for buyer job, product kind, delivery format, layout, background/isolation policy, text/branding policy, originality levers, quality gates, and model-neutral capabilities.

Technical QA checks file integrity, dimensions, megapixels, RGB/sRGB, decodability, and format-specific constraints. The production raster lane targets a 16 MP final master after 4x upscale. Exact duplicate detection uses a SHA-256 artifact gate. Semantic similarity to the source reference remains a human-review responsibility because the production system must not pretend a cheap heuristic is equivalent to expert visual judgment.

The system never auto-approves an asset for marketplace submission. AI-generated content must carry the marketplace-required disclosure and the human reviewer remains responsible for visual quality, IP/trademark risk, releases where applicable, metadata accuracy, and final submission.

## Learning loop

A reviewed result can be recorded in the append-only evaluation ledger. Learning summaries can inform future concept selection and provider policy, but may not silently change production prompts or route jobs without an explicit tested rule.

## Current implementation map

- `frontend/index.html` — Page.dev operator UI.
- `frontend/functions/api/[[path]].js` — Cloudflare Pages API/control-plane fallback routes.
- `frontend/functions/api/references/[referenceId]/generate.js` — durable pipeline trigger.
- `frontend/functions/api/jobs/[jobId].js` — durable job state endpoint.
- `frontend/functions/api/jobs/[jobId]/qa.js` — technical QA gate.
- `frontend/functions/api/jobs/[jobId]/approve.js` — explicit human approval gate.
- `frontend/functions/api/jobs/[jobId]/release.js` — Adobe-ready manifest/package release.
- `frontend/migrations/0001_stockforge.sql` — D1 schema.
- `frontend/wrangler.toml` — Pages bindings for D1, R2, Workers AI, and pipeline service.
- `deploy/pipeline-worker/src/index.js` — durable generation → upscale → QA orchestration.
- `deploy/pipeline-worker/wrangler.toml` — pipeline Worker + Workflow binding.
- `deploy/zerogpu/app.py` — GPU generation runtime.
- `deploy/zerogpu/remote_api.py` — machine generation and upscale endpoints.
- `deploy/zerogpu/upscale.py` — 4x RealESRGAN finalizer.
- `src/stockforge/remote_gradio.py` — reusable remote Gradio client for legacy/CLI execution paths.

## References

- Current state: [`STATUS.md`](STATUS.md)
- Feature state: [`FEATURE_ROADMAP.md`](FEATURE_ROADMAP.md)
- Marketplace standard: [`MARKETPLACE_UPLOAD_READINESS_STANDARD.md`](MARKETPLACE_UPLOAD_READINESS_STANDARD.md)
- Provider backend contract: [`provider-backends.md`](provider-backends.md)
