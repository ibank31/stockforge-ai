# StockForge AI — Session Handover

**Updated:** 2026-08-24

## Purpose of this handover

This document lets a new agent continue the StockForge project without repeating the infrastructure investigation, Kaggle debugging, Adobe portal testing, or Android workflow experiments. The user works primarily from **Android Termux** and wants the system to produce commercially usable standalone GenAI stock assets with minimal phone-side work.

> **Working rule:** Termux is the control plane. Remote services do GPU work. The user should receive a final JPEG package on the phone, review it, and make only the portal actions that cannot be safely automated.

## Current repository state

| Item | Current state |
|---|---|
| Repository | `ibank31/stockforge-ai` |
| Branch | `feat/asset-factory-architecture` |
| Latest functional commit before this handover | `c65db0f` — Adobe XMP portal checklist |
| Main CLI | `python -m stockforge.cli` |
| Android project | `stock-assets` |
| Android project root | `/storage/emulated/0/StockForge/projects/stock-assets` |
| Test status before this handover | `227 passed, 1 skipped` |
| User language | Indonesian |

The user must keep the Android installation lightweight: activate the existing virtual environment, use `python -m stockforge.cli`, and avoid installing local GPU dependencies such as BasicSR or RealESRGAN.

## Production architecture that has been proven

| Stage | Service | Status | Notes |
|---|---|---|---|
| Preview generation | Hugging Face ZeroGPU Space, Z-Image Turbo | **Working** | Space uses standalone portfolio mode; legacy construction injection is removed. |
| Preview layouts | Square and `hero-landscape` canvas | **Working** | `hero-landscape` is 1344×768 and is appropriate for layout/copy-space briefs. |
| Master finalization | Private Kaggle RealESRGAN x4 worker | **Working** | Actual benchmark and fiber-arch master completed with JPEG RGB/sRGB validation. |
| Master delivery | Termux project ZIP | **Working** | Master packages remain `review_ready`; never call them automatically marketplace-approved. |
| Adobe metadata transfer | XMP embedded in upload-JPEG copy | **Working** | Adobe portal was observed to read the embedded title and keywords automatically. CSV is not needed on Android. |
| Adobe submission | Manual portal action | **Required** | Declarations, Terms and Conditions, CAPTCHA, and final submit remain user-controlled. |

## Marketplace policy baseline

Adobe Stock is the primary initial marketplace for fully GenAI assets. The package must use an accurate visual title, only relevant keywords, a truthful GenAI declaration, and human review before submission. The technical target is a JPEG RGB/sRGB master above 4 MP. The repository has policy notes in `docs/research/` and additional research outside the repository.

Do not claim acceptance, sale, download volume, or revenue until the marketplace supplies evidence. Do not claim `submission_ready` merely because a generation or technical check passed.

## Kaggle finalizer status

The selected RealESRGAN x4 Kaggle route has been validated in practice. Earlier runtime issues were fixed: request staging, embedded payload placement, BasicSR/TorchVision compatibility, and the obsolete model-weight URL. The finalizer output was technically validated with actual masters.

The first proven master was a 4096×4096 technical benchmark. The selected fiber-arch candidate was finalized at **5376×3072 px** (about **16.52 MP**), JPEG RGB/sRGB. The finalizer is therefore operational, but it must be used only for visually selected previews—not weak or generic previews.

### GPU quota rule

Every GPU job must create one of the following: a selected master, a new buyer-concept experiment, or isolated diagnostic evidence. Do not use seed-only retries, upscale generic previews, or run blind dependency retries. A sensible future allocation is preview experiments first, selected master upgrades second, then a small diagnostic reserve; adjust it from actual quota and job duration.

## Selected asset: fiber-arch

| Field | Value |
|---|---|
| Preview execution | `7bd60841-264d-5af2-bf86-283813e0b068` |
| Preview artifact | `eb56cad0-3a39-4bfa-89a8-74f329a2c9f0` |
| Master artifact | `192ff467-92c8-4bed-b352-e9bc03a75696` |
| Visual concept | Recycled fiber-paper arch with sage-green inner layer and copy space |
| Master status | `review_ready`; technically passed; human review completed for initial Adobe test |
| First portal submission | User reported completing Adobe submit manually after Terms/CAPTCHA. This is **not evidence of acceptance**. |
| Current XMP upload test | Adobe successfully auto-populated title and keywords from a newly prepared `sf-192ff46.jpg` JPEG upload copy. Do not submit this duplicate test draft; delete it from Adobe New after confirmation. |

## Critical Adobe Android workflow — current standard

### What is proven

The Android file picker displayed local CSVs but disabled selection because Adobe requests strict `text/csv` and the device provider reported an incompatible MIME type. Do **not** spend more time attempting CSV fixes unless an actual future need arises.

The superior approach was verified: StockForge creates a **copy** of the final JPEG with XMP title and keywords embedded. When this JPEG was uploaded to Adobe Contributor, the portal populated the title and keyword fields automatically. The source registered master and its lineage are not modified.

### Preparing an upload folder

After the user has visually approved a master, run in Termux:

```bash
cd ~/stockforge-ai
source .venv/bin/activate
git pull --ff-only origin feat/asset-factory-architecture

python -m stockforge.cli portfolio prepare-adobe-upload \
  --project stock-assets \
  --latest-master \
  --approved
```

