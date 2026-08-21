from pathlib import Path

import pytest
from PIL import Image

from stockforge.realesrgan_upscaler import RealESRGANUpscaler
from stockforge.upscaler import UpscaleRequest, UpscalerError


def test_request_accepts_supported_scale(tmp_path: Path) -> None:
    request = UpscaleRequest(tmp_path / "in.png", tmp_path / "out.png", scale=4)
    assert request.scale == 4


def test_request_rejects_unsupported_scale(tmp_path: Path) -> None:
    with pytest.raises(UpscalerError, match="2x and 4x"):
        UpscaleRequest(tmp_path / "in.png", tmp_path / "out.png", scale=3)


def test_request_rejects_same_path(tmp_path: Path) -> None:
    path = tmp_path / "same.png"
    with pytest.raises(UpscalerError, match="different files"):
        UpscaleRequest(path, path)


def test_realesrgan_healthcheck_requires_model(tmp_path: Path) -> None:
    provider = RealESRGANUpscaler(tmp_path / "missing.pth")
    assert provider.healthcheck() is False


def test_realesrgan_rejects_missing_source(tmp_path: Path) -> None:
    provider = RealESRGANUpscaler(tmp_path / "model.pth")
    with pytest.raises(UpscalerError, match="Source image does not exist"):
        provider.upscale(UpscaleRequest(tmp_path / "missing.png", tmp_path / "out.png"))


def test_realesrgan_rejects_non_4x_request(tmp_path: Path) -> None:
    provider = RealESRGANUpscaler(tmp_path / "model.pth")
    source = tmp_path / "source.png"
    Image.new("RGB", (64, 64)).save(source)
    request = UpscaleRequest(source, tmp_path / "out.png", scale=2)
    with pytest.raises(UpscalerError, match="4x model"):
        provider.upscale(request)
