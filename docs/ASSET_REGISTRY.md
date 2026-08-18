# Asset Registry Contract

The asset registry is the durable identity layer between projects and future production pipelines.

## Required identity

Each asset has an immutable UUID, owning project UUID, human-readable name, controlled asset type, lifecycle status, optional project-relative file path, optional MIME type, optional byte size, optional SHA-256 checksum, source identifier, extensible JSON metadata, and audit timestamps.

## Storage rules

SQLite stores searchable asset records. Binary asset contents remain in the project filesystem.

A registered file must resolve inside its project root. Absolute paths and path traversal using `..` are rejected.

## Integrity rules

Asset names are unique within a project. Non-null relative paths are also unique within a project. Assets reference projects through a foreign key with cascade deletion.

SHA-256 is calculated in streaming chunks so large files do not need to be loaded into memory.

## Lifecycle

Initial controlled states:

`registered` → `processing` → `ready`

Operational terminal states:

- `failed`
- `archived`

The registry stores these states but does not yet implement workflow transitions. Those belong to the job/pipeline stage.
