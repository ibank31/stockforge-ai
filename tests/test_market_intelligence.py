from stockforge.market_intelligence import BuyerProfile, MarketEvidence, MarketOpportunity, build_concept_brief


def evidence():
    return (MarketEvidence(
        source="Adobe 2026 Creative Trends",
        url="https://business.adobe.com/resources/creative-trends-report.html",
        observed_at="2026-08-24",
        signal="cross_industry_visual_demand",
        value="content leaders identify visual content as critical for key business communication",
        confidence="high",
    ),)


def buyer():
    return BuyerProfile(
        segment="web_product_teams",
        industry="software_and_digital_products",
        roles=("product_marketing", "developer_advocacy"),
        communication_jobs=("landing_page", "feature_explainer"),
        channels=("web", "presentation"),
        visual_requirements=("clear_silhouette", "compositing_flexibility"),
        uniqueness_levers=("single_visual_metaphor", "material_specificity"),
    )


def opportunity(**overrides):
    values = dict(
        marketplace="adobe_stock",
        query="tactile material atmosphere",
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
        visual_problem="provide a flexible standalone material metaphor",
        subject="single translucent resin pebble",
        composition="single centered object with clean copy space",
    )
    assert brief["buyer"] == "web_product_teams"
    assert brief["visual_problem"] == "provide a flexible standalone material metaphor"
    assert brief["uniqueness_levers"] == ["single_visual_metaphor", "material_specificity"]
    assert len(brief["evidence"]) == 1
