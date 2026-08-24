# StockForge Development Status

**Updated:** 2026-08-24
**Branch:** `main`
**Latest verified commit:** `0bb3f68`

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

The JPEG path is the only generative route with a recorded live preview and completed master workflow. Native SVG is a genuine local geometry route, not a raster trace. The research-backed folder-upload SVG trial has now been built locally: structural status PASS, visual status REVIEW_REQUIRED pending user review, and no portal validation. Native geometric pattern retains its local repeatability gate. PNG now has a conservative offline true-alpha normalizer that refuses opaque RGB sources and preserves the source, but PNG must never use a white or checkerboard background as a substitute for actual transparency and remains blocked from production.

## Completed foundation

The repository contains the CLI, SQLite project and asset registries, persistent job queue, plugin/pipeline contracts, provenance and lineage records, provider routing, remote Gradio adapter, portfolio planning, asset-type selection, prompt compilation, technical image gates, deduplication controls, review packages, Android export separation, Adobe metadata upload-copy workflow, deterministic native SVG presets for the research-backed folder-upload baseline, a new eight-action file-flow micro-set, modular ribbons, technical badges, and geometric patterns, plus dedicated native-vector element, utility-set, and pattern lanes.

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

1. Mature the JPEG route before any routine generation: select one globally researched buyer job, strengthen the scene prompt/layout contract, and keep one-candidate evidence rules.
2. Benchmark the prepared Kaggle Real-ESRGAN finalizer once the target runtime is available, comparing source/master at 100% for artifacts, texture, edges, color, dimensions, and sRGB.
3. Strengthen semantic/commercial QA for JPEG; the no-provider path must remain review/blocking rather than pretending anatomy, realism, or buyer usefulness passed.
4. Expand reviewed JPEG lane/category mappings conservatively and keep title/keyword generation visual-first, platform-specific, and anti-spam.
5. Keep SVG value-upgrade and PNG alpha work frozen until the JPEG maturation checkpoint is complete; do not generate or upload them in this phase.
6. Keep model/provider registry, health, quota, and failover contracts explicit before adding more GPU providers.

## Non-negotiable safety rules

- Do not generate blindly, retry only by changing seed, or run large batches without a documented buyer hypothesis.
- Do not treat a preview, upscaled image, local SVG, or technical pass as marketplace acceptance.
- Do not upload or submit to Adobe automatically; declarations, CAPTCHA, releases, and final submission remain human-controlled.
- Do not duplicate the same visual as JPEG, PNG, and SVG merely to multiply formats.
- Do not put credentials in files, commits, logs, or user-facing output.
- Use the user-approved Android output folders only for visual files; keep technical files in the project workspace.

## Verification

The current main branch has passed **283 tests with 1 skipped** in the sandbox, with 45 non-blocking Pillow deprecation warnings. Syntax compilation and whitespace checks pass. JPEG market/Adobe research and the frozen SVG plan are durable. JPEG scene prompt safety now distinguishes controlled human-centered scene stories from isolated-object negative prompting while retaining anatomy, text, artifact, and IP safeguards. The JPEG route has a verified historical preview→finalizer→XMP workflow, but the actual target-runtime Real-ESRGAN benchmark and a provider-backed semantic QA pass remain incomplete. Platform-specific metadata relevance safeguards validate limits, duplicate/spam patterns, category requirements, and visual-first keyword ordering without inventing demand. The working tree must be rechecked after this status synchronization.

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
| Global discoverability and SVG value plan | [`research/svg_global_discoverability_notes_2026-08-24.md`](research/svg_global_discoverability_notes_2026-08-24.md) and [`research/SVG_VALUE_AND_MARKET_ALGORITHM_PLAN_2026-08-24.md`](research/SVG_VALUE_AND_MARKET_ALGORITHM_PLAN_2026-08-24.md) |
| JPEG maturation and market research | [`research/JPEG_MATURATION_PLAN_2026-08-24.md`](research/JPEG_MATURATION_PLAN_2026-08-24.md) and [`research/jpeg_market_2026-08-24.md`](research/jpeg_market_2026-08-24.md) |
| Marketplace readiness | [`MARKETPLACE_UPLOAD_READINESS_STANDARD.md`](MARKETPLACE_UPLOAD_READINESS_STANDARD.md) |
| Android operation | [`TERMUX_CONTROL_PLANE.md`](TERMUX_CONTROL_PLANE.md) |
| History | [`CHANGELOG.md`](CHANGELOG.md) |

## References

[1]: https://helpx.adobe.com/ie/stock/contributor/help/png-with-transparency.html "Adobe Stock — PNG files with transparency"
[2]: https://helpx.adobe.com/ie/stock/contributor/help/vector-requirements.html "Adobe Stock — Content Guidelines: Vectors"
[3]: https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends "Adobe — 2026 Creative Trends"
