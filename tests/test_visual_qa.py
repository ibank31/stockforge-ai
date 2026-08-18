from pathlib import Path

from stockforge.image_qa import ImageQAReport
from stockforge.visual_qa import VisualQAPolicy, inspect_visual


def structural_report(path: Path, width: int = 4000, height: int = 3000) -> ImageQAReport:
    return ImageQAReport(
        "pass",
        str(path),
        "png",
        width,
        height,
        width * height / 1_000_000,
        1000,
        {
            "format": "pass",
            "decode_header": "pass",
            "minimum_dimensions": "pass",
            "minimum_megapixels": "pass",
            "recommended_megapixels": "pass",
            "file_size": "pass",
        },
    )


def test_visual_qa_passes_normal_landscape(tmp_path: Path) -> None:
    path = tmp_path / "office.png"
    report = inspect_visual(path, structural=structural_report(path))
    assert report.status == "pass"
    assert report.aspect_ratio == 4 / 3
    assert report.checks["aspect_ratio"] == "pass"


def test_visual_qa_fails_extreme_aspect_ratio(tmp_path: Path) -> None:
    path = tmp_path / "panorama.png"
    report = inspect_visual(
        path,
        structural=structural_report(path, width=10000, height=1000),
    )
    assert report.status == "fail"
    assert report.checks["aspect_ratio"] == "fail"


def test_visual_qa_warns_long_filename(tmp_path: Path) -> None:
    path = tmp_path / "short.png"
    report = inspect_visual(
        path,
        structural=structural_report(path),
        policy=VisualQAPolicy(max_filename_length=4),
    )
    assert report.status == "warn"
    assert report.checks["filename"] == "warn"


def test_visual_qa_fails_when_structural_qa_fails(tmp_path: Path) -> None:
    path = tmp_path / "broken.png"
    structural = ImageQAReport(
        "fail",
        str(path),
        None,
        None,
        None,
        None,
        10,
        {"format": "fail"},
    )
    report = inspect_visual(path, structural=structural)
    assert report.status == "fail"
    assert report.checks["structural"] == "fail"
