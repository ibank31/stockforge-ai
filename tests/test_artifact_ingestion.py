from pathlib import Path

import pytest

from stockforge.artifact_ingestion import ArtifactIngestionError, ArtifactIngestor, ProviderOutputRef


def test_ingest_copies_output_and_records_checksum(tmp_path: Path) -> None:
    project = tmp_path / "project"
    provider = tmp_path / "comfyui"
    project.mkdir()
    (provider / "subfolder").mkdir(parents=True)
    source = provider / "subfolder" / "image.png"
    source.write_bytes(b"stockforge-test-image")

    artifact = ArtifactIngestor(project).ingest(
        project_id="project-1",
        provider_root=provider,
        ref=ProviderOutputRef(filename="image.png", subfolder="subfolder", node_id="9"),
        metadata={"provider": "comfyui", "node_id": "9"},
    )

    destination = project / artifact.relative_path
    assert destination.is_file()
    assert destination.read_bytes() == source.read_bytes()
    assert artifact.sha256
    assert artifact.size_bytes == len(b"stockforge-test-image")
    assert artifact.metadata["provider"] == "comfyui"


def test_ingest_rejects_filename_traversal(tmp_path: Path) -> None:
    project = tmp_path / "project"
    provider = tmp_path / "provider"
    project.mkdir()
    provider.mkdir()
    (provider / "image.png").write_bytes(b"x")

    with pytest.raises(ArtifactIngestionError):
        ArtifactIngestor(project).resolve_source(provider, ProviderOutputRef(filename="../image.png"))


def test_ingest_rejects_subfolder_escape(tmp_path: Path) -> None:
    project = tmp_path / "project"
    provider = tmp_path / "provider"
    outside = tmp_path / "outside"
    project.mkdir()
    provider.mkdir()
    outside.mkdir()
    (outside / "image.png").write_bytes(b"x")

    with pytest.raises(ArtifactIngestionError):
        ArtifactIngestor(project).resolve_source(provider, ProviderOutputRef(filename="image.png", subfolder="../outside"))
