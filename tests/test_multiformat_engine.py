from pathlib import Path

from PIL import Image, ImageCms
import pytest

from stockforge.adobe_png_gate import inspect_transparent_png
from stockforge.asset_spec import AssetSpec, AssetSpecError
from stockforge.format_router import FormatRoutingError, require_production_route, route_asset_spec
from stockforge.native_vector import build_modular_ribbon_svg, inspect_native_svg


def _spec(**overrides: object) -> AssetSpec:
    values: dict[str, object] = {
        "asset_id": "format-test",
        "market_opportunity_id": "F01",
        "buyer_segment": "design_teams",
        "buyer_job": "editable design component",
        "channel": "web",
        "asset_family": "generic",
        "asset_type": "graphic",
        "micro_niche": "abstract modular element",
        "subject": "three modular geometric forms joined by one ribbon",
        "visual_language": "clean abstract editorial vector",
        "medium": "flat editable paths",
        "originality_levers": ("asymmetric rhythm",),
        "product_kind": "raster_illustration",
        "delivery_format": "jpeg",
        "layout_mode": "square",
        "background_policy": "white",
        "isolation_policy": "isolated",
        "text_policy": "none",
    }
    values.update(overrides)
    return AssetSpec(**values)  # type: ignore[arg-type]


def _write_png(path: Path, *, alpha: bool, opaque: bool = False) -> None:
    mode = "RGBA" if alpha else "RGB"
    image = Image.new(mode, (2048, 2048), (255, 255, 255, 0) if alpha else (255, 255, 255))
    if alpha:
        if opaque:
            image = Image.new("RGBA", (2048, 2048), (255, 255, 255, 255))
        else:
            image.paste((16, 78, 99, 255), (350, 350, 1698, 1698))
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    image.save(path, format="PNG", icc_profile=profile)


def test_raster_route_uses_square_without_copy_space_heuristic() -> None:
    route = require_production_route(_spec())
    assert route.delivery_format == "jpeg"
    assert route.canvas == "square"
    assert route.requires_remote_gpu is True


def test_transparent_cutout_requires_true_alpha_contract() -> None:
    with pytest.raises(AssetSpecError, match="transparent background"):
        _spec(
            product_kind="transparent_cutout",
            delivery_format="png",
            background_policy="white",
        )


def test_transparent_route_is_blocked_until_alpha_pipeline_is_verified() -> None:
    spec = _spec(
        product_kind="transparent_cutout",
        delivery_format="png",
        background_policy="transparent",
    )
    route = route_asset_spec(spec)
    assert route.requires_true_alpha is True
    assert route.verified_for_production is False
    with pytest.raises(FormatRoutingError, match="alpha producer"):
        require_production_route(spec)


def test_png_gate_passes_true_alpha_png(tmp_path: Path) -> None:
    candidate = tmp_path / "cutout.png"
    _write_png(candidate, alpha=True)
    report = inspect_transparent_png(candidate)
    assert report.ready is True
    assert report.transparent_fraction is not None and report.transparent_fraction > 0


def test_png_gate_rejects_opaque_png_even_with_png_extension(tmp_path: Path) -> None:
    candidate = tmp_path / "white-background.png"
    _write_png(candidate, alpha=True, opaque=True)
    report = inspect_transparent_png(candidate)
    assert report.ready is False
    assert any(item.name == "true_alpha" and item.status == "FAIL" for item in report.checks)


def test_native_vector_route_builds_auditable_svg_without_gpu(tmp_path: Path) -> None:
    spec = _spec(
        asset_id="modular-ribbon",
        asset_type="icon",
        product_kind="native_vector",
        delivery_format="svg",
        layout_mode="square",
        background_policy="transparent",
        medium="flat editable SVG paths",
        palette=("#164E63", "#F8FAFC", "#F59E0B"),
    )
    route = require_production_route(spec)
    assert route.requires_remote_gpu is False
    report = build_modular_ribbon_svg(spec, tmp_path / "modular-ribbon.svg")
    assert report.ready is True
    assert report.transparent_background is True
    assert report.native_paths_only is True
    assert inspect_native_svg(tmp_path / "modular-ribbon.svg").ready is True


def test_native_vector_rejects_scene_contract() -> None:
    with pytest.raises(AssetSpecError, match="scenes are not supported"):
        _spec(
            product_kind="native_vector",
            delivery_format="svg",
            isolation_policy="scene",
        )


