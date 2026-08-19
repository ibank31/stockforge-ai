from pathlib import Path

from stockforge.artifact import Artifact
from stockforge.database import Database
from stockforge.provenance import ArtifactLineage, ProvenanceRecord


def _artifact(project_id: str, artifact_id: str, path: str, checksum: str) -> Artifact:
    return Artifact(id=artifact_id, project_id=project_id, kind="image", relative_path=path, mime_type="image/png", size_bytes=10, sha256=checksum)


def test_provenance_and_lineage_round_trip(tmp_path: Path):
    db = Database(tmp_path / "stockforge.db")
    db.initialize()
    db.create_project("p1", "Project", tmp_path / "project")

    parent = _artifact("p1", "a1", "assets/input.png", "sha-parent")
    child = _artifact("p1", "a2", "assets/output.png", "sha-child")
    db.create_artifact(parent)
    db.create_artifact(child)

    provenance = ProvenanceRecord.create(
        artifact_id=child.id,
        project_id="p1",
        operation="generate",
        execution_id="e1",
        job_id="j1",
        pipeline_id="stock-v1",
        pipeline_version=1,
        pipeline_hash="pipeline-hash",
        plugin_id="generator.comfyui",
        plugin_version="native-api-v1",
        model_id="model-x",
        model_version="1",
        workflow_hash="workflow-hash",
        prompt_hash="prompt-hash",
        input_artifact_ids=(parent.id,),
        parameters={"seed": 42},
        metadata={"license_policy": "review-required"},
    )
    lineage = ArtifactLineage.create(child.id, parent.id, "p1", relation="derived", execution_id="e1", sequence=0)

    assert db.create_provenance(provenance) == provenance
    assert db.create_lineage(lineage) == lineage
    assert db.get_provenance(provenance.id) == provenance
    assert db.list_provenance(child.id) == [provenance]
    assert db.list_lineage(child.id) == [lineage]
    assert db.list_lineage(parent_artifact_id=parent.id) == [lineage]


def test_lineage_rejects_self_parent():
    try:
        ArtifactLineage.create("a1", "a1", "p1")
    except ValueError as exc:
        assert "own lineage parent" in str(exc)
    else:
        raise AssertionError("self-parent lineage must be rejected")
