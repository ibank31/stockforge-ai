# Reality Knowledge v1

Implemented on `feat/zerogpu-runtime`.

## Machine-enforced layer

- Domain-neutral `RealityScene` contract.
- `ToolAffordance` relationship between tool and target.
- `RealityRules` with MUST / SHOULD / MUST NOT constraints.
- Deterministic `reality_preflight()` before GPU generation.
- Reality-aware prompt compiler.
- Structured construction knowledge pack with ten workflows.
- Source provenance and evidence hierarchy.
- Failure taxonomy and generation gate documentation.

## Design principle

A professional tool is never treated as a decorative noun. The system must model:

`task -> object -> tool -> affordance -> human action -> visible evidence -> environment`

## Research basis

Technical behavior is grounded in manufacturer/professional sources including Leica Geosystems, Hilti, Tramex, and FLIR. Adobe Stock remains the final submission gate. Marketplace research is used only for commercial demand and differentiation.

## GPU discipline

No GPU generation is used to discover deterministic tool-use knowledge. If a generated image fails reality, the failure must first update a rule, knowledge item, or compiler before another generation.
