# StockForge V2 Browser Workflow

StockForge V2 turns a user-supplied visual reference into a materially different asset candidate. The reference is visual intelligence, not a reproduction input. Final marketplace upload remains manual and human review remains mandatory.

## Workflow

1. Start the browser API with `stockforge-web`.
2. Start the queue worker with `stockforge-web-worker` in a second process.
3. Configure a real ComfyUI-compatible provider before starting the worker:

   ```bash
   export STOCKFORGE_COMFYUI_URL=http://127.0.0.1:8188
   stockforge-web-worker
   ```

   The worker refuses to start without this setting and never uses a fake provider.
4. Upload a JPG, PNG, or WebP reference.
5. Review the measurable profile and adjust the crop if necessary.
6. Enter a new commercial direction with at least three explicit creative changes.
7. Review the generated plan and queue the generation job.
8. Monitor the job in the browser. The worker carries the durable reference identity through execution and runs post-generation similarity verification.
9. If the result is `BLOCK`, use bounded regeneration. At most two regeneration attempts are accepted by default, and duplicate child jobs are rejected.
10. If the result is `REVIEW`, inspect the generated artifact in the browser.
11. Run technical QA. A `FAIL` result cannot be approved.
12. Use **Approve for package** only after human visual, rights, policy, distinctness, and metadata review.
13. Create and download the review-ready ZIP package.
14. Review the package contents and upload manually to the selected microstock marketplace.

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

The repository contains a ComfyUI HTTP adapter and a durable recovery-aware worker. A live generation run requires a reachable ComfyUI endpoint, a valid workflow in `GenerationRequest.parameters["comfyui_workflow"]`, and any required model/runtime configuration. Those external runtime prerequisites cannot be verified in a repository-only test run. The automated suite uses deterministic fake providers to validate queue, recovery, ingestion, similarity, QA, and packaging behavior without consuming GPU credits.

## Safety boundary

A successful job is not a marketplace approval. `REVIEW` is not `APPROVE`, and package creation is not marketplace submission. StockForge does not provide legal clearance or guarantee acceptance, sales, or freedom from third-party claims.
