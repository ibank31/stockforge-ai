# StockForge Session Handover — Active Baseline

**Updated:** 2026-08-25
**Branch:** `main`
**Baseline documentation commit:** `6d663ec`
**Deployed HF Space:** `935faa5` — runtime `RUNNING`, domain `READY`
**Current product track:** JPEG technical mechanical component
**Current asset:** rotor-armature
**Submission state:** upload-copy preparation is authorized/available but not yet verified in `READY_UPLOAD_ADOBE`; Adobe upload remains manual and has not been submitted

## Start here

Agent berikutnya harus membaca dokumen ini, lalu `docs/STATUS.md`, `docs/LEARNING_LOOP_POLICY.md`, dan `docs/TERMUX_CONTROL_PLANE.md`. Jangan memulai audit repository dari nol. Dokumen lama dan eksperimen yang tidak aktif berada di `docs/archive/2026-08-25/` dan dipertahankan sebagai sejarah, bukan instruksi.

## User responsibility contract

Pengguna adalah kontributor microstock pemula. Pengguna tidak perlu menentukan niche, buyer job, prompt, negative prompt, format, provider, kategori, keyword, atau jalur finalizer. StockForge memilih semua itu berdasarkan evidence market, buyer utility, technical readiness, compliance risk, cost, dan prior reviewed outcomes. Pengguna hanya memberi penilaian visual sederhana ketika diminta dan melakukan langkah portal manual.

StockForge tidak boleh mengubah satu hasil visual menjadi klaim demand, ranking, approval, atau sales probability. Setiap generation adalah bounded experiment dan harus masuk ke evaluation ledger setelah review. Gunakan `portfolio learning-summary` sebagai decision support konservatif; summary tidak memicu generation, tidak mengubah prompt secara diam-diam, dan tidak memprediksi penjualan.

## Verified JPEG workflow

Workflow resmi yang sudah terbukti adalah:

```text
market evidence and buyer job
  → portfolio plan and one brief
  → dry-run and pre-GPU gates
  → one ZeroGPU preview
  → project artifact, provenance, and review package
  → simple human visual review
  → portfolio evaluate and portfolio learning-summary
  → prepare-master
  → one approved private Kaggle finalizer job
  → import-kaggle-master
  → 4096×4096 RGB/sRGB JPEG technical gate
  → full-resolution visual audit
  → prepare-adobe-upload --latest-master --approved
  → JPEG/XMP/CSV/checklist package
  → manual Adobe upload and submission
```

The rotor-armature trial is the verified reference. Preview execution: `d3c2c121-77c7-590c-97b1-3da15ff26dcc`. Preview artifact: `d419cdcf-da49-49f8-98c4-5ef4c8415920`. The preview reached remote inference and completed sampling. The imported master is 4096×4096, 16.777216 MP, RGB, embedded sRGB, JPEG quality 95, and 4:4:4. It passed the deterministic technical gate and four-tile 100% audit. Its positioning is a conceptual electromechanical rotor/armature illustration, not CAD, blueprint, dimensionally accurate engineering documentation, certified equipment, or manufacturer-specific content.

The private Kaggle finalizer job completed successfully. Do not submit another finalizer job for this asset. The remaining authorized operation is to prepare the upload copy using the finalized-master execution selected by `--latest-master`; this copy has not been verified in `READY_UPLOAD_ADOBE` yet. Never pass the preview execution ID to `prepare-adobe-upload`.

## Android folder contract

