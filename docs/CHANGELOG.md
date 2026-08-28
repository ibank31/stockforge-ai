# StockForge AI — Changelog

## 2026-08-29 — Enforce PNG/JPEG-only active scope

Added a repository-level `AGENTS.md` and `docs/ACTIVE_SCOPE.md` that make PNG and JPEG the only active production outputs. Updated the README, documentation index, canonical workflow, and status snapshot so historical SVG/vector, batch, local-AI, provider-trial, and pretrial material is explicitly non-authoritative. Clarified that `pet_enrichment_object_illustrations → puzzle-feeder` is a JPEG contract.

## 2026-08-26 — Traditional food global asset research

### DONE — country-based catalog, priority tiers, and agent handoff

- Added the operational research handoff for producing traditional-food assets by country with P0/P1/P2 sequencing; this is a production-priority framework, not a sales forecast or cross-country cultural ranking.
- Added a 63-row global seed catalog, a 32-row Indonesia regional catalog, reproducible catalog summary JSON, and CSV/document validation scripts.
- Added evidence-bound guidance for food identity, regional context, metadata, generative-AI disclosure, cultural-risk controls, standalone JPEG pilots, and continuation workflow.
- Work is isolated on branch `research/traditional-food-niches-2026`; no generation, upload, submission, or modification to `main` was performed.

## 2026-08-25 — Seed-starting tray master finalized and audited

### REVIEW_READY — one approved preview, one private finalizer, no upload

- Recorded the user's `keep` verdict for `seed_starting_tray_propagation--seed-tray` with conservative scores: visual 4/5, technical 3/5, buyer fit 4/5, metadata accuracy 4/5, overall 3.75/5.
- `portfolio learning-summary` returned `INSUFFICIENT_EVIDENCE`; one review does not establish demand, ranking, approval, downloads, conversion, or sales.
- Submitted exactly one private Kaggle finalizer job on `iqbalteguh/stockforge-finalizer` using `RealESRGAN_x4plus` at 4×. Imported master artifact `20032d2f-3ef2-43a2-a103-cb2707fe10ed` with execution `83709936-fae9-4643-bd07-bb332b3ba455`.
- Master passed deterministic Adobe checks: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, decodable, 1,451,346 bytes, quality 95, and 4:4:4 subsampling.
- Added `docs/research/SEED_STARTING_TRAY_MASTER_AUDIT_2026-08-25.md` with nine-tile full-resolution review. One apparently empty cell is recorded as a non-blocking natural variation; minor bright plastic specks and smooth leaf texture remain human review notes.
- Master remains `review_ready` / `visual_review_required`. No retry, second finalizer, upload-copy, Android export, Adobe upload, or marketplace submission occurred. Separate explicit approval is required before `portfolio prepare-adobe-upload`.

## 2026-08-25 — New JPEG seed-starting hypothesis prepared

### READY — evidence-bound lane and pre-GPU dry-run

- Added the materially distinct `seed_starting_tray_propagation` JPEG lane with one registered concept, `seed-tray`, and `test_cap=1`.
- Added a niche-specific identity covering modular cell-tray geometry, seedling-stage clarity, moisture/compost material relationship, and propagation-specific silhouette; prohibited brand packets, readable labels, named cultivars, garden-tool piles, greenhouse clutter, certification marks, environmental claims, botanical patterns, and generic plant pots.
- Added public evidence research under `docs/research/NEW_JPEG_NICHE_RESEARCH_2026-08-25.md`. The selection is a conservative hypothesis, not a demand, ranking, approval, download, conversion, or sales claim.
- The saved plan dry-run passed with `jpeg` / `square` / `white` / `isolated`, `human_review_required=true`, and one candidate only. Trial readiness passed as `READY_FOR_TRIAL`; no provider call was made.
- Full regression suite after the lane integration: **298 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.
- A direct `portfolio generate --dry-run` was not available in the sandbox because no enabled remote provider was configured. No provider was enabled, and no live generation, finalizer, upload-copy preparation, Adobe upload, or submission occurred.

## 2026-08-25 — Adobe keyword ceiling corrected

### FIXED — enforce 49-keyword maximum

- Corrected the upload bundle ceiling from 50 to **49 keywords** to match Adobe's current contributor guidance.
- Added boundary regression coverage for exactly 49 keywords and rejection at 50.
- Full suite after the correction: **297 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.

## 2026-08-25 — Automatic category and upload metadata path

### DONE — engine-owned metadata, manual-only portal boundary

- Added automatic Adobe category mapping for `technical_mechanical_component_illustrations` to category **10 — Industry**, based on Adobe's published category definition for work and manufacturing content.
- Confirmed the existing bundle builder automatically generates a safe JPEG filename, title, visual-first keyword list, official CSV, embedded XMP metadata, technical-gate report, generative-AI declaration marker, and manual checklist.
- The upload bundle remains explicitly non-submitting: it requires a reviewed master and explicit approval to prepare files, but it never clicks submit, completes CAPTCHA, or silently asserts rights/marketplace acceptance.
- Full suite after the mapping: **296 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.

## 2026-08-25 — Rotor-armature master finalized and audited

### DONE — Kaggle 4× finalizer, JPEG gate, and full-resolution review

