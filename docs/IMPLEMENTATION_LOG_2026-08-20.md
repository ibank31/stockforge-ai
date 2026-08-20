# StockForge AI — Implementation Log — 2026-08-20

## Image quality preflight

### State
**IN PROGRESS**

### Implemented

- Added `src/stockforge/image_quality.py`.
- Added deterministic raster decoding verification.
- Added exposure clipping screening.
- Added edge-energy sharpness proxy.
- Added extreme-saturation screening.
- Added high-frequency residual audit metric.
- Added structured PASS / REVIEW / FAIL checks.
- Added `tests/test_image_quality.py`.
- Added `docs/IMAGE_QA_PREFLIGHT.md`.

### Evidence

Implementation is committed to branch `feat/zerogpu-runtime` and covered by automated tests. GitHub Actions must finish successfully before this milestone can advance.

### Research basis

Adobe Stock's current guidance explicitly emphasizes sharpness/focus, avoiding noise and artifacts, balanced exposure, natural color, careful sharpening, and inspection at 100%. Adobe also states that generative-AI submissions must be checked for visual anomalies and anatomical errors, and that only differentiated, commercially useful outputs should be selected.

### Important limitation

The implemented numeric thresholds are StockForge screening heuristics, not Adobe-published acceptance thresholds. They intentionally produce `REVIEW` for ambiguous visual signals rather than pretending a formula can replace a human reviewer.

### Next work

1. Verify CI.
2. Run the preflight against the real 1024×1024 ZeroGPU benchmark.
3. Run it against the 4× upscaled result.
4. Calibrate thresholds.
5. Add AI-specific anomaly detection for faces/hands/objects.
6. Add OCR/logo/watermark screening.
7. Persist QA results into asset provenance.
