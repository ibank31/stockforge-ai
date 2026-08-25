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


## Seed-starting tray master — review_ready

The user gave `keep` for the single seed-starting preview and noted that one cell appears without a visible seedling. This was recorded as a non-blocking natural variation under the approved brief, not silently corrected by retry. The preview evaluation ledger now contains one accepted record with visual quality 4/5, technical quality 3/5 because the source was still a 1024px WebP preview, buyer fit 4/5, metadata accuracy 4/5, and overall score 3.75/5. `portfolio learning-summary` correctly returned `INSUFFICIENT_EVIDENCE` because one review cannot establish niche demand or policy.

One private Kaggle finalizer job completed for the selected preview using `RealESRGAN_x4plus` at 4×. The master is `masters/b8c4cc8b-6002-4c09-b3d5-1dd7725f3ca9-master.jpg`, artifact `20032d2f-3ef2-43a2-a103-cb2707fe10ed`, execution `83709936-fae9-4643-bd07-bb332b3ba455`. Adobe deterministic checks pass: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, decodable, 1,451,346 bytes, quality 95, and 4:4:4 subsampling.

The master was inspected in all nine ordered overlapping full-resolution tiles. No readable text, label, logo, watermark, person, hand, seed packet, severe crop loss, major halo, or duplicated structural geometry was observed. Minor bright specks on gray plastic and somewhat smooth AI-upscaled leaf texture remain human review notes. The master remains `review_ready` / `visual_review_required`; no upload-copy, Android export, Adobe upload, or marketplace submission has occurred. A separate explicit approval is required before `portfolio prepare-adobe-upload`.


## Adobe manual upload note — user-reported

The user reports that the seed-starting tray JPEG was uploaded to Adobe Stock manually after the `READY_UPLOAD_ADOBE` package was prepared. No portal screenshot, acceptance result, moderation result, download, revenue, or sales evidence was provided, so the event is recorded only as a user-reported manual upload and does not promote the asset beyond the existing evidence state. The next experiment must use a materially different illustration JPEG niche and must not reuse the seed-starting or rotor-armature lanes as a pseudo-retry.


## Next illustration hypothesis — pet-enrichment object

A new materially distinct illustration lane is registered as `pet_enrichment_object_illustrations` with brief `pet_enrichment_object_illustrations--puzzle-feeder`. It is based on ASPCA/RSPCA enrichment guidance and a narrow Adobe exact-query supply proxy. The selected asset is one square isolated JPEG illustration of an interactive treat-puzzle feeder board with rounded compartments and generic treat pieces, without animals, people, brands, labels, or text.

The repository supports this lane through the new `product_illustration` asset family. Targeted tests passed 17/17 and the full suite passed 299 tests, 1 skipped, with 49 non-blocking Pillow deprecation warnings. One portfolio batch was created at `portfolio-plans/pet_enrichment_object_illustrations-20260825T064838Z-60a86ece.json`. The dry-run pre-GPU gate passed with `gpu_eligible=true`, seven checks pass, zero blockers, square 1024×1024 preview route, and estimated 55 GPU seconds. No provider call or generation has occurred. User approval is required for exactly one preview of this exact brief.


## New tool-and-craft clip-art hypothesis — preview approval pending

The pet-enrichment preview was rejected by the user because the generated image contained an unintended dog silhouette that violated the no-animal brief. It must not be promoted to master or reused as a successful candidate.

A new materially distinct illustration lane is now registered as `sewing_craft_tool_clipart` with brief `sewing_craft_tool_clipart--beginner-kit`. The concept is a compact controlled cluster of unbranded sewing/textile-craft tools—fabric scissors, thread spool, measuring tape, thimble, pincushion, and a seam-ripper-like tool—in cheerful hand-drawn clip-art style with bold outline and bright flat color. The user's Adobe screenshot is treated only as an anecdotal directional signal, not verified sales evidence.

