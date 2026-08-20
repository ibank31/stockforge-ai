# StockForge AI — Feature Roadmap & Implementation Ledger

**Version:** 1.0  
**Date:** 2026-08-20  
**Branch:** `feat/zerogpu-runtime`

This document is the authoritative feature ledger for StockForge AI. It records the complete intended feature set, the current implementation state, and the evidence required before a feature is marked complete.

## Status vocabulary

- **DONE** — implemented and verified with code/tests or a live integration test.
- **LIVE** — deployed and successfully exercised in the target runtime.
- **IN PROGRESS** — implementation exists but is not yet production-complete.
- **PLANNED** — specified but not implemented.
- **BLOCKED** — cannot proceed until a dependency or decision is resolved.

A feature is never marked DONE merely because files were created. The project standard is implementation + verification + correct Git state.

---

# 1. Product definition

StockForge AI is a free-first, Termux-first, plugin-based AI stock asset factory.

The first production output is **commercial stock photography**. The long-term workflow is:

```text
Market intelligence
    ↓
Opportunity scoring
    ↓
Commercial concept
    ↓
Prompt compliance
    ↓
Prompt + variation planning
    ↓
Persistent generation job
    ↓
Generator provider
    ↓
Artifact + provenance
    ↓
Technical QA
    ↓
AI/anatomy/object QA
    ↓
IP/OCR/logo QA
    ↓
Enhancement / upscaling
    ↓
Perceptual deduplication
    ↓
Commercial-value scoring
    ↓
Metadata generation
    ↓
Marketplace compliance package
    ↓
Human approval
    ↓
Marketplace submission
    ↓
Acceptance / sales feedback
    └──────────────→ Market intelligence
```

---

# 2. Core foundation

| Feature | Status | Notes / evidence |
|---|---|---|
| CLI entry point | DONE | Core CLI implemented. |
| `stockforge version` | DONE | Version command implemented. |
| `stockforge init` | DONE | Project initialization implemented. |
| `stockforge doctor` | DONE | Environment diagnostics implemented. |
| SQLite initialization | DONE | Persistent local registry foundation. |
| Project creation/listing | DONE | Project lifecycle implemented. |
| Workspace layout | DONE | Standard project filesystem structure. |
| Versioned project manifest | DONE | Manifest versioning implemented. |
| Atomic manifest writes | DONE | Safe manifest persistence. |
| Rollback handling | DONE | Project creation failure handling. |
| Pytest coverage | DONE | Initial test suite exists. |
| GitHub Actions CI | DONE | CI gate exists. |

---

# 3. Asset registry

| Feature | Status | Notes |
|---|---|---|
| Stable asset UUID | DONE | Persistent asset identity. |
| Project ownership | DONE | Assets belong to projects. |
| Asset type/status contract | DONE | Lifecycle semantics defined. |
| Safe relative paths | DONE | Filesystem safety rules. |
| MIME type / size | DONE | Asset metadata tracked. |
| SHA-256 checksum | DONE | Content identity/integrity. |
| Asset create/list CLI | DONE | Basic asset operations. |
| Artifact lineage | DONE | Parent/child transformation relationship. |
| Immutable artifact identity/version | IN PROGRESS | Contract exists; broader production usage remains. |

---

# 4. Persistent job queue

| Feature | Status | Notes |
|---|---|---|
| Stable job UUID | DONE | Persistent job identity. |
| Project ownership | DONE | Job-to-project relation. |
| Job type | DONE | Typed work units. |
| Priority | DONE | Priority ordering implemented. |
| JSON payload | DONE | Structured job input. |
| Queued/running/succeeded/failed/cancelled | DONE | Durable state machine. |
| Atomic worker claiming | DONE | Prevents duplicate claims. |
| Attempt counting | DONE | Retry accounting. |
| Bounded retries | DONE | Retry ceiling. |
| Completion/failure/cancellation | DONE | Lifecycle operations. |
| CLI create/list/claim/complete/fail/cancel | DONE | Operator controls. |
| Persistent generation jobs | IN PROGRESS | Queue exists; live provider job integration is next. |

