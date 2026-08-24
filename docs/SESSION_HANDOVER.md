# StockForge Active Session Handover

**Updated:** 2026-08-24
**Branch:** `main`

## Continue from here

StockForge adalah asset factory berbasis Android/Termux. Termux menjadi control plane; inference berat dijalankan oleh provider remote; hasil dikembalikan ke project untuk artifact, provenance, QA, metadata, dan human review.

Mulai sesi baru dengan membaca:

1. [`STATUS.md`](STATUS.md) untuk snapshot terbaru.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) untuk alur sistem.
3. [`research/FORMAT_AND_NICHE_DECISION_2026-08-24.md`](research/FORMAT_AND_NICHE_DECISION_2026-08-24.md) untuk keputusan niche/format.
4. [`TERMUX_CONTROL_PLANE.md`](TERMUX_CONTROL_PLANE.md) untuk operasi Android.

## Current product decision

- **JPEG raster:** aktif untuk scene konseptual, surreal, seasonal, workplace, nature, dan visual dengan lighting/depth kompleks.
- **Native SVG:** aktif secara lokal untuk genuine editable object/icon/technical/geometric assets; default `native_object` sekarang adalah research-backed `folder-upload` single icon.
- **PNG transparan:** masih blocked sampai true alpha producer, anti-fringe, trim, sRGB, dan portal validation lulus.
- **Seamless pattern:** wajib lulus `seamless_pattern` edge gate dan review visual.
- **Quote/typography dan video:** research only.

## Evidence rules

Sinyal earnings, best-seller screenshot, social engagement, dan thumbnail hanya boleh dipakai sebagai market hypothesis. Jangan mengubahnya menjadi klaim download, format asli, revenue forecast, atau repeatable demand tanpa evidence yang cukup.

Tiga original attachment yang disebut dalam handoff riset sebelumnya tidak dibuka ulang tanpa izin eksplisit. Jika evidence lokal tidak tersedia, gunakan catatan yang sudah tersimpan dengan confidence terbatas dan jangan mengarang pembacaan baru.

## GPU and marketplace safety

Setiap GPU job harus memiliki buyer hypothesis dan tujuan yang jelas. Jangan melakukan seed-only retry, batch besar, blind upscale, atau generate sebelum pre-GPU gate lulus. Jangan upload atau submit marketplace secara otomatis. Disclosure GenAI, release decision, CAPTCHA, Terms and Conditions, dan final submission tetap dilakukan manusia.

## Current engineering state

Branch remote dan lokal hanya `main`. Folder-upload SVG lane changes are committed at `28e1c85`, single-trial evidence at `ace69e7`, higher-value icon-set/micro-set preparation plus global market notes at `9425b54`, platform metadata relevance safeguards at `7114f00`, micro-set trial evidence at `72cbae4`, expert UI evaluation at `ba4a129`, and the JPEG maturation plan/research at `4e1b149` on `main`. Current SVG evidence is stored under `trial_outputs/`; its future value-upgrade plan is frozen. JPEG is now the active maturation track. Test suite terakhir: **282 passed, 1 skipped**. The file-flow micro-set trial used execution `da022148-f283-48c2-aa6d-41874bf59716` and artifact `47491fba-4303-4203-8bf5-218852f7cdce`; structural status PASS, expert buyer review archived, marketplace validation pending. The JPEG route has a verified historical preview→finalizer→XMP workflow, but the target-runtime Real-ESRGAN benchmark and provider-backed semantic QA pass remain incomplete. Remote Gradio adapter memakai endpoint `generate_remote` dengan durable `stockforge_job_id`; ZeroGPU deployment memakai `remote_api.py` sebagai entrypoint programmatic.

## Output and learning contract

Future generation output may place one review visual in `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/`. Only an explicitly approved final JPEG may be copied into `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/`; the upload copy carries embedded title/keywords where supported, while category, GenAI declaration, release, CAPTCHA, Terms, and final submit remain manual portal steps. Internal JSON, CSV, logs, and review records stay inside the project workspace.

After a human review, record the result with `portfolio evaluate`. The append-only ledger at `evaluations/generation_evaluations.jsonl` is the learning source for later prompt, format, provider, and lane comparisons. Use `portfolio evaluation-summary` only as a descriptive summary; never convert it into an automatic sales or generation decision.

## Next safe work

The asset-type selector, readiness report, trial-readiness guard, and native SVG presets are complete. The rejected local modular-ribbon SVG trial remains evidence: structural status PASS, commercial status rejected at **2/10** because the buyer could not identify the object or its use. The folder-upload and file-flow micro-set SVG trials remain evidence with structural PASS and human commercial review archived; neither is upload-approved. The expert UI evaluation rates the micro-set **8.0/10** but identifies low-medium uniqueness, only eight icons, generic subject matter, and packaging/variant gaps. SVG value-upgrade is frozen while JPEG is matured. JPEG research and the active plan are in `docs/research/JPEG_MATURATION_PLAN_2026-08-24.md` and `docs/research/jpeg_market_2026-08-24.md`. Do not mark JPEG upload-ready or claim portal acceptance until the target-runtime finalizer benchmark, semantic/commercial review, metadata review, and explicit human approval pass. PNG remains blocked until an alpha-capable path and portal validation are complete.
