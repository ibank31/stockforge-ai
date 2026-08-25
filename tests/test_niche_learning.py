from pathlib import Path

from stockforge.generation_evaluation import append_evaluation, new_evaluation
from stockforge.niche_learning import summarize_niche_learning, summarize_niche_records


def _evaluation(**overrides: object):
    values: dict[str, object] = {
        "execution_id": "exec-1",
        "artifact_id": "artifact-1",
        "lane_key": "technical_mechanical_component_illustrations",
        "buyer_job": "conceptual electromechanical component for engineering documentation",
        "product_kind": "raster_illustration",
        "delivery_format": "jpeg",
        "provider_id": "zerogpu",
        "model_id": "z-image-turbo",
        "workflow_hash": "workflow-1",
        "decision": "review",
        "visual_quality": 4,
        "technical_quality": 4,
        "buyer_fit": 3,
        "metadata_accuracy": 4,
        "marketplace_outcome": "not_submitted",
        "notes": "Human review pending.",
    }
    values.update(overrides)
    return new_evaluation(**values)


def test_one_generation_is_learning_evidence_but_not_policy_proof() -> None:
    summary = summarize_niche_records([_evaluation()])[0]

    assert summary.record_count == 1
    assert summary.recommendation == "INSUFFICIENT_EVIDENCE"
    assert summary.confidence == "initial"
    assert "one review" in summary.next_action


def test_multiple_reviews_surface_weak_dimension_without_sales_claim() -> None:
    first = _evaluation(decision="accept")
    second = _evaluation(
        execution_id="exec-2",
        artifact_id="artifact-2",
        decision="reject",
        visual_quality=3,
        technical_quality=4,
        buyer_fit=2,
        metadata_accuracy=4,
        rejection_reasons=("buyer fit unclear",),
        marketplace_outcome="not_submitted",
    )

    summary = summarize_niche_records([first, second])[0]

    assert summary.recommendation == "REFINE_BRIEF"
    assert summary.average_scores["buyer_fit"] == 2.5
    assert summary.rejection_reasons == {"buyer fit unclear": 1}
    assert summary.marketplace_outcome_counts == {"not_submitted": 2}


def test_learning_summary_reads_append_only_ledger(tmp_path: Path) -> None:
    append_evaluation(tmp_path, _evaluation())

    summary = summarize_niche_learning(str(tmp_path))

    assert summary["record_count"] == 1
    assert summary["niche_count"] == 1
    assert summary["niches"][0]["lane_key"] == "technical_mechanical_component_illustrations"
    assert "sales forecasts" in str(summary["notice"])
