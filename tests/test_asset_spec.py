from __future__ import annotations

import pytest

from stockforge.asset_spec import AssetSpecError, standalone_asset_spec


def _spec(**overrides):
    values = {
        "asset_id": "asset-001",
        "market_opportunity_id": "opportunity-ephemera",
        "buyer_segment": "designers",
        "buyer_job": "scrapbook and editorial composition",
        "channel": "digital design",
        "asset_family": "ephemera",
        "asset_type": "ephemera",
        "micro_niche": "vintage botanical postal ephemera",
        "subject": "single fictional botanical postage stamp",
        "visual_language": "tactile antique printmaking",
        "medium": "aged paper and engraved ink",
        "originality_levers": ("fictional botanical specimen", "irregular analog printing"),
    }
    values.update(overrides)
    return standalone_asset_spec(**values)


def test_standalone_policy_is_explicit():
    spec = _spec()
    assert spec.isolation_policy == "isolated"
    assert spec.background_policy == "white"
    assert spec.text_policy == "none"
    assert "thumbnail readability" in spec.quality_gates


def test_spec_is_serializable():
    payload = _spec().to_dict()
    assert payload["asset_family"] == "ephemera"
    assert payload["originality_levers"]


def test_missing_originality_lever_is_rejected():
    with pytest.raises(AssetSpecError):
        _spec(originality_levers=())


def test_isolated_scene_conflict_is_rejected():
    with pytest.raises(AssetSpecError):
        _spec(background_policy="scene")


def test_unsupported_asset_family_is_rejected():
    with pytest.raises(AssetSpecError, match="Unsupported asset family"):
        _spec(asset_family="unsupported")


def test_unsupported_asset_type_is_rejected():
    with pytest.raises(AssetSpecError, match="Unsupported asset type"):
        _spec(asset_type="unsupported")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("background_policy", "scene"),
        ("isolation_policy", "scene"),
        ("text_policy", "controlled"),
        ("branding_policy", "fictional_brand"),
    ),
)
def test_standalone_policy_conflicts_are_rejected(field, value):
    with pytest.raises(AssetSpecError):
        _spec(**{field: value})


def test_provider_specific_model_name_is_rejected():
    with pytest.raises(AssetSpecError, match="provider-neutral capability expressions"):
        _spec(model_preferences=("z-image",))


def test_capability_preferences_are_provider_neutral():
    spec = _spec(model_preferences=("realism=high", "isolation=required", "resolution>=1024"))
    assert spec.model_preferences == ("realism=high", "isolation=required", "resolution>=1024")
