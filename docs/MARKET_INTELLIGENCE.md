# StockForge AI — Marketplace Intelligence

**Version:** 1.0  
**Date:** 2026-08-20  
**Status:** Research foundation; automation not yet implemented

## Purpose

StockForge must not optimize only for image quality or Adobe acceptance. It must also optimize for **commercial differentiation**: why a buyer would choose this asset instead of the thousands of similar assets already available.

Marketplace research is therefore a first-class input to concept selection, prompt construction, variation planning, QA, metadata, and portfolio pruning.

## Evidence hierarchy

Research should be collected in this order:

1. Marketplace-native search/result pages and trend dashboards.
2. Marketplace contributor briefs and official customer-demand guidance.
3. Marketplace editorial/trend reports.
4. Official marketplace licensing and submission rules.
5. Secondary industry research only when primary marketplace evidence is unavailable.

Search-result counts are **signals of supply, not sales**. They must never be interpreted as proof that an asset sells.

## Current market observations

### 1. Generic construction imagery is saturated

Adobe Stock currently exposes tens of millions of results for broad `construction` searches and hundreds of thousands for narrower construction-tech/project-management searches. This means StockForge should not treat `construction meeting`, `workers with blueprint`, or `construction site with crane` as sufficiently differentiated concepts by themselves.

Evidence:
- Adobe Stock `construction`: 49M+ results at research time.
- Adobe Stock `construction tech project management`: 546K+ results.
- Adobe Stock `project management`: 3.2M+ results.

These counts are dynamic and must be rechecked before production campaigns.

### 2. Search demand can rise in narrower emerging concepts

Shutterstock's live trend dashboard shows demand/growth signals for narrower subjects such as `ai governance`, `ai doctor`, `ai chip`, `construction site cartoon`, `hot earth`, and other emerging terms. This demonstrates why StockForge should investigate **specific emerging use cases**, rather than simply selecting the largest keyword.

The dashboard's demand/growth numbers are platform-specific and should be stored with a timestamp if automated later.

### 3. Construction is broader than site photography

Adobe's industry collection groups construction with logistics, smart factories, robotics, supply chain, PPE, manufacturing, and technology-powered workplaces. This suggests a better opportunity model: construction should be treated as an **industry context**, then intersected with business problems and emerging technology.

Examples of intersections to investigate:

- construction + AI governance
- construction + digital twin
- construction + predictive maintenance
- construction + safety technology
- construction + climate resilience
- construction + supply-chain visibility
- construction + BIM coordination
- construction + remote inspection
- construction + infrastructure analytics
- construction + workforce training

These are hypotheses, not claims of sales demand. Each must be validated with current marketplace evidence before production.

## Differentiation framework

Every concept should score across five dimensions:

| Dimension | Question |
|---|---|
| Search opportunity | Is there evidence of current or emerging buyer interest? |
| Supply saturation | How crowded is the exact concept? |
| Buyer utility | Can a designer/editor immediately imagine where it will be used? |
| Visual differentiation | Does the image communicate something more specific than a generic stock scene? |
| Variation potential | Can we create genuinely different assets without producing spam? |

A concept should not enter batch generation merely because it has high search volume. High demand + extreme saturation can be a poor opportunity.

## Commercial-use-case first planning

Instead of:

`construction manager + blueprint`

StockForge should plan:

`buyer/use case → communication problem → visual concept → composition → prompt`

Example:

**Buyer:** construction software company  
**Use:** website hero for digital transformation page  
**Problem:** needs to communicate technology coordinating physical construction  
**Concept:** site supervisor reviewing a tablet-based digital twin beside a partially completed structure, with deliberate negative space for headline placement  
**Differentiator:** physical/digital workflow relationship, not another generic team meeting

## Real-market uniqueness principles

### A. Intersection beats broad category

Combine a stable commercial category with a specific emerging topic.

`construction` alone → saturated  
`construction + AI safety workflow` → narrower hypothesis  
`construction + AI safety + mobile inspection + copy space` → buyer-specific concept