- One private Kaggle `RealESRGAN_x4plus` finalizer job completed successfully and was imported into StockForge with preserved preview-to-master lineage.
- Master `d419cdcf-da49-49f8-98c4-5ef4c8415920-master.jpg` passed deterministic checks: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, quality 95, and 4:4:4 subsampling.
- The 4096×4096 master was inspected through four ordered overlapping tiles. No blocking duplicated shaft, broken ring, severe winding smear, readable text/logo, or major halo was observed; stylized geometry remains a positioning limitation.
- Added `docs/research/ROTOR_ARMATURE_MASTER_FINALIZATION_AUDIT_2026-08-25.md`. The master remains `visual_review_required`; no Adobe upload copy or submission was created.

## 2026-08-25 — Historical evaluation path normalization

### FIXED — Android absolute plan paths

- Diagnosed the second ledger failure: Termux had reached the new historical fallback, but the old execution stored an Android absolute `plan_file`, which the project-local loader correctly rejected.
- Added fail-closed normalization that keeps only the JSON basename and reloads it inside the current project's `portfolio-plans/` directory. No absolute directory is trusted.
- Added regression coverage for Android-style absolute paths and invalid plan references.
- Full suite after the fix: **295 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.

## 2026-08-25 — Evidence-to-learning operating contract

### DONE — user-simple feedback, engine-owned decisions

- Added `src/stockforge/niche_learning.py` and `portfolio learning-summary` to aggregate reviewed generation records by niche and buyer job.
- The learning layer emits conservative actions such as `INSUFFICIENT_EVIDENCE`, `REFINE_BRIEF`, `PAUSE_AND_RESEARCH`, and `KEEP_AND_VALIDATE`; it never predicts sales, ranking, or marketplace approval and never triggers generation.
- Upgraded `portfolio_snapshot` to schema version 2 so future executions persist buyer job, asset specification, and format route with immutable lineage.
- Added historical-plan fallback to `portfolio evaluate`, allowing older executions with minimal snapshots to be evaluated from their saved plan instead of failing closed unnecessarily.
- Added regression tests for one-record uncertainty, repeated review refinement, append-only learning summaries, and the real snapshot structure. Full suite: **294 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.
- Added `docs/LEARNING_LOOP_POLICY.md` to define the operating model: StockForge chooses product decisions; the user supplies simple visual feedback; the agent explains and records the evaluation; the next decision cites the ledger.

## 2026-08-25 — Rotor-armature trial completed end-to-end

### LIVE — review package created; visual review pending

- The authorized `technical_mechanical_component_illustrations--rotor-armature` trial completed with exit code `0` after the WebP preview context-routing correction.
- Job: `8ae398e9-1c15-4ab6-9959-6405cb95bfc3`; execution: `d3c2c121-77c7-590c-97b1-3da15ff26dcc`; artifact: `d419cdcf-da49-49f8-98c4-5ef4c8415920`.
- The review package was created at the Termux project delivery path with status `review_ready`.
- Android export succeeded to `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/technical-mechanical-component-illustrations-rotor-armature__preview.webp`.
- This confirms the remote generation, durable execution persistence, WebP preview handling, release packaging, and preview export path. It does not confirm visual quality, buyer fit, final JPEG technical readiness, marketplace acceptance, or sales potential.
- No upscale, Kaggle run, approved upload copy, Adobe upload, or submission was performed.

All meaningful implementation milestones, live validations, architectural decisions, and verified fixes are recorded here. This is intentionally separate from Git commit history so a future session can understand **what was actually proven** rather than merely what files changed.

## 2026-08-25 — Second controlled trial exposed incomplete WebP context routing

### BLOCKED — no release package returned; no further retry

- The second authorized `technical_mechanical_component_illustrations--rotor-armature` request again passed plan discovery, brief inspection, dry-run, and reached the remote worker.
- The Termux command again stopped at `No technical gate is registered for delivery format: .webp`.
- Diagnosis: the first WebP-preview patch looked for `asset_spec` or top-level `format_route`, but the real `portfolio_snapshot` intentionally stores minimal context and carries the intended delivery format under `pre_gpu_gate.format_route`. The earlier regression fixture was too complete and therefore failed to reproduce the real context.
- The corrected patch now reads `pre_gpu_gate.format_route`, and the regression fixture mirrors the actual snapshot structure. Full verification passes: **291 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.
- No third request, retry, upscale, Kaggle run, XMP export, upload, or submission is allowed until this corrected patch is committed, synchronized to Termux, and verified in the actual run path.

## 2026-08-25 — Controlled rotor-armature trial reached inference; packaging fix required

### REVIEW_REQUIRED — no release package returned

- The single authorized `technical_mechanical_component_illustrations--rotor-armature` trial passed plan discovery, brief inspection, dry-run, and the repaired remote endpoint boundary.
- Hugging Face container logs show the prompt reached the worker, all three model files loaded, and sampling completed 8/8 steps. This proves the worker proceeded through inference for this request; it does not prove commercial quality or marketplace readiness.
- Termux then stopped locally while building the review package: the provider returned a `.webp` preview, but the release builder attempted to select a final-delivery technical gate from that preview suffix and raised `No technical gate is registered for delivery format: .webp`.
- No release package was returned to the user, no retry was performed, and no upscale, Kaggle run, XMP export, upload, or submission occurred.
- A local fix now preserves WebP as a review-only preview and defers the contracted JPEG gate to finalization. The regression and full suite pass: **291 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**. The fix is prepared locally but is not yet deployed or used for another GPU request.

