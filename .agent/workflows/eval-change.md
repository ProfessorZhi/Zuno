# Eval Change Workflow

## Trigger

Use for `tools/evals/zuno`, eval datasets, metrics, profiles, reports, or
public evidence changes.

## Rules

- Smoke tests are not formal evals.
- Eval config, dataset, metrics, and output path must be traceable.
- Do not overwrite historical baselines.
- Local run outputs and public evidence stay separate.

## Verification

Run the smallest eval/test that proves the changed behavior and record whether
external services were required.