---

# 5. Plugin architecture

| Feature | Status | Notes |
|---|---|---|
| Vendor-neutral plugin descriptor | DONE | Provider-neutral contract. |
| Plugin API version | DONE | Compatibility boundary. |
| Plugin kind/capabilities | DONE | Capability discovery. |
| Deterministic registry lookup | DONE | Stable plugin resolution. |
| Capability validation | DONE | Provider compatibility checks. |
| Trust-boundary documentation | DONE | Provider isolation principles documented. |
| Generator adapter interface | IN PROGRESS | Core contract exists; live Comfy adapter hardening remains. |
| Provider-neutral generator switching | PLANNED | Multiple providers/local engines. |

---

# 6. Pipeline engine

| Feature | Status | Notes |
|---|---|---|
| Versioned pipeline definition | DONE | Declarative pipeline contract. |
| Sequential runner | DONE | Initial deterministic runner. |
| Capability validation | DONE | Required capabilities checked. |
| Execution error boundary | DONE | Pipeline failures isolated. |
| Artifact/provenance integration | IN PROGRESS | Contracts and persistence exist; full provider lifecycle remains. |
| DAG execution | PLANNED | Deliberately deferred until contracts mature. |
| Fan-out / batch orchestration | PLANNED | Needed for controlled asset batches. |
| Resumability | PLANNED | Required for production-scale jobs. |
| Deterministic caching | PLANNED | Avoid repeated expensive work. |

---

# 7. Provenance and lineage

| Feature | Status | Notes |
|---|---|---|
| Versioned provenance record | DONE | Domain contract exists. |
| Job ID tracking | DONE | Linked to execution. |
| Pipeline ID/version/hash | DONE | Reproducibility metadata. |
| Step ID | DONE | Pipeline-level traceability. |
| Plugin/provider identity | DONE | Provider traceability contract. |
| Model identity/version | IN PROGRESS | Contract exists; live generator population remains. |
| Workflow hash | PLANNED | Required for exact workflow audit. |
| Prompt record/hash | PLANNED | Required for reproducibility. |
| Seed/generation parameters | IN PROGRESS | Generator exposes seed and parameters; persistent recording remains. |
| Transformation chain | IN PROGRESS | Artifact lineage foundation exists. |
| QA result history | PLANNED | Every gate must be auditable. |
| Metadata version | PLANNED | Submission package traceability. |
| License/policy record | PLANNED | Model/provider policy evidence. |

---

# 8. ZeroGPU generation runtime

| Feature | Status | Notes / evidence |
|---|---|---|
| Hugging Face Space | LIVE | `ibank31/stockforge-zerogpu`. |
| ZeroGPU `zero-a10g` | LIVE | Live runtime verified. |
| Termux/API-driven generation | LIVE | Public Gradio API tested from Termux. |
| Z-Image Turbo integration | LIVE | End-to-end generation succeeded. |
| AE/VAE loading | LIVE | Generation completed successfully. |
| Qwen3 FP8 mixed text encoder | LIVE | `qwen_3_4b_fp8_mixed.safetensors` successfully used through Comfy-compatible loader. |
| Comfy-compatible FP8 loader | LIVE | Replaced incorrect raw `Qwen3ForCausalLM.load_state_dict()` path. |
| 1024×1024 / 8-step baseline | LIVE | Benchmark completed. |
| GPU runtime measurement | LIVE | Benchmark reported 44.238 GPU-function seconds. |
| Batch generation | PLANNED | Must include queueing, deduplication and quota controls. |
| GPU quota-aware scheduling | PLANNED | Minimize waste and avoid unnecessary inference. |
| Generator failure recovery | PLANNED | Bounded retry + persisted failure reason. |

### Verified generation benchmark

- Date: 2026-08-20
- Resolution: 1024×1024
- Steps: 8
- Seed: `2157290427964887587`
- GPU-function seconds: `44.238`
- Result: successful image returned by ZeroGPU API
- Asset concept: construction project planning meeting
- Result assessment: commercially promising, **not yet Adobe submission-ready**

