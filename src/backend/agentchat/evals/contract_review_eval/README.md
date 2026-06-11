# Contract Review Eval

This directory contains low-cost evaluation scaffolding for the `contract_review` domain pack.

Profiles:

- `dev_offline`: no external API dependency
- `dev_local`: local or lightweight dependency path
- `demo`: real extraction and answer generation path

Typical usage:

- `python src/backend/agentchat/evals/contract_review_eval/run_contract_eval.py --profile dev_offline`
- `python src/backend/agentchat/evals/contract_review_eval/run_contract_eval.py --profile demo`
- `python src/backend/agentchat/evals/contract_review_eval/run_contract_eval.py --profiles dev_offline,dev_local,demo`
