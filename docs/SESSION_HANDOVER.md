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
