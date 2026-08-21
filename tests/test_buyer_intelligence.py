from stockforge.buyer_intelligence import BUYER_REGISTRY, build_buyer_concept_brief, rank_buyers
from stockforge.market_intelligence import MarketEvidence, MarketOpportunity


def make_opportunity() -> MarketOpportunity:
    return MarketOpportunity(
        marketplace="adobe_stock",
        query="construction technology",
        result_count=1000,
        demand_score=80,
        growth_score=75,
        saturation_score=45,
        buyer_fit_score=85,
        visual_differentiation_score=80,
        variation_score=80,
        commercial_clarity_score=90,
        buyer=BUYER_REGISTRY[0].to_profile(),
        evidence=(
            MarketEvidence(
                source="test",
                url="https://example.com/evidence",
                observed_at="2026-08-20T00:00:00Z",
                signal="buyer_use_case",
                value="construction technology workflow",
                confidence="high",
            ),
        ),
    )


def test_registry_is_non_empty():
    assert len(BUYER_REGISTRY) >= 5


def test_rank_buyers_returns_descending_scores():
    matches = rank_buyers(make_opportunity())
    assert matches
    assert matches[0].score >= matches[-1].score
    assert matches[0].recommendation in {"PRIORITY", "CANDIDATE"}


def test_build_buyer_concept_brief_contains_constraints():
    opportunity = make_opportunity()
    buyer = BUYER_REGISTRY[0]
    brief = build_buyer_concept_brief(
        opportunity,
        buyer,
        visual_problem="show physical and digital construction coordination",
        subject="site supervisor reviewing field data",
        composition="wide hero with copy space on right",
    )
    assert brief["buyer"]["segment"] == buyer.segment
    assert brief["generation_constraints"]["visual_requirements"]
    assert brief["generation_constraints"]["uniqueness_levers"]


def test_low_fit_buyer_is_rejected():
    opportunity = make_opportunity()
    unrelated = BUYER_REGISTRY[-1]
    try:
        build_buyer_concept_brief(
            opportunity,
            unrelated,
            visual_problem="unrelated",
            subject="unrelated",
            composition="square",
        )
    except ValueError as exc:
        assert "Buyer fit" in str(exc)
