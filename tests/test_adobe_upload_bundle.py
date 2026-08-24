import csv
import json
from pathlib import Path
from uuid import uuid4

import pytest
from PIL import Image, ImageCms

from stockforge.adobe_upload_bundle import AdobeUploadBundleError, prepare_adobe_upload_bundle
from stockforge.artifact import Artifact
from stockforge.database import Database
from stockforge.execution_record import GenerationExecutionRecord


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
    return database, project_id, project_root, execution, artifact


def test_prepare_adobe_upload_bundle_creates_official_csv_and_manifest(tmp_path: Path):
    database, project_id, project_root, execution, artifact = _registered_master(tmp_path)

    bundle = prepare_adobe_upload_bundle(
        database=database,
        project_id=project_id,
        project_root=project_root,
        execution_ids=(execution.id,),
        approved_by_user=True,
    )

    with bundle.csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    manifest = json.loads(bundle.manifest_path.read_text(encoding="utf-8"))

    assert rows[0] == ["Filename", "Title", "Keywords", "Category", "Releases"]
    assert rows[1][0] == f"sf-{artifact.id[:8]}.jpg"
    assert rows[1][1] == _metadata()["title"]
    assert rows[1][3] == "8"
    assert (bundle.image_dir / rows[1][0]).is_file()
    assert manifest["status"] == "portal_upload_prepared_not_submitted"
    assert manifest["submission_requires_explicit_portal_confirmation"] is True
    assert manifest["files"][0]["generative_ai_declaration_required"] is True


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
