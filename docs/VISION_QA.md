# Vision QA

## Purpose

Vision QA is the semantic quality gate between image generation and commercial stock submission.

Adobe Stock guidance requires contributors to select only their best content, avoid image spam, and ensure each submitted file has unique customer value. Technical validity alone cannot establish that. citeturn0search12

## Why a provider boundary exists

The existing structural and pixel QA layers can detect file format, dimensions, aspect ratio, exposure-like signals, clipping, dynamic range, and entropy. They cannot reliably determine whether a generated person has malformed hands, whether a tool is physically plausible, whether a face is uncanny, or whether the scene actually communicates the intended commercial concept.

Therefore `vision_qa.py` defines a provider contract rather than pretending that cheap image statistics are semantic vision.

## Gate dimensions

A real vision provider should score:

- overall visual quality
- commercial usefulness
- subject/scene integrity
- AI artifact risk
- anatomy and hands
- realism
- composition
- subject integrity
- text/logo risk

The provider may also return free-form notes for human review.

## Submission policy

Default policy is conservative:

```text
no vision provider -> FAIL
provider unavailable -> REVIEW
provider assessment below threshold -> FAIL
provider assessment passes all gates -> PASS
```

This is deliberate. A failed vision backend must never silently turn into an approved stock asset.

## Marketplace context

Adobe's contributor guidance emphasizes commercial/aesthetic value and warns against submitting multiple copies that provide no unique value. citeturn0search12

Marketplace trend data is also useful for concept selection, but it is not a substitute for visual QA. Current Shutterstock trend data shows that some topics combine high growth with very different supply levels, so the engine must optimize both commercial relevance and differentiation. citeturn0search0turn0search1

Shutterstock's 2026 content-brief approach is especially relevant to StockForge: briefs combine customer demand, scenarios, casting, styling, and keyword insights. That supports the architecture of feeding buyer/use-case context into the vision review. citeturn0search9

## Current limitation

No heavyweight vision model is bundled into the core package yet. The next implementation should add one or more pluggable providers, with provider-specific dependencies kept outside the lightweight core.

The production gate must remain provider-agnostic so that a free/cloud vision model can be selected later without rewriting the pipeline.
