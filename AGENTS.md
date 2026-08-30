# StockForge AI — Active Repository Scope

## Non-negotiable production scope

StockForge AI is currently focused **only on generating and finalizing raster assets as PNG or JPEG**. Any new implementation, bug fix, test, workflow, or documentation must support one of these two output formats.

The active routes are:

| Output | Intended product | Required technical contract |
|---|---|---|
| **PNG** | Isolated object, cutout, sticker, overlay, or transparent utility asset | RGBA/true alpha, sRGB, transparent background, isolated BiRefNet finalizer, technical and 100% visual edge review |
| **JPEG** | Self-contained scene, environment, hero composition, illustration with background, or copy-space visual | RGB/sRGB, minimum resolution enforced by the active gate, protected RealESRGAN finalizer, technical and full-resolution visual review |

## Agent operating rules

Read [`docs/ACTIVE_SCOPE.md`](docs/ACTIVE_SCOPE.md), then [`docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md), and finally [`docs/STATUS.md`](docs/STATUS.md) before changing or running a production flow. These files are the active source of truth.

Choose PNG versus JPEG from the buyer job and background requirement, never from a filename, source extension, or an intuitively similar lane name. `pet_enrichment_object_illustrations → puzzle-feeder` is a **JPEG** contract in the current portfolio registry; it must not be treated as a PNG candidate merely because the subject is an object.

Do not use, revive, or extend SVG/vector, batch-generation, local-AI, provider-trial, pretrial, or other historical routes as production routes. Do not use archived documents as instructions. They are retained only as historical evidence and must be treated as non-authoritative.

Do not introduce a third production format or a duplicate operational runbook. If a request does not clearly target PNG or JPEG, stop and clarify the requested raster route instead of guessing.

## Safety and validation

Never route JPEG through the PNG worker or PNG through the JPEG worker. Preserve immutable source and provenance lineage. Require the human KEEP/review gate before finalization or submission. The repository does not perform Adobe submission automatically.

When the PNG or JPEG contract changes, update `docs/ACTIVE_SCOPE.md`, `docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`, and `docs/STATUS.md` in the same commit. Keep historical material under `docs/archive/` and label any newly retained historical document as non-authoritative.

## Validation command

Run the test suite from the repository root after changes:

```bash
python3 -m pytest -q
```

If only documentation changed, still verify links and inspect the diff before committing.

> **Short version:** Generate PNG or JPEG. Nothing else is an active production target.