## 2026-08-25 — ZeroGPU endpoint patch deployed and verified

### LIVE — active Space registration fixed

- Deployed the tested worker patch from GitHub commit `c436e93` to Hugging Face Space commit `935faa56da4639260d5547fbbe4cf8d5ccd54bf3` through the authenticated Space editor.
- The Space runtime reached `RUNNING` on `zero-a10g` with domain stage `READY` and runtime SHA matching `935faa56da4639260d5547fbbe4cf8d5ccd54bf3`.
- The live Gradio metadata endpoint exposes `/generate_remote` publicly with the expected seven parameters and stable endpoint description; this is endpoint-registration proof and did not invoke inference.
- Current container startup logs show the runtime audit persisted and Gradio started successfully. The old `FnIndexInferError` is absent from the new startup log.
- No JPEG generation, retry, upscale, Kaggle run, XMP export, upload, or marketplace submission was performed. One fresh live generation still requires explicit user confirmation and remains limited to the authorized single technical mechanical component trial.


## 2026-08-25 — ZeroGPU remote endpoint registration fix

### FIXED — worker API name mismatch diagnosed from live Space logs

- Diagnosed the live HTTP 500 from Hugging Face Space logs as `gradio.routes.FnIndexInferError`: the client called `generate_remote`, but the active `app.py` registered only `generate`; `remote_api.py` was not imported by the Space entrypoint.
- Registered `generate_remote` directly on the active `app.py` demo with the durable `stockforge_job_id` cache and the existing seven-field request contract.
- Added a regression test asserting that the active worker source contains the `generate_remote` function, hidden inputs, and matching API name.
- Full sandbox verification: **290 passed, 1 skipped, 45 non-blocking Pillow deprecation warnings**; compileall and whitespace checks passed.
- At the time this incident was diagnosed, the patch was only prepared in the repository; it was subsequently deployed and verified in the dated entry above. No new image was generated by this fix.

## 2026-08-25 — Adobe Stock best-seller screenshot research

### DONE — classify product families without copying or generating

- Analyzed ten user-provided Adobe Stock best-seller screenshots directly and separated them into technical mechanical components, surreal landscape, symbolic water object, botanical motif, craft toolkit cluster, natural food macro photo, original character group, seasonal topical artwork, and culinary food illustration.
- Cross-checked the interpretation against Adobe category guidance, photo/illustration requirements, generative-AI rules, transparent PNG utility guidance, Adobe Creative Trends 2026, Creative Market garden graphics, Envato clipart categories, and public creator context.
- Recorded that the screenshots are heterogeneous; their shared lesson is recognizable focal subject, clear silhouette, memorable art direction, and imaginable buyer utility—not one universal niche.
- Identified `Technical Mechanical Component Illustrations` as the strongest next research hypothesis because two separate mechanical component examples recur, have concrete buyer jobs, and avoid people/release burden. Technical accuracy must remain conservative and human-reviewed.
- Kept character, seasonal, botanical, and PNG/transparent interpretations separated because their IP, expiry, format, and product-packaging risks differ.
- No generation, provider call, Kaggle run, upload, or submission was performed.

## 2026-08-25 — JPEG niche identity framework

### DONE — nine-lane prompt identity contract

- Added `JpegNicheIdentity` profiles for all nine JPEG lanes, each with a visual signature, lighting signature, framing rule, environmental context, distinctness anchors, and prohibited shorthand.
- Persisted the identity fields into JPEG `AssetSpec` records and restored them through the format router, so saved briefs retain the identity contract.
- Added the identity instructions to compiled JPEG prompts and niche-specific shorthand exclusions to negative prompts; SVG briefs remain unchanged.
- Added lane-by-lane regression coverage proving nine unique JPEG signatures are present in prompts and that the SVG route does not receive JPEG identity fields.
- Full verification: **287 passed, 1 skipped, 45 non-blocking Pillow deprecation warnings**. No generation, provider call, Kaggle run, upload, or submission was performed.
- This milestone improves art-direction consistency only. It does not prove market demand, buyer conversion, Adobe acceptance, semantic quality, legal clearance, or commercial superiority.

## 2026-08-24 — JPEG metadata preflight and portal category safety

### DONE — report-only marketplace metadata gate

- Added `portfolio metadata-preflight` for reviewed JPEG briefs across Adobe Stock, Shutterstock, Freepik, Creative Market, and Etsy.
- The preflight reorders only existing canonical terms using visible-subject and buyer-job context; it never invents keywords, predicts ranking, guesses categories, uploads, or submits.
- Adobe upload instructions no longer hard-code `Illustrations`; file type and category are explicitly manual and must be verified against the actual visual and current portal taxonomy.
- Added regression coverage for reorder-only behavior, platform limits, and report-only status.
- Full verification: **283 passed, 1 skipped, 45 non-blocking Pillow deprecation warnings**. No generation, provider call, Kaggle run, upload, or submission was performed.

## 2026-08-24 — JPEG scene prompt safety tuned

### DONE — conditional human-centered scene guard

