"""Run the StockForge V2 browser service without exposing internals directly."""

from __future__ import annotations

import os
import threading
import time

def _embedded_worker() -> None:
    from .web_worker import run_once
    interval = max(0.5, float(os.getenv("STOCKFORGE_WORKER_INTERVAL", "2")))
    while True:
        try:
            result = run_once()
            if result is None: time.sleep(interval)
        except Exception: time.sleep(max(interval, 5.0))

def main() -> None:
    import uvicorn
    if os.getenv("STOCKFORGE_EMBEDDED_WORKER", "1").strip().lower() not in {"0", "false", "no"}:
        threading.Thread(target=_embedded_worker, name="stockforge-embedded-worker", daemon=True).start()
    uvicorn.run("stockforge.web_app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
