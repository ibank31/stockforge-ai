import pytest

from stockforge import web_worker


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("STOCKFORGE_WEB_UPLOAD_ROOT", str(tmp_path / "references"))
    monkeypatch.setenv("STOCKFORGE_WEB_DATABASE", str(tmp_path / "jobs.sqlite"))
    monkeypatch.setenv("STOCKFORGE_PROVIDER_ROOT", str(tmp_path / "provider"))


def test_web_worker_defaults_to_real_zerogpu_provider(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.delenv("STOCKFORGE_PROVIDER_MODE", raising=False)
    monkeypatch.delenv("STOCKFORGE_HF_TOKEN", raising=False)

    worker = web_worker.build_worker()
    assert worker is not None

    provider = web_worker._build_provider()
    assert provider.descriptor.id == "hf.zerogpu"
    assert provider.base_url == "https://ibank31-stockforge-zerogpu.hf.space"
    assert provider.api_name == "generate_remote"


def test_web_worker_allows_explicit_comfyui_compatibility_mode(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("STOCKFORGE_PROVIDER_MODE", "comfyui")
    monkeypatch.setenv("STOCKFORGE_COMFYUI_URL", "http://127.0.0.1:8188")

    provider = web_worker._build_provider()
    assert provider.descriptor.id == "comfyui.browser"


def test_web_worker_rejects_unknown_provider_mode(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("STOCKFORGE_PROVIDER_MODE", "unknown")
    with pytest.raises(RuntimeError, match="Unsupported STOCKFORGE_PROVIDER_MODE"):
        web_worker.build_worker()


def test_web_worker_requires_comfyui_only_when_explicitly_selected(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("STOCKFORGE_PROVIDER_MODE", "comfyui")
    monkeypatch.delenv("STOCKFORGE_COMFYUI_URL", raising=False)
    with pytest.raises(RuntimeError, match="STOCKFORGE_COMFYUI_URL"):
        web_worker.build_worker()