---

# 9. Adobe Stock readiness gate

The generator is not the submission product. Every asset must pass the Adobe-oriented gates documented in `docs/ADOBE_STOCK_READINESS.md`.

| Feature | Status | Required outcome |
|---|---|---|
| Minimum resolution gate | PLANNED | Reject below Adobe photo minimum. |
| Maximum resolution gate | PLANNED | Reject above marketplace maximum. |
| JPEG finalization | PLANNED | Final photo artifact in supported JPEG form. |
| sRGB validation/conversion | PLANNED | Final color space controlled. |
| File-size gate | PLANNED | Reject oversized submission files. |
| Image decodability/corruption | PLANNED | Reject broken files. |
| Sharpness/noise/quality gate | PLANNED | Detect technical defects. |
| Anatomy/hand/face QA | PLANNED | Detect obvious AI anatomy defects. |
| Object consistency QA | PLANNED | Detect malformed physical objects/interactions. |
| OCR/text QA | PLANNED | Detect unintended text. |
| Logo/trademark detection | PLANNED | Detect and reject unintended branding. |
| Watermark detection | PLANNED | Reject visible watermarks. |
| IP/prompt compliance firewall | PLANNED | Block risky prompts before generation. |
| People/property release logic | PLANNED | Track fictional/real/release requirements. |
| Generative-AI disclosure metadata | PLANNED | Persist required AI disclosure state. |
| Metadata generation | PLANNED | Title/keywords/categories. |
| Metadata compliance validator | PLANNED | Prevent prohibited/misleading metadata. |
| Perceptual deduplication | PLANNED | Prevent near-duplicate submissions. |
| Commercial-value scoring | PLANNED | Rank assets by buyer utility. |
| Human approval gate | PLANNED | No automatic marketplace submission without explicit approval. |
| Submission package exporter | PLANNED | Produce marketplace-ready package. |

---

# 10. Image QA system

| Feature | Status |
|---|---|
| Technical image inspection | PLANNED |
| Resolution/aspect validation | PLANNED |
| Color/profile validation | PLANNED |
| Blur/sharpness detection | PLANNED |
| Noise/compression detection | PLANNED |
| Face detection | PLANNED |
| Hand/anatomy analysis | PLANNED |
| Object anomaly detection | PLANNED |
| OCR | PLANNED |
| Logo/trademark detection | PLANNED |
| Watermark detection | PLANNED |
| Aesthetic/commercial score | PLANNED |
| QA report persistence | PLANNED |
| Hard-fail vs review thresholds | PLANNED |

QA must be deterministic where possible and must preserve the reason for every rejection.

---

# 11. Enhancement and upscaling

| Feature | Status |
|---|---|
| Upscaler plugin contract | PLANNED |
| AI upscaling | PLANNED |
| Target resolution policy | PLANNED |
| Detail preservation QA | PLANNED |
| Halo/artifact detection after upscale | PLANNED |
| Final JPEG export | PLANNED |
| Final sRGB normalization | PLANNED |

The current 1024×1024 generation benchmark is an **intermediate artifact**, not a final Adobe submission file.

---

# 12. Prompt and concept engine

| Feature | Status |
|---|---|
| Market opportunity model | PLANNED |
| Buyer/use-case classification | PLANNED |
| Niche selection | PLANNED |
| Commercial concept planner | PLANNED |
| Prompt generation | PLANNED |
| Prompt compliance firewall | PLANNED |
| Negative-risk term filtering | PLANNED |
| Composition planner | PLANNED |
| Copy-space planner | PLANNED |
| Controlled variation planner | PLANNED |
| Seed/parameter strategy | PLANNED |
| Prompt versioning | PLANNED |

Prompt quality is measured by **commercial utility**, not novelty alone.

---

# 13. Market intelligence

