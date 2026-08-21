# Vision Provider Benchmark

## Goal

Select a vision QA stack using evidence from StockForge outputs, not generic
leaderboards. This benchmark does not predict Adobe acceptance or sales.

## Research-backed shortlist

### Qwen2.5-VL-3B-Instruct

Primary semantic-review candidate. Its model card describes visual understanding
of objects, text, charts, icons and layouts. Production use requires an exact
model/license review and an actual StockForge benchmark.

### InternVL3-2B

Small multimodal alternative worth benchmarking for semantic inspection. The
exact model artifact and license must be checked before deployment.

### Florence-family models

Candidate for specialized/lightweight vision tasks. Benchmark rather than
assuming general-purpose VLM superiority.

### PaddleOCR

Dedicated OCR layer for unexpected text. Keep it separate from semantic review.

## Human labels

Each StockForge image should be reviewed for:

- anatomy / hands
- face integrity
- subject integrity
- realism
- lighting consistency
- generation artifacts
- unexpected text
- logo / trademark risk
- commercial usefulness
- composition / copy space
- similarity to batch

Use 60 images initially: 10 clean stock-like, 10 anatomy defects, 10
object/geometry defects, 10 text/logo artifacts, 10 weak-commercial cases,
and 10 visually strong but generic cases. Two human reviewers establish the
reference labels. Keep private/customer images out of the repository.

## Metrics

The repository benchmark harness reports:

- evaluated samples
- accuracy
- false-positive rate
- false-negative rate

For rejection gates, false negatives are especially important. A missed serious
artifact is more costly than an extra manual review. Thresholds must therefore
be calibrated on held-out images and not copied from generic benchmarks.

## Runtime measurements

Record separately for each provider:

- download/model size
- cold-start time
- warm inference time
- peak RAM
- peak VRAM
- GPU seconds per image

Do not deploy a provider into the production ZeroGPU generator until runtime
cost is measured. Providers remain lazy/optional so the working generator does
not pay the startup cost.

## Decision rule

Choose the smallest provider stack that reaches the required QA recall while
keeping manual-review volume and GPU cost acceptable. A small VLM + OCR +
embedding model may beat a single large VLM for this workload.

## Current status

The offline scoring harness is implemented in `src/stockforge/vision_benchmark.py`.
Actual provider results are intentionally not fabricated. The next step is to
run it against a labeled set of real StockForge outputs.
