# StockForge AI — Changelog

All meaningful implementation milestones, live validations, architectural decisions, and verified fixes are recorded here. This is intentionally separate from Git commit history so a future session can understand **what was actually proven** rather than merely what files changed.

## 2026-08-20 — Adobe technical submission gate implementation

### IN PROGRESS — deterministic Adobe photo technical gate

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

The color-space check intentionally reports **REVIEW** when an ICC profile is absent rather than falsely claiming that the pixels are non-sRGB. A later finalization stage will normalize and embed an sRGB profile.

### Verification findings and fixes

- First GitHub Actions run tested 124 tests and found 2 failures in the new test fixture.
- The failure was caused by using `CmsProfile.tobytes()` directly with Pillow 12.3.0; the documented `ImageCmsProfile` wrapper is required for serialization.
- The test fixture was corrected.
- Local verification against the corrected implementation: **5 Adobe gate tests passed**.
- The implementation was also corrected to parse embedded ICC bytes through `BytesIO`, matching Pillow's supported profile-loading interface.
- A fresh GitHub Actions run is required before this feature can be promoted to `DONE`.

### Known limitations

This is **not yet the complete Adobe submission gate**. It does not yet implement:

- JPEG conversion/finalization
- sRGB conversion
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

The feature must not be marked `DONE` until CI passes and the implementation is audited.

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

The previous loader path:

```text
Qwen3ForCausalLM._from_config()
    ↓
load_file()
    ↓
model.load_state_dict()
```

was abandoned after the checkpoint produced shape mismatches and was identified as a quantized/packed FP8 mixed checkpoint.

The live runtime now loads:

```text
qwen_3_4b_fp8_mixed.safetensors
    ↓
Comfy-compatible CLIPLoader
    ↓
lumina2
    ↓
Z-Image generation
```

The first end-to-end generation is the verification evidence that the FP8 loader path is functional in the deployed environment.

### DONE — ZeroGPU build compatibility fixes

Two build blockers were found and corrected from actual Hugging Face build logs:

1. Python 3.10 could not install `comfy-diffusion==2.6.0`, which requires Python 3.12+.
2. Python 3.12 exposed a dependency conflict between Gradio 5.49 (`Pillow<12`) and `comfy-diffusion 2.6.0` (`Pillow>=12.1.1`).

The Space configuration was updated to Python 3.12 and Gradio 6.25-compatible runtime requirements.

### DONE — Adobe Stock readiness specification

Added `docs/ADOBE_STOCK_READINESS.md` covering:

- resolution
- JPEG/sRGB finalization
- file integrity
- technical quality
- anatomy/hand/face QA
- object consistency
- OCR
- logos/trademarks
- watermark detection
- prompt/IP compliance
- people/property/release logic
- generative-AI disclosure
- metadata
- duplicate/spam prevention
- commercial-value scoring
- copy-space planning
- upscaling
- provenance
- human approval
- marketplace policy maintenance

### DONE — Feature implementation ledger

Added `docs/FEATURE_ROADMAP.md` as the authoritative project feature matrix. It records the state of core foundation, registry, queue, plugin architecture, pipeline engine, provenance, ZeroGPU runtime, Adobe readiness, QA, enhancement, prompt intelligence, market intelligence, metadata, deduplication, compliance, security, and human approval.

## 2026-08-19 — Core/project foundation

Existing completed foundation recorded in `docs/STATUS.md` and `docs/PROJECT_CONTINUATION.md` includes:

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
