from stockforge.intelligence_pipeline import build_intelligence_plan


def payload():
    return {
        "marketplace": "adobe_stock",
        "query": "tactile productivity metaphor",
        "buyer_segment": "web_product_teams",
        "demand_score": 82,
        "growth_score": 75,
        "saturation_score": 38,
        "buyer_fit_score": 90,
        "visual_differentiation_score": 84,
        "variation_score": 80,
        "commercial_clarity_score": 88,
        "evidence": [{
            "source": "manual_research",
            "url": "https://example.com/search",
            "observed_at": "2026-09-13T00:00:00Z",
            "signal": "supply_proxy",
            "value": "crowding observed manually",
            "confidence": "high",
        }],
    }


def test_integrated_plan_reaches_prompt_layer():
    plan = build_intelligence_plan(payload())
    assert plan.assets
    assert plan.opportunity.production_recommendation in {"PRIORITY", "CANDIDATE", "REJECT", "REVIEW"}
    assert all(asset.prompt_package.prompt for asset in plan.assets)
    assert all(asset.asset_spec.originality_levers for asset in plan.assets)


def test_integrated_plan_keeps_evidence_explicit():
    plan = build_intelligence_plan(payload())
    output = plan.to_dict()
    assert output["opportunity"]["evidence"][0]["source"] == "manual_research"
    assert "No provider was called" in output["notice"]
