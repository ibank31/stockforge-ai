import pytest

from stockforge.asset_selector import AssetSelectionError, list_asset_type_policies, select_asset_type


def test_all_asset_types_have_explicit_format_and_readiness() -> None:
    policies = list_asset_type_policies()

    assert {item.key for item in policies} == {
        "scene",
        "native_object",
        "technical_icon",
        "seamless_pattern",
        "transparent_cutout",
    }
    assert all(item.delivery_format for item in policies)
    assert all(item.readiness in {"READY_FOR_TRIAL", "REVIEW_REQUIRED", "BLOCKED"} for item in policies)


def test_scene_is_ready_for_a_controlled_trial_but_not_marketplace_acceptance() -> None:
    policy = select_asset_type("SCENE")

    assert policy.delivery_format == "jpeg"
    assert policy.execution_mode == "remote_raster_generation"
    assert policy.readiness == "READY_FOR_TRIAL"
    assert any("review" in item.casefold() for item in policy.blockers)


def test_transparent_cutout_stays_blocked() -> None:
    policy = select_asset_type("transparent_cutout")

    assert policy.delivery_format == "png"
    assert policy.readiness == "BLOCKED"
    assert any("alpha" in item.casefold() for item in policy.blockers)


def test_unknown_asset_type_fails_closed() -> None:
    with pytest.raises(AssetSelectionError, match="Unsupported asset type"):
        select_asset_type("anything_else")
