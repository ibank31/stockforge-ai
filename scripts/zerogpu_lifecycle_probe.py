#!/usr/bin/env python3
"""Probe one live Gradio remote generation lifecycle without exposing credentials."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = os.environ.get("STOCKFORGE_HF_SPACE_URL", "https://ibank31-stockforge-zerogpu.hf.space").rstrip("/")
API_NAME = os.environ.get("STOCKFORGE_API_NAME", "generate_remote").strip("/")
JOB_ID = os.environ.get("STOCKFORGE_PROBE_JOB_ID", f"diagnostic-{int(time.time())}")
OUT = Path(os.environ.get("STOCKFORGE_PROBE_OUTPUT", "zerogpu-lifecycle.json"))
TIMEOUT = float(os.environ.get("STOCKFORGE_PROBE_TIMEOUT", "180"))


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def request(method: str, url: str, body: bytes | None = None):
    headers = {"cache-control": "no-cache"}
    if body is not None:
        headers["content-type"] = "application/json"
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if token:
        headers["authorization"] = f"Bearer {token}"
    return urllib.request.urlopen(
        urllib.request.Request(url, data=body, headers=headers, method=method),
        timeout=30,
    )


def parse_sse(text: str):
    events = []
    current_event = "message"
    data = []
    for line in text.splitlines():
        if line.startswith("event:"):
            if data:
                events.append({"event": current_event, "data": "\n".join(data)})
            current_event = line[6:].strip()
            data = []
        elif line.startswith("data:"):
            data.append(line[5:].lstrip())
    if data:
        events.append({"event": current_event, "data": "\n".join(data)})
    return events


def safe_data(raw: str, terminal: bool = False):
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_preview": raw[:1000]}
    if terminal and isinstance(value, dict):
        safe = {}
        for key in ("error", "title", "duration", "visible"):
            if key in value:
                item = value[key]
                safe[key] = item[:2000] if isinstance(item, str) else item
        return safe
    if isinstance(value, list):
        return {"kind": "list", "length": len(value), "types": [type(x).__name__ for x in value]}
    if isinstance(value, dict):
        return {"kind": "object", "keys": sorted(str(k) for k in value)[:50]}
    return {"kind": type(value).__name__}


def write_result(result, code):
    result["finished_at"] = stamp()
    result["poll_count"] = len(result.get("poll", []))
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = {k: result[k] for k in ("started_at", "finished_at", "api_name", "submit", "poll_count", "terminal_event", "error") if k in result}
    print(json.dumps(summary, indent=2))
    print(f"diagnostic artifact: {OUT}")
    return code


def main() -> int:
    result = {"started_at": stamp(), "base": BASE, "api_name": API_NAME, "job_id": JOB_ID, "submit": {}, "poll": []}
    payload = {"data": [
        "premium commercial stock asset photograph of one original ceramic travel mug, clean studio lighting, no brand, no logo, no text, no watermark",
        1328, 1328, 4, 123456, False, JOB_ID,
    ]}
    try:
        started = time.monotonic()
        with request("POST", f"{BASE}/gradio_api/call/{API_NAME}", json.dumps(payload).encode()) as response:
            body = response.read().decode("utf-8", "replace")
            result["submit"] = {"http_status": response.status, "elapsed_seconds": round(time.monotonic() - started, 3)}
            parsed = json.loads(body)
            event_id = parsed.get("event_id")
            result["submit"]["has_event_id"] = bool(event_id)
            if not event_id:
                result["submit"]["response"] = {"keys": sorted(parsed) if isinstance(parsed, dict) else type(parsed).__name__}
                raise RuntimeError("submit returned no event_id")
    except urllib.error.HTTPError as exc:
        result["submit"] = {"http_status": exc.code}
        result["error"] = {"type": "http_submit", "message": f"HTTP {exc.code}"}
        return write_result(result, 1)
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)[:1000]}
        return write_result(result, 1)

    deadline = time.monotonic() + TIMEOUT
    poll_url = f"{BASE}/gradio_api/call/{API_NAME}/{event_id}"
    while time.monotonic() < deadline:
        try:
            with request("GET", poll_url) as response:
                body = response.read().decode("utf-8", "replace")
                events = parse_sse(body)
                names = [item["event"] for item in events]
                terminal_names = {"complete", "error", "exception"}
                result["poll"].append({
                    "at": stamp(), "http_status": response.status, "event_names": names,
                    "events": [{"event": item["event"], "data": safe_data(item["data"], item["event"] in terminal_names)} for item in events],
                })
                terminal = next((name for name in names if name in terminal_names), None)
                if terminal:
                    result["terminal_event"] = terminal
                    if terminal != "complete":
                        result["error"] = {"type": "remote_terminal", "event": terminal, "details": result["poll"][-1]["events"][-1]["data"]}
                    return write_result(result, 0 if terminal == "complete" else 1)
        except urllib.error.HTTPError as exc:
            result["poll"].append({"at": stamp(), "http_status": exc.code, "error": "http_poll"})
        except Exception as exc:
            result["poll"].append({"at": stamp(), "error": type(exc).__name__, "message": str(exc)[:500]})
        time.sleep(2)
    result["error"] = {"type": "timeout", "message": f"No terminal SSE event within {TIMEOUT:g}s"}
    return write_result(result, 1)


if __name__ == "__main__":
    raise SystemExit(main())
