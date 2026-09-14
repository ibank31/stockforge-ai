# StockForge V2 + Cloudflare Tunnel

The browser never connects directly to SQLite, GPU providers, or the filesystem.

```
Browser → Cloudflare HTTPS → cloudflared → 127.0.0.1:8000 → StockForge
```

## 1. Install web dependencies

```bash
pip install -e '.[web]'
```

## 2. Start StockForge locally

```bash
uvicorn stockforge.web_app:app --host 127.0.0.1 --port 8000
```

Check:

```bash
curl http://127.0.0.1:8000/health
```

## 3. Temporary Cloudflare URL

Install `cloudflared` using the package method appropriate for the host, then run:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare prints an HTTPS URL. Open it in the browser.

## Production rule

Do not expose the database, artifact directory, or provider endpoints directly. Only the StockForge web API is tunneled.