The command creates an Android folder like:

```text
/storage/emulated/0/Download/AdobeStock/READY_TO_UPLOAD/<batch>/
  asset-<artifact-prefix>/
    sf-xxxxxxxx.jpg       # Upload this file only; title + keywords are embedded
    UPLOAD_METADATA.txt   # Tap to open on Android; portal checks and declarations
```

Each asset folder contains one final upload JPEG and one readable text guide. No CSV is needed. The output also includes `BATCH_MANIFEST.json` and `README.txt` at the batch root for internal traceability.

### Portal actions still required

For a fiber-arch-style visual, after uploading `sf-xxxxxxxx.jpg` through Adobe Browse:

1. Verify that title and keywords were filled from XMP.
2. Set **File type** to **Illustrations**, not Photos.
3. Set **Category** to **Graphic Resources**.
4. Mark **Created using generative AI tools** truthfully.
5. Answer the people/property declaration based on the actual image and prompt. For the abstract fiber arch, no real recognizable people/property were used; follow the portal's subsequent fictional-property requirement truthfully.
6. Review Terms and Conditions personally, complete CAPTCHA personally, and submit only after explicit user approval.

### Metadata policy now enforced in upload copies

The `fiber-arch` upload metadata retains only visible-content terms:

```text
recycled paper, paper arch, fiber texture, sage green, tactile material,
abstract paper sculpture, copy space, minimal design, isolated object,
white background, neutral palette
```

The upload layer removes known nonvisual phrases such as `website hero background`, `presentation cover`, `brand system`, and `generative AI`. These terms describe workflow, buyer use, or generation method rather than visible image content. The GenAI disclosure remains a portal checkbox, not a keyword.

Files implementing the Adobe workflow:

- `src/stockforge/adobe_upload_bundle.py`
- `src/stockforge/portfolio.py`
- `tests/test_adobe_upload_bundle.py`
- `docs/TERMUX_CONTROL_PLANE.md`

## Current user-side output

The user just ran `prepare-adobe-upload` after pulling `c65db0f` and obtained an older-format folder at:

```text
/storage/emulated/0/Download/AdobeStock/READY_TO_UPLOAD/adobe-20260824T080729Z-f5e1a7cf
```

The session then created and tested XMP before the latest final correction. For future folders, the user should pull the post-handover commit and run the command again to obtain the clean current XMP workflow. The current upload test screenshot showed that embedded title and keywords were read successfully but Portal fields still require manual type/category/declarations.

## User preferences and non-negotiable rules

The user wants the agent to do everything feasible and receive final files on Android. Explanations should be in Indonesian, clear and concise. The user prefers very low cost until sales occur.

- No construction-specific work or legacy construction prompt injection.
- Produce diverse standalone assets for web, product, marketing, editorial, and commerce buyers.
- Do not mass-produce. Each new GPU job needs a specific visual or buyer hypothesis.
- Adobe Stock is the primary target. Dreamstime is secondary eligible, but do not automate another marketplace without rechecking its active contributor policy.
- Never auto-submit a marketplace asset. Use explicit confirmation before final submission.
- Do not add paid cloud providers, Cloudflare, permanent workers, or scheduled jobs without explicit user authorization and budget.
- Do not place credentials in files, commits, logs, or messages. Prior Hugging Face and Kaggle tokens were exposed in chat. They should be rotated/revoked by the user; no token remains intentionally stored in the sandbox.

## Recommended next action after session handover

1. Tell the new agent to read this handover first.
2. Confirm current Adobe status: whether the user has already deleted the duplicate XMP test upload from Adobe New, and whether the initial fiber-arch asset is visible in In review.
3. Do not submit another fiber-arch copy.
4. Select a genuinely new portfolio brief, run one ZeroGPU preview, audit the visible image, then use Kaggle only if it passes.
5. For a new final master, use the XMP upload folder workflow described above; remove nonvisual metadata and verify portal fields before the user submits.

## Suggested first message in a new session

> Read `docs/SESSION_HANDOVER_2026-08-24.md` in the `ibank31/stockforge-ai` repository first. Continue StockForge AI from the current Android/Adobe XMP workflow. Do not repeat the CSV Android experiments; use JPEG metadata embedding. Confirm the user’s Adobe portal status and then proceed only with one new, non-duplicate portfolio candidate.

## References

1. [Adobe Stock Contributor content upload guidelines](https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html)
2. [Adobe Stock Generative AI content guidelines](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html)
3. [Adobe Stock Artist Hub: Maximize Metadata to Get Discovered](https://stock.adobe.com/pages/artisthub/get-started/photo-video-metadata-stock-contributor-guide-pt-3)
4. [Adobe Lightroom Classic: Publish from Lightroom Classic to Adobe Stock](https://helpx.adobe.com/si/lightroom-classic/help/prepare-send-or-post-photos.html)
5. [Adobe Stock Contributor CSV requirements](https://helpx.adobe.com/stock/contributor/manage-your-portfolio/csv-requirements-content.html)
6. [Android Storage Access Framework](https://developer.android.com/training/data-storage/shared/documents-files)
7. [RFC 4180: Common Format and MIME Type for CSV Files](https://www.rfc-editor.org/rfc/rfc4180)
