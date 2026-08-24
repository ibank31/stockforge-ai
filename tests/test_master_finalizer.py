from pathlib import Path

import pytest
from PIL import Image

from stockforge.adobe_gate import inspect_image
from stockforge.master_finalizer import (
    MasterFinalizationError,
    MasterTarget,
    finalize_master_candidate,
)
from stockforge.upscaler import UpscaleReport, UpscaleRequest


class _TestFourXUpscaler:
    provider_id = "test-upscaler"
    model_id = "test-x4"

    def healthcheck(self) -> bool:
        return True

    def upscale(self, request: UpscaleRequest) -> UpscaleReport:
        with Image.open(request.source) as source:
            source.load()
            width, height = source.size
            output = source.convert("RGB").resize((width * 4, height * 4))
        request.destination.parent.mkdir(parents=True, exist_ok=True)
        output.save(request.destination, format="PNG")
        return UpscaleReport(
            source_path=str(request.source),
            output_path=str(request.destination),
            provider_id=self.provider_id,
            model_id=self.model_id,
            scale=4,
            source_width=width,
            source_height=height,
            output_width=width * 4,
            output_height=height * 4,
        )


def _preview(path: Path, size: tuple[int, int] = (1024, 1024)) -> None:
    Image.new("RGB", size, (25, 50, 90)).save(path, format="WEBP")


def test_finalizer_creates_review_required_master_jpeg(tmp_path: Path) -> None:
    source = tmp_path / "preview.webp"
    destination = tmp_path / "masters" / "master.jpg"
    _preview(source)

    report = finalize_master_candidate(
        source=source,
        destination=destination,
        upscaler=_TestFourXUpscaler(),
    )
    gate = inspect_image(destination)

    assert report.quality_state == "visual_review_required"
    assert Path(report.intermediate_path).is_file()
    assert report.upscale.provider_id == "test-upscaler"
    assert report.jpeg.width == 4096
    assert report.jpeg.height == 4096
    assert gate.ready is True
    assert gate.megapixels is not None and gate.megapixels >= 6
    assert destination.suffix == ".jpg"


def test_finalizer_fails_before_calling_upscaler_when_target_is_too_small(tmp_path: Path) -> None:
    source = tmp_path / "preview.webp"
    destination = tmp_path / "master.jpg"
    _preview(source, (500, 500))

    with pytest.raises(MasterFinalizationError, match="below"):
        finalize_master_candidate(
            source=source,
            destination=destination,
            upscaler=_TestFourXUpscaler(),
            target=MasterTarget(minimum_megapixels=6, scale=2),
        )


def test_finalizer_rejects_non_jpeg_master_destination(tmp_path: Path) -> None:
    source = tmp_path / "preview.webp"
    _preview(source)

    with pytest.raises(MasterFinalizationError, match=".jpg"):
        finalize_master_candidate(
            source=source,
            destination=tmp_path / "master.png",
            upscaler=_TestFourXUpscaler(),
        )