- Added a JPEG-scene-specific negative prompt policy that permits approved human-centered commercial stories while retaining anatomy, text, logo, artifact, chromatic-aberration, halo, and IP safeguards.
- Isolated-object and vector routes retain the stricter no-people/hands/faces/devices policy.
- Added regression coverage for the conditional split.
- Full verification: **283 passed, 1 skipped, 45 non-blocking Pillow deprecation warnings**. No generation, provider call, Kaggle run, upload, or submission was performed.

## 2026-08-24 — File-flow micro-set trial executed for buyer-value review

### REVIEW_REQUIRED — one local controlled candidate

- Built exactly one `native_vector_utility_sets--file-flow-micro-set` candidate from the market-researched micro-set hypothesis.
- Execution: `da022148-f283-48c2-aa6d-41874bf59716`; artifact: `47491fba-4303-4203-8bf5-218852f7cdce`.
- Result: 2048×2048 transparent native SVG, eight distinct grouped actions, 33 SVG elements, structural inspector PASS.
- Visual review: the eight actions are materially more useful as a product than the single folder-upload baseline, but generic icon language, optical-size balance, and single-sheet delivery still require human buyer review.
- No remote provider, GPU, Kaggle, XMP, Adobe upload, portal submission, or ready-upload export was called. User evaluation is pending.
- Durable evidence: `trial_outputs/file_flow_micro_set/` with source SVG, whole-artboard preview, manifest, and review notes. SHA256 source: `9a84af2b2cbdf212f1ff4b7dd10f2738492332b5b2432664b968e1ffa515014b`.

## 2026-08-24 — File-flow micro-set value upgrade prepared

### DONE — product and contract preparation; no generation

- Added a separate `icon_set` asset type and `native_vector_utility_sets` lane so a higher-value micro-set is not hidden inside the single-icon baseline.
- Added the `file-flow-micro-set` hypothesis: one coherent eight-action SVG sheet covering folder, upload, download, cloud storage, sync, archive, file, and share.
- Added explicit clustered native-vector support, deterministic local builder dispatch, transparent square artboard rules, and structural tests for eight distinct editable icon groups.
- Preserved `native_object` / `folder-upload` as the baseline control and kept modular-ribbon/technical-badge as historical regression concepts.
- Added global discoverability research notes and a platform-specific, anti-spam market-intelligence plan. No ranking guarantee, keyword stuffing, duplicate submission, or automatic platform action is supported.
- Full verification after the implementation: **275 passed, 1 skipped, 45 non-blocking Pillow deprecation warnings**. No provider, GPU, Kaggle, portal, upload, or micro-set generation was performed.

## 2026-08-24 — Folder-upload SVG trial executed for human review

### REVIEW_REQUIRED — local controlled trial

- Built exactly one `native_vector_elements--folder-upload` candidate from the research-backed buyer hypothesis.
- Execution: `f397114e-179e-4992-a1e2-cae0d819d934`; artifact: `282ff154-112b-4203-acf3-92a1098987ba`.
- Produced a 2048×2048 native SVG with transparent canvas, five generated XML elements, no raster/image embed, no text, no script, and no external reference.
- Structural native-vector gate passed and `remote_gpu_called=false`; no ZeroGPU, remote provider, Kaggle, XMP, Adobe upload, portal validation, or submission was performed.
- Internal visual audit found the folder and upload action substantially more recognizable than modular-ribbon, while genericness/distinctiveness and buyer utility remain human review questions.
- Durable evidence is in `trial_outputs/folder_upload_svg/`; the source SHA256 is recorded in `TRIAL_MANIFEST.json` and `REVIEW_NOTES.md`.
- No acceptance or evaluation score was fabricated. User review is required before any `portfolio evaluate` record or future lane change.

## 2026-08-24 — Research-backed folder-upload SVG lane and semantic trial preparation

### DONE — one-candidate implementation preparation

- Completed deep research using Adobe Stock technical/design/legal guidance, Adobe and Envato trend reports, Etsy buyer-context signals, and Adobe search snapshots. The evidence supports a buyer-job-first SVG strategy rather than abstract decorative geometry.
- Added the `folder-upload` concept as the default `native_object` recommendation, tied to file management and cloud workflow use cases.
- Added a deterministic native SVG folder-upload preset with a recognizable folder silhouette, integrated upload arrow, tight square framing, transparent canvas, and no text/raster/script/external content.
- Kept `modular-ribbon` and `technical-badge` available only as legacy/regression concepts; the rejected modular-ribbon trial remains evidence that technical validity does not prove buyer-fit.
- Added regression coverage for selector resolution and folder-upload structural safety.
- Full verification: **273 passed, 1 skipped, 45 non-blocking Pillow deprecation warnings**. No provider, GPU, Kaggle, portal, upload, or new folder-upload trial was run.

## 2026-08-24 — Engine maturation: selector, SVG presets, pattern gate, metadata policy, and delivery tests

### Additional implementation

- Added structural repeatability checks for SVG `<pattern>` definitions, including positive user-space tile dimensions.
- Kept pattern visual attractiveness and marketplace utility as human-review concerns; the gate only proves structural repeatability.
- Full verification after this milestone: **271 passed, 1 skipped**; no generation, provider call, or upload was performed.

## 2026-08-24 — Engine maturation: selector, SVG presets, pattern lane, metadata policy, and delivery tests

