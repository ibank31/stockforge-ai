from pathlib import Path

import pytest

from stockforge.generation_evaluation import (
    EvaluationError,
    append_evaluation,
    load_evaluations,
    new_evaluation,
    summarize_evaluations,
)


def _evaluation(**overrides: object):
    values: dict[str, object] = {
        "execution_id": "exec-1",
        "artifact_id": "artifact-1",
        "lane_key": "tactile_material_atmospheres",
        "buyer_job": "web hero background",
        "product_kind": "raster_illustration",
        "delivery_format": "jpeg",
        "provider_id": "zerogpu",
        "model_id": "z-image-turbo",
        "workflow_hash": "workflow-1",
        "decision": "accept",
        "visual_quality": 4,
        "technical_quality": 5,
        "buyer_fit": 4,
        "metadata_accuracy": 5,
    }
    values.update(overrides)
    return new_evaluation(**values)


def test_evaluation_is_tied_to_generation_identity() -> None:
    record = _evaluation()

    assert record.execution_id == "exec-1"
    assert record.artifact_id == "artifact-1"
    assert record.overall_score == 4.5
    assert record.to_dict()["rejection_reasons"] == []


def test_rejected_evaluation_requires_reason() -> None:
    with pytest.raises(EvaluationError, match="rejection reason"):
        _evaluation(decision="reject")


def test_evaluation_scores_are_bounded() -> None:
    with pytest.raises(EvaluationError, match="integer from 0 to 5"):
        _evaluation(visual_quality=6)


def test_append_and_summary_are_deterministic_and_append_only(tmp_path: Path) -> None:
    accepted = _evaluation()
    rejected = _evaluation(
        execution_id="exec-2",
        artifact_id="artifact-2",
        delivery_format="svg",
        decision="reject",
        visual_quality=2,
        technical_quality=5,
        buyer_fit=1,
        metadata_accuracy=3,
        rejection_reasons=("weak buyer fit", "duplicate composition"),
    )

    path = append_evaluation(tmp_path, accepted)
    append_evaluation(tmp_path, rejected)
    records = load_evaluations(tmp_path)
    summary = summarize_evaluations(tmp_path)

    assert path.name == "generation_evaluations.jsonl"
    assert [item.artifact_id for item in records] == ["artifact-1", "artifact-2"]
    assert summary["record_count"] == 2
    assert summary["decision_counts"] == {"accept": 1, "reject": 1}
    assert summary["format_counts"] == {"jpeg": 1, "svg": 1}
    assert summary["rejection_reasons"] == {"duplicate composition": 1, "weak buyer fit": 1}
    assert summary["average_scores"] == {
        "visual_quality": 3.0,
        "technical_quality": 5.0,
        "buyer_fit": 2.5,
        "metadata_accuracy": 4.0,
    }


def test_empty_summary_makes_no_learning_claim(tmp_path: Path) -> None:
    summary = summarize_evaluations(tmp_path)

    assert summary["record_count"] == 0
    assert "No human evaluation records" in str(summary["notice"])
