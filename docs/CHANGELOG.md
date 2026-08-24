# StockForge AI — Changelog

All meaningful implementation milestones, live validations, architectural decisions, and verified fixes are recorded here. This is intentionally separate from Git commit history so a future session can understand **what was actually proven** rather than merely what files changed.

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
