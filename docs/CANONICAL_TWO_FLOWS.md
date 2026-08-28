# StockForge Canonical Two-Flow Runbook

**Status:** Canonical operating contract  
**Audience:** All StockForge agents and operators  
**Rule:** When another document conflicts with this file, follow this file and report the conflict.

## Core distinction

StockForge memiliki tepat dua cara resmi untuk memperoleh gambar:

1. **Flow A — Full Internal Generation:** brief, prompt, renderer, audit, learning, finalizer, and packaging are controlled by StockForge.
2. **Flow B — External Rendering:** StockForge creates the brief and controls import, provenance, audit, learning, finalizer, and packaging, while the actual first render is made in an external application such as ChatGPT/GPT Image.

Both flows use the same human review gate and the same isolated format routes. Neither flow guarantees sales, marketplace approval, or automatic Adobe submission.

## Universal format decision

| Buyer job | Format | Finalizer | Human gate |
|---|---|---|---|
| Self-contained scene, illustration, environment, hero composition, copy-space visual | JPEG | Protected Kaggle RealESRGAN, one request → one RGB/sRGB JPEG master | Review composition, anatomy, artifacts, text/logo/IP risk, and full-resolution quality |
| Isolated reusable object, cutout, sticker, overlay, transparent utility asset | PNG | Isolated Kaggle BiRefNet, one request → one RGBA/sRGB PNG master | Review alpha at 100%, halos, holes, missing details, edge clipping, and unwanted shadows |
| Editable geometry or true vector requirement | SVG/vector | Frozen/not active for automatic production | Do not route through JPEG or PNG finalizer |

The agent must choose by **buyer job and background requirement**, never by filename or personal preference. JPEG and PNG finalizers must never be mixed.

## Flow A — Full generation inside StockForge

### Purpose

Use this flow when StockForge itself is the renderer and the user wants the complete generation pipeline from a repository-backed brief.

### Canonical sequence

```text
market evidence and portfolio lane
  → StockForge brief and format decision
  → dry-run and pre-GPU gate
  → one internal renderer preview
  → artifact + execution + provenance
  → technical auto-critique + niche memory
  → preview export to Android for human review
  → user KEEP / REJECT / REVIEW
  → format-specific finalizer preparation
  → one Kaggle job for the selected format
  → status COMPLETE
  → request_id and checksum match
  → master import and technical audit
  → 100% visual review
  → metadata and upload package
  → visual-only export to READY_UPLOAD_ADOBE
  → user uploads manually
```

### Operator steps

First, inspect the available lanes and asset-type policies without generating:

```bash
cd "$HOME/stockforge-ai"
export PYTHONPATH="$PWD/src"
export STOCKFORGE_HOME="${STOCKFORGE_HOME:-$HOME/.stockforge}"
python3 -m stockforge.cli portfolio lanes
python3 -m stockforge.cli portfolio asset-types
```

Use the chosen lane to create or load one portfolio plan. Always use the exact plan path and `brief_id` emitted by StockForge; never invent them. Run the dry-run first:

```bash
python3 -m stockforge.cli portfolio generate --dry-run \
  --project stock-assets \
  --plan <plan-file> \
  --brief-id <brief-id>
```

Only after the dry-run and pre-GPU gate pass may the agent run one live generation. One live command means one candidate; do not recreate the retired batch runner and do not perform blind seed retries.

The live internal renderer exports the only preview image for user review to:

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/
```

After the user says KEEP, prepare and submit only the selected route. For JPEG use the protected RealESRGAN path. For PNG use the isolated BiRefNet path. The agent must check the request target before submitting: JPEG must target `ai_upscale`, scale 4, RGB/sRGB JPEG; PNG must target `alpha_finalize`, scale 4, 1024×1024 source, and RGBA/sRGB 4096×4096 output.

After Kaggle is COMPLETE, download output into the project workspace, never into Android visual folders. Match the result `request_id` and source checksum to the submitted request. A mismatched or older result is rejected and must not be imported.

### Flow A output

A successful complete JPEG run produces two user-facing visual files:

| File | Location | Meaning |
|---|---|---|
| Preview | `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/` | Internal renderer output before finalizer |
| Ready upload | `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/` | Audited final JPEG with upload metadata/package support |

A PNG run may produce a technically valid Kaggle master, but the agent must not call it Adobe-ready until the PNG master importer and PNG upload-bundle support are verified in the active repository. If that support is absent, stop at `visual_review_required`, preserve the master in the project workspace, and report the gap.

## Flow B — External rendering, StockForge processing

### Purpose

Use this flow when GPT Image, ChatGPT, or another approved external application creates the initial image and StockForge performs everything after rendering.

### Canonical sequence

```text
StockForge selects candidate and writes detailed prompt
  → user renders one image in external application
  → user copies one source to ~/.stockforge/incoming/external/
  → portfolio import-external
  → source hash + provider provenance + candidate linkage
  → CPU technical audit + conservative learning record
  → preview export to Android for human review
  → user KEEP / REJECT / REVIEW
  → portfolio prepare-external-finalizer
      JPEG: RGB JPEG staging under Kaggle source budget
      PNG: 1024×1024 RGB worker input, no crop, BiRefNet makes alpha
  → one format-specific Kaggle job
  → status COMPLETE
  → request_id and checksum match
  → master import and technical audit
  → 100% visual review
  → metadata and upload package
  → visual-only export to READY_UPLOAD_ADOBE
  → user uploads manually
