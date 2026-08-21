# StockForge AI — Adobe Stock Readiness Specification

**Version:** 1.0  
**Date:** 2026-08-20  
**Purpose:** Define the technical, visual, metadata, intellectual-property, and workflow gates required before a generated asset may be considered ready for Adobe Stock submission.

> This document is an engineering specification, not a guarantee of marketplace acceptance. Adobe can change policies and can reject content for reasons not fully captured by automated checks. Human approval remains mandatory.

## 1. Submission philosophy

StockForge must optimize for **commercially useful, differentiated, technically sound assets**, not maximum generation volume.

The generator produces an intermediate asset. A final submission requires:

```text
Generation
  ↓
Technical QA
  ↓
Visual / AI artifact QA
  ↓
IP / OCR / logo QA
  ↓
Upscale / enhancement
  ↓
Final format + color normalization
  ↓
Technical re-QA
  ↓
Deduplication
  ↓
Commercial-value scoring
  ↓
Metadata + disclosure
  ↓
Human approval
  ↓
Submission package
```

## 2. Current benchmark gap

Benchmark `STOCKFORGE-001` was generated on 2026-08-20 using Z-Image Turbo through the ZeroGPU Space.

Observed result:

- Generation: successful.
- Resolution: 1536×1536, approximately 2.36 MP in the submitted benchmark artifact.
- Final artifact: WEBP.
- Commercial concept: construction professionals reviewing architectural plans.
- Visual quality: promising.
- Submission readiness: **FAIL**.

Primary reasons:

1. The intermediate image is below the current Adobe photo minimum of 4 MP.
2. WEBP is not the intended final photo submission format; finalization must produce a supported JPEG.
3. Anatomy, hands, object consistency, and blueprint details still require automated and/or human QA.
4. AI disclosure and fictional-person/property state must be persisted in the submission manifest.
5. Metadata and deduplication gates are not yet implemented.

This benchmark is therefore a **generation success**, not an Adobe submission success.

## 3. Technical gates

### 3.1 Resolution

For photo submission, enforce the current Adobe Stock minimum and maximum megapixel limits in a configurable policy file rather than hard-coding values throughout the application.

Current policy target:

- minimum: 4 MP
- maximum: 100 MP

The system must reject files outside the policy.

Do not satisfy the gate by naive resizing alone. Upscaling must preserve usable detail and must be followed by artifact/sharpness QA.

### 3.2 Final file format

The production pipeline may retain WEBP/PNG/TIFF/etc. as intermediate artifacts when useful, but the photo submission artifact must be exported to the currently supported marketplace format.

Current target:

- JPEG
- sRGB
- file size within marketplace limits

The source/intermediate artifact must remain available for provenance.

### 3.3 Color/profile

Validate that the final submission is sRGB or convert it deterministically before submission.

Record:

- source color profile
- conversion operation
- final color profile
- tool/version used

### 3.4 File integrity

Reject:

- corrupted files
- unreadable images
- truncated files
- malformed metadata that breaks ingestion
- unexpected alpha/channel state for final photo export

### 3.5 Quality

Measure where practical:

- focus/sharpness
- excessive blur
- compression artifacts
- posterization/banding
- clipping
- excessive noise/grain
- unnatural halos
- oversharpening
- inconsistent lighting
- obvious AI generation defects

A technical score alone must not override a visible critical defect.

## 4. AI visual QA

### 4.1 Human anatomy

For images containing people, inspect:

- hands
- fingers
- arms
- joints
- body proportions
- faces
- eyes
- ears
- teeth
- skin continuity
- object/person interactions

Any severe anomaly is a hard reject.

Minor uncertainty should become a human-review flag rather than an automatic approval.

### 4.2 Object consistency

Inspect high-salience objects and interactions:

- tools
- machinery
- furniture
- vehicles
- protective equipment
- architecture
- screens
- printed documents
- products

Detect impossible geometry, melted objects, duplicated parts, fused objects, and inconsistent perspective.

### 4.3 Text and OCR

Unintended generated text is a high-risk defect.

Run OCR and classify detected text:

- intended/approved text
- unintelligible generated text
- brand/trademark candidate
- safety/signage text
- document text

For the MVP, prefer concepts that intentionally avoid readable text unless text is commercially necessary.

### 4.4 Logos and trademarks

Detect visible logos and trademark-like marks.

Default policy:

- unintended recognizable logo → hard reject/review
- ambiguous brand-like mark → review
- intentionally requested third-party brand → prompt-level block

The system must not rely on the generator prompt alone to prevent logos.

### 4.5 Watermarks

Any visible watermark or stock-site mark should fail the asset.

## 5. Prompt compliance firewall

Prompt generation must be treated as a policy boundary.

Before generation, scan for high-risk references such as:

- real identifiable people when not appropriate
- celebrities
- artists
- copyrighted fictional characters
- named franchises
- trademarks/brands
- third-party copyrighted works
- specific news events
- government/third-party entities where policy requires caution
- instructions intended to reproduce a protected work

The engine should transform or reject unsafe concepts rather than generate first and discover the problem later.

## 6. People and property logic

Every asset containing people/property must carry an explicit provenance state:

```json
{
  "people": {
    "present": true,
    "source": "synthetic",
    "fictional": true,
    "release_required": false
  },
  "property": {
    "present": true,
    "source": "synthetic",
    "fictional": true,
    "release_required": false
  }
}
```

The exact marketplace export fields must be generated from this internal record.

If a workflow uses real people, real property, or source material requiring releases, the system must flag the asset for human review and release documentation.

## 7. Generative AI disclosure

Every generative-AI asset must carry an internal flag indicating that generative AI was used.

Example:

```json
{
  "ai_generated": true,
  "ai_disclosure_required": true,
  "generator": "z-image-turbo"
}
```

