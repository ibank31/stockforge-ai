# StockForge Reality Rules

## Global MUST
- Every professional scene has a concrete task.
- Every tool has a concrete purpose and plausible target.
- Human action must be observable.
- Environment must support the task.
- The image must contain visual evidence of the workflow.
- Technical claims must come from a source-backed knowledge pack.

## Global SHOULD
- Prefer documentary realism over futuristic decoration.
- Use natural documentation artifacts when relevant: plans, checklists, tablets, notes, marks.
- Keep composition commercially useful without breaking physical logic.
- Prefer unbranded equipment unless brand is required.
- Prefer specific workflows over generic professional poses.

## Global MUST NOT
- Do not place a tool in a hand merely because it is associated with the profession.
- Do not describe tool use without a target when an affordance relationship is required.
- Do not use holograms as a substitute for physical evidence.
- Do not make a person use a tool contrary to its intended operation.
- Do not stage unnecessary unsafe behavior.
- Do not treat marketplace imagery as technical truth.
- Do not call an image stock-ready solely because it is attractive.

## Failure taxonomy

- `TOOL_IDENTITY`: wrong or ambiguous tool.
- `TOOL_TARGET`: tool is not connected to a plausible target.
- `AFFORDANCE`: physical use is wrong.
- `HUMAN_ACTION`: posture, hands, or action is implausible.
- `OBJECT_CONTEXT`: object/material does not match the task.
- `ENVIRONMENT`: location does not support the workflow.
- `SAFETY`: PPE or behavior is implausible/unsafe.
- `EVIDENCE`: task cannot be understood visually.
- `SYNTHETIC_DECORATION`: unnecessary holograms/CGI overlays reduce realism.
- `COMMERCIAL_CONTEXT`: buyer job is unclear or generic.

## Pre-generation policy

Known `TOOL_TARGET` or `AFFORDANCE` ambiguity must be fixed before GPU generation. Do not spend GPU time discovering deterministic knowledge errors.

## Post-generation policy

Every controlled benchmark records PASS or FAIL plus failure labels. A failure must produce a rule refinement, knowledge correction, or prompt-compiler change before the same concept is regenerated.
