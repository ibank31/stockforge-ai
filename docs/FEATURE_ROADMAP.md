# StockForge Feature Roadmap

**Updated:** 2026-08-24
**Branch:** `main`
**Status vocabulary:** `DONE` berarti teruji lokal atau live sesuai klaim; `LIVE` berarti exercised di runtime target; `IN PROGRESS` berarti implementasi ada tetapi belum lengkap; `BLOCKED` berarti route sengaja ditahan; `PLANNED` berarti belum diimplementasikan.

## Product flow

```text
market evidence → buyer job → AssetSpec → concept/prompt
→ pre-GPU gate → provider/local route → generation/build
→ artifact/provenance → technical/semantic/commercial QA
→ enhancement/alpha → deduplication → metadata/compliance
→ human review → marketplace package → feedback
```

## Current ledger

| Area | Feature | Status | Evidence / next proof |
|---|---|---|---|
| Core | CLI, project init, SQLite, manifest, rollback | DONE | Core test suite |
| Core | Asset registry and lineage | DONE | Registry/provenance tests |
| Core | Persistent job queue and execution records | DONE | Queue/orchestration tests |
| Core | Plugin and pipeline contracts | DONE | Contract tests |
| Intelligence | Market evidence and buyer taxonomy | DONE | Deterministic module tests; evidence remains human/public-source bounded |
| Intelligence | Concept planner and prompt compiler | DONE | Concept/prompt tests |
| Intelligence | Asset-type selector and format readiness report | DONE | `portfolio asset-types`, `portfolio readiness`, and `portfolio plan-type` dry-run; includes recommended research lanes and never calls a provider |
| Intelligence | Native vector utility lane | DONE | Research-backed `folder-upload` single icon remains baseline; separate `file-flow-micro-set` hypothesis targets higher buyer value; legacy modular ribbon and technical badge remain history briefs |
| Intelligence | Native vector pattern lane | DONE | One controlled repeatable geometric tile brief; local SVG route with structural repeatability gate and one-trial readiness |
| Generation | Provider-neutral GenerationRequest/Result | DONE | Generation contract tests |
| Generation | Provider capability/quota router | DONE | Router tests, including exhausted quota |
| Generation | Remote Gradio durable adapter | DONE | `generate_remote` contract tests; live endpoint remains runtime-dependent |
| Generation | Hugging Face ZeroGPU preview route | LIVE | Recorded Z-Image Turbo benchmark and selected preview workflow |
| Generation | Kaggle finalizer route | LIVE | RealESRGAN master workflow and technical validation |
| Format | JPEG raster route | LIVE | Preview → finalizer → RGB/sRGB/XMP upload-copy workflow |
| Format | Native SVG deterministic route | IN PROGRESS | Single folder-upload and new eight-action file-flow micro-set presets pass local native-structure tests; micro-set is design-ready but has not been generated or commercially validated; human review and Adobe portal validation remain pending |
| Format | PNG true-alpha route | BLOCKED | Conservative alpha normalizer exists; production route still needs anti-fringe, trim policy, and one portal validation |
| Format | Raster seamless-pattern edge gate | DONE | Deterministic horizontal/vertical edge tests |
| QA | Adobe technical gate/finalizer | DONE | JPEG/RGB/sRGB/dimension/file-size tests |
| QA | Deduplication and similarity controls | DONE | Exact/perceptual pipeline tests |
| QA | Semantic/anatomy/OCR/logo/watermark ensemble | IN PROGRESS | Provider boundary exists; production benchmark and policy gates remain |
| Delivery | Review-ready package and Android export separation | LIVE | Package/export tests and handoff workflow |
| Delivery | Adobe metadata XMP upload copy | LIVE | Portal field auto-population observed; final submit remains manual |
| Delivery | Android preview export | DONE | Future successful generation exports one visual to `PREVIEW_TO_MANUS` when the mount exists |
| Delivery | Android ready-upload export | DONE | Approved JPEG upload copy exports to `READY_UPLOAD_ADOBE`; no internal files are copied |
| Learning | Append-only generation evaluation ledger | DONE | `portfolio evaluate` records human scores/reasons without generation |
| Learning | Evaluation summary for future decisions | DONE | `portfolio evaluation-summary` reports reviewed records only; no automatic generation |
| Architecture | Model registry and provider cache abstraction | IN PROGRESS | Contract exists in parts; unify model identity, cache, and delivery evidence |
| Architecture | Provider health, failover, and recovery | IN PROGRESS | Durable identity exists; live failover and worker persistence remain |
| Intelligence | Acceptance/sales feedback loop | PLANNED | Requires trustworthy marketplace outcome data |
| Runtime | Kaggle Qwen-Image end-to-end generation | BLOCKED | Previous experiment exhausted disk before image output |
| Runtime | Live Qwen Image benchmark on ZeroGPU | PLANNED | Must be run once with controlled quota and recorded evidence |

## Active priorities

1. Compare the existing folder-upload single-icon baseline against one controlled file-flow micro-set trial; require buyer-value gates above the internal threshold before any portal validation, then expand other SVG families only when each has a clear buyer job.
2. Keep PNG alpha blocked until its producer and portal path are independently verified.
3. Strengthen provider health, quota, retry, and failover without duplicating logical jobs.
4. Add semantic/commercial QA benchmarks using labeled internal outputs, not generic leaderboards alone.
5. Connect evidence logs to buyer-job scoring while keeping confidence and source URLs explicit.

## Safety gates

No generation route may be activated merely because a format extension exists. No preview, upscale, local SVG, or technical pass is equivalent to marketplace acceptance. Every GPU call needs a documented buyer hypothesis. Upload, disclosure, release decisions, CAPTCHA, and final submission remain human-controlled.

## Source of truth

The current snapshot is [`STATUS.md`](STATUS.md). The system design is [`ARCHITECTURE.md`](ARCHITECTURE.md). The current niche/format decision is [`research/FORMAT_AND_NICHE_DECISION_2026-08-24.md`](research/FORMAT_AND_NICHE_DECISION_2026-08-24.md). Historical milestones belong in [`CHANGELOG.md`](CHANGELOG.md).
