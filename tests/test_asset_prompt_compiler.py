from stockforge.asset_prompt_compiler import compile_asset_prompt
from stockforge.asset_spec import standalone_asset_spec


def _spec():
    return standalone_asset_spec(
        asset_id="asset-001",
        market_opportunity_id="opportunity-material-atmosphere",
        buyer_segment="web_product_teams",
        buyer_job="landing page hero and product explainer",
        channel="web and presentation",
        asset_family="material_atmosphere",
        asset_type="texture",
        micro_niche="tactile translucent resin material study",
        subject="single translucent resin pebble with soft internal color gradient",
        visual_language="clean contemporary studio art direction",
        medium="frosted translucent resin with subtle microtexture",
        palette=("warm ivory", "muted sage", "soft coral"),
        originality_levers=("restrained tactile material", "single clear silhouette"),
        commercial_use_cases=("website hero", "product explainer", "presentation"),
    )


def test_compiler_preserves_standalone_constraints():
    package = compile_asset_prompt(_spec())

    assert "single standalone asset" in package.prompt
    assert "solid clean white background" in package.prompt
    assert "no readable text or typography" in package.prompt
    assert "single clear silhouette" in package.prompt
    assert "meters" in package.negative_prompt
    assert "hands" in package.negative_prompt
    assert "stamps" in package.negative_prompt


def test_compiler_returns_canonical_prompt_package_with_commercial_fields():
    from stockforge.prompt_compiler import PromptPackage

    package = compile_asset_prompt(_spec())

    assert isinstance(package, PromptPackage)
    assert "landing page hero and product explainer" not in package.prompt
    assert "website hero, product explainer, presentation" not in package.prompt
    assert "single translucent resin pebble" in package.prompt
    assert "frosted translucent resin" in package.prompt
    assert "Material behavior" in package.prompt
    assert "Composition contract" in package.prompt
    assert "single standalone object" in package.prompt
    assert "restrained tactile material" in package.prompt
    assert package.legal_constraints
    assert "product explainer" in package.metadata_hints
