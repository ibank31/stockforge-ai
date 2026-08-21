# StockForge Reality Knowledge Architecture

Status: IMPLEMENTED / v1
Date: 2026-08-20

StockForge must generate stock imagery that is visually attractive **and physically/professionally plausible**. The construction tests showed that prompt wording alone is insufficient when the relationship between task, tool, target, and human action is wrong.

## Pipeline

```text
MARKET -> BUYER -> BUYER JOB -> PROFESSIONAL TASK -> DOMAIN KNOWLEDGE
      -> TOOL + OBJECT -> TOOL AFFORDANCE -> HUMAN ACTION -> VISIBLE EVIDENCE
      -> ENVIRONMENT + SAFETY -> COMPOSITION -> PROMPT -> GENERATION
      -> REALITY QA -> COMMERCIAL QA -> ADOBE GATE
```

## Knowledge contract

Each professional workflow should define:

- domain
- task
- problem
- object
- tool
- affordance
- human_action
- environment
- visual_evidence
- safety
- buyer_segments
- buyer_jobs
- composition
- must
- should
- must_not
- sources

## Evidence hierarchy

1. Manufacturer documentation/manuals: tool operation and affordance.
2. Professional standards/guidance: procedure, safety, terminology.
3. Training/professional organizations: workflow context.
4. Marketplace research: commercial patterns only, never technical truth.
5. Generated-image audits: internal evidence for improving rules.

## Reality Gate

A scene must be rejected or corrected before being called stock-ready when:

1. Tool identity or placement is implausible.
2. Tool-to-target relationship is missing or wrong.
3. Human action/posture is implausible.
4. Object/material is incompatible with the task.
5. Environment does not support the workflow.
6. Safety/PPE is implausible where relevant.
7. The stated task has no visible evidence.
8. Unnecessary holograms/CGI effects replace physical evidence.
9. Avoidable logos/brands create commercial risk.
10. The buyer's communication job is unclear.

A beautiful image that fails Reality Gate is **not stock-ready**.

## Construction v1

The first knowledge pack covers ten workflows: wall moisture inspection, room dimensional measurement, door/window opening measurement, concrete crack inspection, rebar scanning, concrete cover measurement, thermal inspection, floor level checking, concrete surface inspection, and construction safety inspection.

## GPU policy

ZeroGPU time is a validation instrument, not a brainstorming mechanism. Validate market fit, task/tool relationship, and deterministic reality constraints before consuming GPU time. Every failed generation becomes a rule, knowledge, or test update.

## Completion policy

A domain feature is complete only when it has structured knowledge, source provenance, must/should/must-not rules, prompt compilation support, deterministic tests, and a generation audit when GPU validation is required.