The one-candidate batch is `sewing_craft_tool_clipart-20260825T073904Z-69b50234`. Dry-run reports `gpu_eligible=true`, seven checks pass, zero blockers, square JPEG route, white background, isolated controlled cluster, and no provider call. Targeted tests pass 18/18. The exact brief remains ready for one user-approved preview only; no generation, finalizer, upload-copy, or submission has occurred.


## Sewing/craft clip-art master ready for review

The user accepted the sewing/craft preview as keep. The learning summary records one accepted review for `sewing_craft_tool_clipart` with overall average 4.5/5, while correctly reporting `INSUFFICIENT_EVIDENCE` because one review and no marketplace outcome cannot establish demand.

One private Kaggle finalizer completed for the exact accepted preview. Master artifact `45a2279b-b72e-46c0-b53c-8c381f2fa50c` is registered from master execution `4d85705f-987d-4cc0-a51a-d3c02ca0d730`; the master is `masters/563e9a47-3dbc-440b-93da-bc7d6535bb75-master.jpg`. Adobe deterministic technical check returned `ready=true`: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB, decodable, 1,164,873 bytes.

Visual review confirms the accepted compact sewing/textile-craft clip-art cluster and no visible Adobe logo, email UI, dollar amount, human, face, readable text, watermark, or copyrighted character. The master is technically ready and retained for manual review. Upload-copy preparation remains a separate explicit gate; no upload or submission has occurred.


## Sewing/craft manual Adobe upload — user-reported only

The user now reports that the finalized sewing/craft JPEG was uploaded to Adobe Stock manually after the approved package was prepared. No portal screenshot, moderation status, acceptance, rejection, download, conversion, revenue, or sales evidence was provided. This event remains a user-reported manual upload only and does not change the asset's evidence state or establish marketplace outcome.

## New mechanical hypothesis — cable-gland, generation still gated

After inspecting the two latest user-provided references, StockForge selected `technical_cable_entry_fitting_illustrations--cable-gland` as a materially distinct mechanical-component hypothesis. Reference 1 is a marketplace screenshot containing a small generic-looking coaxial/threaded component; only generic product grammar was retained as directional evidence. Adobe UI, logos, watermark, reported dollar amount, “best seller” wording, layout, and exact object design were not copied or treated as proof. Reference 2 was a 4096×4096 prior StockForge output audited through all 9 ordered overlapping grid tiles and confirmed as a copper-winding rotor/armature with graphite/gold annular frame and axial shaft. The new cable-gland brief explicitly avoids rotor, armature, winding, coil, annular rotor, and motor-like shorthand.

The selected object is one generic unbranded cable-entry strain-relief fitting with threaded body, cap nut, dark elastomer compression insert, locknut, and short neutral cable stub. The defensible buyer job is an isolated visual for enclosure-installation articles, industrial wiring/interconnect explainers, technical education, and generic product communication. Public sources support these functions, while Adobe exact-query results are treated only as supply proxies: 121 for `cable gland illustration`, compared with 360 for `hydraulic coupling illustration`, 1,254 for `mechanical connection`, 5,258 for `terminal block`, and 48,737 for `pipe fitting vector`. These numbers do not prove demand, sales, ranking, approval, downloads, conversion, or revenue.

A new lane and JPEG identity were registered with `test_cap=1`. Targeted tests passed 19/19. Batch `technical_cable_entry_fitting_illustrations-20260825T085859Z-db437604` was created in the project-local `portfolio-plans/` directory. `portfolio show` and `portfolio generate --dry-run` pass the seven pre-GPU checks with `gpu_eligible=true`, zero blockers, remote provider route `huggingface-zerogpu`, profile `z-image-turbo`, square 1024×1024 preview, 8 steps, batch size 1, and estimated 55 GPU seconds. No provider call, generation, finalizer, upload-copy preparation, or submission has occurred. Explicit user approval is required for exactly one preview of this exact cable-gland brief.

