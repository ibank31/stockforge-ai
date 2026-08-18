# StockForge AI — Project Continuation Brief

**Purpose:** This file is the canonical handoff/context brief for future sessions. Read it before making architectural or implementation decisions.

## 1. End Goal

StockForge AI is intended to become a **free-first, production-grade AI stock asset factory**, focused first on **commercial stock photography/images** that can realistically be submitted to and sold through marketplaces such as Adobe Stock and other compliant stock marketplaces.

The product is NOT merely an image generator. The target system converts market opportunity into controlled asset production:

`market demand → opportunity → concept → prompt → generation → QA → enhancement → deduplication → provenance/compliance → metadata → submission package → human approval → marketplace`

Long-term, the system should learn from portfolio/submission/sales outcomes and improve future concept selection and production. Human approval remains the final gate for submission.

## 2. Core Product Principles

- **Commercial usefulness over visual novelty.** Optimize for buyer utility, not merely beautiful AI images.
- **Quality over raw volume.** Avoid spam, near-duplicates, repetitive batches, and low-value variations.
- **Free/open-source first.** Prefer zero-cost/open-source tools and local execution where practical; remote GPU/API providers are optional adapters, not architectural requirements.
- **Vendor neutral core.** Generators, upscalers, OCR, QA, metadata, and marketplace integrations are plugins/adapters.
- **Provenance first.** Every important asset must be traceable to job, pipeline, model, workflow, prompt, seed, inputs, transformations, QA, and metadata versions.
- **Reproducibility.** Record enough information to reproduce or audit generation and transformations whenever the underlying provider permits it.
- **Marketplace compliance is a first-class feature.** Never assume that technically generated content is commercially/submission compliant.
- **Termux/Android first.** Core must remain usable on modest hardware; heavy generation can be delegated to optional remote/local GPU providers.
- **No hard dependency on one model/provider.** Provider lock-in is a design failure.
- **CI is a gate.** Do not merge untested changes merely to advance the roadmap.

## 3. Current Architecture

Core stack:
- Python
- uv
- Typer CLI
- SQLite
- filesystem as binary/artifact source of truth
- pytest
- GitHub Actions

Architectural style:
- CLI-first
- Termux-first
- microkernel/plugin-oriented
- persistent jobs
- declarative pipelines
- versioned domain contracts
- filesystem artifacts + queryable SQLite registry

## 4. Completed Milestones

### Core Foundation
- CLI entry point
- `stockforge version`
- `stockforge init`
- `stockforge doctor`
- SQLite initialization
- project creation/listing
- workspace layout
- versioned project manifest
- atomic manifest writes
- project creation rollback handling
- initial test suite
- GitHub Actions CI

### Asset Registry
- stable asset UUID
- project ownership
- asset type/status contract
- safe relative paths
- MIME type/file size
- SHA-256 checksum
- asset CLI create/list
- persistent SQLite asset records

### Persistent Job Queue
- stable job UUID
- project ownership
- job type
- priority
- JSON payload
- queued/running/succeeded/failed/cancelled states
- atomic worker claiming
- attempt counting
- bounded retries
- completion/failure/cancellation
- persistent SQLite queue
- job CLI commands

### Plugin Contract
- vendor-neutral plugin descriptor
- plugin API version
- plugin kind/capabilities
- deterministic registry lookup
- capability-based discovery
- API compatibility validation
- trust-boundary documentation

### Pipeline Engine
Current work is in progress on the pipeline layer. The initial runner is intentionally **linear/sequential**. Do NOT prematurely add DAG/fan-out/caching/resumability until artifact/provenance contracts are established.

## 5. Current Branch / Work State

At the latest handoff:
- `main` contains the completed core foundation, asset registry/job queue, and plugin contract.
- PR #4 targets `main` from `feat/pipeline-engine`.
- PR #4 adds the versioned pipeline definition and deterministic sequential runner.
- CI must be green before merge.

Always inspect the actual GitHub state before assuming these statuses remain current.

## 6. Target Architecture

```text
Market Intelligence
        ↓
Opportunity / Concept Planner
        ↓
Prompt + Variation Planner
        ↓
Persistent Job Queue
        ↓
Pipeline Runner
        ↓
Generator Plugin
        ↓
Artifact Registry + Provenance
        ↓
Image QA Gates
        ↓
Enhancement / Upscaling
        ↓
Perceptual Deduplication
        ↓
Commercial / Marketplace Compliance
        ↓
Stock Metadata Engine
        ↓
Submission Package
        ↓
Human Approval
        ↓
Marketplace
        ↓
Sales / Acceptance Feedback
        └────────────→ Market Intelligence
```

## 7. Critical Domain Contracts Still Needed

Build these deliberately before large provider integrations:

1. **Artifact contract**
   - immutable artifact identity/version
   - path/reference
   - MIME/type
   - size
   - checksum
   - creation source
   - parent artifacts
   - transformation history

2. **Provenance/lineage contract**
   - job ID
   - pipeline ID/version/hash
   - step ID
   - plugin/provider ID/version
   - model identifier/version/hash when available
   - workflow hash
   - prompt and negative prompt hashes/records
   - seed/generation parameters
   - input references
   - transformation chain
   - QA results
   - metadata version
   - license/policy record

