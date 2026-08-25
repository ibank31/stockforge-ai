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


## Tool-and-craft clip-art lane — preview approval pending

The user rejected the pet-enrichment preview because an unintended dog silhouette appeared despite the no-animal brief. Do not promote that preview to master, retry it, or treat it as a successful candidate.

The user supplied an Adobe Stock email screenshot showing a compact colorful tool/craft object cluster and a reported `$1276` “best seller” amount. This remains anecdotal user-provided direction only; no independent transaction evidence is available. Do not reproduce Adobe branding, email UI, exact icon designs, or any protected expression.

The next evidence-bound hypothesis is `sewing_craft_tool_clipart--beginner-kit`. It is one controlled square JPEG cluster of unbranded sewing/textile-craft tools in cheerful hand-drawn clip-art style: fabric scissors, thread spool, measuring tape, thimble, pincushion, and a seam-ripper-like tool. The negative prompt excludes Adobe logo, email interface, buttons, dollar amount, human hands/faces, generic hardware, power tools, gears, spark plugs, readable text, trademarks, and copyrighted characters.

Research is recorded in `docs/research/NEW_TOOL_CRAFT_CLIPART_NICHE_RESEARCH_2026-08-25.md`. Adobe exact-query supply proxies were 9,838 for `sewing tools clipart illustration`, 154,438 for `craft tools illustration set`, 33,877 for `home repair tools cartoon illustration`, and 238,612 for `hand tools illustration set`. These are supply proxies only. The user screenshot is not sales proof.

Batch `sewing_craft_tool_clipart-20260825T073904Z-69b50234` is created. Dry-run reports `gpu_eligible=true`, seven checks pass, zero blockers, remote raster route, square JPEG, white background, isolated controlled cluster, and no provider call. Targeted tests pass 18/18. The next allowed action is one preview only after explicit user approval of the exact brief.


## Sewing/craft clip-art master completed

The user accepted the sewing/craft preview as keep. Learning summary records one accepted review for `sewing_craft_tool_clipart` with overall average 4.5/5 and recommendation `INSUFFICIENT_EVIDENCE`; no marketplace outcome is claimed.

Exactly one private Kaggle finalizer completed for the accepted preview. Master artifact `45a2279b-b72e-46c0-b53c-8c381f2fa50c` was registered from master execution `4d85705f-987d-4cc0-a51a-d3c02ca0d730`, with source artifact `563e9a47-3dbc-440b-93da-bc7d6535bb75` and source execution `e5976fb6-0490-556e-94c7-5b4b62bb3c90`. Master path: `masters/563e9a47-3dbc-440b-93da-bc7d6535bb75-master.jpg`. Finalizer was Kaggle private kernel `iqbalteguh/stockforge-finalizer`, using `RealESRGAN_x4plus` at 4×.

Adobe deterministic gate returned `ready=true`: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, decodable, 1,164,873 bytes. Visual review confirms the compact sewing/textile-craft cluster and no visible Adobe logo, email UI, dollar amount, human, face, readable text, watermark, or copyrighted character. Audit report: `docs/research/SEWING_CRAFT_MASTER_AUDIT_2026-08-25.md`.

The master is retained for manual review. Do not prepare upload-copy or submit to Adobe without explicit user approval for that separate action. Do not treat the earlier user-reported Adobe upload as acceptance or sales evidence.


## Mechanical reference audit and cable-gland hypothesis — generation still gated

The user reports that the finalized sewing/craft JPEG was manually uploaded to Adobe Stock after the approved package was prepared. No portal screenshot, moderation result, acceptance, rejection, download, conversion, revenue, or sales evidence was provided; treat this only as a user-reported upload.

The latest reference screenshot `/home/ubuntu/upload/1000802935.jpg` is 1219×1110 and was inspected normally. It contains Adobe UI, branding, a reported dollar amount, promotional text, watermark/handle, and a small isolated coaxial/threaded technical component. Only the generic product grammar—small unbranded component, white background, cylindrical silhouette, threaded end, and material contrast—was retained. Do not copy the UI, logo, number, watermark, layout, or exact object design.

The latest StockForge output `/home/ubuntu/upload/1000803314.jpg` is 4096×4096. Following `read-special-images`, it was inspected through all 9 ordered overlapping grid crops in `/home/ubuntu/tmp/stockforge-reference-1000803314/`, row-major, with findings saved in `docs/research/MECHANICAL_REFERENCE_VISUAL_NOTES_2026-08-25.md`. The full output is a copper-winding rotor/armature assembly with graphite/gold annular frame, fasteners, and axial shaft. It is not a cable gland. The new candidate must remain non-rotating and must avoid rotor, armature, winding, coil, annular rotor body, motor housing, and shaft shorthand.