def test_local_native_vector_build_persists_no_gpu_execution(tmp_path: Path) -> None:
    from stockforge.database import Database
    from stockforge.local_vector_build import build_local_native_vector

    project_root = tmp_path / "project"
    project_root.mkdir()
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project("project-id", "demo", project_root)
    spec = _spec(
        asset_id="persisted-modular-ribbon",
        asset_type="icon",
        product_kind="native_vector",
        delivery_format="svg",
        layout_mode="square",
        background_policy="transparent",
        medium="flat editable SVG paths",
        palette=("#164E63", "#F8FAFC", "#F59E0B"),
    )

    result = build_local_native_vector(
        database=database,
        project_id="project-id",
        project_root=project_root,
        spec=spec,
    )

    execution = database.get_execution(result.execution_id)
    artifact = database.get_artifact(result.artifact_id)
    assert result.report.ready is True
    assert execution is not None and execution.state == "succeeded"
    assert execution.provider_id == "local-native-vector"
    assert artifact is not None and artifact.kind == "native-vector"
    assert artifact.relative_path.endswith(".svg")
    assert database.list_provenance(result.artifact_id)[0].operation == "vector.build_native"


def test_android_export_copies_only_one_visual_file_to_minimal_branch(tmp_path: Path) -> None:
    from stockforge.android_export import PREVIEW_BRANCH, UPLOAD_BRANCH, export_preview, export_ready_upload

    preview = tmp_path / "source.webp"
    preview.write_bytes(b"preview")
    final = tmp_path / "master.jpg"
    final.write_bytes(b"master")
    downloads = tmp_path / "Download"

    review_export = export_preview(source=preview, downloads_root=downloads, asset_name="Woven Loop")
    upload_export = export_ready_upload(source=final, downloads_root=downloads, asset_name="Woven Loop")

    assert review_export.destination.parent.name == PREVIEW_BRANCH
    assert upload_export.destination.parent.name == UPLOAD_BRANCH
    assert review_export.destination.name == "woven-loop__preview.webp"
    assert upload_export.destination.name == "woven-loop__adobe.jpg"
    assert list(review_export.destination.parent.iterdir()) == [review_export.destination]
    assert list(upload_export.destination.parent.iterdir()) == [upload_export.destination]


def test_technical_badge_preset_builds_native_svg_without_text_or_raster(tmp_path: Path) -> None:
    from stockforge.native_vector import build_svg_for_preset

    spec = _spec(
        asset_id="technical-badge",
        asset_type="icon",
        product_kind="native_vector",
        delivery_format="svg",
        layout_mode="square",
        background_policy="white",
        medium="flat editable SVG geometry",
        palette=("#164E63", "#F8FAFC", "#F59E0B"),
        tags=("technical_icon", "badge"),
    )

    report = build_svg_for_preset(spec, tmp_path / "technical-badge.svg", preset="technical_badge")

    assert report.ready is True
    assert report.native_paths_only is True
    assert report.transparent_background is False
    svg = (tmp_path / "technical-badge.svg").read_text(encoding="utf-8")
    assert "<text" not in svg
    assert "<image" not in svg
    assert "native-vector-technical-badge-v1" in svg


def test_true_alpha_finalizer_preserves_source_and_writes_reviewable_png(tmp_path: Path) -> None:
    from stockforge.png_alpha_finalize import prepare_true_alpha_png

    source = tmp_path / "source.png"
    destination = tmp_path / "normalized.png"
    _write_png(source, alpha=True)
    source_before = source.read_bytes()

    report = prepare_true_alpha_png(source, destination)

    assert report.ready is True
    assert report.edge_review_required is True
    assert report.technical.ready is True
    assert destination.is_file()
    assert source.read_bytes() == source_before


def test_true_alpha_finalizer_refuses_opaque_rgb_source(tmp_path: Path) -> None:
    from stockforge.png_alpha_finalize import PngAlphaFinalizeError, prepare_true_alpha_png

    source = tmp_path / "opaque.jpg"
    Image.new("RGB", (2048, 2048), (255, 255, 255)).save(source, format="JPEG")

    with pytest.raises(PngAlphaFinalizeError, match="no real alpha"):
        prepare_true_alpha_png(source, tmp_path / "output.png")
