# Plugin Contract

StockForge core is vendor-neutral. Providers and processing engines are plugins, not core dependencies.

## Plugin kinds

- `generator`: creates or transforms primary assets from structured input.
- `processor`: performs deterministic media operations such as resizing or encoding.
- `analyzer`: evaluates assets and returns quality or policy signals.
- `exporter`: converts approved assets into marketplace-specific submission packages.

## Identity

Each plugin exposes a stable `id`, human-readable name, semantic version, plugin `kind`, and StockForge `api_version`.

The plugin API version is separate from the application version. A provider must explicitly declare the API version it implements so incompatible contracts fail early instead of failing halfway through a production batch.

## Capabilities

Capabilities are explicit strings such as:

- `text-to-image`
- `image-to-image`
- `upscale`
- `ocr`
- `aesthetic-score`
- `metadata-export`

Core orchestration can select a plugin by kind and capability without knowing the provider implementation.

## Runtime contract

A plugin implements:

1. `descriptor` — immutable identity/capability metadata.
2. `healthcheck()` — cheap readiness check with no asset generation.
3. `execute(payload)` — vendor-neutral JSON input and JSON result.

Binary assets are referenced through the existing Asset Registry rather than embedded in job payloads.

## Security boundary

Plugin payloads must never contain API keys or other credentials. Secrets belong to provider configuration managed outside jobs. Plugins must validate external input and must not write outside the project workspace.

## Future discovery

The initial implementation uses explicit in-process registration. Package entry-point discovery can be added later, but discovery must remain opt-in and version-checked. Automatic import of arbitrary installed packages is intentionally not part of the core trust boundary.
