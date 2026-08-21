# Reality Compiler Integration Test Plan

## Current controlled workflow

`wall_moisture_inspection`

This is intentionally hard-coded for the first integration benchmark. It prevents the first test from mixing workflow-selection bugs with reality-compiler bugs.

## Expected transformation

User concept → validated construction workflow → compiled physical constraints → Z-Image prompt.

The compiled prompt must explicitly contain:

- moisture inspection task
- appropriate building material target
- moisture meter interaction with the material
- inspector attention to the measurement
- plausible moisture evidence
- real construction/building environment
- prohibited synthetic decoration

## GPU policy

Reality preflight and prompt compilation occur before `generate_gpu()` is entered. A rejected workflow must therefore consume no ZeroGPU inference time.

## First benchmark success criteria

1. Space reaches RUNNING.
2. `/generate` remains compatible with the existing API.
3. One 1024×1024, 8-step generation completes.
4. Generated scene shows a coherent moisture-inspection workflow.
5. Moisture meter has a plausible physical relationship with the wall/material.
6. Inspector is performing the task rather than posing with the tool.
7. No holographic moisture UI or unrelated futuristic decoration is introduced.
8. Output remains commercially useful as construction/building-inspection stock.

## Failure classification

If the benchmark fails, classify the failure before changing code:

- TOOL_IDENTITY
- TOOL_TARGET
- AFFORDANCE
- HUMAN_ACTION
- OBJECT_CONTEXT
- ENVIRONMENT
- SAFETY
- VISIBLE_EVIDENCE
- SYNTHETIC_DECORATION
- COMMERCIAL_CONTEXT

Do not spend additional GPU runs until the failure hypothesis and code/rule change are recorded.