| Feature | Status |
|---|---|
| Opportunity scoring | PLANNED |
| Buyer utility score | PLANNED |
| Seasonal/evergreen classification | PLANNED |
| Competition/saturation signal | PLANNED |
| Portfolio gap analysis | PLANNED |
| Keyword/search opportunity analysis | PLANNED |
| Variation potential score | PLANNED |
| Production cost estimate | PLANNED |
| Acceptance-risk estimate | PLANNED |
| Commercial-value prediction | PLANNED |
| Sales/acceptance feedback loop | PLANNED |

Market intelligence must use evidence. It must never fabricate demand signals.

---

# 14. Metadata and marketplace export

| Feature | Status |
|---|---|
| Stock title generator | PLANNED |
| Keyword generator | PLANNED |
| Keyword ranking | PLANNED |
| Category suggestion | PLANNED |
| Metadata compliance validation | PLANNED |
| AI disclosure flag | PLANNED |
| Fictional people/property flag | PLANNED |
| Release requirement tracking | PLANNED |
| Submission CSV/package export | PLANNED |
| Human approval manifest | PLANNED |

Internal metadata must remain richer than any marketplace-specific export.

---

# 15. Deduplication and portfolio quality

| Feature | Status |
|---|---|
| Exact duplicate detection | PLANNED |
| Perceptual hash | PLANNED |
| Embedding similarity | PLANNED |
| Batch clustering | PLANNED |
| Best-of-cluster selection | PLANNED |
| Portfolio diversity scoring | PLANNED |
| Repetition/spam prevention | PLANNED |

The system must optimize for **quality and differentiated utility**, not raw image count.

---

# 16. Compliance and policy

| Feature | Status |
|---|---|
| Model license registry | PLANNED |
| Provider license/policy registry | PLANNED |
| Commercial-use policy checks | PLANNED |
| Prompt/IP compliance | PLANNED |
| Provenance record | IN PROGRESS |
| AI disclosure tracking | PLANNED |
| Human submission approval | PLANNED |
| Marketplace-specific rules | PLANNED |

Open-source code or weights are never treated as automatically commercially unrestricted. License evidence must be recorded.

---

# 17. Security and operations

| Feature | Status |
|---|---|
| Secret separation from job payloads | DONE | Core security contract documented. |
| Provider configuration IDs | DONE | Contract exists. |
| No secret leakage in logs | DONE | Security requirement documented. |
| HF token isolation | IN PROGRESS | Runtime deployment workflow established; automated secret handling remains. |
| Rate/quota controls | PLANNED |
| Job cancellation | DONE | Core queue supports cancellation. |
| Bounded retry | DONE | Core queue supports retry limits. |
| Runtime health check | LIVE | Space runtime and HTTP health verified. |
| Structured generation logs | PLANNED |

---

# 18. Human approval and submission

| Feature | Status |
|---|---|
| Review queue | PLANNED |
| Visual QA report | PLANNED |
| Approve/reject decision | PLANNED |
| Reviewer notes | PLANNED |
| Submission manifest | PLANNED |
| Marketplace export | PLANNED |
| Acceptance feedback import | PLANNED |
| Sales feedback import | PLANNED |

Human approval remains the final gate. StockForge must not silently submit assets to a marketplace.

---

# 19. Current priority order

1. Adobe technical submission gate.
2. Image QA gate.
3. Upscaling/finalization.
4. Provenance population for live generation.
5. Prompt/commercial concept engine.
6. Perceptual deduplication.
7. Metadata engine.
8. Submission package + human approval.
9. Market intelligence.
10. Acceptance/sales feedback loop.

---

# 20. Completion rule

Every completed feature must add a dated entry to the project changelog and update this ledger from `PLANNED`/`IN PROGRESS` to `DONE` or `LIVE` only after verification.

Required evidence may include:

- unit/integration tests,
- CI result,
- live provider test,
- real generated artifact,
- benchmark metrics,
- compliance test fixture,
- or an audited repository implementation.

This rule exists to prevent the project from confusing **"code exists"** with **"feature works"**.
