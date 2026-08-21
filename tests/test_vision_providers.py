from stockforge.vision_providers import UnavailableProvider


def test_unavailable_provider_never_returns_pass_signal():
    provider = UnavailableProvider("vision-test", "optional dependency missing")
    result = provider.inspect("missing.png")
    assert result.error
    assert result.signals == {}


def test_provider_contract_is_serializable():
    provider = UnavailableProvider("vision-test", "not installed")
    result = provider.inspect("image.webp")
    assert result.provider == "vision-test"
    assert result.raw is None
