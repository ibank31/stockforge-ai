# StockForge AI — Buyer Segment Intelligence

**Version:** 1.0  
**Date:** 2026-08-20  
**Status:** Research foundation; scoring model defined, automated collection not yet implemented

## Why buyer intelligence exists

A marketplace query tells us what people search for. It does not tell us why an asset is useful. StockForge therefore models the **buyer and the communication job** behind an asset.

Primary evidence from Shutterstock identifies three broad customer groups: corporate professionals/organizations, media and broadcast companies, and SMBs/individual creators. Shutterstock also describes use across websites, advertising, annual reports, brochures, employee communications, newsletters, email marketing, presentations, digital advertising, websites/apps, print, video, and content marketing. Adobe's 2026 trend research likewise emphasizes relevance, usefulness, human connection, authenticity, and regional specificity.

These broad groups must be converted into actionable buyer segments.

## Buyer hierarchy

```text
MARKETPLACE
  ↓
CUSTOMER TYPE
  ↓
INDUSTRY
  ↓
JOB ROLE / CREATIVE ROLE
  ↓
COMMUNICATION TASK
  ↓
PLACEMENT / CHANNEL
  ↓
VISUAL REQUIREMENT
  ↓
ASSET CONCEPT
```

## Core buyer segments

### 1. Brand / Marketing teams

**Who:** marketing managers, brand managers, campaign teams, content strategists.

**Work:** websites, campaigns, social, email, landing pages, product launches, thought leadership.

**They buy:** instantly understandable scenes, authentic people, strong focal point, usable negative space, multiple aspect-ratio compositions.

**StockForge opportunity:** create assets with an explicit communication message rather than generic lifestyle scenes.

**Uniqueness levers:**
- campaign theme
- audience identity
- emotion
- channel-specific framing
- copy space
- seasonal/contextual relevance

### 2. Creative agencies

**Who:** art directors, designers, copywriters, creative directors, production teams.

**Work:** client campaigns, advertising, brand systems, presentations, editorial design.

**They buy:** flexible visuals that can be art-directed into a larger composition.

**Uniqueness levers:**
- unusual but believable visual situations
- clean separation between subject and background
- intentional composition
- multiple crops
- visual metaphor where commercially useful

### 3. Corporate communications / PR

**Who:** communications managers, PR agencies, internal communications teams, investor-relations teams.

**Work:** annual reports, corporate announcements, employer communications, ESG reports, press materials.

**They buy:** credible business situations, diverse but believable teams, restrained aesthetics, copy space, non-branded environments.

**Uniqueness levers:**
- specific business topic
- governance / sustainability / workforce / transformation stories
- realistic workplace behavior
- presentation-safe layouts

### 4. SaaS / technology companies

**Who:** product marketing, demand generation, growth teams, startup founders, UX/content teams.

**Work:** landing pages, product marketing, blog posts, case studies, decks, ads.

**They buy:** visual explanations of abstract technology problems.

**Uniqueness levers:**
- show technology interacting with the physical world
- specific workflow rather than generic laptop imagery
- human + system relationship
- data/technology visual cues without fake readable UI text
- copy space for product messaging

### 5. Construction / engineering / property companies

**Who:** developers, contractors, engineering consultants, architects, construction software vendors, suppliers.

**Work:** project proposals, tender documents, websites, brochures, investor presentations, safety campaigns, training, case studies.

**They buy:** authentic project workflows, site context, engineering processes, safety, infrastructure, planning, materials, digital transformation.

**Uniqueness levers:**
- specific construction problem
- BIM/digital twin
- safety inspection
- predictive maintenance
- infrastructure analytics
- climate resilience
- supply-chain visibility
- regional construction context
- tender/project communication

### 6. Publishers / editorial content teams

**Who:** publishers, bloggers, educational publishers, magazine teams, online media.

**Work:** articles, explainers, reports, books, newsletters.

**They buy:** literal visual explanations of the article topic, often with room for headlines.

**Uniqueness levers:**
- topic specificity
- explanatory composition
- editorial-safe negative space
- contextual details

**Important:** StockForge's commercial-first pipeline should avoid generating newsworthy events or real-person depictions merely to chase editorial demand. Adobe and marketplace licensing rules must be respected.

### 7. Social media creators / SMBs

