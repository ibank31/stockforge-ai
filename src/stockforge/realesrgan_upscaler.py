"""Real-ESRGAN provider for StockForge AI upscaling.

The heavy inference stack is optional and imported only when the provider is
constructed. This keeps the core/CLI lightweight and makes the provider usable
on a GPU host without forcing PyTorch onto every StockForge installation.

Default model: RealESRGAN_x4plus, a general-purpose natural-image model.
The upstream weights are BSD-3-Clause licensed; users must retain the required
license/attribution evidence in production deployments.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .upscaler import UpscaleReport, UpscaleRequest, UpscalerError


class RealESRGANUpscaler:
    """Thin adapter around the official Real-ESRGAN Python inference API."""

    provider_id = "realesrgan"
    model_id = "RealESRGAN_x4plus"

    def __init__(self, model_path: str | Path, *, tile: int = 0, half: bool = True) -> None:
        self.model_path = Path(model_path).expanduser().resolve()
        self.tile = tile
        self.half = half
        self._upsampler = None

    def _load(self):
        if self._upsampler is not None:
            return self._upsampler
        if not self.model_path.is_file():
            raise UpscalerError(f"Real-ESRGAN model not found: {self.model_path}")
        try:
            import torch
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
        except ImportError as exc:
            raise UpscalerError(
                "Real-ESRGAN provider dependencies are not installed. "
                "Install the optional upscaler environment before use."
            ) from exc

        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4,
        )
        self._upsampler = RealESRGANer(
            scale=4,
            model_path=str(self.model_path),
            model=model,
            tile=self.tile,
            tile_pad=10,
            pre_pad=0,
            half=self.half and torch.cuda.is_available(),
        )
        return self._upsampler

    def healthcheck(self) -> bool:
        return self.model_path.is_file()

    def upscale(self, request: UpscaleRequest) -> UpscaleReport:
        if request.scale != 4:
            raise UpscalerError(
                "RealESRGAN_x4plus is a 4x model. Use another provider/model for 2x."
            )
        source = request.source.expanduser().resolve()
        destination = request.destination.expanduser().resolve()
        if not source.is_file():
            raise UpscalerError(f"Source image does not exist: {source}")

        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise UpscalerError(
                "Real-ESRGAN provider requires OpenCV and NumPy."
            ) from exc

        try:
            with Image.open(source) as image:
                image.load()
                source_width, source_height = image.size
                if image.mode not in {"RGB", "RGBA", "L"}:
                    image = image.convert("RGB")
                rgb = image.convert("RGB")
                array = np.asarray(rgb)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise UpscalerError(f"Source image could not be decoded: {exc}") from exc

        # Real-ESRGAN expects BGR uint8 arrays.
        bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        try:
            output, _ = self._load().enhance(bgr, outscale=4)
        except Exception as exc:
            raise UpscalerError(f"Real-ESRGAN inference failed: {exc}") from exc

        destination.parent.mkdir(parents=True, exist_ok=True)
        suffix = destination.suffix.lower() or ".png"
        temporary = destination.with_name(destination.name + ".tmp" + suffix)
        try:
            if not cv2.imwrite(str(temporary), output):
                raise OSError("OpenCV failed to encode the upscaled image")
            temporary.replace(destination)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise UpscalerError(f"Could not write upscaled image: {exc}") from exc

        with Image.open(destination) as result:
            result.load()
            output_width, output_height = result.size

        expected_width = source_width * 4
        expected_height = source_height * 4
        if (output_width, output_height) != (expected_width, expected_height):
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                pass
            raise UpscalerError(
                f"Unexpected Real-ESRGAN output dimensions: {output_width}x{output_height}; "
                f"expected {expected_width}x{expected_height}."
            )

        return UpscaleReport(
            source_path=str(source),
            output_path=str(destination),
            provider_id=self.provider_id,
            model_id=self.model_id,
            scale=4,
            source_width=source_width,
            source_height=source_height,
            output_width=output_width,
            output_height=output_height,
        )