Public research and the scorecard are saved in `docs/research/NEW_MECHANICAL_CABLE_GLAND_NICHE_RESEARCH_2026-08-25.md`. The selected hypothesis is `technical_cable_entry_fitting_illustrations--cable-gland`: one generic unbranded cable gland with threaded body, cap nut, dark elastomer compression insert, locknut, and short neutral cable stub. Buyer job: enclosure-installation articles, industrial wiring/interconnect explainers, technical education, and generic product communication. Adobe exact-query counts are supply proxies only: 121 `cable gland illustration`, 360 `hydraulic coupling illustration`, 1,254 `mechanical connection`, 5,258 `terminal block`, and 48,737 `pipe fitting vector`. No demand, ranking, approval, download, conversion, revenue, or sales claim is permitted.

The new lane and JPEG identity were registered with `test_cap=1`; no new asset family was added. Targeted tests passed 19/19. One project-local batch was created: `technical_cable_entry_fitting_illustrations-20260825T085859Z-db437604`. `portfolio show` verified the persisted brief. `portfolio generate --dry-run` reports `gpu_eligible=true`, seven checks pass, zero blockers, provider route `huggingface-zerogpu`, profile `z-image-turbo`, square 1024×1024, 8 steps, batch size 1, estimated 55 GPU seconds. No provider call or generation has occurred.

The inherited sandbox needed a project-local wrapper config at `/home/ubuntu/stockforge-live/cli-inherited-config/config.json` because the active database is `/home/ubuntu/stockforge-live/stockforge.db` while the workspace config database had no project record. This wrapper contains no credentials and does not alter Android output paths. The old stray `Download/MACHINE STOCKFORGE/PACKAGES` possibility was not inspected or deleted; any cleanup still requires dry-run inventory and explicit user confirmation.

**Next action:** present the exact cable-gland brief and ask for explicit approval for one ZeroGPU preview only. If approved, use the saved batch and execute exactly one preview; then require user visual verdict followed by `portfolio evaluate` and `portfolio learning-summary`. Do not retry, batch, finalize, prepare upload-copy, upload, or submit before the later gates and separate approvals.


## Cable-gland preview executed — human review pending

The user explicitly approved the exact cable-gland brief. StockForge executed exactly one ZeroGPU preview for batch `technical_cable_entry_fitting_illustrations-20260825T085859Z-db437604` using `huggingface-zerogpu`, profile `z-image-turbo`, square 1024×1024, 8 steps, batch size 1. Execution `0485db26-571c-50bb-8fca-469ef84f0817`; artifact `b846ec0c-4017-4221-a803-822b8d3264f0`; release package `deliveries/stockforge-0485db26-571c-50bb-8fca-469ef84f0817.zip`. Android preview export was unavailable in this sandbox, so no Android visual folder was changed. No retry, second generation, finalizer, upload-copy preparation, or submission has occurred.

The rendered preview is one isolated metallic threaded fitting with a dark elastomer ring, faceted central body, upper opening, and lower external thread. The short cable stub is not visually obvious, so the user should judge whether it reads as a cable-entry strain-relief fitting rather than a generic threaded adapter. Do not mutate the prompt or retry based on this note. After the user gives a simple verdict, record it with `portfolio evaluate`, then run `portfolio learning-summary` before any master/finalizer decision.


## Cable-gland finalizer completed after queue delay — upload-copy still gated

The user asked to diagnose the long Kaggle delay. Read-only checks showed the same private kernel `iqbalteguh/stockforge-finalizer` moved from `QUEUED` to `RUNNING`, with latest run timestamp `2026-08-25 09:42:55 UTC`. The output download contained the expected `result.json`, `master.jpg`, `master.upscaled.png`, and log. No retry, second submission, or additional finalizer job was made.

The result matched the original request ID, source lineage, target, and checksums. It was imported as master artifact `7976851d-acfb-4b96-8a9f-3720694296c2` with master execution `9b01c985-d2dd-42a4-a142-42e1118dcca6`. Master path: `masters/b846ec0c-4017-4221-a803-822b8d3264f0-master.jpg`. Deterministic gate: JPEG, 4096×4096, 16.777216 MP, RGB, embedded/assumed sRGB, decodable, quality 95, 4:4:4 subsampling, 723,102 bytes.

