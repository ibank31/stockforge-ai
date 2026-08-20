# StockForge AI — Image Quality Preflight

**Date:** 2026-08-20  
**Status:** IN PROGRESS

## Purpose

This module is the first deterministic visual-quality screening layer before Adobe-oriented submission review.

Adobe's current guidance emphasizes sharp/focused images, controlled noise and artifacts, balanced exposure, natural color, careful sharpening, and inspection at 100%. It does not publish universal numeric thresholds for all of these properties. StockForge therefore treats its numeric thresholds as **screening heuristics**, not Adobe rules.

## Implemented

`src/stockforge/image_quality.py`

- image existence and decoding check
- image dimensions captured for audit
- exposure clipping fraction screening
- deterministic edge-energy sharpness proxy
- extreme-saturation screening
- high-frequency residual audit metric
- PASS / REVIEW / FAIL result model
- machine-readable report via `to_dict()`
- explicit separation between automated screening and human visual review

## Current policy

| Signal | Current behavior |
|---|---|
| Decodability | FAIL if the raster cannot be decoded |
| Exposure clipping | REVIEW when >1.5% of luminance pixels are near black/white clipping |
| Sharpness proxy | REVIEW when edge-energy score is below 2.0 |
| Extreme saturation | REVIEW when >5% of pixels are near fully saturated and bright |
| High-frequency residual | PASS + audit metric only |

These thresholds are intentionally conservative and subject to benchmark calibration against real generated stock images.

## Why REVIEW instead of automatic rejection?

A numeric image signal cannot reliably understand creative intent. Motion blur, shallow depth of field, dramatic lighting, colorful products, and intentional texture can all be legitimate. Adobe's guidance likewise requires contextual judgment and 100% inspection.

Therefore:

```text
FAIL = objective technical corruption / impossible input
REVIEW = signal suggests a human should inspect the asset
PASS = no automatic warning from this layer
```

This layer does **not** determine:

- anatomical correctness
- hands/fingers/faces
- object geometry
- text/OCR
- logos/trademarks
- watermarks
- IP or prompt compliance
- commercial usefulness
- similarity/spam

Those are separate gates.

## Reference basis

Primary Adobe references checked on 2026-08-20:

- Adobe Stock quality and technical standards
- Adobe Stock generative AI content guidelines
- Adobe Stock generative AI submission best practices
- Adobe Stock common refusal reasons

The system must re-check Adobe's current guidance before changing policy thresholds.

## Verification requirement

The feature is not `DONE` until:

1. CI passes.
2. A real StockForge generated image is processed.
3. A real upscaled image is processed.
4. At least one deliberately bad fixture is detected.
5. Thresholds are calibrated against representative stock-photo samples.
6. The report is integrated into the production pipeline and persisted with the asset provenance.
