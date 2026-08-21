from pathlib import Path

import pytest

from stockforge.model_registry import ModelRegistry, ModelRegistryError


REGISTRY = Path(__file__).parents[1] / "models" / "registry.json"


def test_production_registry_loads() -> None:
    registry = ModelRegistry.from_json(REGISTRY)
    model = registry.get("sdxl-lightning")
    assert model.artifact.storage == "huggingface"
    assert model.artifact.repository == "ByteDance/SDXL-Lightning"
    assert "hf_zerogpu" in model.providers
    assert model.requirements.vram_min_bytes == 8 * 1024**3
    assert model.requirements.ram_min_bytes == 16 * 1024**3


def test_registry_rejects_non_huggingface_weight_storage() -> None:
    with pytest.raises(ModelRegistryError):
        ModelRegistry.from_dict(
            {
                "schema_version": 1,
                "models": [
                    {
                        "id": "bad",
                        "version": "1",
                        "kind": "image-generation",
                        "commercial_use": True,
                        "capabilities": ["stock-photo"],
                        "requirements": {"vram_min_bytes": 1, "ram_min_bytes": 1},
                        "artifact": {
                            "repository": "bad/model",
                            "revision": "main",
                            "storage": "local-worker-disk",
                        },
                        "providers": ["hf_zerogpu"],
                    }
                ],
            }
        )


def test_registry_filters_by_resources_and_capability() -> None:
    registry = ModelRegistry.from_json(REGISTRY)
    eligible = registry.eligible(
        capability="stock-photo",
        vram_bytes=16 * 1024**3,
        ram_bytes=32 * 1024**3,
        free_disk_bytes=20 * 1024**3,
    )
    assert [model.id for model in eligible] == ["sdxl-lightning"]

    assert registry.eligible(
        capability="stock-photo",
        vram_bytes=4 * 1024**3,
        ram_bytes=32 * 1024**3,
        free_disk_bytes=20 * 1024**3,
    ) == ()
