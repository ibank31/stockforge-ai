# StockForge AI — Buyer × Market Matrix

**Date:** 2026-08-20  
**Status:** Initial strategic model

This matrix converts marketplace demand into buyer-specific visual opportunities. It is a planning model, not a claim that any listed segment will purchase an asset.

| Industry / topic | Buyer | Typical role | Communication job | Asset opportunity | Differentiation lever |
|---|---|---|---|---|---|
| Construction technology | SaaS/product marketing | Product marketer | Website / case study | Digital workflow on real site | physical + digital relationship |
| Construction safety | Contractor | Safety / project manager | Training / website | Specific inspection behavior | authentic workflow |
| Construction engineering | Consultant | Engineer / BD | Proposal / report | Technical review context | credible process detail |
| Property development | Developer | Marketing manager | Brochure / campaign | Development planning | local/regional context |
| Infrastructure | Engineering / government supplier | Communications | Report / presentation | Infrastructure planning | scale + context |
| Sustainability | Corporate / ESG | Communications manager | ESG report | Human + environmental consequence | specific action, not abstract green imagery |
| AI / business | SaaS / enterprise | Demand generation | Landing page / blog | Human interaction with AI workflow | avoid generic robot/laptop clichés |
| Healthcare technology | Health-tech | Marketing / content | Website / campaign | Clinician + specific digital workflow | authentic clinical context |
| Education technology | EdTech | Growth / content | Social / website | Teacher/student workflow | age/context specificity |
| Logistics technology | Logistics SaaS | Product marketing | Website / article | Warehouse + digital coordination | operational specificity |
| Cybersecurity | B2B SaaS | Marketing / editorial | Article / campaign | Human security workflow | avoid cliché hacker imagery |
| Local SMB | Owner / marketer | Social / web | Promotion / content | authentic local business scene | regional specificity |

## Buyer-first prompt rule

Before prompt generation, the engine should answer:

1. Who is likely to use the asset?
2. What are they trying to communicate?
3. Where will it appear?
4. What visual convention is over-supplied?
5. What specific situation makes this asset more useful than a generic alternative?
6. What composition lets the buyer actually design with it?

If these questions cannot be answered with evidence or an explicitly marked hypothesis, the opportunity remains `REVIEW`.

## Evidence boundary

Buyer segments are derived from public marketplace documentation and industry use cases. Public sources show categories of customers and common uses, but they do not expose complete individual purchase histories. StockForge must therefore store confidence and evidence URLs with every automated opportunity.

## Strategic principle

**The buyer is the unit of differentiation.**

A niche is too broad. A keyword is too shallow. The useful unit is:

`buyer + communication problem + channel + visual situation + differentiation`
