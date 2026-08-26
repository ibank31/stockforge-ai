from stockforge.asset_prompt_compiler import compile_asset_prompt
from stockforge.asset_spec import AssetSpec, standalone_asset_spec
from stockforge.portfolio import build_brief, list_lanes


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


def test_each_jpeg_lane_has_unique_identity_in_prompt_and_negative_prompt():
    jpeg_lanes = [lane for lane in list_lanes() if lane.concepts[0].delivery_format == "jpeg"]
    signatures = []

    for lane in jpeg_lanes:
        brief = build_brief(lane.key, lane.concepts[0].key)
        spec = brief.asset_spec
        signatures.append(spec.identity_signature)
        assert spec.identity_signature
        assert spec.identity_lighting
        assert spec.identity_framing
        assert spec.identity_context
        assert spec.identity_distinctness
        assert spec.identity_prohibited_shorthand
        assert spec.identity_signature in brief.prompt_package.prompt
        assert "niche-specific shorthand:" in brief.prompt_package.negative_prompt

    assert len(jpeg_lanes) == 17
    assert len(set(signatures)) == len(signatures)


def test_svg_briefs_do_not_receive_jpeg_identity_profile():
    brief = build_brief("native_vector_elements", "folder-upload")

    assert brief.asset_spec.identity_signature == ""
    assert "Niche identity signature:" not in brief.prompt_package.prompt


def test_compiler_preserves_standalone_constraints():
    package = compile_asset_prompt(_spec())

    assert "single standalone asset" in package.prompt
    assert "solid clean white background" in package.prompt
    assert "no readable text or typography" in package.prompt
    assert "single clear silhouette" in package.prompt
    assert "meters" in package.negative_prompt
    assert "hands" in package.negative_prompt
    assert "stamps" in package.negative_prompt


def test_scene_jpeg_policy_allows_human_story_subjects_but_keeps_safety_guards():
    spec = AssetSpec(
        asset_id="asset-scene-001",
        market_opportunity_id="opportunity-authentic-remote-work",
        buyer_segment="web_product_teams",
        buyer_job="authentic remote-work and collaboration communication",
        channel="web and presentation",
        asset_family="ui_3d_metaphor",
        asset_type="3d",
        micro_niche="authentic remote work collaboration",
        subject="two diverse coworkers collaborating at home around a shared table",
        visual_language="natural documentary commercial photography",
        medium="soft daylight, realistic skin and fabric texture",
        product_kind="raster_illustration",
        delivery_format="jpeg",
        layout_mode="hero_landscape",
        palette=("natural daylight", "warm neutral", "soft blue"),
        composition="candid collaborative moment with clear focal interaction",
        negative_space="clean copy space on the left for a headline",
        background_policy="scene",
        isolation_policy="scene",
        text_policy="none",
        branding_policy="no_branding",
        originality_levers=("authentic gesture", "regional realism", "clear copy space"),
        variation_policy="retain only commercially distinct variants",
        commercial_use_cases=("website hero", "remote work article", "team collaboration campaign"),
        quality_gates=("thumbnail readability", "natural anatomy", "no accidental text or branding"),
    )

    package = compile_asset_prompt(spec)

    assert "two diverse coworkers collaborating" in package.prompt
    assert "deformed anatomy" in package.negative_prompt
    assert "extra fingers" in package.negative_prompt
    assert "readable text" in package.negative_prompt
    assert "hands, fingers, faces, bodies, tools, measuring devices" not in package.negative_prompt


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
