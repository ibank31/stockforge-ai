# StockForge V2 browser entrypoint

The browser must communicate only with the StockForge control-plane API. It must never access SQLite, runtime files, GPU workers, or credentials directly.

## Production boundary

```text
Cloudflare Pages / browser
        ↓
Pages Function /api/* proxy
        ↓
StockForge V2 CPU control plane
        ↓
Durable job queue + worker
        ↓
Remote provider worker
        ↓
Hugging Face ZeroGPU
```

The production-ready front door is implemented under `frontend/`. The Pages Function at `frontend/functions/api/[[path]].js` forwards browser `/api/*` requests to the configured control plane and maps `/api/health` to the control plane's `/health` endpoint.

The historical `cloudflared tunnel --url http://127.0.0.1:8000` command is a development/debug technique only. It is **not** the canonical production architecture because it makes the user's local machine the availability boundary.

## Control-plane deployment requirements

The deployed control plane must:

1. serve the StockForge V2 web API;
2. run the durable queue worker loop or connect to an equivalent always-on worker;
3. provide persistent writable storage for the SQLite job database, reference files, and provider state when deployed on infrastructure intended for production persistence;
4. have network access to the configured remote provider;
5. keep provider credentials in deployment secrets, never in source code;
6. expose only the web API to the browser.

The repository provides a Hugging Face Docker control-plane definition under `deploy/control-plane/` and a GitHub Actions deployment workflow. The deployment workflow targets `ibank31/stockforge-control-plane` when an HF token secret is configured.

The Cloudflare Pages Function accepts the environment variable `STOCKFORGE_CONTROL_PLANE_URL`; otherwise it uses the canonical control-plane hostname encoded as its safe default. Cloudflare Pages deployment is also automated through GitHub Actions when the required Cloudflare account/token secrets are configured.

The repository does not hard-code the user's `page.dev` hostname as a claim of liveness. The external Pages project/domain is considered production-live only after a successful deployment and endpoint verification.

## Local debugging only

For local debugging, `uvicorn stockforge.web_app:app --host 127.0.0.1 --port 8000` is valid. A temporary Cloudflare quick tunnel may then be used for testing. This must not be used as the permanent production executor or job-control dependency.
