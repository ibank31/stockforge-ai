from stockforge.vision_ensemble import evaluate_ensemble


def test_complete_good_signals_pass():
    report = evaluate_ensemble({
        "aesthetic": 0.9,
        "semantic": 0.9,
        "commercial": 0.9,
        "anatomy": 0.9,
        "subject_integrity": 0.9,
        "artifact_risk": 0.9,
        "unexpected_text": 0.9,
        "ip_risk": 0.9,
        "similarity": 0.2,
    })
    assert report.decision == "PASS"


def test_missing_signal_is_review_not_pass():
    report = evaluate_ensemble({
        "aesthetic": 0.9,
        "semantic": None,
        "commercial": 0.9,
    }, provider_names={"semantic": "vision-llm"})
    assert report.decision == "REVIEW"
    assert "vision-llm" in report.missing_providers


def test_critical_anatomy_failure_is_fail():
    report = evaluate_ensemble({
        "aesthetic": 0.9,
        "semantic": 0.9,
        "commercial": 0.9,
        "anatomy": 0.2,
    })
    assert report.decision == "FAIL"


def test_high_similarity_is_fail():
    report = evaluate_ensemble({
        "aesthetic": 0.9,
        "semantic": 0.9,
        "commercial": 0.9,
        "similarity": 0.98,
    })
    assert report.decision == "FAIL"
