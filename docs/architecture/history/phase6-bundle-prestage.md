# Phase 6 Bundle Prestage Checklist

Use this note immediately before staging the standalone `Phase 6` bundle node.

## Intended Scope

This prestage flow is only for the current `Phase 6` bundled node:

- `docs_and_contract`
- `logical_phase6_delta`
- `eval_entrypoints`
- `runtime_foundations`
- `verification_tests`

Use the grouped preview commands instead of manually counting files:

```powershell
python tools/scripts/preview_phase6_bundle_scope.py --summary
python tools/scripts/preview_phase6_bundle_scope.py --dry-run
python tools/scripts/preview_phase6_bundle_scope.py --group logical_phase6_delta
python tools/scripts/preview_phase6_bundle_scope.py --group runtime_foundations --stat
python tools/scripts/verify_phase6_bundle_ready.py
```

If the node has already been committed locally, `verify_phase6_bundle_ready.py` may validate against the committed snapshot instead of the still-dirty worktree, including the current two-commit local Phase 6 chain.

## Prestage Commands

Run these in order:

```powershell
python tools/scripts/preview_phase6_bundle_scope.py --groups
python tools/scripts/preview_phase6_bundle_scope.py --summary
python tools/scripts/preview_phase6_bundle_scope.py --dry-run
python tools/scripts/verify_phase6_bundle_ready.py
git add docs/architecture/plans/current-phase-audit.md docs/architecture/plans/zuno-refactor-execution-plan.md tools/evals/zuno/rag_eval/README.md tools/evals/zuno/rag_eval/run_local_embedding_eval.py tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py tools/evals/zuno/rag_eval/generate_contract_review_scale_corpus.py tests/compat/test_rag_eval_local_launcher.py tests/compat/test_stackless_compare_matrix.py tools/evals/zuno/rag_eval/run_stackless_local_eval.py tools/evals/zuno/rag_eval/summarize_eval_profiles.py tools/evals/zuno/rag_eval/local_embedding_server.py tools/evals/zuno/rag_eval/local_rerank_server.py src/backend/zuno/legacy/agentchat/services/runtime_registry.py src/backend/zuno/legacy/agentchat/services/domain_pack/ src/backend/zuno/legacy/agentchat/services/graphrag/extractors/ src/backend/zuno/legacy/agentchat/services/graphrag/retrievers/ src/backend/zuno/legacy/agentchat/core/graphs/ src/backend/zuno/legacy/agentchat/core/runtime/ tests/compat/test_rag_eval_local_scheme.py tests/compat/test_contract_eval_runner.py tests/compat/test_contract_graph_query_routing.py tests/compat/test_contract_graph_retriever.py tests/compat/test_domain_pack_loader.py tests/compat/test_domain_pack_runtime_flow.py tests/compat/test_domain_qa_graph_offline.py tests/compat/test_general_agent_domain_pack_runtime.py tests/compat/test_graph_retriever_local_runtime.py tests/compat/test_local_embedding_server.py tests/compat/test_local_rerank_server.py tests/compat/test_local_runtime_registry.py tests/compat/test_multi_agent_supervisor_graph_offline.py tests/compat/test_stackless_local_eval_contract_domain_pack.py tests/compat/test_stackless_local_eval_manifest_filter.py tests/compat/test_stackless_local_eval_rerank_runtime.py tests/compat/test_completion_domain_pack_runtime.py tests/compat/test_workspace_domain_pack_runtime.py tests/compat/test_agent_runtime_multi_agent.py tests/compat/test_zuno_alias_imports.py
git diff --cached --stat
```

## What To Confirm

Before treating the bundle as a real `Phase 6` node, confirm:

1. `preview_phase6_bundle_scope.py --summary` still reports `60` changed files in total after real staging expansion
2. the group counts still match the current bundled contract:
   - `docs_and_contract = 3`
   - `logical_phase6_delta = 5`
   - `eval_entrypoints = 4`
   - `runtime_foundations = 22`
   - `verification_tests = 20`
   - `phase6_node_ops = 6`
3. the staged diff still matches the grouped dry-run output
4. the docs claim and the code/test bundle still move together as one node
5. verification tests stay attached to this node instead of becoming a detached proof story
6. the local operation docs/scripts/tests stay attached too, so the staging contract can be rerun later without guesswork

## If The Cached Diff Looks Wrong

Do not move to `Phase 7` yet.

Instead:

```powershell
git diff --cached --stat
python tools/scripts/preview_phase6_bundle_scope.py --summary
python tools/scripts/preview_phase6_bundle_scope.py --dry-run
git diff --cached -- docs/architecture/plans/current-phase-audit.md docs/architecture/plans/zuno-refactor-execution-plan.md tools/evals/zuno/rag_eval/README.md
```

Then compare the cached diff against the current grouped dry-run before restaging.
