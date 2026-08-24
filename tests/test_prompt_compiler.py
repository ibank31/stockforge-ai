from stockforge.concept_engine import ConceptVariant
from stockforge.prompt_compiler import compile_prompt


def make_concept() -> ConceptVariant:
    return ConceptVariant(
        concept_id="web-product-material-hero-1",
        angle="hero",
        visual_problem="provide a compositable tactile material metaphor",
        subject="single translucent resin pebble with soft internal color gradient",
        action="communicate product value through one clear non-text visual metaphor",
        environment="clean white studio background with no people, hands, devices, screens, or props",
        composition="single centered object, clean copy space right",
        copy_space="right",
        uniqueness_levers=("single_visual_metaphor", "material_specificity"),
        buyer_job="landing_page",
        channel="web",
    )


def test_compiler_contains_concept_and_buyer_job():
    package = compile_prompt(make_concept())
    assert "translucent resin pebble" in package.prompt
    assert "landing_page" in package.prompt
    assert "single_visual_metaphor" in package.prompt


def test_compiler_adds_ip_and_quality_constraints():
    package = compile_prompt(make_concept())
    assert "trademarks" in package.negative_prompt
    assert any("hands" in item for item in package.quality_constraints)
    assert any("brands" in item for item in package.legal_constraints)


def test_compiler_rejects_missing_uniqueness():
    concept = make_concept()
    bad = ConceptVariant(
        concept_id=concept.concept_id,
        angle=concept.angle,
        visual_problem=concept.visual_problem,
        subject=concept.subject,
        action=concept.action,
        environment=concept.environment,
        composition=concept.composition,
        copy_space=concept.copy_space,
        uniqueness_levers=(),
        buyer_job=concept.buyer_job,
        channel=concept.channel,
    )
    try:
        compile_prompt(bad)
    except ValueError as exc:
        assert "uniqueness" in str(exc).lower()
    else:
        raise AssertionError("Expected compiler to reject missing uniqueness")
