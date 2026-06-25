# Contract Review Eval

This directory contains low-cost evaluation scaffolding for the
`contract_review` GraphRAG Project compatibility path.

Current asset source:

- `examples/graphrag-projects/contract_review/`
- The runner uses `GraphRAGProjectLoader` for schema, prompt, retrieval policy,
  and eval dataset assets.
- The runner uses a local GraphRAG Project eval flow and does not execute
  through `DomainQAGraph`.

Profiles:

- `dev_offline`: no external API dependency
- `dev_local`: local or lightweight dependency path
- `demo`: real extraction and answer generation path

Typical usage:

- `python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profile dev_offline`
- `python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profile demo`
- `python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profiles dev_offline,dev_local,demo`
