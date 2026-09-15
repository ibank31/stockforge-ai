# StockForge V2 browser entrypoint

The browser communicates only with the StockForge control plane at `stockforge-ai.pages.dev`. It never accesses SQLite, R2 credentials, HF credentials, or GPU workers directly.

## Production boundary

```text
Browser / page.dev
        ↓
Cloudflare Pages Functions
        ↓
D1 + R2 + Workers AI
        ↓
Cloudflare Workflows
        ↓
HF ZeroGPU
   ┌────┴────┐
   ↓         ↓
Generate   4x Upscale
   └────┬────┘
        ↓
Final master → QA → metadata → human review
        ↓
READY_UPLOAD_ADOBE
```

Pages Functions provide the API and bind D1, R2, and Workers AI. Cloudflare Workflows provide durable execution so a browser can close without killing the production job. The Pages Function starts the Workflow through a Cloudflare service binding.

`ibank31/stockforge-zerogpu` is the only production GPU lane in the $0 architecture. Its machine interface exposes `generate_remote` and `upscale_remote`. Both are queued through the same ZeroGPU Space and remain subject to the account's free GPU quota.

Kaggle is retained only for R&D, model benchmarking, diagnostics, and non-commercial experiments. It is deliberately excluded from the commercial production path.

## Required Cloudflare resources

- Pages project: `stockforge-ai`
- D1 database: `stockforge`
- R2 bucket: `stockforge-assets`
- Workers AI binding: `AI`
- Service binding: `STOCKFORGE_WORKFLOW` → Worker `stockforge-pipeline`
- Workflow binding on the pipeline Worker: `STOCKFORGE_PIPELINE`

The GitHub Actions deployment workflow provisions the Pages project, D1 database, and R2 bucket and deploys the durable pipeline Worker plus Pages front door when Cloudflare deployment credentials are configured.

The repository does not claim that the external `page.dev` domain is live until a real deployment and endpoint verification succeeds.

## Free-first policy

The production pipeline is designed to remain $0 within the active free quotas of Cloudflare and Hugging Face. It must fail closed rather than silently switch to a paid provider. Paid providers may be added later only as an explicitly enabled policy path.

## Local debugging only

`uvicorn stockforge.web_app:app --host 127.0.0.1 --port 8000` and a temporary Cloudflare tunnel are debugging tools only. They are not production dependencies.