### Additional implementation

- Added `native_vector_patterns` with one controlled `pattern-tile` brief.
- Added a native SVG geometric pattern preset using a real SVG `<pattern>` definition and local structural inspection; no raster trace or provider call is involved.
- Full verification after this milestone: **269 passed, 1 skipped**; no generation, provider call, or upload was performed.

## 2026-08-24 — Engine maturation: selector, SVG presets, metadata policy, and delivery tests

### Additional implementation

- Centralized nonvisual keyword filtering so workflow/use-case terms are excluded from portfolio drafts as well as final upload metadata.
- Preserved the existing upload-bundle constant as a compatibility alias and kept the final portal fields manual.
- Full verification after this milestone: **267 passed, 1 skipped**; no generation, provider call, or upload was performed.

## 2026-08-24 — Engine maturation: selector, SVG presets, native-vector lane, and delivery tests

### Additional implementation

- Added the `native_vector_elements` portfolio lane with two controlled briefs: `modular-ribbon` and `technical-badge`.
- Linked asset-type recommendations to research lanes so `native_object` and `technical_icon` no longer stop at a generic format label.
- Updated regression tests for local native-vector execution versus remote raster execution.
- Full verification after this milestone: **267 passed, 1 skipped**; no generation, provider call, or upload was performed.

## 2026-08-24 — Engine maturation: selector, SVG presets, conservative PNG alpha, and delivery tests

### Additional verification

- Locked CLI delivery coverage so only the approved JPEG is copied to `READY_UPLOAD_ADOBE`; manifests and technical files remain outside the user-facing folder.
- Full verification after this milestone: **266 passed, 1 skipped**; no generation, provider call, or upload was performed.

## 2026-08-24 — Engine maturation: selector, SVG presets, and conservative PNG alpha

### DONE — deterministic pre-generation controls

- Added `portfolio asset-types` and `portfolio readiness` so an asset type maps to an explicit format, execution mode, readiness state, blockers, and next step without provider calls.
- Added a deterministic technical-badge SVG preset while preserving the existing modular-ribbon builder.
- Added a conservative true-alpha PNG normalizer that rejects opaque RGB sources, preserves the source, embeds sRGB, and leaves anti-fringe quality as human review.
- Added tests for selector fail-closed behavior, SVG preset safety, and alpha-source preservation.
- Full verification: **265 passed, 1 skipped**; no generation or upload was performed.

### Current limitation

PNG remains blocked from production until anti-fringe/trim policy and one portal validation are complete. The broader SVG family and marketplace validation remain in progress.

## 2026-08-24 — Documentation consolidation

The active documentation set was consolidated around `docs/README.md`, `docs/STATUS.md`, `docs/ARCHITECTURE.md`, `docs/FEATURE_ROADMAP.md`, `docs/SESSION_HANDOVER.md`, and the current research/marketplace references. Superseded handovers, stale branch-era briefs, duplicated marketplace research, and an old merge-resolution note were removed after their relevant decisions were preserved in the active documents. Historical entries below remain as history and are not current status claims.

## 2026-08-21 — Multi-provider architecture and Kaggle Qwen-Image findings

### DONE — research re-baseline

Added:

- research re-baseline and model/provider design, later consolidated into the active status and roadmap
- `docs/MODEL_PROVIDER_ARCHITECTURE.md`
- updated `docs/ARCHITECTURE.md`
- updated `docs/STATUS.md`
- updated the active architecture and status documents

### Verified findings

- Hugging Face ZeroGPU remains a verified remote generation provider.
- Kaggle GPU worker is verified with 2 × Tesla T4 and ~14.56 GiB VRAM per GPU.
- Kaggle Qwen-Image testing successfully installed DiffSynth-Studio from the official GitHub repository.
- Kaggle Qwen-Image reached model loading/download.
- The end-to-end Kaggle Qwen-Image experiment failed with `OSError: [Errno 28] No space left on device` before a generated image was produced.

### Architectural decisions

- Model identity/storage and compute-provider execution are separate concerns.
- Hugging Face and Kaggle are provider adapters, not hard-coded core engines.
- A Model Registry, Provider Capability/Health contract, unified Generation Job/Result contract, provider router, failover policy, and model cache/delivery abstraction are now P0 architecture gaps.
- Qwen-Image remains a top candidate but is **not** declared the universally best stock-photo model without an internal benchmark.
- Free GPU capacity is treated as opportunistic capacity subject to quota, session, storage, and compatibility constraints.

### Important limitation

Do not claim Kaggle is a completed Qwen-Image generator until a real image-generation PASS is recorded.

## 2026-08-20 — AI upscaling layer

### IN PROGRESS — Real-ESRGAN provider and upscaler contract

Implemented the provider-neutral enhancement boundary needed to turn the 1024×1024 ZeroGPU intermediate artifact into an Adobe-eligible resolution candidate:

- `src/stockforge/upscaler.py`
- `src/stockforge/realesrgan_upscaler.py`
- `tests/test_upscaler.py`
- optional `upscale` dependency group in `pyproject.toml`

The contract records:

- source and destination paths
- scale factor
- provider identity
- model identity
- source/output dimensions
- deterministic failure reasons

The first provider is **Real-ESRGAN x4plus**, selected after comparing open-source options for natural stock photography. The official/general-purpose checkpoint is a 4× model and is distributed under BSD-3-Clause. citeturn0search2turn1search0

