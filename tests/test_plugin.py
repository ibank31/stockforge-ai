from dataclasses import dataclass

import pytest

from stockforge.plugin import PluginDescriptor, PluginError, PluginRegistry


@dataclass
class DemoPlugin:
    descriptor: PluginDescriptor

    def healthcheck(self) -> bool:
        return True

    def execute(self, payload: dict) -> dict:
        return {"ok": True, "payload": payload}


def plugin(plugin_id: str, kind: str = "generator", capabilities: frozenset[str] = frozenset()) -> DemoPlugin:
    return DemoPlugin(
        PluginDescriptor(
            id=plugin_id,
            name=plugin_id,
            version="1.0.0",
            kind=kind,
            capabilities=capabilities,
        )
    )


def test_descriptor_serializes_stably():
    descriptor = PluginDescriptor(
        id="image.comfyui",
        name="ComfyUI",
        version="1.2.3",
        kind="generator",
        capabilities=frozenset({"text-to-image", "image-to-image"}),
    )
    assert descriptor.to_dict()["capabilities"] == ["image-to-image", "text-to-image"]


def test_registry_register_get_and_list():
    registry = PluginRegistry()
    first = plugin("z.plugin")
    second = plugin("a.plugin", kind="processor")
    registry.register(first)
    registry.register(second)

    assert len(registry) == 2
    assert registry.get("z.plugin") is first
    assert [item.id for item in registry.list()] == ["a.plugin", "z.plugin"]


def test_registry_rejects_duplicate_ids():
    registry = PluginRegistry()
    registry.register(plugin("demo"))
    with pytest.raises(PluginError, match="already registered"):
        registry.register(plugin("demo"))


def test_registry_filters_by_kind_and_capability():
    registry = PluginRegistry()
    registry.register(plugin("generator.a", capabilities=frozenset({"text-to-image"})))
    registry.register(plugin("generator.b", capabilities=frozenset({"image-to-image"})))
    registry.register(plugin("processor.a", kind="processor", capabilities=frozenset({"upscale"})))

    assert [p.descriptor.id for p in registry.find(kind="generator")] == ["generator.a", "generator.b"]
    assert [p.descriptor.id for p in registry.find(capability="upscale")] == ["processor.a"]
    assert [p.descriptor.id for p in registry.find(kind="generator", capability="image-to-image")] == ["generator.b"]


def test_registry_unknown_plugin_and_kind_fail():
    registry = PluginRegistry()
    with pytest.raises(PluginError, match="not registered"):
        registry.get("missing")
    with pytest.raises(PluginError, match="Unsupported plugin kind"):
        registry.find(kind="unknown")


def test_descriptor_rejects_unknown_api_version():
    with pytest.raises(PluginError, match="Unsupported plugin API version"):
        PluginDescriptor("demo", "Demo", "1.0.0", "generator", api_version="999")
