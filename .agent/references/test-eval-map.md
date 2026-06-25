# Test And Eval Map

## Purpose

Orient test and eval changes.

## Current Paths

- Repo tests: `tests/`
- Compatibility tests: `tests/compat/`
- Multihop evals: `tools/evals/zuno/multihop_eval/`
- RAG evals: `tools/evals/zuno/rag_eval/`
- Contract review evals: `tools/evals/zuno/contract_review_eval/`

## Rule

Smoke tests are not formal evals. Historical baselines must not be overwritten.
Generated local outputs stay ignored unless promoted deliberately.
