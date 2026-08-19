from pathlib import Path

import pytest

from stockforge.artifact import Artifact
from stockforge.database import Database
from stockforge.execution_record import GenerationExecutionRecord


def _artifact(project_id: str, artifact_id: str, path: str, sha: str) -> Artifact:
    return Artifact(
        id=artifact_id,
        project_id=project_id,
        kind="generated-image",
        relative_path=path,
        mime_type="image/png",
        size_bytes=123,
        sha256=sha,
    )


def _execution(project_id: str, artifact_id: str) -> GenerationExecutionRecord:
    return GenerationExecutionRecord.create(
        project_id,
        prompt="test prompt",
        state="succeeded",
        provider_id="test-provider",
        provider_job_id="job-1",
        model_id="test-model",
        artifact_ids=(artifact_id,),
    )


def test_atomic_registration_persists_artifact_and_execution(tmp_path: Path) -> None:
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project("project-1", "Project", tmp_path)

    artifact = _artifact("project-1", "artifact-1", "artifacts/image.png", "a" * 64)
    execution = _execution("project-1", artifact.id)

    actual_artifacts, actual_execution = database.create_artifacts_and_execution((artifact,), execution)

    assert actual_artifacts == (artifact,)
    assert actual_execution.artifact_ids == (artifact.id,)
    assert database.get_artifact(artifact.id) is not None
    assert database.get_execution(execution.id) is not None


def test_exact_duplicate_reuses_existing_artifact_and_keeps_single_row(tmp_path: Path) -> None:
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project("project-1", "Project", tmp_path)

    original = _artifact("project-1", "artifact-original", "artifacts/original.png", "b" * 64)
    database.create_artifact(original)

    regenerated = _artifact("project-1", "artifact-new", "artifacts/regenerated.png", "b" * 64)
    execution = _execution("project-1", regenerated.id)

    actual_artifacts, actual_execution = database.create_artifacts_and_execution((regenerated,), execution)

    assert actual_artifacts[0].id == original.id
    assert actual_execution.artifact_ids == (original.id,)
    assert len(database.list_artifacts("project-1")) == 1
    assert database.get_execution(execution.id) is not None


def test_transaction_rolls_back_artifacts_when_execution_insert_fails(tmp_path: Path) -> None:
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project("project-1", "Project", tmp_path)

    artifact = _artifact("project-1", "artifact-1", "artifacts/image.png", "c" * 64)
    execution = _execution("project-1", artifact.id)
    database.create_execution(execution)

    second_artifact = _artifact("project-1", "artifact-2", "artifacts/image-2.png", "d" * 64)
    conflicting_execution = GenerationExecutionRecord.from_dict(
        {**execution.to_dict(), "artifact_ids": [second_artifact.id]}
    )

    with pytest.raises(Exception):
        database.create_artifacts_and_execution((second_artifact,), conflicting_execution)

    assert database.get_artifact(second_artifact.id) is None
    assert len(database.list_artifacts("project-1")) == 0
