# Reality Knowledge v1

Date: 2026-08-20
Status: Implemented on `feat/zerogpu-runtime`

StockForge now has a domain-neutral Reality layer before generation.

## Implemented

- `src/stockforge/reality.py`: ToolAffordance, RealityRules, RealityScene, deterministic preflight.
- `src/stockforge/reality_prompt.py`: prompt compilation from validated physical relationships.
- `src/stockforge/knowledge.py`: structured knowledge-pack loader.
- `src/stockforge/knowledge/construction_v1.json`: ten construction workflows with source provenance and must/should/must-not rules.
- `tests/test_reality_knowledge.py`: deterministic tests for pack integrity and affordance rejection.
- `docs/REALITY_RULES.md`: global reality rules and failure taxonomy.

## Construction workflows

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

## Key rule

A professional tool is not a prompt noun. StockForge models the relationship:

`task -> object -> tool -> affordance -> human action -> evidence -> environment`

## Source policy

Manufacturer and professional documentation establish technical truth. Marketplace research is a commercial signal only. Generated-image failures are internal evidence for rule refinement.

## GPU policy

ZeroGPU is used only after deterministic preflight. A failed generation must become a knowledge, rule, or test update rather than another blind prompt attempt.

## Next gate

Integrate the Reality compiler into the active production prompt path, then run one controlled construction benchmark. Judge tool-to-target correctness before visual polish.
