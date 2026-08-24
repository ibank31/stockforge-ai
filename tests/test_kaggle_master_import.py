import json
from pathlib import Path

from PIL import Image, ImageCms

from stockforge.artifact import sha256_file
from stockforge.kaggle_master_import import import_kaggle_master


def _srgb() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def test_import_kaggle_master_verifies_request_output_and_technical_gate(tmp_path: Path):
    root = tmp_path / "project"
    source = root / "artifacts" / "preview.webp"
    source.parent.mkdir(parents=True)
    Image.new("RGB", (1024, 1024), (20, 40, 60)).save(source, format="WEBP")
    request_path = root / "master-finalizer-requests" / "request.json"
    request_path.parent.mkdir(parents=True)
    request = {
        "schema_version": 1,
        "kind": "stockforge.master_finalizer_request",
        "request_id": "request-1",
        "status": "prepared_no_gpu",
        "source": {
            "artifact_id": "artifact-1",
            "execution_id": "execution-1",
            "relative_path": "artifacts/preview.webp",
            "sha256": sha256_file(source),
            "width": 1024,
            "height": 1024,
        },
        "target": {
            "mode": "ai_upscale",
            "scale": 4,
            "minimum_megapixels": 6.0,
            "expected_width": 4096,
            "expected_height": 4096,
            "expected_megapixels": 16.7772,
            "format": "jpeg",
            "color_space": "sRGB",
        },
        "destination": "masters/artifact-1-master.jpg",
    }
    request_path.write_text(json.dumps(request), encoding="utf-8")

    result_dir = tmp_path / "result"
    result_dir.mkdir()
    with Image.open(source) as preview:
        master = preview.convert("RGB").resize((4096, 4096))
    intermediate = result_dir / "master.upscaled.png"
    master.save(intermediate, format="PNG")
    master_path = result_dir / "master.jpg"
    master.save(master_path, format="JPEG", quality=95, icc_profile=_srgb())
    result = {
        "schema_version": 1,
        "kind": "stockforge.kaggle_finalizer_result",
        "status": "visual_review_required",
        "request_id": "request-1",
        "source": request["source"],
        "target": request["target"],
        "provider": "kaggle-realesrgan",
        "model_id": "RealESRGAN_x4plus",
        "scale": 4,
        "master": {
            "file": "master.jpg",
            "sha256": sha256_file(master_path),
            "width": 4096,
            "height": 4096,
            "megapixels": 16.7772,
            "icc_profile": "sRGB",
            "jpeg_quality": 95,
            "subsampling": "4:4:4",
            "size_bytes": master_path.stat().st_size,
        },
        "intermediate": {"file": "master.upscaled.png", "sha256": sha256_file(intermediate)},
        "human_review_required": True,
    }
    (result_dir / "result.json").write_text(json.dumps(result), encoding="utf-8")

    report = import_kaggle_master(
        request_path=request_path,
        result_dir=result_dir,
        project_root=root,
    )

    copied = root / "masters" / "artifact-1-master.jpg"
    assert copied.is_file()
    assert report.quality_state == "visual_review_required"
    assert report.upscale.provider_id == "kaggle-realesrgan"
    assert report.jpeg.megapixels >= 6
