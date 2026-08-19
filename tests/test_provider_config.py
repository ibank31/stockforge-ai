from pathlib import Path

import pytest

from stockforge.provider_config import ProviderConfig, ProviderConfigError, ProviderConfigStore


def test_provider_config_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "providers.json"
    config = ProviderConfig(
        provider_id="comfyui",
        endpoint="http://127.0.0.1:8188",
        timeout_seconds=90,
        capabilities=("image.generate", "generation.async"),
        secret_env="COMFYUI_API_KEY",
        metadata={"workflow": "stock-image"},
    )
    store = ProviderConfigStore(path)
    store.save_all([config])

    loaded = store.load_all()
    assert loaded == [config]
    assert loaded[0].resolve_secret({"COMFYUI_API_KEY": "secret-value"}) == "secret-value"
    assert "secret-value" not in path.read_text(encoding="utf-8")


def test_provider_config_rejects_unknown_schema() -> None:
    with pytest.raises(ProviderConfigError):
        ProviderConfig.from_dict({
            "schema_version": 999,
            "provider_id": "comfyui",
            "endpoint": None,
            "enabled": True,
            "timeout_seconds": 120,
            "capabilities": [],
            "secret_env": None,
            "metadata": {},
        })


def test_provider_config_rejects_invalid_timeout() -> None:
    with pytest.raises(ProviderConfigError):
        ProviderConfig(provider_id="comfyui", timeout_seconds=0)


def test_provider_config_requires_exact_serialized_schema() -> None:
    data = ProviderConfig(provider_id="comfyui").to_dict()
    data["unexpected"] = True
    with pytest.raises(ProviderConfigError):
        ProviderConfig.from_dict(data)
