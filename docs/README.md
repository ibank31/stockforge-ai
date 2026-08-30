# StockForge Documentation

> **Active scope:** StockForge production currently generates and finalizes **PNG and JPEG only**. Do not treat the presence of other code or documents as support for another production format.

## Required reading order

For any implementation or production operation, read these files in order:

1. [`ACTIVE_SCOPE.md`](ACTIVE_SCOPE.md) — the authoritative output-format boundary and agent rules.
2. [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md) — the only active end-to-end operational workflow.
3. [`STATUS.md`](STATUS.md) — the current implementation snapshot and known limitations.
4. The relevant source code and tests — the detailed executable contract for the selected PNG or JPEG route.

If these files disagree with a historical document, the active files win. If a request does not clearly identify PNG or JPEG, stop and clarify instead of choosing a route by filename or subject intuition.

## Active production routes

| Route | Intended use | Worker finalizer | Output |
|---|---|---|---|
| **JPEG** | Scene, environment, hero composition, illustration with background, or copy-space visual | Protected Kaggle RealESRGAN | RGB/sRGB JPEG master |
| **PNG** | Isolated object, cutout, sticker, overlay, or transparent utility asset | Isolated Kaggle BiRefNet | RGBA/true-alpha/sRGB PNG master |

The route is selected from the buyer job and background requirement. In particular, `pet_enrichment_object_illustrations → puzzle-feeder` is a **JPEG** contract in the portfolio registry; it is not a PNG candidate merely because the subject is an object.

## Canonical storage boundary

```text
Download/MACHINE STOCKFORGE/
├── PREVIEW_TO_MANUS/       # visual previews only
└── READY_UPLOAD_ADOBE/     # approved JPEG/PNG masters only
```

JSON, logs, requests, `result.json`, ZIP files, WebP intermediates, staging images, databases, models, checksums, and other technical artifacts remain in the project workspace.

## Non-active material

SVG/vector generation, retired batch-generation runners, local-AI trials, provider experiments, pretrials, and other exploratory workflows are **not active production routes**. Research is evidence only, not an operational instruction. Historical documents are retained under [`archive/`](archive/) and must not be linked as current runbooks.

Do not revive, extend, or create a parallel runbook for a non-active route. The repository may retain implementation and tests for compatibility or audit history; that does not change the production scope.

## Maintenance rule

When the PNG or JPEG flow changes, update [`ACTIVE_SCOPE.md`](ACTIVE_SCOPE.md), [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md), and [`STATUS.md`](STATUS.md) in the same commit. Keep the canonical workflow as the single operational guide.