The implementation deliberately keeps the heavy inference stack optional. Core StockForge installations do not pull PyTorch/BasicSR merely to run the registry, queue, CLI, or Adobe technical gate.

### Safety rules

- only 4× is accepted by the x4plus provider
- source must exist and decode successfully
- source/destination must differ
- model weights must exist before provider healthcheck passes
- output dimensions must equal exactly 4× source dimensions
- output is written atomically through a temporary file with a real image extension
- inference errors become explicit `UpscalerError` failures

### Important policy decision

Real-ESRGAN is an **enhancement stage**, not an Adobe submission gate. It does not get to declare an image commercially acceptable. The resulting image still has to pass technical inspection, visual-quality QA, artifact/anatomy checks, deduplication, metadata validation, and human approval.

The 1024×1024 benchmark becomes 4096×4096 (16.78 MP) with this provider, which is inside the Adobe 4–100 MP technical range. This is an intended path, not yet a live benchmark result.

### Verification status

The unit-test contract has been added, but the actual Real-ESRGAN inference benchmark has **not** yet been run in the target GPU environment. Therefore this milestone remains `IN PROGRESS` by project policy.

## 2026-08-20 — Adobe JPEG/sRGB finalization milestone

### DONE — deterministic Adobe technical finalization

Implemented and verified the next executable layer of the Adobe Stock readiness pipeline:

- `src/stockforge/adobe_finalize.py`
- `tests/test_adobe_finalize.py`
- `stockforge adobe finalize <source> <destination>` CLI command

The finalizer:

- preserves source pixel dimensions
- refuses candidates outside Adobe's 4–100 MP range instead of silently resizing them
- converts supported profiled raster inputs to RGB/sRGB through Pillow + LittleCMS
- embeds a canonical sRGB ICC profile in the JPEG output
- refuses unprofiled sources unless `assume_srgb=True` / `--assume-srgb` is explicitly supplied
- refuses non-opaque transparency instead of silently compositing against an arbitrary background
- writes optimized progressive JPEG
- searches JPEG quality 95 down to 85 and then 4:2:0 subsampling only when necessary to remain under Adobe's 45 MB limit
- refuses uncontrolled quality degradation when the file cannot fit the limit
- writes through a temporary file and atomically replaces the destination
- immediately re-runs the finished artifact through `inspect_image()` and deletes the output if the technical gate fails

### Verification evidence

GitHub Actions run `32361084347` completed successfully:

- **130 passed**
- **1 skipped**
- `stockforge version` passed
- Python 3.11 CI environment
- Pillow 12.3.0

The first finalizer CI run exposed an actual Pillow 12.3.0 API mistake: raw ICC bytes must be supplied through a file-like wrapper to `ImageCmsProfile`. The finalizer was corrected to use `BytesIO`, and the complete suite then passed.

### Architectural decision

The finalizer does **not** perform AI upscaling, sharpening, denoising, artifact removal, anatomy analysis, OCR, logo detection, watermark detection, legal/IP checks, metadata generation, or deduplication. Those concerns remain separate gates so each transformation can be audited and verified independently.

The current 1024×1024 ZeroGPU benchmark therefore remains an intermediate artifact. It correctly fails the 4 MP finalization requirement until a dedicated upscaling stage is implemented.

## 2026-08-20 — Adobe technical submission gate implementation

### DONE — deterministic Adobe photo technical gate

Implemented the first executable layer of the Adobe Stock readiness pipeline:

- `src/stockforge/adobe_gate.py`
- `tests/test_adobe_gate.py`
- `stockforge adobe check <path>` CLI command
- Pillow promoted to a core dependency because image inspection is now part of the product core.

The gate currently checks:

- file existence
- JPEG format
- 4–100 megapixel resolution range
- maximum 45 MB file size
- RGB pixel mode
- embedded ICC profile inspection
- image structure verification
- full pixel decodability

The color-space check intentionally reports **REVIEW** when an ICC profile is absent rather than falsely claiming that the pixels are non-sRGB. The finalization stage now normalizes and embeds an sRGB profile.

### Verification findings and fixes

- First GitHub Actions run exposed two failures in the new Adobe test fixture.
- The failure was caused by using `CmsProfile.tobytes()` directly with Pillow 12.3.0; the documented `ImageCmsProfile` wrapper is required for serialization.
- The test fixture was corrected.
- The implementation parses embedded ICC bytes through `BytesIO`, matching Pillow's supported profile-loading interface.
- The complete Adobe gate is now covered by the passing CI suite recorded above.

### Known limitations

This is **not yet the complete Adobe submission gate**. It does not yet implement:

- sharpness/noise/artifact analysis
- anatomy/hand/face QA
- OCR
- logo/trademark detection
- watermark detection
- AI disclosure/release metadata
- prompt/IP compliance
- deduplication
- metadata validation
- human approval

These remain separate planned stages.

## 2026-08-20 — ZeroGPU generation milestone

### LIVE — Hugging Face ZeroGPU runtime

- Space: `ibank31/stockforge-zerogpu`
- Hardware: `zero-a10g`
- Termux-to-Space HTTP API verified.
- Runtime status verified as `RUNNING`.
- Public app endpoint verified with HTTP 200.

