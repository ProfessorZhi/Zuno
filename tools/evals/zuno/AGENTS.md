# Zuno Eval Agent Rules

Before changing `tools/evals/zuno`, read:

1. `.agent/references/verification-map.md`
2. `.agent/workflows/eval-change.md`

Rules:

- Smoke tests are not formal evals.
- Eval configuration, dataset, metrics, and output paths must be traceable.
- Do not overwrite historical baselines.
- Keep local run artifacts separate from public evidence.
