from stockforge.market_intelligence import BuyerProfile, MarketEvidence, MarketOpportunity, build_concept_brief


def evidence():
    return (MarketEvidence(
        source="Adobe Stock",
        url="https://stock.adobe.com/",
        observed_at="2026-08-20",
        signal="supply",
        value="dynamic marketplace result count",
        confidence="high",
    ),)


def buyer():
    return BuyerProfile(
        segment="construction_technology_marketing",
        industry="construction_technology",
        roles=("product_marketing", "content_marketing"),
        communication_jobs=("website_hero", "blog_article"),
        channels=("web", "presentation"),
        visual_requirements=("authentic_workflow", "copy_space"),
        uniqueness_levers=("physical_digital_relationship", "specific_workflow"),
    )


def opportunity(**overrides):
    values = dict(
        marketplace="adobe_stock",
        query="construction AI safety workflow",
        result_count=10000,
        demand_score=80,
        growth_score=75,
        saturation_score=30,
        buyer_fit_score=90,
        visual_differentiation_score=85,
        variation_score=80,
        commercial_clarity_score=90,
        buyer=buyer(),
        evidence=evidence(),
    )
    values.update(overrides)
    return MarketOpportunity(**values)


def test_opportunity_score_is_transparent_and_bounded():
    item = opportunity()
    assert 0 <= item.opportunity_score <= 100
    assert item.production_recommendation == "PRIORITY"


def test_high_saturation_reduces_score():
    low = opportunity(saturation_score=20)
    high = opportunity(saturation_score=90)
    assert low.opportunity_score > high.opportunity_score


def test_missing_evidence_is_rejected():
    item = opportunity(evidence=())
    try:
        item.validate()
    except ValueError as exc:
        assert "evidence" in str(exc).lower()
    else:
        raise AssertionError("Expected evidence validation failure")


def test_risk_flags_force_review():
    item = opportunity(risk_flags=("insufficient_market_evidence",))
    assert item.production_recommendation == "REVIEW"


def test_concept_brief_preserves_buyer_and_evidence():
    item = opportunity()
    brief = build_concept_brief(
        item,
        visual_problem="communicate digital safety workflow",
        subject="site supervisor reviewing a mobile inspection workflow",
        composition="subject left with clean copy space right",
    )
    assert brief["buyer"] == "construction_technology_marketing"
    assert brief["visual_problem"] == "communicate digital safety workflow"
    assert brief["uniqueness_levers"] == ["physical_digital_relationship", "specific_workflow"]
    assert len(brief["evidence"]) == 1