The project-local wrapper config used for this inherited sandbox session is `/home/ubuntu/stockforge-live/cli-inherited-config/config.json`; it points to the active database and project root without changing Android output folders or credentials. The earlier stray `Download/MACHINE STOCKFORGE/PACKAGES` instruction remains subject to the documented dry-run inventory and explicit cleanup confirmation; no cleanup was performed in this milestone.


## Cable-gland preview generated — human review pending

After the user explicitly approved `SETUJU PREVIEW CABLE GLAND`, StockForge executed exactly one ZeroGPU preview for batch `technical_cable_entry_fitting_illustrations-20260825T085859Z-db437604`. Provider route was `huggingface-zerogpu`, profile `z-image-turbo`, square 1024×1024, 8 steps, batch size 1. Execution `0485db26-571c-50bb-8fca-469ef84f0817`, artifact `b846ec0c-4017-4221-a803-822b8d3264f0`, and project-local release package `deliveries/stockforge-0485db26-571c-50bb-8fca-469ef84f0817.zip`. The preview is `review_ready`; Android preview export was not available in this sandbox. No retry, second generation, finalizer, upload-copy preparation, or submission has occurred.

At first visual glance, the rendered object is a single isolated metallic threaded fitting with a dark elastomer ring, faceted central body, upper opening, and lower external thread. The cable stub is not visually obvious in this preview, so human review must specifically assess whether the object reads as a cable-entry strain-relief fitting rather than a generic threaded adapter. This note does not authorize prompt mutation or a retry; the user verdict must be recorded through `portfolio evaluate` and followed by `portfolio learning-summary`.


## Cable-gland finalizer queued — no retry

After the user approved finalization, KEEP was recorded with conservative scores: visual 4/5, technical 3/5, buyer fit 3/5, metadata accuracy 4/5, overall 3.5/5, marketplace outcome `not_submitted`. `portfolio learning-summary` returned `INSUFFICIENT_EVIDENCE` for the cable-gland lane, correctly stating that one review cannot establish a niche policy or market demand.

One private Kaggle finalizer submission was made for request `master-b846ec0c-4017-4221-a803-822b8d3264f0-af74b4a5.json` using the existing `iqbalteguh/stockforge-finalizer` kernel and `RealESRGAN_x4plus` route. Kaggle accepted the push as kernel version 12. Repeated read-only status checks report `KernelWorkerStatus.QUEUED`; no second submission or retry is allowed. The public browser page did not expose the private kernel page, so CLI status remains the source for job state. Master import and audit must wait for a completed output.


## Cable-gland finalizer completed and master audited

The earlier long delay was a Kaggle queue delay, not a failed submission. Read-only checks showed the same private kernel `iqbalteguh/stockforge-finalizer` moving from `QUEUED` to `RUNNING`; the latest run timestamp was `2026-08-25 09:42:55 UTC`. The output download then contained `result.json`, `master.jpg`, `master.upscaled.png`, and the run log. No retry or second finalizer was submitted.

The output passed lineage/checksum validation and was imported. Master artifact is `7976851d-acfb-4b96-8a9f-3720694296c2`, master execution `9b01c985-d2dd-42a4-a142-42e1118dcca6`, and file `masters/b846ec0c-4017-4221-a803-822b8d3264f0-master.jpg`. Deterministic gate passed: JPEG, 4096×4096, 16.777216 MP, RGB, embedded/assumed sRGB, decodable, quality 95, 4:4:4 subsampling, 723,102 bytes. The master was inspected in all 9 ordered overlapping full-resolution tiles; no readable text, branding, watermark, people, hands, tools, protected characters, severe crop loss, halo, colored fringe, or duplicated geometry was observed.

Non-blocking visual notes: the central metal body has irregular stippled/speckled surface texture at 100%, and the short cable stub remains not visually obvious, so the object may read as a generic threaded adapter rather than an unmistakable cable gland. These are recorded for truthful human review; no prompt mutation or retry is allowed. Master status remains `review_ready` / `visual_review_required`.

