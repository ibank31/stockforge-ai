# StockForge Engine Maturation Plan

**Updated:** 2026-08-24
**Branch:** `main`
**Policy:** No generation unless a deterministic validation gap makes a trial necessary.

## Goal

Make StockForge usable as a product-type selector and controlled asset factory. The user selects an asset type; StockForge chooses the buyer job, niche, prompt, format, provider, quality gates, metadata draft, and delivery path. The user receives only a review visual and, after explicit approval, an upload copy. Marketplace-only fields remain manual.

## Milestones

| Stage | Scope | Generation allowed? | Exit evidence |
|---|---|---:|---|
| 0 | Baseline and checkpoint | No | Clean `main`, tests pass, current docs read |
| 1 | Asset-type selector and format route | No | `portfolio asset-types` and `portfolio readiness` map each supported type to one explicit route and blocker set |
| 2 | Prompt and policy compiler | No | Rights-safe prompt, negative prompt, metadata draft, and pre-GPU blockers are test-covered |
| 3 | Format builders and technical gates | No | JPEG/SVG/PNG/pattern contracts pass local tests; blocked formats remain blocked until their gates exist |
| 4 | Output and learning loop | No | HP folders, upload-copy metadata, append-only evaluation ledger, and summary are test-covered |
| 5 | Trial readiness review | No | A written gap identifies why one trial is necessary and which exact hypothesis it tests |
| 6 | One controlled trial per approved format | Yes, one at a time | Preview, finalization, human review, metadata review, and evaluation record exist |
| 7 | Learning and regression update | No | Trial findings are documented; changes are tested before another trial |

## Format release gates

### JPEG raster scene

A trial is allowed only after the selected brief passes buyer-job, prompt/IP, layout, provider/quota, and duplicate-risk preflight. The output must be reviewed at full size, finalized to RGB/sRGB JPEG when needed, packaged with metadata draft, and recorded in the evaluation ledger.

### Native SVG

A trial is local and does not need GPU. The SVG must contain genuine editable geometry, no raster embed, script, external link, hidden object, or live font. The first trial should use a deterministic object/icon preset, not a raster trace or a complex scene.

### PNG transparent asset

A trial is not allowed until a real alpha producer exists. A white or checkerboard preview is not evidence of transparency. The path must include alpha assertion, anti-fringe review, excess-canvas trim, sRGB/decodability checks, and one manual portal validation plan.

### Seamless pattern

A trial is not allowed to claim seamlessness until the candidate passes horizontal and vertical edge continuity. The gate checks boundaries only; visual utility and marketplace suitability still require human review.

## Learning contract

Each future trial is a controlled experiment with one buyer hypothesis, one asset brief, one chosen format, one provider/model context, and a bounded output. After review, record visual quality, technical quality, buyer fit, metadata accuracy, decision, rejection reasons, and marketplace outcome in `evaluations/generation_evaluations.jsonl`.

Evaluation summaries are descriptive. They cannot automatically change prompts, provider routing, format policy, or generation volume. A later engine change must cite the records that motivate it and must pass regression tests before another trial is considered.

## Delivery contract

A future generation preview may be copied to `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/`. Only an explicitly approved final upload copy may be copied to `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/`. Embedded JPEG title/keywords are convenience metadata; category, GenAI declaration, release, CAPTCHA, Terms, and submit remain manual.

## Current state

Stage 1 is complete. The selector, readiness report, and `portfolio plan-type` entry point are implemented and tested without generation. Supported types are `scene`, `native_object`, `technical_icon`, `seamless_pattern`, and `transparent_cutout`. Native SVG now has a dedicated `native_vector_elements` lane with modular-ribbon and technical-badge briefs and deterministic presets. PNG has a conservative true-alpha normalizer that refuses opaque sources, but the production route remains explicitly blocked. Unsupported asset types fail closed.

## Current next action

Continue the deterministic SVG preset family beyond the two controlled briefs and integrate the true-alpha normalizer into a future PNG production gate only after anti-fringe and portal evidence are available. `portfolio plan-type --asset-type <type>` is now the no-generation entry point for future user selection. A generation trial is not yet needed. It becomes justified only when a remaining provider, visual, or marketplace fact cannot be established locally and the exact hypothesis is documented first.
