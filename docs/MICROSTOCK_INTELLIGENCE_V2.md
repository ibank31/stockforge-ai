# Microstock Intelligence V2

Branch implementation: `feature/microstock-intelligence-v2`.

## What changed

This branch connects the previously isolated deterministic layers into one
planning path:

`MARKET EVIDENCE -> MARKET SCORE -> BUYER MATCH -> CONCEPT VARIANTS -> ASSET SPEC -> PROMPT PACKAGE`

The new core is `stockforge.intelligence_pipeline`.

## Boundary

The planner requires explicit timestamped evidence. It does not scrape a
marketplace, invent demand, call a generation provider, auto-approve an asset,
or claim marketplace acceptance.

This is intentionally the first integration layer for a future SaaS API or
Gemini Canvas frontend: the frontend can submit structured research while the
deterministic Python core returns explainable concepts and provider-neutral
prompt packages.
