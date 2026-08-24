# Portfolio Production Engine

**Status:** Implementation specification for the StockForge portfolio engine.  
**Scope:** Build repeatable, research-aligned, standalone asset batches for the ten prioritised lanes.  
**Boundary:** `submission_ready` means all available machine checks and required human-review records are present. It is **not** a marketplace acceptance, sales, rights, or legal guarantee.

## Objective

StockForge currently accepts one prompt from Termux, asks one remote worker to generate one image, persists the artifact, and delivers a `review_ready` ZIP. The portfolio engine adds a deterministic planning layer before that existing generation path. It turns an approved lane into a small, auditable set of materially distinct asset briefs; attaches accurate draft metadata and policy declarations; and records which assets still need visual, rights, and marketplace review.

The engine is intentionally **not** an automatic marketplace uploader. It should never claim acceptance, invent commercial evidence, use artist names or brands, fabricate legal/compliance statements, or mark a generated asset safe merely because its generation succeeded.

## Design Principles

| Principle | Implementation consequence |
|---|---|
| Buyer job precedes prompt | Every brief names a buyer segment, a communication job, a use case, and a channel. |
| One niche is a controlled hypothesis | A lane is seeded from the 2026 research shortlist and has an evidence-confidence label, test size, and scaling status. |
| Useful variation, not prompt spam | A batch varies concept mechanism, subject silhouette, material, composition, and copy-space direction. Seed-only or color-only siblings are not distinct concepts. |
| Standalone-first remains default | The remote free-worker path continues to use a no-text, no-brand, no-people, no-screen, isolated white-background policy unless an explicitly approved future lane changes it. |
| Machine checks are necessary but insufficient | Technical checks, metadata checks, and dedupe checks move an asset to `human_review_required`; a person remains accountable for rights, accuracy, and marketplace submission. |
| No hidden “high demand” claims | Niche rank and confidence are internal planning data; public marketplace transactions are recorded as `DATA NOT PUBLICLY AVAILABLE`. |

## Supported 2026 Lanes

The initial registry implements the evidence-selected top ten as **named portfolio lanes**. The first three have a production allocation; the remainder are held for smaller, test-first batches.

| Lane key | Commercial visual job | Initial tier | Target test size | Default family |
|---|---|---|---:|---|
| `ai_governance` | Explain accountability, review, traceability, and controlled release | First | 20 | `ui_3d_metaphor` |
| `playful_surreal_product_metaphors` | Create a memorable single-object benefit metaphor with copy space | First | 20 | `surreal_concept` |
| `tactile_material_atmospheres` | Supply functional tactile hero/background systems | First | 20 | `material_atmosphere` |
| `synthetic_media_trust` | Explain provenance, verification, and media literacy | Secondary | 15 | `ui_3d_metaphor` |
| `returns_recommerce` | Explain return, recovery, refurbishment, and resale loops | Secondary | 15 | `ui_3d_metaphor` |
| `digital_accessibility` | Communicate adaptable input, clarity, and participation | Secondary | 15 | `ui_3d_metaphor` |
| `retro_tech_developer_metaphors` | Support developer/editorial concepts without brands or screens | Experimental | 15 | `retro_tech_nostalgia` |
| `human_made_collage_elements` | Provide coherent reusable editorial craft components | Experimental | 10 | `craft_element` |
| `circular_packaging_systems` | Explain refill, return, and material-flow systems | Experimental | 10 | `ui_3d_metaphor` |
| `software_supply_chain_integrity` | Explain dependencies, build integrity, and maintenance | Experimental | 10 | `ui_3d_metaphor` |

A lane can be expanded only when its own generated assets pass technical and distinctness review, contributor review feedback is recorded, and future account-level evidence supports continued allocation. Public category sales remain unavailable.

## Domain Model

```text
PortfolioLane
  -> LaneConcept (materially distinct buyer/use-case answer)
  -> AssetSpec (provider-neutral asset contract)
  -> PromptPackage (positive prompt, negative prompt, QA/legal constraints)
  -> PortfolioAssetManifest (metadata draft, AI disclosure, human-review checklist)
  -> existing Termux `generate` request
  -> generated artifact + provenance
  -> technical QA / dedupe / metadata QA
  -> review package
```

### `PortfolioLane`

A lane has: tier, confidence, research opportunity key, buyer segment, buyer job, asset family/type, test limit, initial status, a set of concept cards, and a keyword map. It has no sales or demand number.

### `LaneConcept`

A concept is one distinct commercial visual answer. It holds a primary subject, visual mechanism, material/medium, composition, copy-space placement, palette, commercial uses, and originality levers. An asset generated from a concept may be rejected; this does not make a different concept redundant.

