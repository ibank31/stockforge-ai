# StockForge Active Session Handover

**Updated:** 2026-08-25
**Branch:** `main`
**Latest GitHub commit:** `058f3cb`
**Deployed Space commit:** `935faa5` (runtime `RUNNING`, domain `READY`)
**Latest trial:** execution `d3c2c121-77c7-590c-97b1-3da15ff26dcc`, artifact `d419cdcf-da49-49f8-98c4-5ef4c8415920`, package `review_ready`

## Continue from here

StockForge adalah asset factory berbasis Android/Termux. Termux menjadi control plane; inference berat dijalankan oleh provider remote; hasil dikembalikan ke project untuk artifact, provenance, QA, metadata, dan human review.

Mulai sesi baru dengan membaca:

1. [`STATUS.md`](STATUS.md) untuk snapshot terbaru.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) untuk alur sistem.
3. [`research/FORMAT_AND_NICHE_DECISION_2026-08-24.md`](research/FORMAT_AND_NICHE_DECISION_2026-08-24.md) untuk keputusan niche/format.
4. [`TERMUX_CONTROL_PLANE.md`](TERMUX_CONTROL_PLANE.md) untuk operasi Android.

## Current product decision

- **JPEG raster:** aktif untuk scene konseptual, surreal, seasonal, workplace, nature, dan visual dengan lighting/depth kompleks.
- **Native SVG:** future plan/frozen selama JPEG dimatangkan; evidence lokal dan rencana value-upgrade tetap diarsipkan, tetapi tidak ada SVG trial/expansion aktif.
- **PNG transparan:** masih blocked sampai true alpha producer, anti-fringe, trim, sRGB, dan portal validation lulus.
- **Seamless pattern:** wajib lulus `seamless_pattern` edge gate dan review visual.
- **Quote/typography dan video:** research only.

## Evidence rules

Sinyal earnings, best-seller screenshot, social engagement, dan thumbnail hanya boleh dipakai sebagai market hypothesis. Jangan mengubahnya menjadi klaim download, format asli, revenue forecast, atau repeatable demand tanpa evidence yang cukup.

Tiga original attachment yang disebut dalam handoff riset sebelumnya tidak dibuka ulang tanpa izin eksplisit. Jika evidence lokal tidak tersedia, gunakan catatan yang sudah tersimpan dengan confidence terbatas dan jangan mengarang pembacaan baru.

## GPU and marketplace safety

Setiap GPU job harus memiliki buyer hypothesis dan tujuan yang jelas. Jangan melakukan seed-only retry, batch besar, blind upscale, atau generate sebelum pre-GPU gate lulus. Jangan upload atau submit marketplace secara otomatis. Disclosure GenAI, release decision, CAPTCHA, Terms and Conditions, dan final submission tetap dilakukan manusia.

## Current engineering state

