# StockForge Concept Engine v4

## Purpose

Concept Engine v4 converts an evidence-backed market opportunity and explicit buyer profile into a small set of commercially differentiated visual concepts.

It is intentionally deterministic. It does **not** invent market demand, buyer facts, or marketplace evidence.

## Design principle

A prompt is an implementation detail. The commercial concept comes first:

`market evidence -> opportunity -> buyer -> communication job -> visual problem -> concept -> prompt`

This follows two external signals:

- Adobe says its 2026 trends are informed by commercial campaigns, customer feedback, and search history, and emphasizes relevance, usefulness, human connection, and local specificity.
- Shutterstock describes content briefs as customer-demand-driven guides containing desired scenarios, casting/style considerations, and keyword insights.

Sources reviewed 2026-08-20:

- https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends
- https://www.shutterstock.com/blog/stock-visuals-content-briefs
- https://www.shutterstock.com/id/trends
- https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/distinct-generative-ai-submission-best-practices.html

## Concept dimensions

Every generated concept carries:

- buyer segment
- buyer job
- channel
- visual problem
- subject
- action
- environment
- composition
- copy-space direction
- uniqueness levers

## Anti-spam rule

The engine creates a limited set of genuinely different angles rather than changing only crop, color, or post-processing. Adobe warns contributors to avoid image spam and to ensure each file provides unique value.

The default planner produces four angles:

1. hero
2. workflow
3. detail
4. decision

These are planning primitives, not a guarantee that all four should be submitted. Final QA and duplicate/differentiation gates must decide that.

## Current limitations

- Marketplace collection is still external; this module does not scrape or assert live demand.
- Buyer registry is an initial evidence-backed taxonomy, not a complete market model.
- Concept templates are deterministic and must later be complemented by a prompt compiler.
- No claim is made that an opportunity score predicts sales.
- Human review remains required for final commercial judgment.
