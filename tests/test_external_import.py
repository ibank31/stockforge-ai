from pathlib import Path

from PIL import Image

from stockforge.database import Database
from stockforge.external_import import import_external_image
from stockforge.job_database import JobDatabase


def _database(tmp_path: Path) -> tuple[JobDatabase, Path, str]:
    database = JobDatabase(tmp_path / "stockforge.db")
    database.initialize()
    project_root = tmp_path / "projects" / "stock-assets"
    project_root.mkdir(parents=True)
    database.create_project("project-1", "stock-assets", project_root)
    return database, project_root, "project-1"


def _png(path: Path, size=(128, 96), mode="RGB") -> None:
    image = Image.new(mode, size, (120, 140, 160, 255) if mode == "RGBA" else (120, 140, 160))
    image.save(path, format="PNG")


def test_import_external_registers_execution_artifact_and_provenance(tmp_path: Path) -> None:
    database, project_root, project_id = _database(tmp_path)
    source = tmp_path / "crate.png"
    _png(source)
    source_bytes = source.read_bytes()

    result = import_external_image(
        database=database,
        project_id=project_id,
        project_root=project_root,
        source=source,
        candidate_id="png-v2-002",
        provider_label="chatgpt",
        model_label="external-image-model",
        original_filename="crate-from-chatgpt.png",
        prompt="crate prompt",
    )

    assert source.read_bytes() == source_bytes
    assert result.execution.operation == "image.import_external"
    assert result.execution.state == "succeeded"
    assert result.execution.artifact_ids == (result.artifact.id,)
    assert result.artifact.kind == "generated-image"
    assert result.artifact.metadata["provider_label"] == "chatgpt"
    assert result.report["technical_report"]["intended_delivery_format"] == "png"
    assert result.report["technical_report"]["gate"]["ready"] is False
    assert any(item["name"] == "true_alpha" and item["status"] == "FAIL" for item in result.report["technical_report"]["gate"]["checks"])
    assert len(database.list_provenance(result.artifact.id)) == 1
    assert result.report_path.is_file()


def test_import_external_jpeg_scene_keeps_png_source_encoding_explicit(tmp_path: Path) -> None:
    database, project_root, project_id = _database(tmp_path)
    source = tmp_path / "e-cargo.png"
    _png(source, size=(1254, 1254))

    result = import_external_image(
        database=database,
        project_id=project_id,
        project_root=project_root,
        source=source,
        candidate_id="jpeg-external-e-cargo-battery-swap",
        provider_label="chatgpt",
    )

    report = result.report["technical_report"]
    assert report["intended_delivery_format"] == "jpeg"
    assert report["source_encoding"] == "PNG"
    assert "later JPEG finalizer/export" in report["note"]
    assert result.execution.parameters["portfolio"]["asset_spec"]["delivery_format"] == "jpeg"
    assert result.execution.parameters["portfolio"]["asset_spec"]["layout_mode"] == "hero_landscape"


def test_unknown_candidate_requires_complete_context(tmp_path: Path) -> None:
    database, project_root, project_id = _database(tmp_path)
    source = tmp_path / "unknown.png"
    _png(source)

    try:
        import_external_image(
            database=database,
            project_id=project_id,
            project_root=project_root,
            source=source,
            candidate_id="new-candidate",
            provider_label="external",
        )
    except ValueError as exc:
        assert "missing" in str(exc) or "requires" in str(exc)
    else:
        raise AssertionError("unknown candidate must require explicit context")
