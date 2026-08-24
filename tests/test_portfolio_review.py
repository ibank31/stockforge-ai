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


def test_portfolio_review_rejects_an_exact_project_duplicate(tmp_path: Path):
    project_id = str(uuid4())
    root = tmp_path / "project"
    root.mkdir()
    candidate = root / "candidate.png"
    existing = root / "existing.png"
    _image(candidate)
    _image(existing)
    artifact = Artifact.from_file(project_id, "existing.png", root, kind="generated-image")

    report = evaluate_portfolio_candidate(
        candidate,
        project_root=root,
        current_artifact_id="new-artifact",
        project_artifacts=[artifact],
    )

    assert report.decision == "REJECT"
    assert report.similarities[0].classification == "exact_duplicate"
    assert any(reason.startswith("duplicate") for reason in report.reasons)


def test_portfolio_review_keeps_distinct_candidate_for_human_review(tmp_path: Path):
    project_id = str(uuid4())
    root = tmp_path / "project"
    root.mkdir()
    candidate = root / "candidate.png"
    existing = root / "existing.png"
    _image(candidate)
    _image(existing, invert=True)
    artifact = Artifact.from_file(project_id, "existing.png", root, kind="generated-image")

    report = evaluate_portfolio_candidate(
        candidate,
        project_root=root,
        current_artifact_id="new-artifact",
        project_artifacts=[artifact],
    )

    assert report.decision == "REVIEW"
    assert report.quality["ready_for_review"] is True
    assert report.similarities[0].classification == "distinct"
    assert "human" in report.notice.lower()