### LIVE — Z-Image Turbo generation

- Z-Image Turbo successfully generated an image through the deployed Space.
- Baseline benchmark: 1024×1024, 8 steps.
- Benchmark seed: `2157290427964887587`.
- Measured GPU-function time: `44.238` seconds.
- Result artifact returned successfully through the Gradio API.

### LIVE — Qwen3 FP8 mixed loader

The previous loader path was abandoned after the checkpoint produced shape mismatches and was identified as a quantized/packed FP8 mixed checkpoint.

The live runtime now loads `qwen_3_4b_fp8_mixed.safetensors` through the Comfy-compatible loader and successfully generates through Z-Image.

### DONE — ZeroGPU build compatibility fixes

Two build blockers were found and corrected from actual Hugging Face build logs:

1. Python 3.10 could not install `comfy-diffusion==2.6.0`, which requires Python 3.12+.
2. Python 3.12 exposed a dependency conflict between Gradio 5.49 (`Pillow<12`) and `comfy-diffusion 2.6.0` (`Pillow>=12.1.1`).

The Space configuration was updated to Python 3.12 and Gradio 6.25-compatible runtime requirements.

### DONE — Adobe Stock readiness specification

Added `docs/ADOBE_STOCK_READINESS.md` covering resolution, JPEG/sRGB finalization, file integrity, technical quality, anatomy/hand/face QA, object consistency, OCR, logos/trademarks, watermark detection, prompt/IP compliance, people/property/release logic, generative-AI disclosure, metadata, duplicate/spam prevention, commercial-value scoring, copy-space planning, upscaling, provenance, human approval, and marketplace policy maintenance.

### DONE — Feature implementation ledger

Added `docs/FEATURE_ROADMAP.md` as the authoritative project feature matrix.

## 2026-08-19 — Core/project foundation

Existing completed foundation is recorded in `docs/STATUS.md` and the historical entries in this changelog, including:

- CLI foundation
- project initialization
- SQLite registry
- asset registry
- persistent job queue
- plugin contract
- sequential pipeline runner
- artifact/provenance contracts
- lineage persistence
- validation tests
- GitHub Actions CI

## Documentation rule

Every future completed feature must add a dated entry here containing:

1. feature name
2. implementation state
3. verification evidence
4. relevant benchmark/result when applicable
5. known limitations or follow-up work

If a feature is implemented but not verified, record it as `IN PROGRESS`, not `DONE`.


## 2026-08-25 — Cross-agent baseline and documentation consolidation

### DONE — verified JPEG workflow and one Android visual root

- Consolidated the active lifecycle as market evidence → one brief → one ZeroGPU preview → learning record → one selected Kaggle finalizer → master audit → metadata upload-copy → manual Adobe upload.
- Rewrote `STATUS.md`, `SESSION_HANDOVER.md`, `TERMUX_CONTROL_PLANE.md`, and `FEATURE_ROADMAP.md` as the active baseline so future agents do not restart historical audits.
- Archived superseded SVG research, old pretrial notes, historical portal notes, and replaced portfolio runbooks under `docs/archive/2026-08-25/` without deleting their evidence.
- Locked user-visible Android output to `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/` and `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/`.
- Moved the default Adobe technical bundle destination to the project-local `adobe-upload-bundles/`; only the approved JPEG visual is copied to Android.
- Fixed active documentation links and command terminology so `portfolio learning-summary` is the current niche-learning command and legacy `evaluation-summary` is not the primary continuation path.
- No generation, finalizer, upload, or marketplace submission was triggered by this consolidation.


## 2026-08-25 — New illustration JPEG niche prepared

### READY — evidence-bound pet-enrichment object trial, no generation

- Recorded the user's report that the seed-starting tray was uploaded manually to Adobe; no acceptance, moderation, download, revenue, or sales evidence was inferred.
- Added the materially distinct `pet_enrichment_object_illustrations` lane with one registered concept, `puzzle-feeder`, and `test_cap=1`.
- Added the supported `product_illustration` asset family and regression coverage for the new identity, prompt contract, metadata, and square isolated JPEG route.
- Evidence is recorded in `docs/research/NEW_ILLUSTRATION_NICHE_RESEARCH_2026-08-25.md`; ASPCA/RSPCA buyer-job guidance and Adobe exact-query supply proxy support a controlled test, not a sales claim.
- Full suite after the lane addition: **299 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.
- Created one portfolio batch: `pet_enrichment_object_illustrations-20260825T064838Z-60a86ece`; pre-GPU gate reports `gpu_eligible=true`, seven checks pass, zero blockers, remote route `huggingface-zerogpu`, and one square 1024×1024 preview.
- No provider call, generation, retry, finalizer, upload-copy, Adobe upload, or submission has occurred. Explicit user approval is required before one preview of the exact brief.


## 2026-08-25 — Sewing/craft clip-art hypothesis prepared

### READY — one-candidate preview pending

The pet-enrichment preview was rejected because an unintended dog silhouette violated the no-animal brief; no master or retry was created. The user's Adobe screenshot was recorded as anecdotal directional evidence only, without inferring sales or approval.

