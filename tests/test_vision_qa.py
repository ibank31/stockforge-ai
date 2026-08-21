from pathlib import Path

from stockforge.vision_qa import VisionAssessment, VisionQAPolicy, evaluate_vision


class GoodProvider:
    name = "test-good"

    def assess(self, path: Path, *, context: str = "") -> VisionAssessment:
        return VisionAssessment(
            overall_score=0.92,
            commercial_score=0.88,
            integrity_score=0.94,
            artifact_score=0.04,
            anatomy_ok=True,
            realism_ok=True,
            composition_ok=True,
            subject_integrity_ok=True,
            text_or_logo_risk=False,
            provider=self.name,
        )


class BadProvider:
    name = "test-bad"

    def assess(self, path: Path, *, context: str = "") -> VisionAssessment:
        return VisionAssessment(
            overall_score=0.50,
            commercial_score=0.40,
            integrity_score=0.45,
            artifact_score=0.60,
            anatomy_ok=False,
            realism_ok=False,
            composition_ok=True,
            subject_integrity_ok=False,
            text_or_logo_risk=True,
            provider=self.name,
        )


def test_missing_provider_blocks_submission(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"placeholder")
    report = evaluate_vision(path, provider=None)
    assert report.status == "fail"
    assert report.assessment is None


def test_good_provider_passes(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"placeholder")
    report = evaluate_vision(path, provider=GoodProvider())
    assert report.status == "pass"
    assert report.assessment is not None


def test_bad_provider_fails(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"placeholder")
    report = evaluate_vision(path, provider=BadProvider())
    assert report.status == "fail"
    assert "AI artifact risk above threshold" in report.reasons
    assert "anatomy or hands failed" in report.reasons


def test_provider_error_requires_review(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"placeholder")

    class Broken:
        name = "broken"

        def assess(self, path: Path, *, context: str = "") -> VisionAssessment:
            raise RuntimeError("backend down")

    report = evaluate_vision(path, provider=Broken(), policy=VisionQAPolicy())
    assert report.status == "review"
    assert report.assessment is None
