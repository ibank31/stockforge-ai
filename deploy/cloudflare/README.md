# StockForge V2 browser entrypoint

The browser must communicate only with the StockForge control-plane API. It must never access SQLite, runtime files, GPU workers, or credentials directly.

## Production boundary

```text
page.dev / browser
        ↓
HTTPS deployment / reverse proxy
        ↓
StockForge V2 control plane
        ↓
Durable job queue
        ↓
Remote provider worker
```

The historical `cloudflared tunnel --url http://127.0.0.1:8000` command is a development/debug technique only. It is **not** the canonical production architecture because it makes the user's local machine the availability boundary.

## Control-plane deployment requirements

The deployed control plane must:

1. serve `stockforge.web_app:app`;
2. provide persistent writable storage for the SQLite job database, reference files, and provider state;
3. have network access to the configured remote provider;
4. keep provider credentials in deployment secrets, never in source code;
5. expose only the web API to the browser.

The repository does not hard-code the user's `page.dev` hostname. The external Cloudflare Pages/domain configuration is deployment state and must be verified there before calling the browser deployment production-live.

## Local debugging only

For local debugging, `uvicorn stockforge.web_app:app --host 127.0.0.1 --port 8000` is valid. A temporary Cloudflare quick tunnel may then be used for testing. This must not be used as the permanent production executor or job-control dependency.
