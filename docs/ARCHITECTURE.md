# StockForge Active Architecture

**Updated:** 2026-08-24
**Branch:** `main`

StockForge adalah control plane ringan berbasis Android/Termux yang mengubah market signal menjadi asset package yang dapat ditinjau. Generator bukan produk akhir; produk akhirnya adalah asset dengan buyer hypothesis, provenance, QC, metadata, dan submission state.

## End-to-end flow

```text
Market evidence
    ↓
Market opportunity + buyer job
    ↓
AssetSpec
    ↓
Concept variant + prompt package
    ↓
Pre-GPU compliance/layout/quota gate
    ↓
Provider router
    ├── Remote ZeroGPU / JPEG raster
    ├── Kaggle finalizer or future provider
    └── Local native SVG / no GPU
    ↓
Generation or local build
    ↓
Artifact + provenance
    ↓
Technical / semantic / commercial QA
    ↓
Enhancement or alpha finalization when verified
    ↓
Similarity and duplicate gate
    ↓
Metadata + marketplace compliance
    ↓
Human review
    ↓
Export / manual submission package
    ↓
Evidence and feedback loop
```

## Core boundaries

### Termux control plane

Termux owns project configuration, typed request construction, persistent job identity, routing policy, provenance, output folders, and human-review packages. It does not download or run heavy model checkpoints.

### Asset specification

`AssetSpec` carries the commercial constraints that must not be hidden in one prompt: buyer job, product kind, delivery format, layout, background/isolation policy, text/branding policy, originality levers, quality gates, and model-neutral capability preferences.

### Format routing

The router selects one product route, not every possible extension:

| Product kind | Format | Execution | Current status |
|---|---|---|---|
| `raster_illustration` | JPEG | Remote raster generation | Verified production path |
| `native_vector` | SVG | Local editable geometry | Locally verified; portal validation pending |
| `transparent_cutout` | PNG | Alpha producer/finalizer | Blocked until true-alpha path is verified |

A white-background PNG is not transparent. A raster trace is not a native vector. A square image is not automatically a seamless pattern.

### Provider and model separation

A model has an identity, revision, license/policy evidence, resource requirements, supported resolutions, and compatibility metadata. A provider supplies compute and execution. The core must not import vendor-specific engines directly; adapters isolate Gradio, ZeroGPU, Kaggle, Diffusers, Comfy-compatible loaders, or future providers.

The remote Gradio contract uses `generate_remote` with seven positional inputs, including durable `stockforge_job_id`, followed by event polling and output ingestion. Provider failures belong to execution records and must not corrupt the logical asset job.

### Quality and compliance

Technical checks cover dimensions, file integrity, RGB/sRGB, alpha, decodability, and format-specific structure. Semantic and commercial checks cover subject presence, object count, composition, text/brand risk, thumbnail readability, unique value, buyer-job fit, and duplicate/spam risk. Human review remains mandatory for visual quality, rights, releases, declarations, and final marketplace submission.

## Current compute policy

GPU quota is opportunistic capacity. A GPU call requires a specific buyer hypothesis and must produce a selected master, a meaningful concept experiment, or isolated diagnostic evidence. The system must not spend GPU on blind seed retries, large unreviewed batches, or weak previews.

## Active implementation map

- `src/stockforge/asset_spec.py` — typed commercial asset contract.
- `src/stockforge/format_router.py` — product-to-format routing and production blocks.
- `src/stockforge/native_vector.py` — deterministic editable SVG builder and inspector.
- `src/stockforge/seamless_pattern.py` — deterministic raster edge-continuity gate.
- `src/stockforge/remote_gradio.py` — remote worker adapter.
- `src/stockforge/recovery_orchestrator.py` — durable execution and artifact ingestion.
- `deploy/zerogpu/remote_api.py` — machine generation endpoint.

## References

- Current state: [`STATUS.md`](STATUS.md)
- Feature state: [`FEATURE_ROADMAP.md`](FEATURE_ROADMAP.md)
- Format decision: [`research/FORMAT_AND_NICHE_DECISION_2026-08-24.md`](research/FORMAT_AND_NICHE_DECISION_2026-08-24.md)
- Marketplace standard: [`MARKETPLACE_UPLOAD_READINESS_STANDARD.md`](MARKETPLACE_UPLOAD_READINESS_STANDARD.md)
- Provider backend contract: [`provider-backends.md`](provider-backends.md)