```

### Operator steps

The agent first provides the user a repository-backed prompt. The external app is a renderer only; it must not be treated as the source of StockForge metadata or approval.

The user copies one image into the incoming folder:

```bash
mkdir -p "$HOME/.stockforge/incoming/external"
cp "/storage/emulated/0/Pictures/<external-file>" \
  "$HOME/.stockforge/incoming/external/<candidate-id>-source.png"
```

The agent imports exactly one source:

```bash
cd "$HOME/stockforge-ai"
export PYTHONPATH="$PWD/src"
export STOCKFORGE_HOME="${STOCKFORGE_HOME:-$HOME/.stockforge}"
python3 -m stockforge.cli portfolio import-external \
  --project stock-assets \
  --source "$HOME/.stockforge/incoming/external/<candidate-id>-source.png" \
  --candidate-id <candidate-id> \
  --provider chatgpt
```

The import command creates provenance, hash, artifact, execution, technical findings, learning record, and a review preview. It does not call ZeroGPU, Kaggle, Adobe, or a finalizer.

After the user says KEEP, prepare the external asset for the correct worker:

```bash
python3 -m stockforge.cli portfolio prepare-external-finalizer \
  --project stock-assets \
  --execution <import-external-execution-id>
```

For JPEG, this creates an immutable derived RGB JPEG staging artifact while preserving source dimensions and composition. This prevents a large external PNG source from making the Kaggle kernel source invalid. For PNG, this creates an immutable derived 1024×1024 RGB artifact by fitting the complete source into a square canvas without crop. The BiRefNet worker then generates the final alpha channel. Neither operation overwrites the original external source.

Submit exactly one job to the matching worker. Never send a JPEG-intent scene to the PNG worker and never send a transparent utility object to the JPEG worker. Download output into the project workspace and match request ID before import.

### Flow B output

The visible output contract is identical to Flow A:

| File | Location | Meaning |
|---|---|---|
| Preview | `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/` | Imported external source for human review |
| Ready upload | `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/` | Audited final visual only, after route-specific package support |

All technical material remains in:

```text
/storage/emulated/0/StockForge/projects/stock-assets/
```

That includes request JSON, result JSON, logs, reports, database records, provenance, intermediate files, WebP files, model weights, and ZIP bundles. These files must never be copied to either Android visual folder.

## Non-negotiable rules

The agent must not claim that a file is ready to upload because it has a large resolution alone. It must verify request ID, checksum, format, color mode, color profile, megapixels, alpha requirements, visual review state, metadata support, and package support.

The agent must not submit a finalizer before an explicit user KEEP. It must not auto-submit to Adobe. It must not revive the retired batch runner. It must not force-push, reset, rebase, delete protected workers, expose credentials, or modify JPEG and PNG workers while preparing an external asset.

If a command fails, preserve the evidence, stop that route, and report the failure. Do not rerun the same request blindly. If a final result is `visual_review_required`, it remains review-required until a human checks it; technical success is not marketplace approval.

## Agent decision table

| Situation | Required action |
|---|---|
| Image not yet rendered | Generate the brief/prompt only; do not create a fake artifact |
| Internal renderer chosen | Use Flow A and one live candidate |
| External GPT image supplied | Use Flow B; import before any finalizer operation |
| Scene with background | JPEG route |
| Isolated transparent object | PNG route |
| User says KEEP | Prepare the matching finalizer; do not infer visual quality beyond the verdict |
| Request/result IDs mismatch | Reject result; do not import |
| Technical files appear in Android visual folder | Move them back to project workspace and report the violation |
| PNG importer/package support absent | Preserve PNG master in workspace and stop before ready-upload claim |

## References

[1] OpenAI, “The new ChatGPT Images is here,” https://openai.com/index/new-chatgpt-images-is-here/  
[2] OpenAI, “GPT Image Generation Models Prompting Guide,” https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide  
[3] Tongyi-MAI, “Z-Image-Turbo model card,” https://huggingface.co/Tongyi-MAI/Z-Image-Turbo  
[4] Tongyi-MAI, “Z-Image GitHub repository,” https://github.com/Tongyi-MAI/Z-Image