The project-local audit report is `docs/research/CABLE_GLAND_MASTER_AUDIT_2026-08-25.md`. No upload-copy, Android export, Adobe upload, or submission has occurred for cable-gland. A separate explicit approval is required before `portfolio prepare-adobe-upload` creates the JPEG upload-copy/package; Adobe portal action remains manual.


## Cable-gland Adobe upload package prepared — manual submission pending

After explicit user approval `SETUJU SIAP UPLOAD CABLE GLAND`, StockForge prepared one manual Adobe upload bundle for finalized-master execution `9b01c985-d2dd-42a4-a142-42e1118dcca6` using explicit reviewed category `10 — Industry`. The initial automatic category lookup correctly blocked because the new lane had no safe mapping; the explicit category was then supplied from the lane's industrial buyer-job research. Bundle status is `manual_portal_upload_prepared_not_submitted`.

Project-local bundle: `adobe-upload-bundles/adobe-20260825T101659Z-9b01c985/`. It contains one JPEG upload-copy `asset-7976851d/sf-7976851d.jpg`, embedded XMP title/keywords, `UPLOAD_METADATA.txt`, `BATCH_MANIFEST.json`, and `README.txt`. Title: `Unbranded Cable Gland Strain Relief Fitting with Generic Cable`. The bundle records 15 visual-first keywords and requires truthful GenAI disclosure. The technical ZIP is `/home/ubuntu/stockforge-live/CABLE_GLAND_ADOBE_UPLOAD_PACKAGE.zip`.

No Android Download mount was available in this sandbox, so no local Android folder was modified. Only the JPEG upload-copy was placed at a temporary CDN URL for the user's Termux pull. The technical ZIP, CSV/manifest/checklist, JSON, and XMP-sidecar-type technical data remain project-local and must not be copied into `Download/MACHINE STOCKFORGE/`. Adobe portal upload/submission remains manual and has not occurred.


## Cable-gland manual upload reported by user

The user reported that the cable-gland JPEG was manually uploaded to Adobe Stock. This is user-reported operational history only. No Adobe moderation result, approval, rejection, download, ranking, conversion, revenue, or sales evidence was provided or inferred. The project bundle remains `manual_portal_upload_prepared_not_submitted` from StockForge's perspective until an official outcome is supplied by the user.

A new research request now pivots to a separate generic illustrated animal-character direction inspired by the user's screenshot. The screenshot is treated as anecdotal directional evidence for recognizable focal character, team composition, bright accessories, and social/marketing utility; its text, interface, revenue figure, branding, exact masks/costumes, and exact animal designs must not be copied.


## New animal adoption/foster character hypothesis — dry-run ready

A new materially distinct JPEG lane `animal_adoption_foster_helper_characters` was added after the user supplied a screenshot showing a group of colorful animal characters. The screenshot is only anecdotal directional evidence for focal-character clarity, group hierarchy, bright accessory contrast, and social/marketing utility; its text, UI, revenue number, branding, masks, capes, symbols, exact animals, and exact designs are not copied. The rejected `pet_enrichment_object_illustrations` experiment remains rejected and is not being retried.

The selected hypothesis is `rescue-foster-helpers`: one compact trio of original fictional animal community helpers with three distinct species silhouettes, plain color-block volunteer vests, simple bandanas, warm expressions, and no emblem or text. Buyer job: original friendly animal characters for shelter adoption campaigns, foster recruitment, volunteer education, and animal-welfare social content. ASPCA and Best Friends public resources support the existence of campaign, adoption, foster, social, poster, flyer, and volunteer-communication jobs; Adobe query counts are supply proxies only. No demand, approval, ranking, download, conversion, revenue, or sales claim is made.