Branch remote dan lokal hanya `main`. Folder-upload SVG lane changes are committed at `28e1c85`, single-trial evidence at `ace69e7`, higher-value icon-set/micro-set preparation plus global market notes at `9425b54`, platform metadata relevance safeguards at `7114f00`, micro-set trial evidence at `72cbae4`, expert UI evaluation at `ba4a129`, JPEG maturation plan/research at `4e1b149`, JPEG scene prompt safety at `0bb3f68`, and the JPEG metadata-preflight milestone at `3b7d7c3` on `main`. Current SVG evidence is stored under `trial_outputs/`; its future value-upgrade plan is frozen. JPEG is now the active maturation track. The committed milestone adds `portfolio metadata-preflight`, a non-upload report across Adobe Stock, Shutterstock, Freepik, Creative Market, and Etsy that reorders only existing visual terms and leaves category selection/upload manual. A follow-up local milestone adds a nine-lane `JpegNicheIdentity` registry with signature, lighting, framing, context, distinctness anchors, and prohibited shorthand persisted into JPEG AssetSpecs and compiled prompts; it is art-direction infrastructure, not demand or output-quality proof. Test suite before this documentation sync: **287 passed, 1 skipped**. The file-flow micro-set trial used execution `da022148-f283-48c2-aa6d-41874bf59716` and artifact `47491fba-4303-4203-8bf5-218852f7cdce`; structural status PASS, expert buyer review archived, marketplace validation pending. The JPEG route has a verified historical preview→finalizer→XMP workflow, but the target-runtime Real-ESRGAN benchmark and provider-backed semantic QA pass remain incomplete. The JPEG scene prompt now allows approved human-centered commercial stories while keeping the stricter isolated-object guard. Remote Gradio adapter memakai endpoint `generate_remote` dengan durable `stockforge_job_id`. The active ZeroGPU Space `app.py` now registers that endpoint directly: Space commit `935faa5` is live, `/gradio_api/info` exposes `/generate_remote` with the seven-field contract, and startup logs show successful Gradio boot without the old `FnIndexInferError`. This proves endpoint deployment only; one fresh trial was subsequently authorized. The worker loaded all models and completed 8/8 sampling steps on the successful final request. The corrected context-routing fix reads the actual minimal `portfolio_snapshot` context, so the Termux path now persists the execution, artifact, review package, and Android preview export. The preview is available at `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/technical-mechanical-component-illustrations-rotor-armature__preview.webp`. No final JPEG master exists yet; no upscale, Kaggle run, upload, or submission was performed. Human visual review is required before any finalization decision.

## Output and learning contract

Future generation output may place one review visual in `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/`. Only an explicitly approved final JPEG may be copied into `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/`; the upload copy carries embedded title/keywords where supported, while category, GenAI declaration, release, CAPTCHA, Terms, and final submit remain manual portal steps. Internal JSON, CSV, logs, and review records stay inside the project workspace.

After a human review, record the result with `portfolio evaluate`. The append-only ledger at `evaluations/generation_evaluations.jsonl` is the learning source for later prompt, format, provider, and lane comparisons. Use `portfolio evaluation-summary` only as a descriptive summary; never convert it into an automatic sales or generation decision.

## Next safe work

The asset-type selector, readiness report, trial-readiness guard, and native SVG presets are complete. The ZeroGPU endpoint deployment and non-inference API verification are complete; do not infer model-inference success from this proof. The rejected local modular-ribbon SVG trial remains evidence: structural status PASS, commercial status rejected at **2/10** because the buyer could not identify the object or its use. The folder-upload and file-flow micro-set SVG trials remain evidence with structural PASS and human commercial review archived; neither is upload-approved. The expert UI evaluation rates the micro-set **8.0/10** but identifies low-medium uniqueness, only eight icons, generic subject matter, and packaging/variant gaps. SVG value-upgrade is frozen while JPEG is matured. JPEG research and the active plan are in `docs/research/JPEG_MATURATION_PLAN_2026-08-24.md` and `docs/research/jpeg_market_2026-08-24.md`. Before any future upload, run `portfolio metadata-preflight` on the reviewed JPEG brief; it is report-only, does not upload, and does not guess a category. JPEG identity profiles now make each lane more distinctive at prompt-contract level, but do not replace a lane-specific buyer hypothesis, target-runtime finalizer benchmark, semantic/commercial review, metadata review, or explicit human approval. A new evidence-bound report, `docs/research/ADOBE_STOCK_BEST_SELLER_SCREENSHOT_ANALYSIS_2026-08-25.md`, analyzes ten user screenshots and identifies multiple product families. `docs/research/LEGACY_BEST_SELLER_EVIDENCE_RECOVERY_2026-08-25.md` recovers 31 historical screenshot records from the prior Git handover; the old raw/tile folders are unavailable in the current sandbox, so those rows are not re-verified imagery. `docs/research/FIRST_SALE_JPEG_NICHE_SHORTLIST_2026-08-25.md` identifies Technical Mechanical Component Illustrations as the lowest-burden next research hypothesis because two mechanical examples recur, but it is not a proven high-demand lane. Official Adobe content-need guidance and catalog result counts are signals, not sales proof. Do not mark JPEG upload-ready or claim portal acceptance until all of the target-runtime benchmark, semantic/commercial review, metadata review, and explicit human approval pass. PNG remains blocked until an alpha-capable path and portal validation are complete.