### B. Show the problem, not only the profession

Generic:

`engineers discussing plans`

Better:

`engineer documenting a site safety anomaly on a tablet`

Better still when evidence supports it:

`remote construction inspection workflow using mobile visual documentation`

The asset becomes useful for an article, product page, training material, SaaS campaign, or presentation.

### C. Design for layout use

A stock asset is often purchased because it fits a design, not merely because it is beautiful.

Concept planning should explicitly request:

- left copy space
- right copy space
- top copy space
- center subject
- wide banner composition
- vertical editorial composition
- presentation-safe framing

### D. Regional specificity can create differentiation

Adobe's 2026 Creative Trends identify `Local Flavor` and emphasize authentic regional perspectives, specificity, and narratives shaped by lived experience. StockForge should therefore investigate underrepresented regional business contexts instead of producing only generic US/European office imagery.

Potential examples for later validation:

- Southeast Asian construction workflows
- tropical construction environments
- dense urban development in emerging markets
- local materials and work practices
- regional logistics and infrastructure

Regional specificity must never be faked in a way that introduces inaccurate cultural or technical details.

### E. Human usefulness over AI spectacle

Adobe's 2026 trend research emphasizes relatable, relevant, useful content and growing demand for human connection and authenticity. Shutterstock's 2026 contributor guidance similarly frames successful collections around clear briefs, distinct human stories, customer demand, and useful metadata.

Therefore StockForge should avoid making `AI-looking` visuals its differentiator. The differentiator should be **specific commercial storytelling**.

## Collection strategy

StockForge should create **micro-collections**, not random image dumps.

A collection example:

`Construction AI Safety`

1. Supervisor reviewing safety anomaly on tablet.
2. Worker using mobile inspection workflow.
3. Engineer reviewing site risk data with copy space.
4. Remote expert inspecting construction imagery.
5. Safety briefing around digital site map.
6. Close-up of tablet + PPE + site context.

Each image must have a different buyer use case, composition, or story. Merely changing camera angle, color grading, clothing, or seed is not sufficient differentiation.

## Anti-spam rule

Adobe warns contributors to select only the best content and ensure each file offers unique value. Multiple near-identical submissions can be treated as image spam.

StockForge therefore requires future batch selection to use:

`generate → QA → perceptual clustering → best-of-cluster selection → portfolio diversity check`

The system should optimize **expected value per submitted asset**, not number of generated files.

## Current benchmark lesson

Benchmark #001 (`construction professionals reviewing architectural plans`) is visually competent but commercially generic. Its main weakness is not image quality; it is differentiation in a heavily supplied category.

The next generation should therefore test a more specific commercial story rather than simply producing another construction meeting.

## Research record — 2026-08-20

Sources reviewed:

- Adobe Stock search pages for construction, project management, and construction-tech project management.
- Adobe 2026 Creative Trends and creator guidance.
- Shutterstock Trends dashboard.
- Shutterstock contributor/content-brief guidance.
- Shutterstock 2026 AI production guidance.

Key external references:

- Adobe 2026 Creative Trends: https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends
- Shutterstock Trends: https://www.shutterstock.com/trends
- Shutterstock content briefs: https://www.shutterstock.com/blog/stock-visuals-content-briefs
- Shutterstock AI production: https://www.shutterstock.com/blog/ai-production-is-more-than-prompt-and-pray

## Automation target

Future Market Intelligence module should collect, timestamp, and normalize:

```text
marketplace
query
result_count
trend_signal
demand_signal
growth_signal
related_queries
commercial_use_cases
visual_patterns
saturation_score
opportunity_score
research_timestamp
source_urls
```

No market score may be presented as factual unless its source and timestamp are retained.

## Principle

**StockForge should not ask: "What image can we generate?"**

It should ask:

> **"What commercial visual problem exists, how crowded is the current solution, and what asset can we make that solves that problem better or differently?"**