Marketplace-specific submission tooling must map this internal state to the correct disclosure control.

## 8. Metadata rules

The metadata engine must produce:

- accurate title
- relevant keywords
- appropriate category
- AI disclosure state
- people/property state
- release state

Metadata must describe what is actually visible.

Do not use:

- misleading claims
- irrelevant keyword stuffing
- artist names as discovery bait
- celebrity names when not actually depicted and permitted
- brand names used solely to attract search traffic
- fictional character names
- false event/location claims

### Example for benchmark #001

**Title:**

`Construction professionals reviewing architectural plans in a modern project office`

**Candidate keywords:**

`construction, construction management, architecture, architectural plans, blueprint, engineering, project planning, building, development, professionals, teamwork, collaboration, project management, construction site, business, office, infrastructure, real estate, engineering team, building project`

The metadata engine must rank keywords by relevance and enforce marketplace-specific limits.

## 9. Duplicate and spam prevention

StockForge must not turn one concept into a mass of near-identical submissions.

Pipeline:

```text
Batch
  ↓
Exact hash
  ↓
Perceptual hash
  ↓
Embedding similarity
  ↓
Similarity clusters
  ↓
Best-of-cluster selection
  ↓
Portfolio diversity check
```

The system should reject or hold near-duplicates even when the images are technically different.

Variation is valid only when it creates meaningful commercial utility, such as:

- different buyer use case
- different composition
- different subject action
- different copy-space placement
- different season/context
- genuinely different visual concept

Changing a shirt color is not sufficient differentiation.

## 10. Commercial-value gate

Technical acceptance is not enough.

Score candidate assets on:

| Factor | Target weight |
|---|---:|
| Buyer/use-case utility | 25% |
| Visual quality | 20% |
| Uniqueness/differentiation | 15% |
| Searchability/relevance | 15% |
| Composition | 10% |
| Copy-space usefulness | 5% |
| Technical quality | 5% |
| Competition/saturation | 5% |

Initial policy:

- `<70`: reject
- `70–79`: human review
- `80–89`: production candidate
- `90+`: premium candidate

Weights and thresholds must remain configurable.

## 11. Copy-space requirements

The concept planner should choose copy-space placement from the buyer use case.

Examples:

- website hero → left/right copy space
- annual report → broad negative space
- presentation → side copy space
- social post → central subject
- editorial article → balanced composition

Copy space must be measured from the actual generated image, not assumed from the prompt.

## 12. Upscaling policy

The generation model is allowed to operate below final marketplace resolution to conserve GPU resources.

Target pipeline:

```text
1024×1024 or other efficient generation size
        ↓
AI upscaler
        ↓
≥4 MP
        ↓
quality QA
        ↓
JPEG / sRGB
```

A higher production target such as 4096×4096 may be used when the chosen upscaler produces reliable detail, but the target must be benchmarked for:

- visual quality
- file size
- processing time
- artifact rate
- commercial acceptance

## 13. Provenance requirements

Every production asset must preserve:

```json
{
  "asset_id": "...",
  "job_id": "...",
  "pipeline_id": "...",
  "pipeline_version": "...",
  "plugin_id": "...",
  "provider": "...",
  "model": "...",
  "model_revision": "...",
  "text_encoder": "...",
  "workflow_hash": "...",
  "prompt": "...",
  "prompt_version": "...",
  "seed": 0,
  "width": 1024,
  "height": 1024,
  "steps": 8,
  "gpu_seconds": 0,
  "generated_at": "...",
  "parents": [],
  "transformations": [],
  "qa": {},
  "metadata_version": "...",
  "policy_record": "..."
}
```

Secrets must never be stored in this record.

## 14. Final submission gate

An asset may enter `SUBMISSION_READY` only if all hard gates pass:

- [ ] resolution policy passed
- [ ] final JPEG exported
- [ ] sRGB verified
- [ ] file-size policy passed
- [ ] file integrity passed
- [ ] technical quality passed
- [ ] anatomy/object QA passed or explicitly human-approved
- [ ] OCR/logo/watermark QA passed
- [ ] prompt/IP policy passed
- [ ] people/property/release state resolved
- [ ] AI disclosure state recorded
- [ ] metadata validated
- [ ] duplicate/spam check passed
- [ ] commercial-value threshold passed
- [ ] provenance complete
- [ ] human approval recorded

No single AI score may bypass a hard compliance failure.

## 15. Adobe policy maintenance

Marketplace rules can change. Therefore:

1. Store policy thresholds/configuration separately from core code.
2. Record the policy version/date used during evaluation.
3. Re-verify current Adobe requirements before production submission.
4. Never encode an assumption such as "Adobe will always accept X" as a hard fact.

## 16. Implementation roadmap

### Phase A — Submission gate

1. resolution checker
2. JPEG exporter
3. sRGB validator/converter
4. file-size checker
5. image integrity checker
6. watermark detection
7. OCR
8. logo/IP detection
9. AI disclosure manifest
10. people/property/release logic

### Phase B — Visual QA

11. face QA
12. hand/anatomy QA
13. object anomaly detection
14. sharpness/noise/color checks
15. automated QA report

### Phase C — Commercial intelligence

16. buyer/use-case classifier
17. commercial score
18. copy-space analysis
19. perceptual deduplication
20. portfolio diversity score

### Phase D — Production factory

21. market opportunity engine
22. concept planner
23. prompt engine
24. variation planner
25. controlled batch generation
26. automatic selection
27. metadata engine
28. submission package exporter
29. human review queue
30. acceptance/sales feedback loop

## 17. Current decision

**Do not modify the working ZeroGPU generator solely to chase submission requirements.**

The generator is an adapter. Adobe readiness belongs in the downstream pipeline so that the same core can eventually accept multiple generators/providers.