A new `sewing_craft_tool_clipart` lane with concept `beginner-kit` was added. It targets a compact controlled cluster of unbranded sewing/textile-craft tools in cheerful hand-drawn clip-art style: fabric scissors, thread spool, measuring tape, thimble, pincushion, and a seam-ripper-like tool. Adobe branding, email UI, dollar amounts, human hands/faces, generic hardware, power tools, gears, spark plugs, readable text, trademarks, and copyrighted characters are prohibited.

Research is stored in `docs/research/NEW_TOOL_CRAFT_CLIPART_NICHE_RESEARCH_2026-08-25.md`. The one-candidate batch is `sewing_craft_tool_clipart-20260825T073904Z-69b50234`; its pre-GPU gate reports `gpu_eligible=true`, seven checks pass, zero blockers, and no provider call. Targeted tests pass 18/18. User approval is required before exactly one preview.


## 2026-08-25 — Sewing/craft clip-art master completed

The user accepted the sewing/craft clip-art preview as keep. One evaluation record was added with overall score 4.5/5; the learning summary remains `INSUFFICIENT_EVIDENCE` because the sample contains one review and no marketplace outcome.

Exactly one private Kaggle finalizer completed for the accepted preview. Master artifact `45a2279b-b72e-46c0-b53c-8c381f2fa50c` was registered from master execution `4d85705f-987d-4cc0-a51a-d3c02ca0d730`. Adobe deterministic technical gate returned `ready=true`: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, decodable, and 1,164,873 bytes. Full audit is stored in `docs/research/SEWING_CRAFT_MASTER_AUDIT_2026-08-25.md`.

No upload-copy, Adobe upload, or submission occurred. Upload preparation remains a separate explicit user gate.


## 2026-08-26 — PNG transparent-alpha remote preflight

### DONE — isolated BiRefNet runtime; production candidate still gated

- Diagnosed PNG preflight v1 as a P100 `sm_60` versus Kaggle Torch `2.10.0+cu128` incompatibility: the default build supports `sm_70+`, so CUDA inference failed with `no kernel image is available for execution on the device`. This was not a VRAM, storage, model-cache, alpha, or JPEG failure.
- Added capability-aware CPU fallback to the isolated PNG worker and synthetic preflight. Kaggle preflight v2 completed with offline BiRefNet model load, CPU inference on the remote kernel, RGBA output, alpha range 0–255, elapsed 97.426 seconds, `hf_token_used=false`, and `jpeg_pipeline_touched=false`.
- Added `kaggle-png-finalizer prepare` and a request builder that validates `.png/.webp` square 1024×1024 sources and declares 4096×4096 RGBA/sRGB/true-alpha output with deterministic and human edge gates.
- Added controller and bundle isolation guards: private/offline metadata, BiRefNet cache-only dataset, JPEG source rejection, protected JPEG finalizer rejection, path/checksum/size validation, and no RealESRGAN route.
- Focused PNG/multiformat/selector tests passed 35/35. Full regression suite passed **327 tests, 1 skipped**; compileall, `git diff --check`, PNG CLI test/doctor, and protected JPEG doctor passed.
- Production status remains `BLOCKED` / `visual_review_required`. No real asset, Android export, Adobe upload, or marketplace submission was performed in this milestone.


## 2026-08-26 — Thailand Tomyum Kung trial and JPEG master finalized

### REVIEW_READY — one food preview, one accepted review, compatible-accelerator finalizer

- Read the traditional-food research branch without checkout or modification and selected the evidence-bound global P0 candidate `traditional_food_tomyum_kung` / `tomyum-kung` from Thailand. UNESCO identifies Tomyum Kung as a traditional Thai prawn soup with aromatic herbs and vibrant colours; Adobe category guidance places food-focused content in category 7 (Food). Research and references are stored in `docs/research/TRADITIONAL_FOOD_TOMYUM_KUNG_TRIAL_2026-08-26.md`.
- Created exactly one project-local batch and generated exactly one 1024×1024 ZeroGPU preview. Preview execution `32a8bd7c-6565-547c-8433-2fa51b7baf3c`; preview artifact `ed286457-fd83-4065-a1e2-6757d476bf2e`; user verdict `KEEP`; evaluation overall 3.75/5; marketplace outcome `not_submitted`.
- The first finalizer submission, kernel version 14 on Kaggle P100, failed for a confirmed runtime/accelerator mismatch: P100 `sm_60` versus current Torch support `sm_70+`, failing in RealESRGAN at `model.half()`. The protected JPEG worker was not changed and no blind retry was made.
- The identical request was submitted to compatible T4 as kernel version 15 and completed with `RealESRGAN_x4plus` at 4×. Imported master execution `4c8d3bfd-c3ef-49ae-95fb-5e0fbafce0fa`; master artifact `7d506166-62b2-4c61-988c-4c72d42a8860`.
- Master passed deterministic checks: JPEG, 4096×4096, 16.777216 MP, RGB, sRGB, decodable, quality 95, 4:4:4, and 1,755,278 bytes. Full-resolution whole-image and four-tile audit found no fatal text/logo/watermark/hand/scene/halo/object-drift issue. A non-blocking note remains that pale curved strands resemble noodles despite the no-noodle prompt; the user accepted the preview.
- Master remains `review_ready` / `visual_review_required`. No upload-copy, Android export, Adobe upload, or marketplace submission was created. A separate explicit approval is required before preparing the manual Adobe upload bundle.
