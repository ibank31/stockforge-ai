# StockForge AI

## StockForge V2 Mission

**StockForge V2 is a Microstock Intelligence and Asset Generation System.**

Its purpose is not to copy, trace, or recreate an uploaded reference asset.

The system learns from a reference asset to identify its **commercial intent and market-relevant characteristics**, then creates a genuinely new creative direction with explicit similarity-risk controls.

### Core workflow

```text
MARKET-PROVEN REFERENCE ASSET
        ↓
UPLOAD TO STOCKFORGE V2
        ↓
REFERENCE INTELLIGENCE
(subject, category, commercial intent, composition,
visual style, color, buyer relevance)
        ↓
CREATIVE OPPORTUNITY ANALYSIS
        ↓
CREATIVE DISTANCE / ANTI-SIMILARITY
        ↓
NEW CONCEPT
        ↓
MODEL-SPECIFIC PROMPT
        ↓
AI GENERATION
        ↓
QUALITY + SIMILARITY GATES
        ↓
FINALIZATION
        ↓
REVIEW-READY ASSET
        ↓
HUMAN REVIEW → MARKETPLACE UPLOAD
```

### The fundamental rule

> **Preserve market intent. Change creative expression.**

A reference may help StockForge understand *why* an asset is commercially interesting. It must not become a template for producing a confusingly similar copy.

StockForge V2 should actively explore a new creative space through changes such as:

- subject or object selection
- composition and spatial arrangement
- camera angle or viewpoint
- color direction
- visual treatment
- context and use case
- buyer intent
- uniqueness levers

### Required intelligence layers

The V2 architecture should evolve toward these layers:

1. **Reference Intelligence** — extract structured, useful signals from uploaded reference images.
2. **Market Intelligence** — combine evidence about demand, supply, crowding, and opportunity.
3. **Creative Opportunity Engine** — identify viable directions instead of blindly reproducing references.
4. **Anti-Similarity Engine** — evaluate exact, perceptual, semantic, compositional, and conceptual similarity risk where technically available.
5. **Concept Engine** — turn intelligence into a distinct commercial concept.
6. **Model-Specific Prompt Engine** — translate the concept for the selected generation model/provider.
7. **Generation & Recovery** — preserve durable job identity, idempotency, and recovery guarantees.
8. **Quality & Release Gates** — reject clear technical failures and route uncertain decisions to human review.

### Non-goals

StockForge V2 must not be designed as:

- a competitor asset copier
- an image tracing system
- a prompt-only image generator with no intelligence layer
- an automatic marketplace uploader
- a system that auto-approves commercial originality

The system may generate and analyze automatically, but **final commercial judgment remains human-reviewed**.

## Agent and maintainer priority

Before extending a subsystem, agents must first verify that it is connected to the active production call graph.

A module that exists and passes unit tests is **not automatically an active V2 capability**.

When implementing V2, prefer this order:

1. Wire the intelligence layer into the real production path.
2. Add safety and validation at the actual ingestion boundary.
3. Add similarity controls before generation and after generation.
4. Preserve provenance and lineage across every transformation.
5. Keep job execution idempotent and recoverable.
6. Avoid creating isolated “smart” modules that are never called by production.

Historical or isolated code may be reused only after verifying that its assumptions match the V2 mission.

---

## Current production scope

StockForge currently operates as an Android-first digital-asset production automation platform with active PNG and JPEG output routes. V2 development expands the intelligence and reference-analysis architecture while preserving the existing production reliability boundaries.

### Active output routes

| Route | Intended use | Final technical contract |
|---|---|---|
| **PNG** | Isolated objects, cutouts, stickers, overlays, and transparent utility assets | RGBA/true alpha, sRGB, isolated BiRefNet finalizer, technical alpha gate, and 100% visual edge review |
| **JPEG** | Self-contained scenes, environments, hero compositions, illustrations with backgrounds, and copy-space visuals | RGB/sRGB, active resolution gate, protected RealESRGAN finalizer, and full-resolution visual review |

StockForge does not automatically submit assets to Adobe or another marketplace.

## Start here

Agents and maintainers must read these files in order:

1. `README.md` — V2 mission, goals, and production direction.
2. [`AGENTS.md`](AGENTS.md) — repository-wide operating rules.
3. [`docs/ACTIVE_SCOPE.md`](docs/ACTIVE_SCOPE.md) — current production contract.
4. [`docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](docs/GPT_TO_TERMUX_CANONICAL_WORKFLOW.md) — active operational workflow.
5. [`docs/STATUS.md`](docs/STATUS.md) — implementation snapshot and limitations.

Historical material is under [`docs/archive/`](docs/archive/) and must not be treated as active instructions without explicit verification.

## Development

Install the package and development dependencies, then run the test suite from the repository root:

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest -q
```

When changing an active production flow, update the relevant scope and status documentation in the same commit. Documentation drift is how repositories become archaeological sites with CI.