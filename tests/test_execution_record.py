from pathlib import Path
from uuid import uuid4

import pytest

from stockforge.database import Database
from stockforge.execution_record import ExecutionRecordError, GenerationExecutionRecord


def test_prompt_is_hashed_without_storing_prompt() -> None:
    record = GenerationExecutionRecord.create("project-1", prompt="a commercial stock photo")
    assert record.prompt_hash
    assert "commercial stock photo" not in record.json()


def test_succeeded_requires_artifact() -> None:
    with pytest.raises(ExecutionRecordError):
        GenerationExecutionRecord.create("project-1", state="succeeded")


def test_failed_requires_structured_error() -> None:
    with pytest.raises(ExecutionRecordError):
        GenerationExecutionRecord.create("project-1", state="failed")


def test_database_round_trip(tmp_path: Path) -> None:
    database = Database(tmp_path / "stockforge.db")
    database.initialize()
    project_id = str(uuid4())
    database.create_project(project_id, "demo", tmp_path / "project")
    record = GenerationExecutionRecord.create(
        project_id,
        state="succeeded",
        provider_id="comfyui.local",
        provider_job_id="prompt-123",
        artifact_ids=("artifact-1",),
        parameters={"seed": 123},
    )

    database.create_execution(record)
    restored = database.get_execution(record.id)

    assert restored is not None
    assert restored.to_dict() == record.to_dict()