Added JPEG identity prohibits superhero/comic/cape/mask/lightning/shield shorthand, named shelters, slogans, brands, fictional copyrighted characters, artists, celebrities, real events, and medical claims. The lane uses one candidate, square 1024×1024 ZeroGPU preview route, JPEG delivery, white background, human review required, and no people/property claim until visual review. Quality gates explicitly permit fictional animal faces/bodies while still prohibiting real people, human hands/faces/bodies, text, brands, tools, screens, props, and outcome guarantees.

Full verification after code/schema updates: **302 passed, 1 skipped, 49 non-blocking Pillow warnings**, compileall passed, and `git diff --check` passed. Project-local batch: `animal_adoption_foster_helper_characters-20260825T103937Z-5097e7a7`; brief: `animal_adoption_foster_helper_characters--rescue-foster-helpers`. `portfolio generate --dry-run` returned **7/7 pre-GPU checks pass, 0 blockers**, profile `z-image-turbo`, 1024×1024 square, 8 steps, batch size 1, estimated 55 GPU seconds. No provider call or generation has occurred. Explicit approval is still required before exactly one preview.


## Animal-helper preview rejected for generic visual language

The user reviewed execution `9e49d293-914e-53d6-9c31-eba714bb5622` / artifact `344d9992-34ac-41c7-b070-794b70aa88c9` and stated that it was not interesting enough and felt like a standard/template mascot. This is recorded as a **REJECT for promotion**, not as a marketplace outcome. The visible issue is weak differentiation: four simple dog/cat-like characters in plain tops and bandanas, with limited narrative action and a generic mascot-group silhouette. No retry, color-only edit, crop-only edit, or silent prompt mutation is authorized. Any revision must be a materially changed candidate with a documented buyer-job and visual-identity change, followed by a new dry-run and explicit approval before generation.


## Revised animal adoption/foster story-vignette — dry-run ready

The first animal-helper preview was rejected by the user as too standard/template-like. It remains frozen as rejected and is not being retried. A materially new lane `animal_adoption_foster_story_vignettes` with concept `first-day-home` was created: a small puppy-like focal animal visibly steps out from an open unbranded soft carrier, flanked by a cat-like helper and rabbit-like helper in plain volunteer styling, with a folded blanket and blank circular tag as approved care props. The changed buyer-job expression is a first-day-home adoption/foster story vignette rather than a static mascot lineup.

The new identity requires visible transition action, triangular/diagonal focal hierarchy, three-species silhouette contrast, tactile care-prop storytelling, and plain non-superhero styling. It prohibits generic mascot lineup, generic character sheet, superhero/comic/cape/mask/lightning/shield shorthand, named shelter, slogan, brand, artist, celebrity, copyrighted character, real event, medical claim, text, and unrelated props. Adobe category mapping remains Animals (1) for future packaging, subject to portal verification.

Targeted tests: **27 passed**. Full suite after the revision: **303 passed, 1 skipped, 49 non-blocking Pillow warnings**; compileall and `git diff --check` passed. New project-local batch: `animal_adoption_foster_story_vignettes-20260825T114431Z-7152b2fd`; brief: `animal_adoption_foster_story_vignettes--first-day-home`. `portfolio generate --dry-run` returned **7/7 pre-GPU checks pass, 0 blockers**, `z-image-turbo`, square 1024×1024, 8 steps, batch size 1, estimated 55 GPU seconds. No provider call has occurred for the revised candidate. Explicit approval is still required before exactly one new preview.


## Animal adoption story-vignette finalized and ready upload

The user gave KEEP for execution `a20f3fca-9903-5fc3-afee-fc97fe6a2317`. Mandatory evaluation was recorded as accepted with conservative overall score 4.0/5: visual 4, technical 4, buyer fit 4, metadata accuracy 4. Marketplace outcome remains `not_submitted`. Learning summary returned `INSUFFICIENT_EVIDENCE`; one review cannot establish market demand or a niche policy.

