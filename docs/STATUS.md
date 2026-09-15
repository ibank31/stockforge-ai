# StockForge Active Status

**Updated:** 2026-09-15
**Branch:** `main`
**Active scope:** [`ACTIVE_SCOPE.md`](ACTIVE_SCOPE.md)
**Operational source of truth:** [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md)

## Current architecture

StockForge is now a **remote-first** production system. The intended boundary is:

```text
page.dev / browser
→ StockForge V2 control plane
→ durable job queue
→ remote provider router
→ artifact ingestion
→ similarity + technical gates
→ human review
→ READY_UPLOAD_ADOBE
→ manual Adobe upload
```

Hugging Face ZeroGPU is the default remote generation provider. Kaggle integrations remain available as explicit secondary/finalization paths. Termux is an operator/client surface and is not required to remain alive as a production GPU executor.

## Production routes

| Route | Status | Finalizer | Technical master gate |
|---|---|---|---|
| JPEG | **Active / mature** | Protected RealESRGAN route | JPEG, RGB/sRGB, valid dimensions, decodable, within configured limits |
| PNG | **Active / end-to-end implementation** | Isolated BiRefNet route | PNG, RGBA/true alpha, sRGB, valid dimensions, decodable |

Technical pass is not marketplace approval. Human visual review, metadata accuracy, rights checks, generative-AI disclosure, and manual Adobe upload remain required.

## V2 browser workflow

The browser API supports reference upload/profiling, crop application, creative opportunity planning, durable generation queue submission, job polling, post-generation similarity verification, technical QA, human approval, and release-package creation.

The embedded browser page is a reference implementation. The user's `page.dev` hostname/configuration is external deployment state and is not hard-coded into the repository, so the repository must not claim a specific hostname is live without deployment evidence.

## Remote generation recovery

The ZeroGPU adapter submits the durable StockForge job identity and receives a Gradio `event_id`. The adapter now persists event identities and materialized output references under its provider state directory. A control-plane restart can therefore recover a known remote event instead of silently losing the event identity.

The remote worker contract is:

```text
POST /gradio_api/call/generate_remote
→ event_id
→ GET /gradio_api/call/generate_remote/{event_id}
→ SSE completion
→ FileData download
→ artifact ingestion
```

## Safety gates

The system must never auto-approve commercial originality or auto-submit to Adobe. Generated candidates with a reference are fail-closed through the post-generation similarity gate. Provider completion must not be accepted without matching durable job/request identity.

Credentials must never be committed or exposed. Blind retries, arbitrary provider substitution, and cross-route finalizer substitution are prohibited.

## Branch truth

`main` is the single canonical development line. Feature branches and closed pull requests may remain as historical Git refs, but they are not active implementation sources.