The master was inspected in all 9 ordered overlapping full-resolution tiles. It is one centered, fully contained metallic threaded fitting with dark elastomer ring and clean white background. No readable text, label, logo, watermark, person, hand, tool, protected character, severe crop loss, major halo, colored fringe, or duplicated geometry was observed. Non-blocking notes are irregular stippled/speckled metal texture on the central body and the continued absence of an obvious short cable stub; the object may read as a generic threaded adapter rather than an unmistakable cable gland. Do not mutate the prompt or retry.

Audit report: `docs/research/CABLE_GLAND_MASTER_AUDIT_2026-08-25.md`. Master remains `review_ready` / `visual_review_required`. No upload-copy, Android export, Adobe upload, or submission has occurred. The next gate is a separate explicit user approval for `portfolio prepare-adobe-upload`; Adobe submission remains manual.


## Cable-gland Adobe package prepared — manual portal action pending

The user explicitly approved `SETUJU SIAP UPLOAD CABLE GLAND`. StockForge prepared one manual Adobe upload bundle for master execution `9b01c985-d2dd-42a4-a142-42e1118dcca6`, with explicit reviewed category `10 — Industry` after the safe automatic mapping correctly blocked the new lane. Bundle: `adobe-upload-bundles/adobe-20260825T101659Z-9b01c985/`; upload-copy: `asset-7976851d/sf-7976851d.jpg`; technical ZIP: `/home/ubuntu/stockforge-live/CABLE_GLAND_ADOBE_UPLOAD_PACKAGE.zip`. The JPEG contains embedded XMP title/keywords; metadata records 15 visual-first keywords, GenAI disclosure required, and title `Unbranded Cable Gland Strain Relief Fitting with Generic Cable`.

The sandbox had no Android Download mount, so no Android folder was changed. Only the JPEG upload-copy was uploaded to a temporary CDN URL for Termux transfer. User-facing Termux transfer must create/use only `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/` and download the JPEG; never copy the ZIP, CSV, JSON, Markdown, log, XMP sidecar, PNG intermediate, request, or other technical files into the visual root. Adobe upload and submission remain manual and unconfirmed.


## Animal adoption/foster character lane — dry-run ready, generation not authorized

The user reported the cable-gland JPEG was manually uploaded; this remains user-reported only with no official Adobe outcome. The user then supplied a screenshot showing a group of colorful animal characters with superhero-like accessories. Treat it only as anecdotal direction for recognizable focal character, group hierarchy, bright contrast, and social/marketing utility. Do not copy its text, UI, revenue figure, branding, masks, capes, symbols, exact animals, or exact design.

Research selected `animal_adoption_foster_helper_characters` with concept `rescue-foster-helpers`: one compact trio of original fictional animal community helpers with three distinct species silhouettes, plain color-block volunteer vests, simple bandanas, warm expressions, and no emblem or text. Buyer job: shelter adoption campaigns, foster recruitment, volunteer education, and animal-welfare social content. ASPCA/Best Friends resources support the communication job; Adobe result counts are supply proxies only. The lane is materially distinct from seed tray, sewing tools, cable-gland, and the rejected pet-enrichment object experiment.

Registry and identity were added with `test_cap=1`, JPEG square/white/isolated route, explicit animal-helper quality gates, and prohibited superhero/comic/cape/mask/lightning/shield/brand/named-shelter/slogan/copyrighted-character/real-event/medical-claim shorthand. Adobe category mapping is Animals (1) for future package preparation, subject to portal verification.

Full suite: **302 passed, 1 skipped, 49 non-blocking Pillow warnings**; compileall and `git diff --check` passed. Batch: `animal_adoption_foster_helper_characters-20260825T103937Z-5097e7a7`; brief: `animal_adoption_foster_helper_characters--rescue-foster-helpers`. Dry-run: **7/7 pre-GPU checks pass, 0 blockers**, `z-image-turbo`, square 1024×1024, 8 steps, batch size 1, estimated 55 GPU seconds. No provider call or generation has occurred. Await explicit approval for exactly one preview.


## Animal adoption/foster story-vignette revision — approval pending

The user rejected the first animal-helper preview as too standard/template-like. Keep execution `9e49d293-914e-53d6-9c31-eba714bb5622` and artifact `344d9992-34ac-41c7-b070-794b70aa88c9` rejected/frozen; do not retry it, recolor it, crop it, or silently mutate its prompt.

