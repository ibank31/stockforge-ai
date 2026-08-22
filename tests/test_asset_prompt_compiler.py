from stockforge.asset_prompt_compiler import compile_asset_prompt
from stockforge.asset_spec import standalone_asset_spec


def test_compiler_preserves_standalone_constraints():
    spec = standalone_asset_spec(
        asset_id="asset-001",
        market_opportunity_id="opportunity-ephemera",
        buyer_segment="designers",
        buyer_job="scrapbook composition",
        channel="digital design",
        asset_family="ephemera",
        asset_type="ephemera",
        micro_niche="vintage botanical postal ephemera",
        subject="single fictional botanical postage stamp",
        visual_language="tactile antique printmaking",
        medium="aged paper and engraved ink",
        palette=("warm ivory", "muted burgundy", "dusty blue"),
        originality_levers=("fictional botanical specimen", "irregular analog printing"),
        commercial_use_cases=("scrapbook", "stationery", "editorial collage"),
    )

    package = compile_asset_prompt(spec)
    assert "single standalone asset" in package.prompt
    assert "solid clean white background" in package.prompt
    assert "no readable text or typography" in package.prompt
    assert "fictional botanical specimen" in package.prompt
    assert "logos" in package.negative_prompt
