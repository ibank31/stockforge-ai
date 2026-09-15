# StockForge AI

## StockForge V2

**StockForge V2 is a remote-first Microstock Intelligence and Asset Generation System.**

The system learns from a reference asset to identify commercial intent and market-relevant characteristics, then creates a genuinely new creative direction with explicit similarity-risk controls. It is not a tracing or copying system, and final commercial judgment remains human-reviewed.

### Canonical end-to-end architecture

```text
Cloudflare Pages / browser front door
        ↓
Pages Function /api/* proxy
        ↓
StockForge V2 CPU control plane
        ↓
Reference Intelligence
        ↓
Market / Creative Opportunity
        ↓
Creative Distance / Anti-Similarity
        ↓
Concept + Model-Specific Prompt
        ↓
Durable Job Queue + Worker
        ↓
Provider Router
   ┌────┴───────────────┐
   │                    │
HF ZeroGPU          Kaggle worker
primary renderer    secondary/finalizer
   │                    │
   └──────────┬─────────┘
              ↓
Artifact Ingestion
              ↓
Post-Generation Similarity Gate
              ↓
Technical QA
              ↓
Human Review
              ↓
READY_UPLOAD_ADOBE
              ↓
Manual Adobe upload
```

`main` is the canonical source of truth for this architecture. The browser front door is intentionally separated from provider internals. Termux may be used as an operator/client tool, but production generation does not depend on a local GPU, local ComfyUI, or a Termux process staying alive.

## Core workflow

```text
MARKET-PROVEN REFERENCE ASSET
        ↓
UPLOAD
        ↓
REFERENCE INTELLIGENCE
        ↓
CREATIVE OPPORTUNITY
        ↓
ANTI-SIMILARITY PLAN
        ↓
NEW CONCEPT
        ↓
MODEL-SPECIFIC PROMPT
        ↓
REMOTE GENERATION
        ↓
QUALITY + SIMILARITY GATES
        ↓
FINALIZATION / RELEASE PACKAGE
        ↓
HUMAN REVIEW
        ↓
MANUAL MARKETPLACE UPLOAD
```

### Fundamental rule

> **Preserve market intent. Change creative expression.**

A reference may help StockForge understand why an asset is commercially interesting. It must not become a template for producing a confusingly similar copy.

### Intelligence layers

1. **Reference Intelligence** — extract structured signals from uploaded references.
2. **Market Intelligence** — demand, supply, crowding, and opportunity evidence.
3. **Creative Opportunity Engine** — select viable new directions.
4. **Anti-Similarity Engine** — exact, perceptual, semantic, compositional, and conceptual checks where technically available.
5. **Concept Engine** — turn intelligence into a distinct commercial concept.
6. **Model-Specific Prompt Engine** — translate the concept for the selected provider.
7. **Generation & Recovery** — durable job identity, idempotency, provider-event recovery, and artifact lineage.
8. **Quality & Release Gates** — technical rejection plus human review for uncertain originality and marketplace judgment.

## Production routes

StockForge currently supports exactly two production output routes:

| Route | Intended use | Final technical contract |
|---|---|---|
| **PNG** | Isolated objects, cutouts, stickers, overlays, transparent utility assets | PNG, RGBA/true alpha, sRGB, isolated finalizer, technical alpha gate, full visual edge review |
| **JPEG** | Scenes, environments, hero compositions, illustrations, backgrounds, copy-space visuals | JPEG, RGB/sRGB, resolution gate, protected finalizer, full-resolution visual review |

The route is selected from the buyer job and composition requirements, not from the source filename or extension.

## Remote provider boundary

The default browser provider is **Hugging Face ZeroGPU**. The application adapter uses the Gradio queue contract: submit one durable StockForge job identity, receive a remote `event_id`, poll the corresponding SSE endpoint, download the returned file, and ingest it into the durable StockForge project.

Remote Gradio event identities and materialized output references are persisted by the adapter, so a control-plane worker restart can resume a known remote event instead of silently creating a second submission.

The repository also contains Kaggle worker/finalizer integrations. They are not a reason to make local Termux or local GPU execution part of the production control plane.

## Browser deployment

The production browser entrypoint is designed as a Cloudflare Pages static front door plus a same-origin Pages Function proxy:

```text
https://stockforge-ai.pages.dev
        ↓
/frontend/index.html
        ↓
/frontend/functions/api/[[path]].js
        ↓
STOCKFORGE_CONTROL_PLANE_URL
        ↓
HF CPU control-plane Space
        ↓
HF ZeroGPU generation Space
```

The Pages Function keeps provider URLs, runtime storage, SQLite, and credentials out of the browser. The control-plane target can be overridden with the Cloudflare Pages environment variable `STOCKFORGE_CONTROL_PLANE_URL`.

GitHub Actions provide deployment hooks for both the HF control-plane Space and the Cloudflare Pages front door. Those workflows intentionally skip remote deployment when their corresponding secrets are not configured. A skipped workflow is not proof that the public browser is live.

## Browser API

The V2 web application provides:

- reference upload and profiling;
- crop application;
- creative opportunity planning;
- durable generation queue submission;
- job status polling;
- post-generation similarity verification;
- technical QA;
- human approval gate;
- release-package creation.

The API never performs automatic Adobe submission and never auto-approves commercial originality.

The embedded `stockforge.web_app` page remains a reference implementation. The deployable production front door is under `frontend/`; public `page.dev` behavior remains external deployment state and must be verified through deployment evidence.

## Development and CI

Install the package with the required extras:

```bash
python3 -m pip install -e '.[dev,image,web]'
python3 -m pytest -q
```

CI installs `dev`, `image`, and `web` extras and runs the complete test suite before the version check.

## Repository operating rule

Before extending a subsystem, verify that it belongs to the active production call graph. A module that exists and passes unit tests is not automatically an active V2 capability.

When changing an active production flow, update the corresponding scope/status documentation in the same commit. Historical or isolated material may remain for auditability, but it is not an active instruction.
