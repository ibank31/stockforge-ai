# StockForge Remote-First Canonical Workflow

**Status:** Canonical operating instruction for GPT, the browser UI, Termux operators, and StockForge workers.

> This document supersedes the old Termux-executor workflow. Termux is an optional operator/client surface. Production generation is remote-first and must not depend on a local GPU, local ComfyUI, or a long-running Termux process.

## 1. Roles and boundaries

```text
Cloudflare Pages / browser
        ↓
Pages Function /api/* proxy
        ↓
StockForge V2 control plane
        ↓
Durable job queue
        ↓
Remote provider router
        ├── Hugging Face ZeroGPU (default generation provider)
        └── Kaggle integrations (secondary/finalization path where explicitly selected)
```

The browser talks only to the StockForge web API. The Pages function provides the same-origin `/api/*` boundary. Provider endpoints, SQLite, runtime files, credentials, and internal worker state are never exposed directly to the browser.

GPT makes the commercial and creative decision. The control plane records it. Remote workers perform GPU execution. Adobe upload remains manual.

## 2. Canonical lifecycle

```text
reference / market evidence
→ reference intelligence
→ creative opportunity
→ anti-similarity plan
→ new concept
→ model-specific prompt
→ durable queued job
→ remote generation
→ artifact ingestion
→ post-generation similarity gate
→ technical QA
→ human review
→ release package
→ READY_UPLOAD_ADOBE
→ manual Adobe upload
```

The system must preserve provenance, job identity, provider identity, request parameters, output lineage, and human decisions at every boundary.

## 3. Reference and planning rules

A reference is evidence, not a template. Preserve commercial intent while changing creative expression.

The planning boundary must explicitly record the intended changes to subject, composition, viewpoint, color direction, context, use case, and other uniqueness levers. Similarity checks are gates, not decoration.

No generation job is considered commercially approved merely because technical generation succeeded.

## 4. Remote generation contract

The default provider is the configured Hugging Face ZeroGPU Space:

```text
POST /gradio_api/call/generate_remote
        ↓
{event_id}
        ↓
GET /gradio_api/call/generate_remote/{event_id}
        ↓
SSE completion
        ↓
Gradio FileData download
        ↓
StockForge artifact ingestion
```

The seven remote values are:

```text
prompt
width
height
steps
seed
randomize_seed
stockforge_job_id
```

`stockforge_job_id` is the durable identity sent to the worker. The adapter persists the returned `event_id` and the materialized output references so control-plane restart does not silently create a second submission for an already-known execution.

The default repository configuration points to the StockForge ZeroGPU Space through environment variables and may be overridden without changing application code.

## 5. Worker operation

The control plane claims queued jobs from SQLite, constructs a provider-neutral `GenerationRequest`, and runs the recovery-aware orchestrator.

The ZeroGPU adapter is the default. Local ComfyUI is an explicit compatibility mode only and is not the default browser production path.

Worker retry behavior must be driven by durable execution state and provider status. Blind resubmission is prohibited.

## 6. Output gates

Every generated candidate with a reference path is checked after generation. The system fails closed when the reference or generated artifact is unavailable.

The V2 post-generation decision is:

```text
BLOCK  → stop release
REVIEW → human inspection required
```

Technical QA is separate from originality/commercial judgment.

Human approval is required before release packaging. Adobe upload is never performed automatically.

## 7. PNG and JPEG route policy

| Buyer job | Route | Finalizer contract |
|---|---|---|
| isolated object, cutout, sticker, overlay, transparent utility asset | PNG | RGBA/true alpha, sRGB, isolated finalizer, alpha/edge QA |
| scene, environment, hero composition, background, illustration, copy-space asset | JPEG | RGB/sRGB, valid resolution, protected finalizer, full-resolution QA |

Choose by buyer job and composition, not filename or source extension.

## 8. Termux operator mode

Termux may be used to inspect the repository, query the control plane, inspect jobs, download approved artifacts, run audits, and perform administrative operations.

Typical setup:

```bash
cd "$HOME/stockforge-ai"
export PYTHONPATH="$PWD/src"
export STOCKFORGE_HOME="${STOCKFORGE_HOME:-$HOME/.stockforge}"
```

Termux must not be treated as the production GPU executor. A production run should continue to work when the operator closes the terminal after submitting or inspecting a durable job, provided the control-plane/worker deployment itself remains available.

## 9. Safety rules

Never expose provider credentials. Never expose SQLite or runtime directories directly. Never auto-approve originality. Never auto-upload to Adobe. Never route PNG through the JPEG finalizer or JPEG through the PNG finalizer. Never treat provider `COMPLETE` as proof that an output belongs to the latest request without identity matching.

Do not invent execution IDs, job IDs, result paths, request IDs, or verification results.

## 10. Deployment truth boundary

The canonical browser implementation is stored under `frontend/` and is designed for Cloudflare Pages. Its Pages Function forwards browser `/api/*` requests to the StockForge CPU control plane. The control plane runs the browser API and the durable worker loop; the worker delegates generation to the configured remote ZeroGPU Space.

The Pages function supports `STOCKFORGE_CONTROL_PLANE_URL` as an external deployment override. The repository's default target is the canonical StockForge control-plane Space, but the public `page.dev` hostname and Cloudflare project settings remain deployment state outside source code.

GitHub Actions provide automated deployment hooks for both boundaries. They run only when the corresponding deployment credentials are configured as repository secrets. A skipped deployment must not be interpreted as a live production deployment.

A local Cloudflare quick tunnel is a development/debug mechanism, not the canonical production deployment.

## 11. Current source-of-truth rule

`main` is the only canonical development branch. Closed feature branches and historical documents are not active instructions.

When the production call graph changes, update this file, `docs/ACTIVE_SCOPE.md`, `docs/STATUS.md`, and the root `README.md` together.
