# StockForge Asset Factory Architecture v1

Status: proposed implementation architecture
Branch: `feat/asset-factory-architecture`

## 1. Objective

StockForge is an evidence-driven commercial asset factory. The system must not treat image generation as the product. Generation is one execution step inside a larger chain:

```text
MARKET SIGNALS
    ↓
MARKET OPPORTUNITY
    ↓
BUYER + COMMUNICATION JOB
    ↓
ASSET SPECIFICATION
    ↓
CONCEPT VARIANT
    ↓
PROMPT PACKAGE
    ↓
MODEL ROUTER
    ↓
GENERATION
    ↓
VISUAL QC
    ↓
ENHANCEMENT / CLEANUP
    ↓
SIMILARITY / DUPLICATE GATE
    ↓
METADATA
    ↓
COMPLIANCE GATE
    ↓
EXPORT / SUBMISSION PACKAGE
    ↓
PROVENANCE + FEEDBACK LOOP
```

The commercial unit is therefore an **asset package with evidence, provenance, QC, metadata and submission state**, not merely an image file.

## 2. Existing StockForge contracts to preserve

The architecture extends existing contracts rather than replacing them.

- `market_intelligence.py` remains the source of evidence-backed opportunities.
- `buyer_intelligence.py` remains the buyer taxonomy and match layer.
- `concept_engine.py` remains the deterministic concept planner.
- `prompt_compiler.py` remains the prompt-package compiler.
- `pipeline.py` remains the provider-neutral ordered execution contract.
- `plugin.py` remains the provider/processor plugin boundary.
- `dedup.py`, `dedupe_candidates.py`, and `dedupe_pipeline.py` remain the similarity controls.
- `artifact.py`, `asset.py`, `asset_manager.py`, and `provenance.py` remain asset/provenance foundations.
- `adobe_gate.py` and `adobe_finalize.py` remain Adobe-specific finalization gates.
- `portfolio.py`, `portfolio_io.py`, `PORTFOLIO_PRODUCTION_ENGINE.md`, and `PORTFOLIO_DELIVERY_PIPELINE.md` define the active standalone portfolio-planning and brief-to-review-package path.

No provider is allowed to leak credentials, network configuration, or model-specific secrets into the core pipeline definition.

## 3. New commercial asset model

The first-class planning object should be an `AssetSpec` with these logical fields:

```text
asset_id
market_opportunity_id
buyer_segment
buyer_job
channel
asset_family
micro_niche
asset_type                 # photo | illustration | ephemera | 3d | icon | texture | etc.
subject
visual_language
medium
palette
composition
negative_space
background_policy
isolation_policy
text_policy
branding_policy
originality_levers
variation_policy
commercial_use_cases
quality_gates
model_preferences          # provider-neutral capability requirements only
metadata_hints
```

The important change is that **subject and visual requirements become typed commercial constraints**, rather than being buried in one long prompt string.

## 4. Market-to-asset planning

The market layer must produce an opportunity object with evidence and a score, then the asset planner turns it into production specifications.

```text
Evidence
  → Opportunity
  → Buyer Match
  → AssetSpec
  → ConceptVariant
```

For small standalone assets, `AssetSpec` must explicitly support:

- isolated object
- transparent/white-background intent
- extraction-friendly silhouette
- thumbnail readability
- modular reuse
- tactile/material requirements
- restrained composition
- no unnecessary scene context
- originality and variation controls

This prevents the existing scene-oriented defaults from leaking into ephemera, culinary ingredients, UI objects, nursery illustrations, textures, and similar non-scene categories.

## 5. Concept planning

`ConceptVariant` remains the planning boundary before prompting.

For standalone assets, the concept planner should use an asset-specific angle set instead of automatically applying the current `hero/workflow/detail/decision` scene templates.

Recommended standalone primitives:

1. `hero_object` — the primary isolated object.
2. `material_detail` — a materially distinctive close visual.
3. `functional_variant` — a commercially different use-oriented variation.
4. `style_variant` — a genuinely different visual language or medium.

These are planning primitives only. The similarity gate decides which variants are sufficiently different to retain.

## 6. Prompt compiler architecture

The prompt compiler should compile structured constraints in layers:

```text
BASE COMMERCIAL INTENT
    +
ASSET TYPE
    +
SUBJECT SPECIFICATION
    +
VISUAL LANGUAGE
    +
MATERIAL / MEDIUM
    +
COMPOSITION
    +
BACKGROUND / ISOLATION
    +
COMMERCIAL USE
    +
ORIGINALITY LEVERS
    +
QUALITY CONSTRAINTS
    +
NEGATIVE CONSTRAINTS
    +
MODEL ADAPTER
    =
PromptPackage
```

The compiler must never invent demand evidence, brands, people, product claims, or legal clearance.

### Model adapter rule

The semantic asset specification is provider-neutral. A model adapter may translate it into provider-specific syntax or parameters.

```text
AssetSpec
   ↓
Prompt Compiler
   ↓
Canonical PromptPackage
   ↓
Model Adapter
   ├── z-image
   ├── flux-klein
   ├── qwen-image
   ├── external/google-flow/manual
   └── future providers
```

This allows a stronger model to be swapped in without rewriting the market, concept, QC, metadata, or compliance layers.

## 7. Generation routing

The router chooses a provider/model using capability requirements rather than hard-coded model names.

Example requirements:

```text
realism = high
text_accuracy = low/none
isolation = required
transparent_background = preferred
style_control = high
resolution = >= 1024
cost_budget = low
latency_budget = medium
```

The router returns:

```text
provider_id
model_id
capabilities_used
parameters
fallback_chain
estimated_cost
routing_reason
```

A queue timeout or unavailable GPU is a routing failure, not a visual-quality failure. The system must be able to fall back to another eligible provider without corrupting the asset record.

## 8. Visual QC architecture

QC is split into deterministic preflight and post-generation inspection.

### Preflight

Reject before generation when constraints are internally contradictory or impossible to satisfy.

Examples:

- isolation required but composition explicitly requests a scene
- no text but text-dependent concept
- transparent extraction required but provider cannot return usable alpha
- unsupported dimensions

### Post-generation

```text
IMAGE
 ↓
Technical QC
 ├── dimensions
 ├── file integrity
 ├── background policy
 ├── alpha/edge quality
 └── artifact detection
 ↓
Semantic QC
 ├── subject presence
 ├── object count
 ├── composition
 ├── material/medium
 ├── text/brand detection
 └── concept adherence
 ↓
Commercial QC
 ├── thumbnail readability
 ├── design utility
 ├── originality
 ├── buyer-job fit
 └── marketplace readiness
```

Every failed benchmark must record explicit failure labels and produce a rule, knowledge, or compiler refinement before regeneration.

## 9. Similarity architecture

Similarity is evaluated at three levels:

```text
A. exact/near-exact file duplicate
B. visual near-duplicate
C. semantic/commercial near-duplicate
```

The third layer is essential for stock production. Changing only crop, color, seed, or post-processing must not automatically qualify an asset as a new submission.

Each candidate should carry:

```text
similarity_status
nearest_asset_ids
visual_similarity_score
semantic_similarity_score
variation_reason
submission_group
```

## 10. Metadata architecture

Metadata is generated from the approved asset specification, not hallucinated from the final image alone.

```text
AssetSpec
   +
Vision inspection
   ↓
Title candidates
Keywords
Description
Category
Use-case hints
AI disclosure flag
IP/compliance flags
```

Metadata must remain differentiated between variants. A batch must not receive the same generic title and keyword block with superficial substitutions.

## 11. Compliance architecture

Compliance is destination-specific.

```text
Universal safety/IP checks
        ↓
Marketplace-specific gate
   ├── Adobe
   ├── other AI-accepting marketplace
   └── manual/export destination
```

A prompt safeguard is not legal clearance. Final rights, trademark, recognizable-person, and destination-policy review remains explicit.

## 12. Provenance

Every production run should persist enough information to reproduce or audit the asset:

```text
job_id
asset_id
pipeline_id + pipeline_version
concept_id
prompt_package_hash
provider_id
model_id + model_version
workflow_hash
seed
width / height / steps
source/reference hashes
QC results
similarity results
metadata version
compliance result
artifact hashes
timestamps
```

This information belongs in provenance, not hidden inside arbitrary provider parameters.