The materially revised lane is `animal_adoption_foster_story_vignettes`, concept `first-day-home`, with one small original fictional puppy-like focal animal stepping out from an open unbranded soft pet carrier, flanked by a cat-like helper and rabbit-like helper in plain color-block volunteer vests and simple bandanas; a folded blanket and blank circular tag are the only approved care props. The visual identity is a story vignette with visible transition action, triangular/diagonal focal hierarchy, three-species contrast, tactile care-prop storytelling, and no superhero/IP shorthand.

Registry category mapping is Animals (1), subject to portal verification. Full suite after revision: **303 passed, 1 skipped, 49 non-blocking Pillow warnings**; compileall and `git diff --check` passed. New batch `animal_adoption_foster_story_vignettes-20260825T114431Z-7152b2fd` and brief `animal_adoption_foster_story_vignettes--first-day-home` are project-local. Dry-run: **7/7 pre-GPU checks pass, 0 blockers**, `z-image-turbo`, 1024×1024 square, 8 steps, batch size 1, estimated 55 GPU seconds. No provider call or generation has occurred for the revision. Await explicit approval for exactly one preview.


## Animal adoption story-vignette — finalized, package ready

User KEEP recorded for execution `a20f3fca-9903-5fc3-afee-fc97fe6a2317`; evaluation accepted with overall 4.0/5 and marketplace outcome `not_submitted`. Learning summary is `INSUFFICIENT_EVIDENCE`; do not infer demand or sales.

Exactly one private Kaggle RealESRGAN_x4plus finalizer was submitted for this preview as kernel version 13 and completed. Imported master execution: `d27d373c-33d1-4785-8505-5e1462530148`; artifact: `a37740f9-c5a0-4629-8749-6689240362d3`. Full-resolution 9-tile audit completed. Master is JPEG 4096×4096, 16.777216 MP, RGB, assumed sRGB, quality 95, 4:4:4, decodable; no obvious text/logo/watermark/human/tool/IP issue observed. Minor note: painterly/stipple texture and a blank heart-shaped collar tag.

User requested finalization through ready-upload status. Bundle: `/home/ubuntu/stockforge-live/workspace/projects/stock-assets/adobe-upload-bundles/adobe-20260825T120521Z-d27d373c`; category 1 Animals; status `manual_portal_upload_prepared_not_submitted`. Only JPEG upload-copy was uploaded to temporary storage for Termux retrieval; Adobe submission remains manual and no marketplace outcome is known.


## Vector native route recommendation — approval pending

User asked how to obtain a vector format that is easier to commercialize through StockForge. Current route: local native SVG construction only; do not trace JPEG or ask the raster model to imitate vector style. Adobe accepts AI/EPS/SVG and requires editable/original content, organized groups/layers, RGB, artboard offset `(0,0)`, max 45 MB, and appropriate size. Adobe's generative-AI vector guidance requires reworking output for editability and limits acceptable submissions to original editable scenes/subjects, simple editable icon shapes, or seamless patterns.

StockForge has verified deterministic SVG presets `folder_upload`, `file_flow_micro_set`, `technical_badge`, `geometric_pattern`, and `modular_ribbon`. The active route validates native XML geometry and forbids raster/script/text embeds. It uses no GPU, Kaggle, or credential. It is suitable for utility icons, icon sheets, and simple repeat patterns, not general AI-to-SVG illustration.

Recommended first vector hypothesis: `document_review_delivery_micro_set`, eight coherent utility symbols for intake, organize, review, approve, archive, restore, sync, and share. This is a buyer-job hypothesis for UI, documentation, marketing, presentations, and animation—not a sales promise. Adobe supply proxies on 2026-08-25 were 604,515 for `utility icons`, 384,106 for `file management icon`, 25,018 for `"tech icons"`, 86,903 for `"icon pack"`, and 6,279,918 for `seamless geometric pattern`; these counts do not establish demand, approval, ranking, conversion, revenue, or sales.

No vector lane, batch, SVG, preview, or upload was created. Await user approval before implementing one buyer-specific preset and dry-run. Research report: `docs/research/VECTOR_NATIVE_WORKFLOW_RECOMMENDATION_2026-08-25.md`; evidence: `docs/research/VECTOR_ROUTE_EVIDENCE_2026-08-25.md`.


## Higher-value native vector workflow — trial approval pending

User requested a more valuable native vector than previous generic work. Implemented lane `native_vector_workflow_sets` with concept `document-review-delivery-micro-set`: one coherent eight-symbol SVG micro-set for intake, organize, review, approve, archive, restore, sync, and share. This is materially different from `file-flow-micro-set`, not a recolor/rotation retry. Visual system: circular containers, document motifs, consistent action arrows, transparent spacing, editable shapes/groups, no text or branding.

