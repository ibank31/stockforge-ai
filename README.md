# StockForge AI

StockForge AI is an Android-first digital-asset production automation platform. The repository’s **active production scope is limited to two raster output formats: PNG and JPEG**.

> **If a task does not target PNG or JPEG, it is not an active StockForge production task. Do not infer a third route from old code, research notes, or archived runbooks.**

## Start here

Agents and maintainers must read these files in order:

1. [`AGENTS.md`](AGENTS.md) — repository-wide operating rules and the format boundary.
2. [`docs/ACTIVE_SCOPE.md`](docs/ACTIVE_SCOPE.md) — the authoritative PNG/JPEG contract.
3. [`docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md) — the only active end-to-end operational workflow.
4. [`docs/STATUS.md`](docs/STATUS.md) — the current implementation snapshot and limitations.

Historical material is under [`docs/archive/`](docs/archive/) and must not be used as instructions.

## Active output routes

| Route | Intended use | Final technical contract |
|---|---|---|
| **PNG** | Isolated objects, cutouts, stickers, overlays, and transparent utility assets | RGBA/true alpha, sRGB, isolated BiRefNet finalizer, technical alpha gate, and 100% visual edge review |
| **JPEG** | Self-contained scenes, environments, hero compositions, illustrations with backgrounds, and copy-space visuals | RGB/sRGB, active resolution gate, protected RealESRGAN finalizer, and full-resolution visual review |

Select the route from the buyer job and background requirement, not from the source file extension or filename. The current portfolio contract maps `pet_enrichment_object_illustrations → puzzle-feeder` to **JPEG**.

## Repository boundaries

SVG/vector generation, retired batch runners, local-AI trials, provider experiments, pretrials, and other historical workflows are not active production targets. Their source code or tests may remain for compatibility and audit evidence, but they must not be extended or invoked for a new production run.

The repository preserves provenance and requires human review before finalization and upload packaging. StockForge does not automatically submit assets to Adobe or another marketplace.

## Development

Install the package and development dependencies, then run the test suite from the repository root:

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest -q
```

When changing an active PNG or JPEG flow, update [`docs/ACTIVE_SCOPE.md`](docs/ACTIVE_SCOPE.md), [`docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md), and [`docs/STATUS.md`](docs/STATUS.md) in the same commit. Do not add a competing operational runbook.
