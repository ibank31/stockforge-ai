# Pipeline Contract

## Purpose

The pipeline layer defines production steps without knowing which provider executes them. A pipeline is a versioned, ordered list of steps. Provider credentials, network configuration, and model secrets are deliberately outside the pipeline definition.

## Step contract

Each step declares:

- `id`: stable step identifier within the pipeline.
- `plugin_id`: registered plugin responsible for execution.
- `capability`: required capability exposed by that plugin.
- `input_key`: state object consumed by the step.
- `output_key`: state object produced by the step.
- `parameters`: provider-neutral step parameters.

The runner validates the capability before execution and rejects non-object inputs or outputs.

## Reproducibility

The pipeline definition is serializable and versioned. Future production records should persist the exact pipeline definition/version alongside job and asset provenance. Provider/model versions, workflow hashes, seeds, and generated artifacts belong to the provenance layer and must not be hidden inside arbitrary parameters.

## Execution model

The initial runner is intentionally linear and deterministic. DAG scheduling, conditional branches, parallel fan-out, caching, and resumable execution are later extensions that must preserve the same explicit step contract.

## Stock asset requirement

A marketplace production pipeline should eventually resemble:

1. opportunity/concept selection
2. prompt construction
3. generation
4. image validation
5. enhancement/upscale
6. duplicate/similarity screening
7. metadata generation
8. compliance gate
9. export/submission package

No marketplace provider is hard-coded into this core contract.
