# StockForge AI — Reality Knowledge Architecture v1

## Purpose

StockForge must generate professional stock imagery from real-world task knowledge, not from object names alone.

The Reality Knowledge Layer converts a buyer/use case into a physically plausible professional scene.

## Core pipeline

Buyer → Buyer Job → Professional Task → Object/Material → Tool → Tool Affordance → Human Action → Visible Evidence → Environment → Safety → Composition → Prompt → Generation → Reality QA → Commercial QA → Adobe QA

## Scene schema

Every professional scene should be representable using these fields:

- `domain`
- `task`
- `problem_or_goal`
- `object`
- `material`
- `tool`
- `tool_affordance`
- `human_action`
- `human_attention`
- `target`
- `visible_evidence`
- `environment`
- `safety`
- `buyer`
- `buyer_job`
- `commercial_use_case`
- `composition`
- `must`
- `should`
- `must_not`
- `sources`

## Tool affordance principle

Knowing the name of a tool is insufficient. The system must know what the tool physically interacts with, how it is oriented or positioned, what the user is doing with it, and what evidence should be visible.

Examples:

### Moisture meter
- target: building material such as drywall, plaster, wood, or masonry
- action: place/scan the meter against the material according to the instrument type
- context: suspected dampness, water intrusion, or moisture investigation
- evidence: affected area, meter interaction with material, inspector observing result
- avoid: meter floating in air or being used like a camera

### Laser distance meter
- target: a measurable surface or point, commonly an opposite wall/opening/element
- action: aim device at the intended target from a plausible measurement origin
- context: room dimensions, openings, heights, lengths, area/volume, or documentation
- evidence: clear geometric relationship between observer, device, and target
- avoid: random aiming, aiming at people, or using it like a total station

### Rebar/cover scanner
- target: concrete surface
- action: scan/move instrument across the concrete element
- context: locating reinforcement or estimating cover depth
- evidence: device in contact/near-contact with concrete surface and plausible structural element
- avoid: holding scanner in mid-air or visually pointing at exposed rebar without a scanning task

## Reality rule levels

### MUST
Facts required for the scene to make professional sense.

### SHOULD
Helpful visual evidence that improves clarity and commercial usefulness.

### MUST_NOT
Conditions that create a technically implausible, contradictory, or synthetic-looking professional scene.

## Source hierarchy

Technical truth must come primarily from authoritative sources:

1. Standards/regulators/professional bodies
2. Manufacturer manuals and technical documentation
3. Professional procedures/training material
4. Marketplace research for commercial/visual patterns
5. Generated images as failure evidence, never as technical authority

Marketplace imagery may reveal buyer demand and visual conventions, but it must not be treated as proof of correct tool usage.

## Reality QA taxonomy

A generated scene can fail independently on:

- `TOOL_IDENTITY`
- `TOOL_TARGET`
- `AFFORDANCE`
- `HUMAN_ACTION`
- `OBJECT_CONTEXT`
- `ENVIRONMENT`
- `SAFETY`
- `VISIBLE_EVIDENCE`
- `SYNTHETIC_DECORATION`
- `COMMERCIAL_CONTEXT`

## GPU efficiency rule

Reality preflight must run before generation. If a concept is internally contradictory, the system should reject or revise the concept without consuming ZeroGPU inference time.

## Construction Knowledge Pack v1 targets

1. Wall moisture inspection
2. Room dimensional measurement
3. Door/window opening measurement
4. Concrete crack inspection
5. Rebar scanning
6. Concrete cover measurement
7. Thermal inspection
8. Floor level checking
9. Concrete surface inspection
10. Construction safety inspection

## Definition of success

A scene is not considered production-ready merely because it looks photorealistic. It must also depict a believable professional task in which the tool, target, human action, environment, and visible evidence agree with one another.
