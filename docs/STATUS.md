# Development Status

## Current milestone

**v0.1 Core Foundation → Asset Registry → Persistent Job Queue**

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

## Next

1. Plugin contract and registry
2. Pipeline definition/runner
3. Config command and provider configuration
4. ComfyUI adapter
