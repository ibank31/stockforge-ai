import json
import zipfile
from pathlib import Path
from uuid import uuid4

import pytest

from stockforge.artifact import Artifact
from stockforge.database import Database
from stockforge.execution_record import GenerationExecutionRecord
from stockforge.release_package import ReleasePackageError, build_release_package


def _successful_execution(database: Database, project_id: str, artifact_id: str) -> GenerationExecutionRecord:
    record = GenerationExecutionRecord.create(
        project_id,
        state="succeeded",
        operation="image.generate",
        provider_id="zerogpu",
        model_id="z-image-turbo",
        model_version="2025-11-27",
        artifact_ids=(artifact_id,),
        parameters={"profile": "z-image-turbo", "seed": 42},
    )
    database.create_execution(record)
    return record


def test_release_package_contains_only_images_and_manifest(tmp_path: Path):
    project_id = str(uuid4())
    project_root = tmp_path / "project"
    image_path = project_root / "artifacts" / "candidate.png"
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"png-bytes")
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project(project_id, "demo", project_root)
    artifact = Artifact.from_file(project_id, "artifacts/candidate.png", project_root, kind="generated-image")
    database.create_artifact(artifact)
    execution = _successful_execution(database, project_id, artifact.id)

    package = build_release_package(
        database=database,
        project_id=project_id,
        project_root=project_root,
        execution_id=execution.id,
    )

    assert package.path.is_file()
    assert package.status == "review_ready"
    with zipfile.ZipFile(package.path) as archive:
        assert sorted(archive.namelist()) == ["README.txt", "images/%s.png" % artifact.id, "manifest.json"]
        manifest = json.loads(archive.read("manifest.json"))
    assert manifest["status"] == "review_ready"
    assert manifest["artifacts"][0]["sha256"] == artifact.sha256


def test_release_package_rejects_unsuccessful_execution(tmp_path: Path):
    project_id = str(uuid4())
    project_root = tmp_path / "project"
    project_root.mkdir()
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project(project_id, "demo", project_root)
    execution = GenerationExecutionRecord.create(project_id, state="failed", operation="image.generate", error_code="failed", error_message="provider unavailable")
    database.create_execution(execution)

    with pytest.raises(ReleasePackageError, match="Only succeeded"):
        build_release_package(
            database=database,
            project_id=project_id,
            project_root=project_root,
            execution_id=execution.id,
        )
