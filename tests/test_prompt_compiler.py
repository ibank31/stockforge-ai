from stockforge.prompt_compiler import compile_prompt
from stockforge.concept_engine import ConceptVariant


def make_concept() -> ConceptVariant:
    return ConceptVariant(
        concept_id="construction-saas-hero-1",
        angle="hero",
        visual_problem="show physical and digital construction coordination",
        subject="site supervisor reviewing project information on a tablet",
        action="compare live field conditions with non-branded digital project data",
        environment="active construction site with authentic equipment",
        composition="subject left, clean copy space right",
        copy_space="right",
        uniqueness_levers=("physical_digital_relationship", "specific_workflow"),
        buyer_job="website_hero",
        channel="web",
    )


def test_compiler_contains_concept_and_buyer_job():
    package = compile_prompt(make_concept())
    assert "site supervisor" in package.prompt
    assert "website_hero" in package.prompt
    assert "physical_digital_relationship" in package.prompt


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