## 2026-08-25 — User-simple decision and niche-learning contract

The user is a first-time microstock contributor and does not want to choose niches, buyer jobs, prompts, negative prompts, formats, providers, categories, or metadata. StockForge must own those decisions using explicit market evidence, buyer utility, technical readiness, compliance risk, cost, and prior reviewed outcomes. The user should only be asked for a simple visual verdict when needed; the agent must perform the detailed technical, buyer-fit, metadata, and market audit and explain the resulting evaluation.

Every generation is a bounded experiment and must become learning evidence after review. `evaluations/generation_evaluations.jsonl` remains append-only. The new `portfolio learning-summary` command aggregates reviewed records by lane and buyer job and returns conservative recommendations such as `INSUFFICIENT_EVIDENCE`, `REFINE_BRIEF`, `PAUSE_AND_RESEARCH`, or `KEEP_AND_VALIDATE`. These are decision-support labels only: they do not predict sales, ranking, approval, or automatically trigger generation.

Future execution snapshots now use schema version 2 and retain buyer job, asset specification, and format route. The evaluation command can also reconstruct the brief from the historical saved plan for older executions whose snapshot was intentionally minimal. The foundation is covered by tests; no new generation is authorized merely because the learning summary exists.

The rotor-armature preview audit concluded: strong visual recognizability and silhouette, moderate buyer utility, promising but unproven niche hypothesis, review-ready WebP only, no final JPEG, and no marketplace submission. See `docs/research/ROTOR_ARMATURE_TRIAL_VISUAL_MARKET_AUDIT_2026-08-25.md` and `docs/LEARNING_LOOP_POLICY.md`.

Do not reopen prohibited image `1000802462.jpg`. Do not run another GPU request, upscale, Kaggle job, upload, or submission without a new explicit decision after the visual audit.


## 2026-08-25 — Historical evaluation path fix

The first attempt to record the successful rotor-armature trial in the learning ledger failed because Termux was still on `e082695`. After syncing `b3a6291`, the historical fallback correctly activated but rejected the old execution's Android absolute `plan_file`. The fix now strips the directory and loads only the JSON basename from the current project-local `portfolio-plans/` directory; no absolute path is trusted. Full suite after this fix: 295 passed, 1 skipped, 49 non-blocking Pillow warnings. This is a no-GPU code/documentation fix. Do not regenerate the rotor-armature image because of this ledger issue.


## 2026-08-25 — Rotor-armature master finalized

The one authorized private Kaggle finalizer job completed successfully. The imported master is `/storage/emulated/0/StockForge/projects/stock-assets/masters/d419cdcf-da49-49f8-98c4-5ef4c8415920-master.jpg`, 4096×4096, 16.777216 MP, RGB, embedded sRGB, JPEG quality 95, 4:4:4. It passed the deterministic Adobe-oriented technical gate and a four-tile full-resolution audit. The master remains `visual_review_required`: it is a conceptual electromechanical illustration with strong silhouette and clean winding continuity, but it must not be described as CAD, blueprint, dimensionally accurate, certified, standard-compliant, or manufacturer-specific.

The review package is `/storage/emulated/0/StockForge/projects/stock-assets/deliveries/stockforge-6b828979-3d26-485d-a33e-5b6b92c0991a.zip`. No `READY_UPLOAD_ADOBE` copy exists and no marketplace submission has occurred. Do not prepare the upload bundle until the user explicitly approves after the final master audit; even then, portal declarations, generative-AI disclosure, category, title, and keywords require final manual verification.
