# StockForge V2 Browser Workflow

StockForge V2 turns a user-supplied visual reference into a materially different asset candidate. The reference is visual intelligence, not a reproduction input. Final marketplace upload remains manual and human review remains mandatory.

## Workflow

1. Start the browser API with `stockforge-web`.
2. Start the queue worker with `stockforge-web-worker` in a second process.
3. The production worker defaults to the public Hugging Face ZeroGPU Space `ibank31/stockforge-zerogpu` through the `generate_remote` Gradio queue endpoint. No local GPU or local ComfyUI endpoint is required.
4. Upload a JPG, PNG, or WebP reference.
5. Review the measurable profile and adjust the crop if necessary.
6. Enter a new commercial direction with at least three explicit creative changes.
7. Review the generated plan and queue the generation job.
8. Monitor the job in the browser. The worker carries the durable reference identity through remote ZeroGPU execution and runs post-generation similarity verification.
9. If the result is `BLOCK`, use bounded regeneration. At most two regeneration attempts are accepted by default, and duplicate child jobs are rejected.
10. If the result is `REVIEW`, inspect the generated artifact in the browser.
11. Run technical QA. A `FAIL` result cannot be approved.
12. Use **Approve for package** only after human visual, rights, policy, distinctness, and metadata review.
13. Create and download the review-ready ZIP package.
14. Review the package contents and upload manually to the selected microstock marketplace.

## Provider configuration

The browser worker uses this provider policy:

- `STOCKFORGE_PROVIDER_MODE=zerogpu` by default.
- `STOCKFORGE_ZEROGPU_SPACE` defaults to `ibank31/stockforge-zerogpu`.
- `STOCKFORGE_ZEROGPU_URL` defaults to `https://ibank31-stockforge-zerogpu.hf.space`.
- `STOCKFORGE_ZEROGPU_API` defaults to `generate_remote`.
- `STOCKFORGE_HF_TOKEN` is optional. When supplied, the worker authenticates its Hugging Face request; without it, the public Space can still be called subject to Hugging Face's unauthenticated/shared quota rules.
- `STOCKFORGE_PROVIDER_MODE=comfyui` is retained only as an explicit compatibility path and requires `STOCKFORGE_COMFYUI_URL`.

The worker never silently falls back to a fake provider and never treats queue submission as generation success. A successful production job requires a real remote output that can be downloaded and ingested.

## Browser API stages

| Stage | Endpoint | Purpose |
| --- | --- | --- |
| Reference | `POST /api/references` | Upload and profile a reference |
| Crop | `POST /api/references/{id}/crop` | Confirm a manual crop |
| Plan | `POST /api/references/{id}/plan` | Build creative opportunity and anti-similarity plan |
| Generate | `POST /api/references/{id}/generate` | Create a durable V2 queue job |
| Status | `GET /api/jobs/{id}` | Read queue, execution, artifact, and gate state |
| Regenerate | `POST /api/jobs/{id}/regenerate` | Queue a bounded retry after `BLOCK` |
| Artifact | `GET /api/artifacts/{id}` | Preview/download a registered generated artifact |
| QA | `POST /api/jobs/{id}/qa` | Run deterministic technical checks |
| Approval | `POST /api/jobs/{id}/approve` | Record human approval for package preparation only |
| Package | `POST /api/jobs/{id}/release` | Build the review-ready ZIP |
| Download | `GET /api/jobs/{id}/download` | Download the package for manual review/upload |

## Provider boundary

The repository contains a ComfyUI HTTP adapter and a remote Gradio provider adapter. The live browser path now uses the existing Hugging Face ZeroGPU Space and its stable `generate_remote` endpoint. The ZeroGPU Space uses the StockForge FP8-aware Z-Image runtime and the `ibank31/stockforge-models` model repository. Kaggle remains a separate compute/finalizer layer and is not required for the first V2 generation proof. A live E2E run still requires the remote Space to be reachable and its model/runtime configuration to be healthy.

## Safety boundary

A successful job is not a marketplace approval. `REVIEW` is not `APPROVE`, and package creation is not marketplace submission. StockForge does not provide legal clearance or guarantee acceptance, sales, or freedom from third-party claims.
