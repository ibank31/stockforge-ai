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
- **Native SVG:** aktif secara lokal untuk object/icon/technical/geometric assets yang genuine editable.
- **PNG transparan:** masih blocked sampai true alpha producer, anti-fringe, trim, sRGB, dan portal validation lulus.
- **Seamless pattern:** wajib lulus `seamless_pattern` edge gate dan review visual.
- **Quote/typography dan video:** research only.

## Evidence rules

Sinyal earnings, best-seller screenshot, social engagement, dan thumbnail hanya boleh dipakai sebagai market hypothesis. Jangan mengubahnya menjadi klaim download, format asli, revenue forecast, atau repeatable demand tanpa evidence yang cukup.

Tiga original attachment yang disebut dalam handoff riset sebelumnya tidak dibuka ulang tanpa izin eksplisit. Jika evidence lokal tidak tersedia, gunakan catatan yang sudah tersimpan dengan confidence terbatas dan jangan mengarang pembacaan baru.

## GPU and marketplace safety

Setiap GPU job harus memiliki buyer hypothesis dan tujuan yang jelas. Jangan melakukan seed-only retry, batch besar, blind upscale, atau generate sebelum pre-GPU gate lulus. Jangan upload atau submit marketplace secara otomatis. Disclosure GenAI, release decision, CAPTCHA, Terms and Conditions, dan final submission tetap dilakukan manusia.

## Current engineering state

Branch remote dan lokal hanya `main`. Commit aktif terakhir adalah `7f2f730`. Test suite terakhir: **253 passed, 1 skipped**. Remote Gradio adapter memakai endpoint `generate_remote` dengan durable `stockforge_job_id`; ZeroGPU deployment memakai `remote_api.py` sebagai entrypoint programmatic.

## Output and learning contract

Future generation output may place one review visual in `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/`. Only an explicitly approved final JPEG may be copied into `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/`; the upload copy carries embedded title/keywords where supported, while category, GenAI declaration, release, CAPTCHA, Terms, and final submit remain manual portal steps. Internal JSON, CSV, logs, and review records stay inside the project workspace.

After a human review, record the result with `portfolio evaluate`. The append-only ledger at `evaluations/generation_evaluations.jsonl` is the learning source for later prompt, format, provider, and lane comparisons. Use `portfolio evaluation-summary` only as a descriptive summary; never convert it into an automatic sales or generation decision.

## Next safe work

Continue with deterministic contract hardening, evaluation workflows, and format-specific tests. Do not generate now. Do not activate the PNG production route before alpha pipeline and portal validation are complete. A future generation requires a documented hypothesis, one controlled candidate, full review, and an evaluation record before it can inform any future engine change.
