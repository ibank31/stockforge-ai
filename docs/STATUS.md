# StockForge Development Status — Active Snapshot

**Updated:** 2026-08-25
**Branch:** `main`
**Baseline documentation commit:** `6d663ec`
**Deployed HF Space:** `935faa5` — runtime `RUNNING`, domain `READY`

## Current decision

StockForge is currently operating the **JPEG technical mechanical component** track as a controlled first-sale hypothesis. The active reference brief is `technical_mechanical_component_illustrations--rotor-armature`. The niche is promising but unproven: market evidence supports recognizable technical/industrial buyer jobs, but no screenshot, catalog count, internal score, upload, approval, download, or sale is treated as demand proof.

The user is a first-time microstock contributor and should not be asked to choose the niche, buyer job, prompt, negative prompt, format, provider, category, keywords, or finalizer. StockForge owns those decisions from evidence, buyer utility, technical readiness, compliance risk, cost, and prior reviewed outcomes. The user’s role is limited to simple visual review, portal declarations, CAPTCHA, Terms, and manual submission.

## Verified JPEG workflow

```text
market evidence and buyer job
  → one portfolio brief
  → dry-run and pre-GPU gates
  → one ZeroGPU preview
  → artifact/provenance/review package
  → visual and technical review
  → portfolio evaluate
  → portfolio learning-summary
  → prepare-master
  → one private Kaggle finalizer job
  → import-kaggle-master
  → 4096×4096 RGB/sRGB master audit
  → prepare-adobe-upload --latest-master --approved
  → JPEG upload-copy with embedded metadata
  → manual Adobe upload and submission
```

This workflow is verified end-to-end for the rotor-armature reference. The preview execution is `d3c2c121-77c7-590c-97b1-3da15ff26dcc`; the preview artifact is `d419cdcf-da49-49f8-98c4-5ef4c8415920`. The remote ZeroGPU worker completed inference and returned a review package. One private Kaggle RealESRGAN finalizer job completed, was imported, and produced a 4096×4096 JPEG master with 16.777216 MP, RGB, embedded sRGB, quality 95, and 4:4:4 subsampling. The master passed the deterministic technical gate and a four-tile full-resolution audit.

The master is a conceptual electromechanical illustration. It must not be described as CAD, blueprint, certified engineering documentation, dimensionally accurate reference, standard-compliant equipment, or manufacturer-specific content. Its strongest honest buyer use is an industrial technology article, presentation, general education visual, or conceptual manufacturing communication.

## Current production routes

| Route | Status | Boundary |
|---|---|---|
| JPEG raster | **LIVE / verified** | One preview, one learning record, selected finalizer, master audit, metadata upload-copy, manual portal action |
| Native SVG | **FROZEN** | Local editable route and evidence retained; no active expansion during JPEG track |
| PNG with real alpha | **BLOCKED** | Requires true-alpha producer, anti-fringe/trim gates, and portal validation |
| Seamless pattern | **GATED** | Edge continuity is testable; commercial review remains separate |

## Learning loop

Every completed or rejected generation must be reviewed and recorded in the append-only project ledger with `portfolio evaluate`. `portfolio learning-summary` aggregates the evidence by niche and buyer job and returns conservative actions such as `INSUFFICIENT_EVIDENCE`, `REFINE_BRIEF`, `PAUSE_AND_RESEARCH`, or `KEEP_AND_VALIDATE`. These actions are decision support only. They do not predict sales, ranking, approval, or automatically trigger a new generation.

Execution snapshots retain the buyer job, asset specification, and format route. Historical Android absolute plan paths are normalized safely to the basename and reloaded only from the current project-local `portfolio-plans/` directory. The learning layer must never overwrite the original master or silently mutate a prompt.

## Android output contract