**Who:** small business owners, freelancers, influencers, solo marketers.

**Work:** social posts, ads, blogs, newsletters, simple presentations.

**They buy:** immediately usable, relatable images that communicate one idea quickly.

**Uniqueness levers:**
- vertical-first compositions
- strong subject readability
- relatable everyday situations
- local/regional authenticity
- simple visual storytelling

## Buyer-specific composition matrix

| Buyer | Typical job | Preferred visual strategy |
|---|---|---|
| Brand marketing | Campaign / landing page | Strong hero + copy space |
| Creative agency | Campaign composition | Flexible subject/background separation |
| Corporate comms | Report / announcement | Credible, restrained, presentation-safe |
| SaaS | Product storytelling | Human + technology workflow |
| Construction/engineering | Project communication | Authentic site/process context |
| Publisher | Article illustration | Literal topic clarity + headline space |
| SMB/social | Quick communication | Vertical, relatable, immediately legible |

## Buyer-specific uniqueness rule

The same subject should **not** be generated identically for every buyer.

Example: construction safety.

### SaaS buyer

Visual problem: communicate digital safety workflow.

Concept: supervisor reviewing a mobile safety anomaly dashboard beside a live site.

### Contractor

Visual problem: communicate site safety culture.

Concept: supervisor conducting a real toolbox briefing with PPE and active work area.

### Engineering consultant

Visual problem: communicate risk assessment.

Concept: engineer comparing site conditions with technical plans and inspection evidence.

### Corporate/ESG team

Visual problem: communicate workforce safety investment.

Concept: safety training in a modern construction environment with deliberate report-style composition.

### Publisher

Visual problem: illustrate construction safety technology.

Concept: contextual close-up showing PPE, inspection device, worker, and site environment.

The topic stays related, but the **communication job changes the image**.

## Buyer-to-asset scoring

Future Concept Engine should calculate:

```text
buyer_fit
use_case_fit
channel_fit
visual_clarity
copy_space_fit
specificity
regional_relevance
uniqueness
saturation_risk
variation_value
```

Suggested initial weighting:

| Signal | Weight |
|---|---:|
| Buyer/use-case fit | 25 |
| Visual differentiation | 20 |
| Marketplace opportunity | 15 |
| Commercial clarity | 15 |
| Composition/layout utility | 10 |
| Regional/context relevance | 5 |
| Variation potential | 5 |
| Compliance risk | 5 |

These are **StockForge internal heuristics**, not marketplace rules. They must be validated against portfolio outcomes later.

## Buyer research evidence

Shutterstock states that its customers include corporate professionals and organizations, media/broadcast companies, SMBs and individual creators. It describes business use across websites, advertisements, annual reports, brochures, employee communications, newsletters, email marketing and presentations.

Shutterstock's current use-case documentation explicitly includes digital advertising, website/app builders, print/merchandise, video creation, and content/email marketing.

Shutterstock's customer case studies show use by major brands and organizations including Facebook, Microsoft, AWS, Porsche, Snapchat and others, reinforcing that stock assets serve both internal creative teams and external campaign production.

Adobe's 2026 Creative Trends research states that its trends are informed by commercial campaigns, customer feedback and search history, and emphasizes useful, relevant, relatable and regionally specific visual content.

## Research limitations

Buyer segment labels are useful planning abstractions, not direct evidence that a particular person will purchase a particular image. Marketplace customer databases are not fully public, and public search counts are not sales data.

StockForge must therefore record evidence and confidence rather than presenting buyer assumptions as facts.

## Automation target

Future Market Intelligence should output a buyer profile for every opportunity:

```json
{
  "buyer_segment": "construction_technology_marketing",
  "industry": "construction_technology",
  "roles": ["product_marketing", "content_marketing", "creative_director"],
  "communication_jobs": ["website_hero", "blog_article", "case_study", "presentation"],
  "channels": ["web", "social", "presentation", "email"],
  "visual_requirements": ["authentic_workflow", "copy_space", "non_branded_ui"],
  "uniqueness_levers": ["physical_digital_relationship", "specific_workflow"],
  "confidence": 0.0,
  "evidence": []
}
```

## Principle

**Do not create an image for a niche. Create an image for a buyer's communication problem inside that niche.**
