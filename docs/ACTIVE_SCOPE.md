# Active Scope: PNG and JPEG Generation

**Status:** Active production contract
**Last reviewed:** 2026-08-29

> StockForge AI currently supports exactly two production output routes: **PNG** and **JPEG**. Everything else in the repository is either implementation support, test coverage, research, or historical material; it is not an active generation target.

## Route contract

| Route | Use when | Final output | Finalizer | Review requirement |
|---|---|---|---|---|
| **PNG** | The buyer needs an isolated object, cutout, sticker, overlay, or transparent utility asset. | PNG, RGBA/true alpha, sRGB | Isolated BiRefNet route | Technical alpha gate plus 100% visual edge review |
| **JPEG** | The buyer needs a self-contained scene, environment, hero composition, background, illustration, or copy-space visual. | JPEG, RGB/sRGB | Protected RealESRGAN route | Technical image gate plus full-resolution visual review |

The route is selected from **buyer job, composition, and background requirement**. It is not selected from the source extension, filename, subject category, or a casual interpretation of a lane name. For example, the current portfolio contract maps `pet_enrichment_object_illustrations → puzzle-feeder` to **JPEG**, not PNG.

## Canonical production sequence

Both routes follow the same high-level lifecycle: choose a registered concept, generate or import one preview, preserve provenance, obtain an explicit human `KEEP`, prepare the matching format-specific finalizer request, run the matching worker, import and audit the master, write metadata and the upload package, then export only the approved visual master. JPEG and PNG workers are never interchangeable.

The complete operational command sequence is maintained only in [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md). The current repository snapshot and known limitations are maintained only in [`STATUS.md`](STATUS.md).

## Current registered production candidates

The current PNG candidates include `household_furniture_small_space_png--rolling-kitchen-island-cart-cutout` for isolated small-space furniture and `traditional_food_banh_mi_cutaway_png--banh-mi-cutaway` for one isolated Vietnamese banh mi sandwich cutaway. The banh mi candidate is a single unbranded baguette sandwich with a visible layered filling, intended for recipe cards, menu layouts, culinary tourism, packaging concepts, and social compositions. Mango sticky rice and Tom Yum Kung are excluded from this new trial because the user reports they were already used; mango sticky rice was rejected for Similar Content. Do not choose an excluded candidate or create seed/color/crop variants. Use the explicit lane and concept registry; do not infer PNG compatibility from a lane name.

## Explicitly out of scope

The following are not active production routes and must not be revived, extended, or used as instructions for a new run:

- SVG or native-vector generation;
- batch-generation runners and retired batch orchestration;
- local AI generation trials, including llama.cpp and Qwen experiments;
- provider trials, pretrials, and exploratory research workflows;
- any third raster or editable output format.

Source files and tests related to these areas may remain temporarily for historical compatibility or auditability. Their presence does not make them supported production functionality. Historical documents belong under [`archive/`](archive/) and are non-authoritative.

## Maintenance rule

Any change to an active PNG or JPEG flow must update this file, [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md), and [`STATUS.md`](STATUS.md) in the same commit. Do not create another operational runbook. If a historical document is retained, label it as historical and do not link it as an active instruction.

## Agent checklist

Before acting, an agent must identify the requested route as PNG or JPEG, locate the relevant source code and tests, and state the format-specific contract it will preserve. If the requested output is not PNG or JPEG, the agent must stop rather than silently selecting an unsupported route.
