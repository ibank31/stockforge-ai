# StockForge QA Dataset

This directory defines the reproducible workflow for building the internal Vision QA benchmark.

## Dataset policy

Generated images are not committed to Git. Store them locally or in an approved artifact store. Commit only labels, manifests, hashes, and benchmark reports.

## Required manifest fields

Each sample should contain:

- `id`
- `image_path`
- `sha256`
- `category`
- `human_labels`
- `reviewer_count`
- `notes`

Categories:

- `clean_stock_like`
- `anatomy_defect`
- `object_geometry_defect`
- `text_logo_artifact`
- `weak_composition`
- `beautiful_generic`

## Human label scale

Use 0-1 values. `1` means acceptable/clean for the named dimension. `0` means clearly unacceptable.

Required dimensions:

`anatomy`, `face_integrity`, `subject_integrity`, `realism`, `lighting_consistency`, `artifact_risk`, `unexpected_text`, `ip_risk`, `commercial_usefulness`, `composition`, `similarity_risk`.

For risk dimensions, a high score means low risk.

## Split

Do not tune thresholds and report final performance on the same images. Use a development set and a held-out evaluation set.

## Reproducibility

Use SHA-256 hashes so benchmark results can be tied to exact image bytes. Keep provider/model version and runtime measurements with every benchmark result.
