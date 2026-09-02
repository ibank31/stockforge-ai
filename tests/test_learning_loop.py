import json
from pathlib import Path

from PIL import Image

from stockforge.learning_loop import critique_image, load_memory, save_critique, summarize_learning_memory


def test_auto_critique_records_technical_observations_without_semantic_claims(tmp_path: Path):
    image_path = tmp_path / "preview.jpg"
    Image.new("RGB", (128, 128), (120, 150, 180)).save(image_path, format="JPEG", quality=92)

    critique = critique_image(
        image_path=image_path,
        execution_id="exec-001",
        artifact_id="artifact-001",
        lane_key="circular-retail",
        buyer_job="refill-store hero image",
        delivery_format="jpeg",
        product_kind="raster_illustration",
        title="Refill Bar",
    )

    assert critique.decision == "REVIEW_REQUIRED"
    assert critique.recommendation == "HUMAN_REVIEW_REQUIRED"
    assert critique.technical_score is not None
    assert critique.semantic_score is None
    assert critique.aesthetic_score is None
    assert any("semantic vision provider" in item for item in critique.limitations)

    path = save_critique(tmp_path, critique)
    assert path.is_file()
    memory = load_memory(tmp_path)
    key = "circular-retail|refill-store hero image|jpeg"
    assert memory["records"][key]["generation_count"] == 1
    assert memory["records"][key]["hypotheses"][0]["status"] == "unverified"

    summary = summarize_learning_memory(tmp_path)
    assert summary["record_count"] == 1
    assert "not a sales forecast" in summary["notice"]
    assert json.loads(path.read_text(encoding="utf-8"))["execution_id"] == "exec-001"


def test_auto_critique_marks_missing_image_as_technical_failure(tmp_path: Path):
    critique = critique_image(
        image_path=tmp_path / "missing.jpg",
        execution_id="exec-002",
        artifact_id="artifact-002",
        lane_key="test-lane",
        buyer_job="test buyer job",
        delivery_format="jpeg",
        product_kind="raster_illustration",
        title="Missing Preview",
    )

    assert critique.decision == "FAIL_TECHNICAL"
    assert critique.recommendation == "DO_NOT_FINALIZE"
    assert any(signal.name == "file_exists" and signal.status == "FAIL" for signal in critique.signals)


def test_png_preview_defers_final_master_alpha_gate(tmp_path: Path):
    image_path = tmp_path / "preview.webp"
    Image.new("RGB", (1024, 1024), (240, 240, 240)).save(image_path, format="WEBP", quality=90)
    critique = critique_image(
        image_path=image_path,
        execution_id="exec-png-preview",
        artifact_id="artifact-png-preview",
        lane_key="household_furniture_small_space_png",
        buyer_job="small-space furniture compositing asset",
        delivery_format="png",
        product_kind="transparent_cutout",
        title="Compact Rolling Kitchen Island Cart",
    )
    assert critique.decision == "REVIEW_REQUIRED"
    assert critique.recommendation == "HUMAN_REVIEW_REQUIRED"
    assert not any(signal.name.startswith("png_") and signal.status == "FAIL" for signal in critique.signals)
    assert any("deferred to finalized-master import" in item for item in critique.limitations)
