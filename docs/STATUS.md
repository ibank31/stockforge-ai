# StockForge Development Status

**Updated:** 2026-08-24
**Branch:** `main`
**Latest verified commit:** `28e1c85`

## Current milestone

**Evidence-backed multi-format asset factory for Android/Termux and Adobe Stock.**

StockForge treats generation as one step inside an asset package containing a buyer hypothesis, typed asset specification, prompt, provider execution, visual/technical QA, provenance, metadata, and human-review state. The system must not turn a market signal or a clean file into a claim of sales or marketplace acceptance.

## Verified production paths

| Path | Format | Execution | Status |
|---|---|---|---|
| Conceptual scene / raster illustration | JPEG | Remote ZeroGPU preview, optional finalizer, XMP upload copy | **Verified workflow** |
| Native geometric object/icon/pattern | SVG | Local deterministic builder, no GPU | **Locally verified; portal not yet verified** |
| Transparent cutout / overlay | PNG with real alpha | Alpha producer and PNG finalizer | **Blocked until alpha path is validated** |
| Seamless raster pattern | PNG/JPEG candidate | Local edge-continuity gate | **Gate implemented; commercial review still required** |

The JPEG path is the only generative route with a recorded live preview and completed master workflow. Native SVG is a genuine local geometry route, not a raster trace. Native geometric pattern now has a local repeatability gate and is eligible for one controlled local trial. PNG now has a conservative offline true-alpha normalizer that refuses opaque RGB sources and preserves the source, but PNG must never use a white or checkerboard background as a substitute for actual transparency and remains blocked from production.

## Completed foundation

The repository contains the CLI, SQLite project and asset registries, persistent job queue, plugin/pipeline contracts, provenance and lineage records, provider routing, remote Gradio adapter, portfolio planning, asset-type selection, prompt compilation, technical image gates, deduplication controls, review packages, Android export separation, Adobe metadata upload-copy workflow, deterministic native SVG presets for a research-backed folder-upload icon, modular ribbons, technical badges, and geometric patterns, plus dedicated native-vector element and pattern lanes.

`portfolio asset-types` lists the supported asset categories. `portfolio readiness --asset-type <type>` explains the chosen format, readiness state, blockers, candidate niches, and next step without calling a provider. `portfolio plan-type --asset-type <type>` turns a supported choice into one evidence-aligned brief with niche, prompt, format route, and no-generation notice; `native_object` now defaults to the research-backed `folder-upload` icon hypothesis. `portfolio trial-readiness` requires a written hypothesis and purpose before a future provider call, and enforces one candidate per trial. The selector fails closed rather than silently converting an unsupported type into JPEG.

The remote worker contract is aligned with the deployed `generate_remote` endpoint. It uses a durable `stockforge_job_id`, bounded single-image requests, terminal-state polling, and output ingestion. The ZeroGPU deployment entrypoint is `deploy/zerogpu/remote_api.py` for programmatic generation.

## Current research conclusion

The preserved social/marketplace evidence supports three buyer jobs rather than one universal format:

| Buyer job | Recommended lane | Evidence interpretation |
|---|---|---|
| Cinematic, surreal, seasonal, workplace, nature, and conceptual scenes | JPEG raster | Motif signal; not proof of sales or format. |
| Isolated objects, technical clip-art, icons, badges, food/produce, and geometric elements | Native SVG first; PNG later when alpha is real | Utility-asset signal; thumbnail background does not prove transparency. |
| Patterns, backgrounds, and decorative elements | SVG or raster according to material | Requires an explicit seamless test for seamless claims. |

Adobe’s public guidance supports transparent PNG utility assets and genuine editable vectors, while its 2026 trend report supports tactile/material, surreal, local-specific, and emotionally useful creative hypotheses. These sources guide experiments; they do not predict revenue.[1] [2] [3]

## Current priorities

1. Complete the semantic review and one controlled local trial for the research-backed folder-upload SVG icon, then expand deterministic native SVG builders for technical, food/produce, badge, simple-character, and geometric-pattern families only when each has a clear buyer job.
2. Keep JPEG scene generation behind the pre-GPU prompt, rights, layout, quota, and visual-quality gates.
3. Build a local PNG alpha producer with true-alpha assertion, anti-fringe checks, canvas trimming, sRGB validation, and one controlled portal validation.
4. Connect evidence logs to buyer-job and format routing without turning engagement or earnings screenshots into sales forecasts.
5. Keep model/provider registry, health, quota, and failover contracts explicit before adding more GPU providers.

## Non-negotiable safety rules

- Do not generate blindly, retry only by changing seed, or run large batches without a documented buyer hypothesis.
- Do not treat a preview, upscaled image, local SVG, or technical pass as marketplace acceptance.
- Do not upload or submit to Adobe automatically; declarations, CAPTCHA, releases, and final submission remain human-controlled.
- Do not duplicate the same visual as JPEG, PNG, and SVG merely to multiply formats.
- Do not put credentials in files, commits, logs, or user-facing output.
- Use the user-approved Android output folders only for visual files; keep technical files in the project workspace.

## Verification

The current main branch has passed **273 tests with 1 skipped** in the sandbox. Syntax compilation and whitespace checks pass after the folder-upload lane changes; the working tree is clean at commit `28e1c85`.

The test suite includes the remote generation contract, provider quota routing, asset specification, format routing, PNG alpha gate and conservative normalizer, native SVG builder, seam gate, provenance, portfolio delivery, deduplication, evaluation ledger, and existing core behavior. Pillow deprecation warnings remain non-blocking cleanup items.

## Output and learning contract

A future successful generation may export one visual preview to `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/` when an Android Download mount is available. An approved final JPEG may be copied as a separate upload copy to `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/`; the original master and project records remain unchanged. Project packages, JSON, CSV, logs, and review records stay inside the project workspace.

Every reviewed generation can be recorded in the project-local append-only ledger at `evaluations/generation_evaluations.jsonl`. The ledger ties human scores and rejection reasons to execution, artifact, buyer job, format, provider, model, and workflow hash. Its summary is descriptive only: it does not predict sales or trigger a new generation. No generation is required to create or test the ledger.

## Source of truth

| Purpose | Document |
|---|---|
| Navigation | [`docs/README.md`](README.md) |
| Current status | This file |
| Current architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Feature state and next work | [`FEATURE_ROADMAP.md`](FEATURE_ROADMAP.md) |
| Product/format decision | [`research/FORMAT_AND_NICHE_DECISION_2026-08-24.md`](research/FORMAT_AND_NICHE_DECISION_2026-08-24.md) |
| SVG market research | [`research/SVG_MARKET_RESEARCH_2026-08-24.md`](research/SVG_MARKET_RESEARCH_2026-08-24.md) and [`research/svg_market_2026-08-24.md`](research/svg_market_2026-08-24.md) |
| Marketplace readiness | [`MARKETPLACE_UPLOAD_READINESS_STANDARD.md`](MARKETPLACE_UPLOAD_READINESS_STANDARD.md) |
| Android operation | [`TERMUX_CONTROL_PLANE.md`](TERMUX_CONTROL_PLANE.md) |
| History | [`CHANGELOG.md`](CHANGELOG.md) |

## References

[1]: https://helpx.adobe.com/ie/stock/contributor/help/png-with-transparency.html "Adobe Stock — PNG files with transparency"
[2]: https://helpx.adobe.com/ie/stock/contributor/help/vector-requirements.html "Adobe Stock — Content Guidelines: Vectors"
[3]: https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends "Adobe — 2026 Creative Trends"