The only user-facing StockForge folder is:

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/
├── PREVIEW_TO_MANUS/       # review images only
└── READY_UPLOAD_ADOBE/     # explicitly approved JPEG upload copies only
```

The old Download export folders were deleted by the user. The process workspace `/storage/emulated/0/StockForge/` was preserved because it contains the project database, plans, artifacts, evaluation ledger, master lineage, Kaggle requests, and technical bundles. The code repository is `$HOME/stockforge-ai`. HF and Kaggle are remote services and were not deleted. Documentation has been consolidated; superseded plans and runbooks are in `docs/archive/2026-08-25/`.

Source code now defines `USER_VISIBLE_ROOT = "MACHINE STOCKFORGE"`. Preview export writes only one visual file to `PREVIEW_TO_MANUS`. Approved upload export writes only one JPEG per asset to `READY_UPLOAD_ADOBE`. The default Adobe bundle destination is the project-local `adobe-upload-bundles/`; it must not recreate `Download/AdobeStock/` or any other Download folder. JSON, CSV, XMP sidecars, ZIP, Markdown, logs, request files, model weights, PNG intermediates, and databases are technical files and must remain in the project workspace.

## Current files and manual boundary

The final master remains in the project `masters/` directory. The upload bundle command creates a safe filename, title, visual-first keywords with a maximum of 49, embedded XMP, official CSV, automatic Adobe category mapping for this lane to Industry, technical report, GenAI disclosure marker, and manual checklist. The JPEG copied to `READY_UPLOAD_ADOBE` is the only file intended for manual portal selection. The user must still inspect the JPEG, verify the portal fields, select the generative-AI disclosure, confirm rights/releases as applicable, accept Terms, pass CAPTCHA, and press Submit manually.

## Commands and safety

Always synchronize Termux with `git pull --ff-only origin main` while on `main`. For a new niche, let StockForge choose the brief from a documented lane and run exactly one candidate unless a new evidence-based decision authorizes otherwise. Do not perform seed-only retries, blind batches, automatic upload, or automatic submission.

After every completed or rejected visual review, record the outcome with `portfolio evaluate` and inspect `portfolio learning-summary`. Keep the original master unchanged. Prepare an upload bundle only after the master passes technical and visual review and the user explicitly approves the preparation step.

## Active non-JPEG state

SVG value-upgrade remains frozen. PNG production remains blocked until a true-alpha producer, anti-fringe/trim gates, and portal validation are complete. These tracks are not reasons to reopen archived documents or generate additional files during the JPEG upload test.

## Evidence and archive rule

Historical screenshot notes, market counts, Adobe guidance, and prior SVG experiments remain evidence with their original limitations. They do not prove sales, ranking, demand, or acceptance. Current decisions belong in `STATUS.md`; implementation history belongs in `CHANGELOG.md`; operational instructions belong here and in `TERMUX_CONTROL_PLANE.md`. Archived documents must not override the active baseline.


## New JPEG hypothesis selected — generation still gated

The 2026-08-25 research session selected `seed_starting_tray_propagation` as the next materially distinct JPEG hypothesis. The single candidate is `seed_starting_tray_propagation--seed-tray`: one recognizable modular seed-starting tray with a small number of emerging seedlings, isolated on a clean white square background. The intended buyer job is gardening tutorials, horticulture education, seed-supplier articles, and growing guides.

Evidence is conservative. Public horticulture guides support the recognizability and tutorial context of trays, modules, compost, seedlings, labeling, watering, and indoor propagation. Adobe search returned 6,589 results for `seed starting tray` at the research timestamp; this is only a supply proxy, not demand or sales proof. Adobe and Getty trend guidance supports authentic, specific, useful visual communication but does not prove marketplace conversion.

The lane and JPEG identity are registered in `src/stockforge/portfolio.py` and `src/stockforge/jpeg_niche_identity.py`. The lane has `test_cap=1`, no people/property subject, no labels or brands, and manual category review only. Full regression verification is `298 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings`. The portfolio plan dry-run and readiness report passed locally without a provider call. A direct `portfolio generate --dry-run` was blocked by the sandbox's lack of an enabled remote provider; this does not authorize enabling a provider or running generation.

Next action requires explicit user approval of this exact hypothesis and brief. If approved, synchronize Termux from `main`, confirm the provider path and pre-GPU gates, then execute exactly one ZeroGPU preview. Do not run a retry, batch, Kaggle finalizer, upload preparation, Adobe upload, or submission before the prescribed review and learning-loop gates.


## Seed-starting tray master completed — upload still gated

The user gave `keep` for the single `seed_starting_tray_propagation--seed-tray` preview and noted one apparently empty tray cell. The observation was recorded as a non-blocking natural variation under the brief, with no retry. The evaluation ledger contains one accepted record: visual 4/5, technical 3/5 because the source was a 1024px WebP preview, buyer fit 4/5, metadata accuracy 4/5, overall 3.75/5. `portfolio learning-summary` returned `INSUFFICIENT_EVIDENCE`, correctly stating that one review cannot establish demand or a niche policy.

One private Kaggle finalizer job completed on `iqbalteguh/stockforge-finalizer` using `RealESRGAN_x4plus` at 4×. Master artifact `20032d2f-3ef2-43a2-a103-cb2707fe10ed`, master execution `83709936-fae9-4643-bd07-bb332b3ba455`, file `masters/b8c4cc8b-6002-4c09-b3d5-1dd7725f3ca9-master.jpg`. The Adobe deterministic gate passes: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, decodable, 1,451,346 bytes, quality 95, and 4:4:4 subsampling.

The master was reviewed in the whole-image view and all nine ordered overlapping 100% tiles. No readable text, label, logo, watermark, person, hand, seed packet, severe crop loss, major halo, or duplicated structural geometry was observed. Minor bright specks on gray plastic and somewhat smooth AI-upscaled leaf texture remain marketplace-review notes. The master remains `review_ready` / `visual_review_required`. No upload-copy, Android export, Adobe upload, or submission has occurred. Next action requires explicit approval before `portfolio prepare-adobe-upload`; if approved, metadata and category must still be reviewed truthfully and the portal submission remains manual.


## Next illustration lane — preview approval pending

The user reports that the seed-starting tray was manually uploaded to Adobe Stock; no moderation, acceptance, download, revenue, or sales evidence was provided. A materially distinct illustration hypothesis is now prepared: `pet_enrichment_object_illustrations--puzzle-feeder`. The selected object is one square isolated JPEG illustration of an interactive treat-puzzle feeder board with rounded compartments and generic treat pieces, without animals, people, brands, labels, or text.

Evidence is recorded in `docs/research/NEW_ILLUSTRATION_NICHE_RESEARCH_2026-08-25.md`. Buyer-job evidence comes from ASPCA and RSPCA pet-enrichment guidance; Adobe exact-query proxy is 339 results for `pet enrichment toy illustration`, compared with much denser sourdough/fermentation queries. This is evidence for a controlled test, not a sales or demand claim.

Lane registration and the `product_illustration` asset family are complete. Targeted tests passed 17/17; full suite passed 299 passed, 1 skipped, and 49 non-blocking Pillow deprecation warnings. Portfolio batch `pet_enrichment_object_illustrations-20260825T064838Z-60a86ece` was created. Dry-run reports `gpu_eligible=true`, seven checks pass, zero blockers, remote provider route `huggingface-zerogpu`, profile `z-image-turbo`, square 1024×1024 preview, and estimated 55 GPU seconds. No provider call or generation has occurred.

Next allowed action is exactly one preview only after the user explicitly approves this exact brief. Do not run live generation, retries, batches, finalizer, upload preparation, or submission before that approval.
