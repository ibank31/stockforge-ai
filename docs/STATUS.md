# Development Status

## Current milestone

**v0.1 Core Foundation → Asset Registry → Persistent Job Queue → Plugin Contract → Pipeline Engine → Artifact/Provenance**

## Completed

- CLI entry point
- `stockforge version`
- `stockforge init`
- `stockforge doctor`
- SQLite initialization
- Project creation and listing
- Project workspace layout
- Versioned project manifest
- Atomic manifest writes
- Project creation rollback handling
- Initial pytest coverage
- GitHub Actions CI
- Persistent asset registry
- Asset UUID and project ownership
- Asset lifecycle status contract
- File path validation and SHA-256 checksum support
- Asset CLI create/list commands
- Persistent job model
- Durable SQLite-backed job queue
- Priority ordering
- Atomic worker claiming
- Attempt counting and bounded retries
- Job completion, failure, and cancellation
- Job CLI create/list/claim/complete/fail/cancel commands
- Vendor-neutral plugin descriptor and API contract
- Plugin registry with deterministic lookup
- Capability-based plugin discovery
- Plugin API version validation
- Plugin trust-boundary documentation
- Versioned pipeline definition
- Deterministic sequential pipeline runner
- Pipeline capability validation
- Pipeline execution error boundary
- Pipeline contract documentation
- Versioned provenance record contract
- Explicit artifact lineage contract
- Durable SQLite provenance records
- Durable SQLite artifact lineage records
- Provenance/lineage round-trip and validation tests

## Next

1. Provider configuration and secret handling
2. ComfyUI generator adapter hardening/live integration
3. Image QA pipeline integration
4. Enhancement/upscaling pipeline
5. Stock metadata and marketplace export
