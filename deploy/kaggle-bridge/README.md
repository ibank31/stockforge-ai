---
title: StockForge Kaggle Upscale Bridge
sdk: docker
app_port: 7860
---

CPU control service for StockForge. It does not perform GPU work itself. It stages one source image, submits the existing private `iqbalteguh/stockforge-finalizer` kernel to Kaggle, polls it, and exposes the resulting JPEG to the Cloudflare pipeline.

Required Space secret:

- `KAGGLE_API_TOKEN`

Optional variables:

- `STOCKFORGE_KAGGLE_KERNEL` (default `iqbalteguh/stockforge-finalizer`)
- `STOCKFORGE_KAGGLE_ACCELERATOR` (default `NvidiaTeslaT4`)

The bridge is intentionally one-job-at-a-time at the application level. Batch orchestration is not part of this stage.

Deployment smoke target: `/health`.