3. **Provider configuration/secrets contract**
   - secrets never stored in job payloads
   - provider configuration referenced by stable ID
   - credentials separated from reproducible job data
   - no secret leakage in logs/errors

4. **QA contract**
   - deterministic technical checks
   - image dimensions/aspect ratio
   - decodability/corruption
   - color/profile sanity
   - duplicate/similarity score
   - OCR/text/logo detection
   - face/anatomy/artifact checks where feasible
   - aesthetic/commercial usefulness score
   - marketplace-specific rejection gates

5. **Marketplace metadata contract**
   Internal metadata must be richer than any one marketplace export. Preserve internal provenance separately from submission title/description/keywords/categories/AI disclosure fields.

## 8. Image Generation Direction

The first production target is **photo-first stock imagery**.

ComfyUI is a preferred adapter because it provides workflow-level control and can remain outside the core. Do not hardwire ComfyUI into core services.

Prior technology research identified a free-first ecosystem including tools such as Diffusers, Pillow, rembg, Real-ESRGAN, CleanVision, imagededup, vtracer, SVGO, and ExifRead. Treat every model/tool license separately and verify current licensing before commercial deployment. **Open-source does not automatically mean commercially unrestricted.**

Model selection must consider:
- commercial-use rights
- model-weight license
- code license
- dataset/provenance considerations
- marketplace policy
- output restrictions
- resource footprint
- reproducibility

A previously researched MVP candidate was Stable Diffusion 3.5 Medium under its applicable Stability license/registration terms. Do not treat this as permanently approved: re-check the current license and marketplace policies before implementation or distribution.

FLUX was previously excluded from the free commercial MVP pending license/use-rights analysis. Revisit only with current evidence.

## 9. Stock Marketplace Reality

The financial goal is real but not guaranteed. Existing contributor reports indicate that AI-generated stock can earn money, but outcomes vary enormously with portfolio size, quality, demand, acceptance, niche, marketplace, account history, and metadata.

Do not optimize StockForge around simplistic `generate 1,000 images → upload 1,000 images` behavior. The system should actively avoid:
- near-duplicate spam
- repetitive concepts
- obvious AI artifacts
- trademark/logo contamination
- unsafe/unlicensed source material
- low-value generic imagery
- misleading metadata
- marketplace policy violations

The strategic objective is **high-value, commercially useful, differentiated stock content**.

## 10. Market Intelligence Direction

A future intelligence layer should score opportunities using evidence rather than inventing demand. Candidate dimensions:
- buyer/use-case utility
- seasonal vs evergreen demand
- competition/saturation signals
- portfolio gaps
- search/keyword opportunity where data is legally and technically available
- variation potential
- production difficulty/cost
- predicted acceptance risk
- predicted commercial value

Construction/property/architecture can be an early domain advantage because the project owner has strong construction/property domain knowledge, but the machine should remain general enough for broader stock categories.

## 11. Free-First / Resource Constraints

The system must work from Android/Termux and modest hardware.

Design rules:
- lightweight core
- streaming file operations
- SQLite instead of heavyweight infrastructure for MVP
- filesystem artifacts rather than storing binaries in DB
- optional worker machines/remote GPU through adapters
- resumable jobs
- bounded retries
- cache expensive deterministic operations
- avoid unnecessary memory duplication
- no mandatory paid SaaS dependency

## 12. Quality Bar

User explicitly requires:
- work incrementally
- detailed implementation
- no avoidable mistakes
- verify code rather than assume
- CI/test before merge
- research before committing to important technology choices
- maintain continuity across sessions

Do not say a stage is complete merely because files were written. Completion means implementation + tests + CI + audit + correct Git state.

## 13. Immediate Roadmap

1. Finish and validate Pipeline Engine PR #4.
2. Artifact + provenance/lineage contract.
3. Provider configuration + secure secret handling.
4. ComfyUI generator adapter.
5. Real image-generation workflow integration.
6. Automated image QA gates.
7. Enhancement/upscaling pipeline.
8. Perceptual duplicate/similarity control.
9. Stock metadata engine.
10. Marketplace-specific compliance/export packages.
11. Human approval workflow.
12. Market intelligence + concept planning.
13. Sales/acceptance feedback loop.
14. Optimization for scalable production.

## 14. Non-Negotiable Product Definition

When future sessions ask “what are we building?”, the answer is:

> **StockForge AI is a free-first, Termux-first, plugin-based AI stock asset factory. Its first and most important output is high-quality commercial stock photography. It should transform market opportunities into generation jobs, produce controlled image batches, automatically reject technical/commercial failures, preserve complete provenance, create compliant marketplace metadata, prevent duplicate/spam submissions, and produce human-reviewable submission packages. Its long-term advantage is not merely generation; it is the closed production-and-learning loop from market demand → asset → acceptance/sales feedback → better future production.**

The machine should eventually be capable of operating most of this workflow automatically while keeping final marketplace submission under explicit human approval and maintaining auditable provenance/compliance records.
