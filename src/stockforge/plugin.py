"""Vendor-neutral plugin contract for StockForge."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

PLUGIN_API_VERSION = "1"
PLUGIN_KINDS = frozenset({"generator", "processor", "analyzer", "exporter"})


class PluginError(ValueError):
    """Raised when a plugin violates the StockForge plugin contract."""


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    """Stable, serializable identity and capability information."""

    id: str
    name: str
    version: str
    kind: str
    api_version: str = PLUGIN_API_VERSION
    capabilities: frozenset[str] = field(default_factory=frozenset)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id or len(self.id) > 128:
            raise PluginError("Plugin id must be between 1 and 128 characters.")
        if not self.name or not self.version:
            raise PluginError("Plugin name and version must be non-empty.")
        if self.kind not in PLUGIN_KINDS:
            raise PluginError(f"Unsupported plugin kind: {self.kind}")
        if self.api_version != PLUGIN_API_VERSION:
            raise PluginError(
                f"Unsupported plugin API version: {self.api_version}. Expected {PLUGIN_API_VERSION}."
            )
        if any(not capability or len(capability) > 128 for capability in self.capabilities):
            raise PluginError("Plugin capabilities must be non-empty strings of at most 128 characters.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "kind": self.kind,
            "api_version": self.api_version,
            "capabilities": sorted(self.capabilities),
            "description": self.description,
        }


class StockForgePlugin(Protocol):
    """Runtime contract implemented by provider/processor plugins."""

    @property
    def descriptor(self) -> PluginDescriptor: ...

    def healthcheck(self) -> bool: ...

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class PluginRegistry:
    """In-process registry with deterministic lookup and capability filtering."""

    def __init__(self) -> None:
        self._plugins: dict[str, StockForgePlugin] = {}

    def register(self, plugin: StockForgePlugin) -> None:
        descriptor = plugin.descriptor
        if descriptor.id in self._plugins:
            raise PluginError(f"Plugin already registered: {descriptor.id}")
        self._plugins[descriptor.id] = plugin

    def unregister(self, plugin_id: str) -> StockForgePlugin:
        try:
            return self._plugins.pop(plugin_id)
        except KeyError as exc:
            raise PluginError(f"Plugin not registered: {plugin_id}") from exc

    def get(self, plugin_id: str) -> StockForgePlugin:
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise PluginError(f"Plugin not registered: {plugin_id}") from exc

    def list(self) -> tuple[PluginDescriptor, ...]:
        return tuple(self._plugins[key].descriptor for key in sorted(self._plugins))

    def find(self, *, kind: str | None = None, capability: str | None = None) -> tuple[StockForgePlugin, ...]:
        plugins = self._plugins.values()
        if kind is not None:
            if kind not in PLUGIN_KINDS:
                raise PluginError(f"Unsupported plugin kind: {kind}")
            plugins = (plugin for plugin in plugins if plugin.descriptor.kind == kind)
        if capability is not None:
            plugins = (plugin for plugin in plugins if capability in plugin.descriptor.capabilities)
        return tuple(sorted(plugins, key=lambda plugin: plugin.descriptor.id))

    def __len__(self) -> int:
        return len(self._plugins)
