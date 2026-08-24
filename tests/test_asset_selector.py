import pytest

from stockforge.asset_selector import AssetSelectionError, list_asset_type_policies, select_asset_type


def test_all_asset_types_have_explicit_format_and_readiness() -> None:
    policies = list_asset_type_policies()

    assert {item.key for item in policies} == {
        "scene",
        "icon_set",
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


def test_icon_set_recommendation_resolves_to_clustered_svg_brief() -> None:
    from stockforge.portfolio import build_brief, lane_for

    policy = select_asset_type("icon_set")
    lane = lane_for(policy.recommended_lane_keys[0])
    brief = build_brief(lane.key, policy.recommended_concept_keys[0])

    assert brief.concept.key == "file-flow-micro-set"
    assert brief.asset_spec.asset_type == "icon_set"
    assert brief.asset_spec.product_kind == "native_vector"
    assert brief.asset_spec.delivery_format == "svg"
    assert brief.asset_spec.isolation_policy == "cluster"
    assert "file-management" in brief.asset_spec.buyer_job
    assert brief.metadata.human_review_required is True


def test_native_object_recommendation_resolves_to_valid_svg_briefs() -> None:
    from stockforge.portfolio import build_brief, lane_for

    policy = select_asset_type("native_object")
    lane = lane_for(policy.recommended_lane_keys[0])
    brief = build_brief(lane.key, policy.recommended_concept_keys[0])

    assert brief.concept.key == "folder-upload"
    assert brief.asset_spec.product_kind == "native_vector"
    assert brief.asset_spec.delivery_format == "svg"
    assert "file management" in brief.asset_spec.buyer_job
    assert brief.metadata.human_review_required is True


def test_plan_type_cli_builds_no_generation_svg_brief() -> None:
    import json
    from typer.testing import CliRunner
    from stockforge.cli import app

    result = CliRunner().invoke(app, ["portfolio", "plan-type", "--asset-type", "native_object"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "planned_no_generation"
    assert payload["format_route"]["delivery_format"] == "svg"
    assert payload["brief"]["asset_spec"]["product_kind"] == "native_vector"
    assert "No provider or GPU was called" in payload["notice"]


def test_trial_readiness_allows_only_explicit_single_candidate_scene() -> None:
    from stockforge.trial_gate import assess_trial_readiness

    readiness = assess_trial_readiness(
        asset_type="scene",
        hypothesis="A tactile surreal scene may serve a commercial web hero buyer job.",
        purpose="Validate one JPEG preview against the selected buyer job and visual quality gates.",
    )

    assert readiness.readiness == "READY_FOR_TRIAL"
    assert readiness.trial_allowed is True
    assert readiness.provider_call_allowed is True
    assert readiness.single_candidate_only is True


def test_trial_readiness_keeps_png_blocked() -> None:
    from stockforge.trial_gate import assess_trial_readiness

    readiness = assess_trial_readiness(
        asset_type="transparent_cutout",
        hypothesis="A true-alpha isolated object could serve an overlay buyer job.",
        purpose="Validate the alpha pipeline only after its technical gates exist.",
    )

    assert readiness.readiness == "BLOCKED"
    assert readiness.trial_allowed is False
    assert readiness.provider_call_allowed is False
    assert any("alpha" in item.casefold() for item in readiness.blockers)


def test_trial_readiness_allows_local_svg_but_not_provider_call() -> None:
    from stockforge.trial_gate import assess_trial_readiness

    readiness = assess_trial_readiness(
        asset_type="seamless_pattern",
        hypothesis="A repeatable geometric tile may serve a decorative background buyer job.",
        purpose="Validate SVG repeatability and human visual utility before portal review.",
    )

    assert readiness.readiness == "READY_FOR_TRIAL"
    assert readiness.trial_allowed is True
    assert readiness.provider_call_allowed is False
    assert readiness.single_candidate_only is True