### `PortfolioAssetManifest`

The manifest has a deterministic draft title, accurate keyword candidates, AI disclosure flag, release/review declarations, provenance links, policy constraints, and an explicit `human_review_required` state. A metadata draft is not a claim that the asset may be submitted.

## Batch Lifecycle

| Status | Meaning | Transition owner |
|---|---|---|
| `planned` | Brief exists but has not been generated. | Portfolio planner |
| `generated` | Provider returned an image and provenance is stored. | Existing generation pipeline |
| `technical_review` | Candidate needs format/image/visual/dedupe checks. | Deterministic QA |
| `human_review_required` | Machine gates passed or require a reviewer decision; rights/accuracy remain open. | Human contributor |
| `submission_ready` | Human review fields completed and required checks passed. | Human contributor only |
| `rejected` | Technical, policy, quality, or uniqueness failure is recorded. | QA or human contributor |

The current `review_ready` delivery ZIP remains compatible. New portfolio metadata is added alongside images; it does not silently change an artifact to `submission_ready`.

## Quality Gates

| Gate | Decision rule | Machine role | Human role |
|---|---|---|---|
| Brief validity | Supported lane, non-empty buyer use, positive originality levers | Block invalid plans | Confirm commercial relevance |
| Prompt policy | No text/brands/people/screens in default standalone lanes | Build constraints and flag banned phrases | Reject ambiguous prompt intent |
| Technical image integrity | Existing Adobe technical check/finalization | Pass/review/fail | Decide if review case is acceptable |
| Visual defect / quality | Existing visual QA modules | Flag likely defects | Inspect at full size |
| Distinctness | Existing perceptual-hash pipeline | Group likely siblings | Select only best conceptually distinct asset |
| Metadata safety | Title/keywords are accurate, no banned terms, AI disclosure present | Block unsafe draft metadata | Verify all terms appear in image |
| Rights/compliance | No automatic legal conclusion | Record open checklist | Complete accountability declaration |

## Termux Commands

The active implementation preserves the existing single-image `generate` command and adds a `portfolio` command group for saved, lineage-aware production briefs.

```bash
# Show supported lane names, tiers, and safe batch caps.
python -m stockforge.cli portfolio lanes

# Preview generation-ready brief cards; no remote GPU call.
python -m stockforge.cli portfolio plan \
  --lane ai_governance \
  --count 5

# Write a reusable batch plan to the selected project.
python -m stockforge.cli portfolio create-batch \
  --project stock-assets \
  --lane tactile_material_atmospheres \
  --count 5

# View planned assets and their metadata/review state.
python -m stockforge.cli portfolio list \
  --project stock-assets \
  --status planned
```

Generation remains intentionally explicit and one-at-a-time: use `portfolio show` to inspect a saved brief and `portfolio generate` to submit exactly one selected brief. The command freezes its batch/brief/metadata context into the execution and includes the metadata draft plus review checklist in the download package. A future bounded batch runner may sequence already approved briefs, but it must not submit parallel or unlimited provider calls.

## Phased Implementation

| Phase | Deliverable | Not included |
|---|---|---|
| 1: Portfolio foundation | Lane registry, deterministic concepts, safe metadata manifest, validation tests, CLI preview/create/list. **Complete.** | Remote batch submission. |
| 2: Artifact linkage | `portfolio show`/`portfolio generate`, frozen brief snapshot, and richer review package. **Complete.** | Automatic marketplace upload. |
| 3: Portfolio QA dashboard/CLI | Aggregate technical, dedupe, and metadata status; manual review recording. | Automated legal acceptance claims. |
| 4: Bounded batch orchestration | One-at-a-time quota-aware sequence with stop-on-failure behavior. | Background worker or unlimited execution. |
| 5: Account-feedback learning | Import contributor acceptance/download evidence supplied by the user; revise allocation transparently. | Publicly invented sales data. |

## Safety and Operations

Use the existing remote-worker quota policy: one candidate per request, bounded image size/steps, explicit provider selection, and a downloadable review package. No persistent server, webhook, or background scheduler is required for the active phases; Termux remains the user-controlled trigger. The remote Space cleanup remains outside this scope until expressly re-requested.

## Definition of Done for Active Phases

The active foundation and delivery linkage are complete when: all ten lanes are discoverable; lane plans produce distinct `AssetSpec` and `PromptPackage` objects; batch caps follow the research allocation; metadata has explicit AI disclosure and human-review state; unsafe/banned metadata is rejected; a saved brief can be previewed and generated one at a time; its execution preserves portfolio lineage; the review ZIP includes its metadata draft and checklist; direct generation remains compatible; and tests pass.