One and only one private Kaggle RealESRGAN_x4plus finalizer was submitted for the accepted preview, kernel version 13. It completed successfully. Output was downloaded into the project-local `kaggle-finalizer-output/story-vignette-v13` directory and imported with matching request lineage. Master execution: `d27d373c-33d1-4785-8505-5e1462530148`; master artifact: `a37740f9-c5a0-4629-8749-6689240362d3`.

The master passed deterministic technical checks: JPEG 4096×4096, 16.777216 megapixels, RGB, assumed sRGB, quality 95, 4:4:4, decodable, approximately 1.34 MB. Full-resolution audit viewed all 9 row-major overlapping tiles. The image retains the three-character first-day-home story: puppy-like focal animal at open carrier, cat-like helper, rabbit-like helper, folded blanket, and blank tag. No readable text, logo, watermark, human, tool, or obvious IP was observed. Minor non-blocking notes: painterly/stipple texture from upscale and a blank heart-shaped collar tag.

The user explicitly requested finalization through ready-upload status. A manual Adobe bundle was prepared project-locally at `adobe-upload-bundles/adobe-20260825T120521Z-d27d373c`, with category 1 (Animals), XMP title/keywords, manifest, CSV, and checklist. Status is `manual_portal_upload_prepared_not_submitted`. Only the JPEG upload-copy was uploaded to temporary storage for Termux retrieval; no ZIP, CSV, JSON, Markdown, PNG, log, or credential was sent to the Android visual root. Adobe submission remains manual by the user, and no approval, download, ranking, conversion, revenue, or sales claim is made.


## Vector native workflow recommendation — no generation yet

The user asked how to obtain a vector format that is easier to commercialize through StockForge. Current findings: the safest route is local native SVG construction, not raster-to-vector tracing and not asking the raster image model to imitate vector style. Adobe officially accepts AI, EPS, and SVG vectors; it requires editable/original content, logical groups/layers, RGB, artboard offset `(0,0)`, maximum 45 MB, and appropriate artboard sizes [VECTOR_ROUTE_EVIDENCE-1]. Adobe's generative-AI vector guidance specifically says to rework generated vectors so they are easy to edit and to submit only original editable scenes/subjects, simple editable icon shapes, or seamless patterns [VECTOR_ROUTE_EVIDENCE-2].

StockForge already has a verified local native-vector route with deterministic SVG presets: `folder_upload`, `file_flow_micro_set`, `technical_badge`, `geometric_pattern`, and `modular_ribbon`. The current route validates XML, allowed native SVG elements, no raster/script/text embeds, dimensions, and pattern repeatability. It does not use GPU, Kaggle, or credentials. The route is appropriate for simple utility icons, icon sheets, and geometric patterns; it is not yet a general AI-to-SVG illustrator.

The recommended first vector hypothesis is a themed `document_review_delivery_micro_set`, not a generic icon pack: eight coherent symbols for intake, organize, review, approve, archive, restore, sync, and share. Buyer-job evidence comes from Adobe's icon guidance and Google Material Design guidance that icons function as quickly recognizable building blocks for UI, marketing, presentations, and animation. Adobe supply proxy snapshots are crowded: `utility icons` 604,515, `file management icon` 384,106, `"tech icons"` 25,018, `"icon pack"` 86,903, and `seamless geometric pattern` 6,279,918. These are supply proxies only, not demand, approval, ranking, conversion, revenue, or sales evidence.

No new vector lane, batch, SVG, preview, or upload was created in this milestone. The next gated step is to add one buyer-specific native SVG preset, run full tests and dry-run, and ask explicit approval for one local SVG trial. Reference report: `docs/research/VECTOR_NATIVE_WORKFLOW_RECOMMENDATION_2026-08-25.md`.

[VECTOR_ROUTE_EVIDENCE-1]: https://helpx.adobe.com/in/stock/contributor/help/vector-requirements.html
[VECTOR_ROUTE_EVIDENCE-2]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-vector-submission-guidelines.html
