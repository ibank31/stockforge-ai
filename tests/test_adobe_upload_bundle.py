import json
from pathlib import Path
from uuid import uuid4

import pytest
from PIL import Image, ImageCms

from stockforge.adobe_upload_bundle import AdobeUploadBundleError, latest_finalized_master_execution_id, prepare_adobe_upload_bundle
from stockforge.artifact import Artifact
from stockforge.database import Database
from stockforge.execution_record import GenerationExecutionRecord
from stockforge.provenance import ProvenanceRecord


def _srgb() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def _metadata() -> dict[str, object]:
    return {
        "title": "Recycled Fiber Paper Arch with Sage Green Inner Layer",
        "keywords": [
            "recycled paper", "paper arch", "fiber texture", "sage green",
            "tactile material", "abstract paper sculpture", "copy space", "website hero background",
        ],
        "created_using_generative_ai": True,
        "people_or_property": "none depicted; human review required to confirm",
        "status": "human_review_required",
        "human_review_required": True,
        "marketplace_transaction_data": "DATA NOT PUBLICLY AVAILABLE",
        "reviewer_checklist": ["Confirm the master is free of visual and rights issues."],
    }


def _registered_master(tmp_path: Path):
    project_id = str(uuid4())
    project_root = tmp_path / "project"
    source = project_root / "masters" / "master.jpg"
    source.parent.mkdir(parents=True)
    Image.new("RGB", (2048, 2048), (220, 220, 220)).save(
        source, format="JPEG", quality=95, icc_profile=_srgb(), subsampling=0
    )
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project(project_id, "demo", project_root)
    artifact = Artifact.from_file(project_id, "masters/master.jpg", project_root, kind="finalized-master")
    database.create_artifact(artifact)
    execution = GenerationExecutionRecord.create(
        project_id,
        state="succeeded",
        operation="image.finalize_master",
        artifact_ids=(artifact.id,),
        parameters={
            "portfolio": {
                "lane_key": "tactile_material_atmospheres",
                "metadata": _metadata(),
            }
        },
    )
    database.create_execution(execution)
    database.create_provenance(ProvenanceRecord.create(
        artifact.id,
        project_id,
        "image.upscale_and_finalize",
        execution_id=execution.id,
    ))
    return database, project_id, project_root, execution, artifact


def test_prepare_adobe_upload_bundle_creates_official_csv_and_manifest(tmp_path: Path):
    database, project_id, project_root, execution, artifact = _registered_master(tmp_path)

    bundle = prepare_adobe_upload_bundle(
        database=database,
        project_id=project_id,
        project_root=project_root,
        execution_ids=(execution.id,),
        approved_by_user=True,
        destination_root=tmp_path / "Download" / "AdobeStock" / "READY_TO_UPLOAD",
    )

    manifest = json.loads(bundle.manifest_path.read_text(encoding="utf-8"))

    filename = f"sf-{artifact.id[:8]}.jpg"
    asset_dir = bundle.asset_dirs[0]
    upload_jpeg = asset_dir / filename
    assert upload_jpeg.is_file()
    upload_bytes = upload_jpeg.read_bytes()
    assert _metadata()["title"].encode("utf-8") in upload_bytes
    assert b"recycled paper" in upload_bytes
    assert bundle.path.parents[1].name == "AdobeStock"
    assert bundle.metadata_path == asset_dir / "UPLOAD_METADATA.txt"
    assert sorted(item.name for item in asset_dir.iterdir()) == [
        "UPLOAD_METADATA.txt", filename
    ]
    assert sorted(item.name for item in bundle.path.iterdir()) == [
        "BATCH_MANIFEST.json", "README.txt", f"asset-{artifact.id[:8]}"
    ]
    assert manifest["status"] == "manual_portal_upload_prepared_not_submitted"
    assert manifest["folder_contract"].startswith("Each asset folder contains one JPEG")
    assert manifest["submission_requires_explicit_portal_confirmation"] is True
    assert manifest["files"][0]["generative_ai_declaration_required"] is True


def test_latest_finalized_master_execution_uses_registered_provenance(tmp_path: Path):
    database, project_id, _project_root, execution, _artifact = _registered_master(tmp_path)

    assert latest_finalized_master_execution_id(database=database, project_id=project_id) == execution.id


def test_prepare_adobe_upload_bundle_requires_explicit_review_approval(tmp_path: Path):
    database, project_id, project_root, execution, _artifact = _registered_master(tmp_path)

    with pytest.raises(AdobeUploadBundleError, match="explicit user approval"):
        prepare_adobe_upload_bundle(
            database=database,
            project_id=project_id,
            project_root=project_root,
            execution_ids=(execution.id,),
            approved_by_user=False,
        )
