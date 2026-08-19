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


def test_existing_execution_is_updated_atomically(tmp_path: Path) -> None:
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project("project-1", "Project", tmp_path)
    artifact = _artifact("project-1", "artifact-1", "artifacts/image.png", "c" * 64)
    execution = _execution("project-1", "old-artifact")
    database.create_execution(execution)
    final_execution = GenerationExecutionRecord.from_dict(
        {**execution.to_dict(), "artifact_ids": [artifact.id], "state": "succeeded"}
    )
    actual_artifacts, actual_execution = database.create_artifacts_and_execution((artifact,), final_execution)
    assert actual_artifacts == (artifact,)
    assert actual_execution.artifact_ids == (artifact.id,)
    persisted = database.get_execution(execution.id)
    assert persisted is not None
    assert persisted.artifact_ids == (artifact.id,)
    assert persisted.state == "succeeded"
    assert len(database.list_artifacts("project-1")) == 1


def test_transaction_rolls_back_artifacts_when_execution_update_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    database.create_project("project-1", "Project", tmp_path)
    execution = _execution("project-1", "old-artifact")
    database.create_execution(execution)
    artifact = _artifact("project-1", "artifact-2", "artifacts/image-2.png", "d" * 64)
    final_execution = GenerationExecutionRecord.from_dict(
        {**execution.to_dict(), "artifact_ids": [artifact.id]}
    )

    def fail_update(_: object, __: GenerationExecutionRecord) -> None:
        raise RuntimeError("simulated execution update failure")

    monkeypatch.setattr(Database, "_update_execution_connection", staticmethod(fail_update))
    with pytest.raises(RuntimeError, match="simulated execution update failure"):
        database.create_artifacts_and_execution((artifact,), final_execution)

    assert database.get_artifact(artifact.id) is None
    assert len(database.list_artifacts("project-1")) == 0
    persisted = database.get_execution(execution.id)
    assert persisted is not None
    assert persisted.artifact_ids == ("old-artifact",)
