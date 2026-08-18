# Core Foundation Contract

## Project identity

Every project has a stable UUID stored in both SQLite and `project.json`.

## Project manifest

`project.json` is the durable project manifest. It is versioned independently from the application version:

- `schema_version`: manifest schema version.
- `id`: immutable project UUID.
- `name`: validated project name.
- `version`: project content version.
- `created_at`: UTC creation timestamp in ISO 8601 format.
- `metadata`: extensible project metadata object.

The manifest is written atomically so a process interruption cannot leave a partially written JSON document.

## Storage boundary

SQLite stores queryable registry state. The project filesystem stores project files and generated assets. Future asset records must reference filesystem objects rather than embedding binary data in SQLite.

## Compatibility rule

Core services must remain vendor-neutral. AI providers, image generators, enhancement engines, QC tools, and marketplace integrations belong behind explicit adapters/plugins.