Added native builder preset `document_review_delivery_micro_set`, local tag routing, selector recommendation, Adobe category mapping 8 (Graphic Resources), and regression coverage. Batch `native_vector_workflow_sets-20260825T130127Z-411eacf7` and brief `native_vector_workflow_sets--document-review-delivery-micro-set` were created project-local. The remote `portfolio generate --dry-run` command correctly failed closed because this lane is local-native-vector; the correct readiness report passed with `trial_allowed=true`, `provider_call_allowed=false`, and `single_candidate_only=true`. No SVG file was built, no provider/GPU call was made, and no upload occurred.

Targeted tests: 42 passed. Full suite: 304 passed, 1 skipped, 49 existing Pillow deprecation warnings. Compileall and whitespace check passed. Awaiting explicit user approval for exactly one local SVG build and visual review. No marketplace outcome may be inferred.


## SVG two-trial diagnosis — redesign required before trial three

User feedback: both prior SVG trials were visually unsatisfying; many elements collide with lines. Trial 1 `file-flow-micro-set` is native and clean but generic (broad primitives, equal grid, no workflow rhythm). Trial 2 `document-review-delivery-micro-set` is more buyer-specific but cramped: circular containers leave insufficient usable space, thick strokes/arrowheads merge with outer rings or document corners, and the set remains eight independent primitives rather than a composed visual system.

Root cause: current QA validates XML/native elements and forbidden embeds but not stroke envelopes, inner-boundary clearance, pairwise overlap, min gaps, or thumbnail readability. The current transparent SVG preview on a dark viewer backdrop also makes pale fills and edge collisions harder to evaluate. The next redesign must be substantive: editable workflow diagram kit, larger safe cells, lighter stroke hierarchy, fewer decorative rings, intentional connectors/rhythm, explicit geometry clearance checks, overlap checks, and white/checkerboard renders. No third trial has been built or authorized.

Research diagnosis: `docs/research/DOCUMENT_WORKFLOW_VECTOR_TRIAL_DIAGNOSIS_2026-08-25.md`.


## Monochrome convention and vector quality diagnosis

User observed that Adobe Stock icon results often appear black-and-white and said both StockForge SVG trials are visibly behind in quality. Official Adobe guidance explains that vector value includes adaptability such as changing icon colors; Adobe's icon guidance prioritizes simple communication, instant recognition, and coherent themed sheets. Google Material Icons provides a monochrome/tinting precedent. These are functional design conventions, not evidence that monochrome dominates Adobe Stock or sells better.

Trial 1 remains generic and uses broad primitives with semantic marks touching their base shapes. Trial 2 is more specific but decorative circular containers reduce inner space; thick child strokes and arrowheads collide with container borders. Existing native SVG validation only checks XML/elements/forbidden embeds, so it can pass despite poor art direction and geometric collisions. The correction is not recolor-only: use monochrome-first/two-tone-neutral, remove non-semantic circles, reduce stroke hierarchy, enforce safe grid/clearance, and add geometry QA for bounds, stroke envelopes, pairwise overlap, and thumbnail readability. No third trial built. Evidence appended to `VECTOR_ROUTE_EVIDENCE_2026-08-25.md`; status updated without marketplace claims.

## Redesign implementation after explicit approval

User approved the monochrome-first redesign. A materially distinct lane was added: `native_vector_workflow_diagram_kits` / `document-lifecycle-diagram-kit`; this does not mutate either rejected SVG trial. The brief defines six large independent workflow modules—intake, organize, review, approve, archive, deliver—with dark-neutral primary geometry, restrained neutral accents, no decorative circular badges, and five connector lanes outside card interiors.

Preset `document_lifecycle_diagram_kit` now builds locally but has not been invoked for a visual trial. Each card has a named group, explicit global card bounds, inner safe-zone metadata, and a measurable glyph group. The validator has stroke-aware conservative bounds for rect/circle/line/polygon/polyline/path, checks glyph envelopes inside safe zones, checks connectors against card bounds, and requires six cards/five connectors for the declared workflow contract. Selector recommendation and portfolio tests were updated; old lanes remain historical/reference.

Focused tests and the full suite passed (`305 passed, 1 skipped, 49 warnings`); compileall and diff check passed. CLI readiness, plan-type, and trial-readiness dry-runs passed; `single_candidate_only=true`, `trial_allowed=true`, `provider_call_allowed=false`. No new SVG, upload package, Android export, provider/GPU/Kaggle call, or marketplace action was performed. Next gate: report the implementation and ask separately for approval to build exactly one visual trial of the new preset.
