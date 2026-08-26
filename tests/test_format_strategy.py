import pytest

from stockforge.format_strategy import FormatStrategyError, recommend_format, validate_format_decision
from stockforge.portfolio import build_brief


def test_self_contained_food_composition_routes_to_jpeg() -> None:
    decision = recommend_format(
        asset_type="illustration",
        buyer_job="recognizable Thai soup bowl for recipe editorial and menu concepts",
    )

    assert decision.delivery_format == "jpeg"
    assert decision.product_kind == "raster_illustration"
    assert decision.strategy_key == "self_contained_raster"
    assert decision.requires_true_alpha is False


def test_drop_in_food_element_routes_to_true_alpha_png() -> None:
    decision = recommend_format(
        asset_type="illustration",
        buyer_job="drop-in food element for recipe cards and layered menu layouts",
        compositing_required=True,
    )

    assert decision.delivery_format == "png"
    assert decision.product_kind == "transparent_cutout"
    assert decision.strategy_key == "transparent_utility_cutout"
    assert decision.requires_true_alpha is True


def test_editable_icon_job_routes_to_svg_without_remote_gpu() -> None:
    decision = recommend_format(
        asset_type="icon_set",
        buyer_job="editable workflow icons for a web interface",
    )

    assert decision.delivery_format == "svg"
    assert decision.product_kind == "native_vector"
    assert decision.requires_remote_gpu is False


def test_png_decision_rejects_white_background_contract() -> None:
    decision = recommend_format(
        asset_type="illustration",
        buyer_job="transparent isolated food overlay",
        compositing_required=True,
    )

    with pytest.raises(FormatStrategyError, match="transparent background"):
        validate_format_decision(
            decision,
            delivery_format="png",
            product_kind="transparent_cutout",
            background_policy="white",
            isolation_policy="isolated",
        )


def test_portfolio_brief_persists_explicit_format_decision_for_jpeg() -> None:
    brief = build_brief("traditional_food_tomyum_kung", "tomyum-kung").to_dict()

    assert brief["asset_spec"]["delivery_format"] == "jpeg"
    assert brief["format_decision"]["delivery_format"] == "jpeg"
    assert brief["format_decision"]["strategy_key"] == "self_contained_raster"


def test_portfolio_brief_persists_explicit_format_decision_for_png() -> None:
    brief = build_brief(
        "traditional_food_mango_sticky_rice_png",
        "mango-sticky-rice-cutout",
    ).to_dict()

    assert brief["asset_spec"]["delivery_format"] == "png"
    assert brief["asset_spec"]["product_kind"] == "transparent_cutout"
    assert brief["format_decision"]["delivery_format"] == "png"
    assert brief["format_decision"]["strategy_key"] == "transparent_utility_cutout"
    assert brief["format_decision"]["requires_true_alpha"] is True