The only user-facing StockForge folder is:

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/
├── PREVIEW_TO_MANUS/       # review images only
└── READY_UPLOAD_ADOBE/     # explicitly approved JPEG upload copies only
```

The user removed old Download export folders. The process workspace `/storage/emulated/0/StockForge/` remains intact because it contains the database, plans, artifacts, evaluations, master lineage, Kaggle requests/results, and technical bundles. The code repository is `$HOME/stockforge-ai`. HF Space and Kaggle remote services are unchanged.

Source code defines `USER_VISIBLE_ROOT = "MACHINE STOCKFORGE"`. Preview export copies one visual to `PREVIEW_TO_MANUS`. Approved upload preparation copies one JPEG per asset to `READY_UPLOAD_ADOBE`. CSV, XMP sidecars, ZIP, JSON, JSONL, Markdown, logs, request files, model weights, PNG intermediates, and database files remain in the technical project workspace. The default Adobe technical bundle destination is project-local `adobe-upload-bundles/`; it must not recreate `Download/AdobeStock/` or old review/final folders.

## Upload readiness

The upload bundle automatically creates a safe filename, title, visual-first keywords capped at 49, embedded XMP title/keywords, official CSV, reviewed Adobe category mapping, technical report, GenAI marker, and manual checklist. The category mapping for the technical mechanical component lane is Adobe **Industry**. A bundle is not marketplace approval.

The user must still inspect the JPEG at full resolution, confirm that metadata matches the visible subject, select the generative-AI disclosure, confirm rights/releases as applicable, accept Terms, pass CAPTCHA, and press Submit manually. StockForge never submits to Adobe.

## Evidence and archive

Active evidence includes the JPEG niche shortlist, niche knowledge audit, screenshot analysis, legacy screenshot recovery, technical-component pretrial specification, rotor-armature visual/market audit, and rotor-armature master finalization audit under `docs/research/`. Superseded SVG research, old pretrial notes, old portal interaction notes, and replaced operational runbooks are preserved under `docs/archive/2026-08-25/` and are not active instructions.

## Verification and safety

The source tree has passed **297 tests, 1 skipped**, with 49 non-blocking Pillow deprecation warnings; `compileall`, `git diff --check`, and the remote endpoint contract checks pass. The HF Space endpoint patch is deployed and `/gradio_api/info` exposes `generate_remote` with the seven-field contract. Do not use endpoint metadata as inference proof; the rotor-armature inference and finalizer results are separately recorded above.

Never run blind seed retries, large batches, automatic upload, automatic submission, or a new finalizer job solely because a document says “next step.” Preserve the project workspace, code repository, learning ledger, master lineage, and remote service configuration when cleaning user-facing Download folders.

## Source of truth

| Purpose | Document |
|---|---|
| Navigation | [`README.md`](README.md) |
| Current snapshot | This file |
| Continuation | [`SESSION_HANDOVER.md`](SESSION_HANDOVER.md) |
| User/engine and folder contract | [`LEARNING_LOOP_POLICY.md`](LEARNING_LOOP_POLICY.md) |
| Termux commands | [`TERMUX_CONTROL_PLANE.md`](TERMUX_CONTROL_PLANE.md) |
| Active roadmap | [`FEATURE_ROADMAP.md`](FEATURE_ROADMAP.md) |
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| History | [`CHANGELOG.md`](CHANGELOG.md) |
| Archived context | [`archive/2026-08-25/README.md`](archive/2026-08-25/README.md) |


## New JPEG hypothesis — pending explicit generation approval

On 2026-08-25, StockForge researched and selected `seed_starting_tray_propagation` as a materially distinct JPEG hypothesis from the technical mechanical component lane. The product is one isolated square raster illustration of a recognizable modular seed-starting tray with a small number of emerging seedlings, white background, no text, no label, no packet, no brand, and no people or property release requirement expected when those elements are absent.

The buyer job is gardening tutorials, horticulture education, seed-supplier articles, and growing guides. Evidence supports the clarity of this job and the recognizability of tray-based propagation workflows, but does not prove demand, ranking, approval, downloads, conversion, or sales. Adobe Stock supply search for `seed starting tray` returned 6,589 results at the research timestamp and is treated only as a supply proxy.

The new lane is registered in code with one concept and `test_cap=1`. The plan dry-run returned `seed_starting_tray_propagation--seed-tray`, delivery `jpeg`, layout `square`, background `white`, isolation `isolated`, and `human_review_required=true`. The non-provider readiness report is `READY_FOR_TRIAL` with `single_candidate_only=true`. No live generation, finalizer, upload-copy preparation, Adobe upload, or submission has occurred for this lane. A direct `portfolio generate --dry-run` invocation was not available because the sandbox has no enabled remote provider; the saved portfolio plan and pre-GPU readiness checks completed successfully without a provider call.
