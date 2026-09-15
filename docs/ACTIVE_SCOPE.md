# Active Scope: Remote-First PNG and JPEG Generation

**Status:** Active production contract
**Last reviewed:** 2026-09-15

> StockForge AI currently supports exactly two production output routes: **PNG** and **JPEG**. The control plane and generation path are remote-first. Termux is an optional operator/client surface, not the production GPU executor.

## Route contract

| Route | Use when | Final output | Finalizer | Review requirement |
|---|---|---|---|---|
| **PNG** | isolated object, cutout, sticker, overlay, transparent utility asset | PNG, RGBA/true alpha, sRGB | Isolated BiRefNet route | Technical alpha gate plus 100% visual edge review |
| **JPEG** | self-contained scene, environment, hero composition, background, illustration, copy-space visual | JPEG, RGB/sRGB | Protected RealESRGAN route | Technical image gate plus full-resolution visual review |

The route is selected from **buyer job, composition, and background requirement**. It is not selected from source extension, filename, subject category, or lane naming.

## Canonical production sequence

```text
reference / market evidence
→ reference intelligence
→ creative opportunity
→ anti-similarity plan
→ new concept + model-specific prompt
→ durable job queue
→ remote provider
→ artifact ingestion
→ post-generation similarity gate
→ technical QA
→ human review
→ release package
→ READY_UPLOAD_ADOBE
→ manual Adobe upload
```

The default generation provider is Hugging Face ZeroGPU. Local ComfyUI is compatibility-only and not the browser production default. Kaggle integrations remain available where the selected route explicitly requires them.

## Browser boundary

The browser/front door communicates only with the StockForge web API. It must never access SQLite, runtime directories, credentials, provider endpoints, or worker internals directly.

The user's existing `page.dev` hostname is external deployment configuration and is not hard-coded in this repository. A deployment is considered connected only when that front door targets the current StockForge control-plane API.

## Current registered candidates

The current PNG candidates include `household_furniture_small_space_png--rolling-kitchen-island-cart-cutout` and `traditional_food_banh_mi_cutaway_png--banh-mi-cutaway`. Mango sticky rice and Tom Yum Kung remain excluded according to the project candidate history.

## Explicitly out of scope

The following are not active production routes:

- SVG or native-vector generation;
- retired batch-generation runners;
- local AI generation trials, including llama.cpp and Qwen experiments;
- provider trials, pretrials, and exploratory research workflows;
- third raster or editable output formats;
- automatic Adobe or marketplace submission.

Historical source files may remain for auditability. Their presence does not make them supported production functionality.

## Maintenance rule

Any change to an active PNG/JPEG flow or the remote control-plane call graph must update this file, `docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`, `docs/STATUS.md`, and the root `README.md` in the same change set.
