# StockForge Vision QA Ensemble

## Purpose

Combine independent image-quality signals before an asset reaches the
submission pipeline. This is a QA system, not a predictor of marketplace
sales or guaranteed Adobe acceptance.

## Signals

- aesthetic: LAION/NIMA-style aesthetic provider
- semantic: vision-language model inspection
- commercial: buyer/use-case usefulness review
- anatomy: human anatomy/hand integrity
- subject_integrity: requested subject consistency
- artifact_risk: visible generation artifacts
- unexpected_text: OCR/text detector result
- ip_risk: logo/trademark/copyright risk detector
- similarity: CLIP/embedding similarity to the current batch/library

## Policy

`PASS` requires all available required signals to pass. Missing providers
produce `REVIEW`, never an automatic pass. Critical anatomy, subject, artifact,
text/IP failures can fail an image. High similarity can fail a duplicate.

Thresholds in code are StockForge heuristics. They are not Adobe thresholds.
They must be calibrated against real StockForge images and submission outcomes.

## Provider strategy

Providers remain behind interfaces so we can benchmark Qwen-VL/InternVL/
Florence-family vision models, LAION/NIMA aesthetic models, OCR, and CLIP
without coupling the policy layer to one model.

## Next

1. Implement concrete provider adapters.
2. Build a small labeled StockForge QA set.
3. Benchmark providers on anatomy, artifacts, text, realism, and commercial
   usefulness.
4. Calibrate thresholds from human review and marketplace outcomes.
5. Keep the final Adobe submission check separate from model scores.
