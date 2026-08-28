from pathlib import Path

from PIL import Image

from stockforge.external_finalizer_prep import prepare_external_finalizer
from stockforge.external_import import import_external_image
from stockforge.job_database import JobDatabase


def _setup(tmp_path: Path) -> tuple[JobDatabase, Path, str]:
    database = JobDatabase(tmp_path / "stockforge.db")
    database.initialize()
    root = tmp_path / "projects" / "stock-assets"
    root.mkdir(parents=True)
    database.create_project("project-1", "stock-assets", root)
    return database, root, "project-1"


def _source(path: Path, size: tuple[int, int], mode: str = "RGBA") -> None:
    image = Image.new(mode, size, (120, 140, 160, 255) if mode == "RGBA" else (120, 140, 160))
    image.save(path, format="PNG")


def test_png_preparation_fits_entire_source_to_worker_square_without_crop(tmp_path: Path) -> None:
    database, root, project_id = _setup(tmp_path)
    source = tmp_path / "crate.png"
    _source(source, (1536, 1024), "RGBA")
    imported = import_external_image(
        database=database,
        project_id=project_id,
        project_root=root,
        source=source,
        candidate_id="png-v2-002",
        provider_label="chatgpt",
    )

    prepared = prepare_external_finalizer(
        database=database,
        project_id=project_id,
        project_root=root,
        execution_id=imported.execution.id,
    )

    assert prepared["delivery_format"] == "png"
    assert prepared["status"] == "prepared_no_gpu"
    assert prepared["preparation"]["crop"] is False
    assert prepared["prepared_artifact_id"]
    request = prepared["request"]
    assert request["source"]["width"] == 1024
    assert request["source"]["height"] == 1024
    assert request["source"]["color_mode"] == "RGB"
    assert request["target"]["expected_width"] == 4096
    assert request["target"]["expected_height"] == 4096
    derived = database.get_artifact(prepared["prepared_artifact_id"])
    assert derived is not None
    with Image.open(root / derived.relative_path) as image:
        assert image.size == (1024, 1024)
        assert image.mode == "RGB"
    lineage = database.list_lineage(artifact_id=derived.id)
    assert len(lineage) == 1
    assert lineage[0].relation == "transformed"
    assert lineage[0].parent_artifact_id == imported.artifact.id


def test_jpeg_preparation_uses_four_x_request_without_mutating_source(tmp_path: Path) -> None:
    database, root, project_id = _setup(tmp_path)
    source = tmp_path / "e-cargo.png"
    _source(source, (1254, 1254), "RGB")
    imported = import_external_image(
        database=database,
        project_id=project_id,
        project_root=root,
        source=source,
        candidate_id="jpeg-external-e-cargo-battery-swap",
        provider_label="chatgpt",
    )
    source_bytes = (root / imported.artifact.relative_path).read_bytes()

    prepared = prepare_external_finalizer(
        database=database,
        project_id=project_id,
        project_root=root,
        execution_id=imported.execution.id,
    )

    assert prepared["delivery_format"] == "jpeg"
    assert prepared["prepared_artifact_id"]
    assert prepared["preparation"]["mode"] == "rgb_jpeg_staging"
    assert prepared["request"]["target"]["format"] == "jpeg"
    assert prepared["request"]["target"]["scale"] == 4
    assert prepared["request"]["target"]["expected_megapixels"] > 6
    staged = database.get_artifact(prepared["prepared_artifact_id"])
    assert staged is not None
    with Image.open(root / staged.relative_path) as image:
        assert image.format == "JPEG"
        assert image.size == (1254, 1254)
    assert (root / imported.artifact.relative_path).read_bytes() == source_bytes
