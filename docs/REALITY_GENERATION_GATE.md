# Reality Generation Gate

Before a ZeroGPU generation job is submitted:

1. Select a source-backed workflow.
2. Resolve buyer and buyer job.
3. Resolve object and tool.
4. Resolve tool affordance and target.
5. Resolve observable human action.
6. Resolve visual evidence.
7. Resolve environment and safety.
8. Run deterministic Reality preflight.
9. Compile reality constraints into the prompt.
10. Only then submit the GPU job.

After generation, audit the image using the failure taxonomy in `docs/REALITY_RULES.md`.

A failed image must not simply be regenerated with more adjectives. The failure must be classified and the underlying knowledge, rule, or compiler updated first.

## Minimum benchmark record

- task id
- prompt
- seed
- resolution
- steps
- GPU seconds
- tool correctness
- target correctness
- affordance correctness
- human-action correctness
- environment correctness
- safety correctness
- visible evidence
- commercial usefulness
- Adobe readiness
- failure labels
- corrective change
