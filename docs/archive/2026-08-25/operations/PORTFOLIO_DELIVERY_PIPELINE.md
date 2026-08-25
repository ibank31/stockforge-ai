# Portfolio Delivery Pipeline

**Status:** Approved implementation plan for the active standalone portfolio path.
**Scope:** Connect an approved portfolio brief to one remote generation, immutable execution provenance, deterministic technical checks, draft marketplace metadata, and a human-review package.
**Non-goal:** Automatic marketplace submission or a claim that an image is legally accepted, commercially successful, or technically accepted by a marketplace.

## Current Gap

The portfolio planner creates safe, research-aligned brief cards and saves them in `portfolio-plans/*.json`. The existing `generate` command persists one generation and returns a `review_ready` ZIP, but it currently has no durable pointer back to the selected lane/brief and the package has no asset-specific metadata/checklist.

The implementation closes that gap with a **one-brief, one-execution** contract. It deliberately does not add parallel batch generation because the user’s remote free-worker quota and prior provider behavior require visible, recoverable, one-at-a-time execution.

## Active Lifecycle

```text
Portfolio plan (planned)
  -> selected brief (brief_id)
  -> explicit one-brief generation request
  -> immutable execution parameters include portfolio snapshot
  -> artifact ingestion and execution provenance
  -> technical/readiness inspection
  -> review package: image + manifest + metadata draft + checklist
  -> human review required
  -> optional manual finalization / metadata verification
  -> human may record submission_ready; machine never self-promotes
```

| State | What it means | Who can set it |
|---|---|---|
| `planned` | A deterministic brief exists; no provider call. | Portfolio planner |
| `generating` | A one-brief remote execution has been claimed. | Existing job orchestrator |
| `review_ready` | Image is persisted with portfolio lineage and review files. | Machine, after successful generation only |
| `human_review_required` | Metadata, rights, visible content, unique value, and policy must be reviewed. | Machine declaration; human action pending |
| `submission_ready` | A human has completed review records and technical finalization. | Human only |
| `rejected` | Failure is documented; it must not be submitted. | Machine or human |

## Linkage Contract

The selected brief is frozen into `GenerationRequest.parameters["portfolio"]`; the request includes only serializable data:

```json
{
  "batch_id": "...",
  "brief_id": "ai_governance--review-gate",
  "lane_key": "ai_governance",
  "tier": "first",
  "metadata": {"title": "...", "keywords": ["..."], "created_using_generative_ai": true},
  "reviewer_checklist": ["..."],
  "human_review_required": true
}
```

This protects reproducibility: the final ZIP preserves the metadata draft and policy context that existed when the image was requested, even if the batch plan is edited later.

## CLI Contract

```bash
# No remote call: inspect a saved brief.
python -m stockforge.cli portfolio show \
  --project stock-assets \
  --plan /storage/emulated/0/StockForge/projects/stock-assets/portfolio-plans/<batch>.json \
  --brief ai_governance--review-gate

# Exactly one remote request, selected explicitly from a saved plan.
python -m stockforge.cli portfolio generate \
  --project stock-assets \
  --plan /storage/emulated/0/StockForge/projects/stock-assets/portfolio-plans/<batch>.json \
  --brief ai_governance--review-gate \
  --provider zerogpu \
  --profile z-image-turbo \
  --seed 42

# Preview the exact one-brief remote request without spending GPU quota.
python -m stockforge.cli portfolio generate \
  --project stock-assets \
  --plan /storage/emulated/0/StockForge/projects/stock-assets/portfolio-plans/<batch>.json \
  --brief ai_governance--review-gate \
  --provider zerogpu \
  --profile z-image-turbo \
  --seed 42 \
  --dry-run
```

The source batch plan must be inside that project’s `portfolio-plans/` directory. This prevents accidental use of an unrelated or manually forged file path. `portfolio generate` rejects absent/mismatched project, malformed plans, unsupported status, duplicate brief IDs, or a brief that lacks mandatory AI-disclosure/human-review metadata.

## Review Package Contract

The existing image archive is enriched only when the execution has portfolio linkage. It contains:

| File | Purpose |
|---|---|
| `images/<artifact-id>.<ext>` | Original provider output preserved by artifact ingestion. |
| `manifest.json` | Execution, artifact hashes, status, and immutable portfolio snapshot. |
| `portfolio_metadata_draft.json` | Draft title/keywords/AI declaration; never an acceptance claim. |
| `portfolio_metadata_draft.csv` | Human-editable generic metadata worksheet, not a marketplace upload template. |
| `TECHNICAL_READINESS.json` | Output gate teknis deterministik per image; dapat berstatus pass, review, atau fail dan bukan keputusan moderation. |
| `REVIEW_CHECKLIST.md` | Technical, visible-content, rights, uniqueness, dan metadata checks. |
| `README.txt` | Explicit explanation that the package is review-ready, not submission/acceptance-ready. |

The package does not include logs, worker staging files, tokens, credentials, or raw provider responses.

## Deterministic Gates

The machine runs existing technical image inspection for each portfolio artifact before packaging. Its output is saved as `TECHNICAL_READINESS.json` with `PASS`, `REVIEW`, or `FAIL` checks, but it cannot replace visual or rights review. The report is particularly expected to mark many raw provider outputs for review or failure until they are explicitly finalized to the marketplace file policy.

Before a final contributor upload, the reviewer must verify: no textual artifacts, no logos/brands/IP, accurate description/keywords, truthful GenAI declaration, visual geometry/material quality, distinctness within portfolio, required releases/people/property fields, policy compliance, and final technical state.

## Documentation boundary

The standalone portfolio path uses the active contracts in `docs/STATUS.md`, `docs/ARCHITECTURE.md`, `docs/FEATURE_ROADMAP.md`, and `docs/TERMUX_CONTROL_PLANE.md`. Obsolete Reality-layer implementation notes are no longer part of the active documentation set. Historical implementation details belong in `docs/CHANGELOG.md`, not in the operator workflow.

## Definition of Done

The pipeline is done when a saved portfolio brief can be previewed and generated one at a time; the execution is stamped with the frozen brief; the resulting archive includes safe metadata/review material; malformed or cross-project plans are rejected; raw direct `generate` behavior remains compatible; legacy Reality code/docs have no remaining active references; and the complete test suite passes.
