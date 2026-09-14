from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw

from stockforge.artifact import Artifact
from stockforge.portfolio_review import evaluate_portfolio_candidate


def _image(path: Path, *, invert: bool = False) -> None:
    image = Image.new("RGB", (128, 128), "white")
    draw = ImageDraw.Draw(image)
    if invert:
        draw.rectangle((64, 16, 112, 112), fill="navy")
    else:
        draw.rectangle((16, 16, 64, 112), fill="navy")
    image.save(path, format="PNG")


def _review(tmp_path: Path, *, invert: bool = False):
    project_id = str(uuid4())
    root = tmp_path / "project"
    root.mkdir()
    candidate, existing = root / "candidate.png", root / "existing.png"
    _image(candidate, invert=invert)
    _image(existing)
    artifact = Artifact.from_file(project_id, "existing.png", root, kind="generated-image")
    return evaluate_portfolio_candidate(candidate, project_root=root,
        current_artifact_id="new-artifact", project_artifacts=[artifact])


def test_portfolio_review_rejects_an_exact_project_duplicate(tmp_path: Path):
    report = _review(tmp_path)
    assert report.decision == "REJECT"
    assert report.similarities[0].classification == "exact_duplicate"
    assert "V2 risk=" in report.similarities[0].detail
    assert any(reason.startswith("duplicate") for reason in report.reasons)


def test_portfolio_review_keeps_distinct_candidate_for_human_review(tmp_path: Path):
    report = _review(tmp_path, invert=True)
    assert report.decision == "REVIEW"
    assert report.quality["ready_for_review"] is True
    assert report.similarities[0].classification == "distinct"
    assert "V2 risk=" in report.similarities[0].detail
    assert "human" in report.notice.lower()
