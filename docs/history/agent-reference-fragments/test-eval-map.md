# Test And Eval Map

## Purpose

Orient test and eval changes.

## Current Paths

- Repo tests: `tests/`
- Migration compatibility tests: `tests/`
- Multihop evals: `tools/evals/zuno/multihop_eval/`
- RAG evals: `tools/evals/zuno/rag_eval/`
- Contract review evals: `tools/evals/zuno/contract_review_eval/`

Contract Review and stackless local evals load GraphRAG Project assets as the
current mainline evidence. Their graph extraction calls should use
`project_payload=project_payload`; active graph extractor APIs no longer expose
a `domain_pack` payload alias. Stackless local eval must not restore a private
`_load_graph_project_domain_payload` alias.
Contract Review stackless local eval coverage should use
`tests/test_stackless_local_eval_contract_project_query_policy.py` and
`graphrag_project_id`; the old Domain Pack named test file must not return as a
current test.

## Rule

Smoke tests are not formal evals. Historical baselines must not be overwritten.
Generated local outputs stay ignored unless promoted deliberately.
