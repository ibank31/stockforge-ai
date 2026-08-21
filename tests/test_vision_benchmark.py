from stockforge.vision_benchmark import LabeledImage, rank_providers, score_provider


def test_score_provider():
    refs = [
        LabeledImage("a", {"anatomy": True}),
        LabeledImage("b", {"anatomy": False}),
        LabeledImage("c", {"anatomy": True}),
    ]
    preds = {
        "a": {"anatomy": 0.9},
        "b": {"anatomy": 0.1},
        "c": {"anatomy": 0.2},
    }
    metrics = score_provider("test", refs, preds, "anatomy")
    assert metrics.evaluated == 3
    assert metrics.accuracy == 0.6667
    assert metrics.false_negative_rate == 0.5


def test_rank_providers():
    refs = [LabeledImage("a", {"artifact": True}), LabeledImage("b", {"artifact": False})]
    good = score_provider("good", refs, {"a": {"artifact": .9}, "b": {"artifact": .1}}, "artifact")
    bad = score_provider("bad", refs, {"a": {"artifact": .1}, "b": {"artifact": .9}}, "artifact")
    assert rank_providers([bad, good])[0].provider == "good"
