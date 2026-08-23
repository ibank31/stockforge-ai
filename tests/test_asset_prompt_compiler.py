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


def test_compiler_returns_canonical_prompt_package_with_commercial_fields():
    from stockforge.prompt_compiler import PromptPackage

    spec = standalone_asset_spec(
        asset_id="asset-002",
        market_opportunity_id="opportunity-ephemera",
        buyer_segment="editorial designers",
        buyer_job="journal and stationery composition",
        channel="digital design",
        asset_family="ephemera",
        asset_type="ephemera",
        micro_niche="vintage botanical postal ephemera",
        subject="single fictional vintage botanical postage stamp",
        visual_language="tactile early-20th-century-inspired analog print ephemera",
        medium="aged paper and engraved botanical print",
        originality_levers=("fictional botanical specimen", "irregular analog printing"),
        commercial_use_cases=("scrapbook", "journal", "stationery", "editorial design"),
    )

    package = compile_asset_prompt(spec)

    assert isinstance(package, PromptPackage)
    assert "journal and stationery composition" in package.prompt
    assert "single fictional vintage botanical postage stamp" in package.prompt
    assert "tactile early-20th-century-inspired analog print ephemera" in package.prompt
    assert "aged paper and engraved botanical print" in package.prompt
    assert "single standalone object" in package.prompt
    assert "scrapbook, journal, stationery, editorial design" in package.prompt
    assert "fictional botanical specimen" in package.prompt
    assert package.legal_constraints
    assert "journal" in package.metadata_hints
