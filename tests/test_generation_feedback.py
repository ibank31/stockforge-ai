from stockforge.generation_feedback import build_feedback_plan
from stockforge.learning_loop import AutoCritique, LearningSignal


def _critique(status="FAIL"):
    return AutoCritique(
        critique_id="crit-1", execution_id="exec-1", artifact_id="art-1",
        image_path="/tmp/a.jpg", lane_key="lane", buyer_job="web",
        delivery_format="jpeg", product_kind="image", title="Test",
        created_at="2026-09-13T00:00:00Z", technical_score=0.0,
        semantic_score=None, aesthetic_score=None, commercial_score=None,
        differentiation_score=None, decision="FAIL_TECHNICAL" if status=="FAIL" else "REVIEW_REQUIRED",
        recommendation="DO_NOT_FINALIZE",
        signals=(LearningSignal("sharpness", status, 0.0, "too soft", "test"),),
        limitations=("No semantic vision provider was used.",),
    )


def test_failure_becomes_regeneration_constraint():
    plan = build_feedback_plan(_critique())
    assert plan.regenerate is True
    assert any("edge clarity" in item for item in plan.prompt_constraints)
    assert "semantic" in " ".join(plan.unresolved_limitations).casefold()


def test_review_does_not_auto_approve_or_force_regeneration():
    plan = build_feedback_plan(_critique("REVIEW"))
    assert plan.regenerate is False
    assert plan.decision == "REVIEW_REQUIRED"