## 13. Pipeline stages

The canonical v1 production pipeline is:

```text
01 opportunity_select
02 buyer_match
03 asset_spec_compile
04 concept_plan
05 prompt_compile
06 route_model
07 generate
08 visual_qc
09 enhance
10 similarity_gate
11 metadata_compile
12 compliance_gate
13 export_package
14 persist_provenance
```

Stages 1–5 are GPU-free planning stages whenever possible. This is intentional: deterministic failures should be caught before consuming scarce generation capacity.

## 14. Provider architecture

Provider plugins expose capabilities, for example:

```text
image.generate
image.edit
image.upscale
image.background_remove
image.inspect
image.embed
```

A provider may implement several capabilities. The pipeline requests capabilities, while the router chooses an implementation.

This keeps ZeroGPU, Kaggle, Modal, Hugging Face, external APIs, and future local runners behind the same execution boundary.

## 15. Feedback loop

The factory must learn from production outcomes:

```text
Generation
  ↓
QC
  ↓
Submission
  ↓
Marketplace outcome
  ↓
Acceptance / rejection / sales / engagement
  ↓
Market intelligence update
  ↓
Opportunity reprioritization
```

The feedback loop must distinguish:

- generation failure
- QC failure
- policy rejection
- no demand
- weak metadata
- weak visual utility
- successful commercial signal

A rejected image is not automatically evidence that the niche is bad.

## 16. First production family

The first implementation target is **small standalone visual assets**, not generic full-scene photography.

The architecture must support the research-ranked families without hard-coding one niche:

1. Ephemera / journal / scrapbook
2. Culinary raw-ingredient illustration
3. Glasscore / 3D UI elements
4. Nursery boho animals
5. Retro / tech nostalgia

A niche is data. It must not become a hard-coded branch in the generation engine.

## 17. Implementation sequence

### Current implementation — PR #38

The implemented boundary is deliberately narrow. `AssetSpec` validates provider-neutral commercial requirements, including capability-style model preferences; `standalone_asset_spec()` fixes the standalone policy to a white background, isolated placement, no text, and no branding; and `compile_asset_prompt()` returns the existing canonical `PromptPackage` with standalone quality, legal, and metadata constraints. Existing `ConceptVariant`, `Pipeline`, and `Plugin` contracts remain unchanged and compatible.

The market-to-asset planner, standalone `ConceptVariant` primitives, model adapters and routing, QC/similarity/metadata execution, and end-to-end factory orchestration remain planned. They are not represented as completed runtime stages by this implementation.

### Phase A — contracts

- Implement `AssetSpec` validation and the standalone asset policy.
- Keep the existing `ConceptVariant` interface unchanged.
- Plan standalone concept templates without forcing the scene-oriented `hero/workflow/detail/decision` defaults onto small assets.

### Phase B — compiler

- Compile structured asset constraints into the existing `PromptPackage` contract.
- Add standalone negative, quality, legal, and metadata policies.
- Plan model adapters as the next provider-specific layer.

### Phase C — router

- Capability-based provider selection.
- Explicit fallback chain.
- Queue/error classification.

### Phase D — QC

- Technical image inspection.
- Background/edge checks.
- Object/text/brand checks.
- Asset-specific policy evaluation.

### Phase E — similarity + metadata

- Visual embeddings.
- Semantic similarity.
- Variant grouping.
- Metadata compiler.

### Phase F — factory orchestration

- Connect all stages through the existing provider-neutral pipeline contract.
- Persist full provenance.
- Add resumable jobs and later conditional/parallel execution.

## 18. Non-goals

This architecture does not assume:

- one permanent image model
- one marketplace
- one visual style
- automatic legal clearance
- automatic sales prediction
- unlimited near-identical submissions
- generation before evidence

## 19. Acceptance criteria

The architecture is considered operational when one standalone asset can travel end-to-end as:

```text
market evidence
→ approved opportunity
→ buyer/job
→ structured asset spec
→ differentiated concept
→ model-neutral prompt
→ routed generation
→ QC decision
→ similarity decision
→ differentiated metadata
→ destination compliance
→ export package
→ reproducible provenance
```

without requiring a human to manually rewrite the prompt between stages.
