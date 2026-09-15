import pytest

from stockforge import web_worker


def test_web_worker_requires_explicit_real_provider(monkeypatch):
    monkeypatch.delenv("STOCKFORGE_COMFYUI_URL", raising=False)
    with pytest.raises(RuntimeError, match="STOCKFORGE_COMFYUI_URL"):
        web_worker.build_worker()
