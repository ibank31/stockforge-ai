import pytest

from stockforge.provider import ProviderConfig, ProviderConfigError, SecretRef


def test_secret_ref_does_not_store_secret():
    ref = SecretRef("COMFYUI_API_KEY")
    assert ref.to_dict() == {"env": "COMFYUI_API_KEY"}
    assert "secret" not in ref.to_dict()


def test_secret_ref_resolves_explicit_environment():
    ref = SecretRef("TEST_PROVIDER_KEY")
    assert ref.resolve({"TEST_PROVIDER_KEY": "secret-value"}) == "secret-value"


def test_missing_secret_is_rejected():
    ref = SecretRef("TEST_PROVIDER_KEY")
    with pytest.raises(ProviderConfigError, match="not set"):
        ref.resolve({})


def test_provider_round_trip():
    config = ProviderConfig(
        id="comfyui.local",
        kind="image-generator",
        endpoint="http://127.0.0.1:8188",
        secret_ref=SecretRef("COMFYUI_API_KEY"),
        options={"timeout_seconds": 120, "default_workflow": "stock-photo-v1"},
    )
    restored = ProviderConfig.from_dict(config.to_dict())
    assert restored == config


def test_provider_rejects_inline_secret_field():
    data = ProviderConfig(id="local", kind="image-generator").to_dict()
    data["api_key"] = "should-never-be-here"
    with pytest.raises(ProviderConfigError, match="unexpected: api_key"):
        ProviderConfig.from_dict(data)


def test_provider_id_validation():
    with pytest.raises(ProviderConfigError, match="Provider id"):
        ProviderConfig(id="bad id", kind="image-generator")


def test_provider_schema_validation():
    data = ProviderConfig(id="local", kind="image-generator").to_dict()
    data["schema_version"] = 999
    with pytest.raises(ProviderConfigError, match="Unsupported provider config schema"):
        ProviderConfig.from_dict(data)
