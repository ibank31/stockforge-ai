from pathlib import Path

import pytest

from stockforge.artifact import Artifact, ArtifactError, sha256_file
from stockforge.provenance import ArtifactLineage, ProvenanceError, ProvenanceRecord


def test_artifact_from_file_is_fingerprinted(tmp_path: Path):
    root = tmp_path / "project"
    target = root / "assets" / "photo.txt"
    target.parent.mkdir(parents=True)
    target.write_text("hello", encoding="utf-8")

    artifact = Artifact.from_file("project-1", "assets/photo.txt", root, kind="image")

    assert artifact.project_id == "project-1"
    assert artifact.relative_path == "assets/photo.txt"
    assert artifact.size_bytes == 5
    assert artifact.sha256 == sha256_file(target)
    assert artifact.fingerprint() == artifact.sha256


def test_artifact_rejects_escape(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ArtifactError, match="inside the project root"):
        Artifact.from_file("project-1", "../outside.txt", root)


def test_artifact_round_trip():
    artifact = Artifact(
        id="a1", project_id="p1", kind="image", relative_path="assets/a.png",
        mime_type="image/png", size_bytes=10, sha256="abc", metadata={"role": "hero"}
    )
    restored = Artifact.from_dict(artifact.to_dict())
    assert restored == artifact


def test_provenance_records_generation_lineage():
    record = ProvenanceRecord.create(
        artifact_id="a1", project_id="p1", operation="generate", job_id="j1",
        pipeline_id="stock-photo-v1", pipeline_version=1, step_id="generate",
        plugin_id="generator.comfyui", plugin_version="0.1.0", model_id="model.example",
        model_version="1", workflow_hash="wf123", prompt_hash="prompt123",
        input_artifact_ids=("input-1",), parameters={"seed": 42},
    )
    restored = ProvenanceRecord.from_dict(record.to_dict())
    assert restored == record
    assert restored.input_artifact_ids == ("input-1",)


def test_provenance_rejects_unknown_fields():
    record = ProvenanceRecord.create("a1", "p1", "generate").to_dict()
    record["unexpected"] = True
    with pytest.raises(ProvenanceError, match="Invalid provenance fields"):
        ProvenanceRecord.from_dict(record)


def test_lineage_round_trip_and_relations():
    lineage = ArtifactLineage.create("child", "parent", "p1", relation="upscaled", execution_id="e1", sequence=2)
    assert ArtifactLineage(**lineage.to_dict()) == lineage


def test_lineage_rejects_self_parent_and_unknown_relation():
    with pytest.raises(ProvenanceError, match="own lineage parent"):
        ArtifactLineage.create("a1", "a1", "p1")
    with pytest.raises(ProvenanceError, match="Unsupported lineage relation"):
        ArtifactLineage.create("a2", "a1", "p1", relation="invented")
