from stockforge.buyer_intelligence import BUYER_REGISTRY
from stockforge.concept_engine import build_concept_plan
from stockforge.market_intelligence import MarketEvidence, MarketOpportunity


def opportunity():
    buyer = BUYER_REGISTRY[0].to_profile()
    return MarketOpportunity(
        marketplace="adobe_stock",
        query="construction technology",
        result_count=1000,
        demand_score=80,
        growth_score=75,
        saturation_score=40,
        buyer_fit_score=90,
        visual_differentiation_score=85,
        variation_score=90,
        commercial_clarity_score=90,
        buyer=buyer,
        evidence=(MarketEvidence(
            source="test",
            url="https://example.com/evidence",
            observed_at="2026-08-20T00:00:00Z",
            signal="buyer_use_case",
            value="construction software marketing",
            confidence="high",
        ),),
    )


def test_plan_creates_distinct_angles():
    plan = build_concept_plan(opportunity(), BUYER_REGISTRY[0], max_variants=4)
    assert len(plan.concepts) == 4
    assert len({c.angle for c in plan.concepts}) == 4
    assert all(c.uniqueness_levers for c in plan.concepts)


def test_plan_carries_buyer_job_and_channel():
    plan = build_concept_plan(opportunity(), BUYER_REGISTRY[0], max_variants=2)
    assert all(c.buyer_job for c in plan.concepts)
    assert all(c.channel for c in plan.concepts)


def test_variant_limit_is_guarded():
    try:
        build_concept_plan(opportunity(), BUYER_REGISTRY[0], max_variants=0)
    except ValueError as exc:
        assert "between 1 and 8" in str(exc)
