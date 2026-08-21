# StockForge Prompt Compiler

## Purpose

The Prompt Compiler converts an approved `ConceptVariant` into a deterministic `PromptPackage` for the image-generation layer.

It does **not** decide market demand and does **not** provide legal clearance. Market evidence and buyer selection happen upstream; final compliance remains a human review gate.

## Pipeline

```text
Market Evidence
  -> Market Opportunity
  -> Buyer Match
  -> Concept Variant
  -> Prompt Compiler
  -> Image Generator
  -> Visual QA
  -> Compliance Review
  -> Submission
```

## Prompt requirements

Every compiled prompt must preserve:

- buyer communication job
- visual problem
- subject
- action
- environment
- composition
- copy-space intent
- uniqueness levers
- commercial stock-photo intent

The compiler must not invent a brand, person, product, customer claim, or market fact.

## Quality constraints

The compiler explicitly asks the generator to favor:

- believable anatomy and hands
- physically plausible objects and perspective
- realistic materials and lighting
- authentic workplace behavior
- clean commercial composition
- useful negative space
- restrained color treatment
- realistic, non-CGI appearance

## IP and legal-risk constraints

The negative prompt and legal constraints explicitly avoid:

- trademarks and logos
- celebrity/public-figure likeness
- copyrighted characters
- brand endorsement implications
- proprietary readable software interfaces
- watermarks and signatures

These are generation safeguards, not legal clearance. Adobe and marketplace submission rules still require human review of the final asset.

## Marketplace research basis

Adobe's contributor guidance emphasizes quality, legal permissions/releases, and commercially usable content. Adobe's current creative-trend reporting also emphasizes relevance, usefulness, human connection, and regional specificity.

Shutterstock's current contributor policy is materially different: Shutterstock does **not** accept AI-generated content directly from contributors into its core contributor library. Therefore StockForge currently treats Adobe Stock and other AI-accepting destinations separately and must not assume that a prompt suitable for Adobe is automatically eligible everywhere.

References checked during implementation:

- Adobe Stock Contributor Guide: https://helpx.adobe.com/stock/contributor/help/photography-guidelines.html
- Adobe Creative Trends 2026: https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends
- Shutterstock AI contributor policy: https://submit.shutterstock.com/help/en/articles/10594622-ai-generated-content-policy-update
- Shutterstock submission guidance: https://submit.shutterstock.com/help/en/articles/12136175-how-to-submit-content-to-shutterstock

## Status

Implemented: deterministic compiler + tests.

Not yet implemented here: automatic image inspection, duplicate/near-duplicate detection, metadata generation, and marketplace-specific submission gates.
