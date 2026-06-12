# Contract Review Eval

This directory contains low-cost evaluation scaffolding for the `contract_review` domain pack.

Profiles:

- `dev_offline`: no external API dependency
- `dev_local`: local or lightweight dependency path
- `demo`: real extraction and answer generation path

Typical usage:

- `python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profile dev_offline`
- `python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profile demo`
- `python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profiles dev_offline,dev_local,demo`
