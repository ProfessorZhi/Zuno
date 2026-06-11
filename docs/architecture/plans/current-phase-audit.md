# Current Phase Audit

## Status Snapshot (2026-06-11)

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: completed
- `Phase 4`: completed
- `Phase 5`: completed
- `Phase 6`: completed
- `Phase 7`: current serial phase

## Current Default Judgment

Do not declare the final interview-facing closure complete yet.

The active serial problem is now `Phase 7`: align the final interview-facing runtime, docs, evaluation story, and GitHub showcase surface on top of the now-closed `Phase 1-6` mainline.

This branch is using the current `main` line as the real base. That matters:

- the clean `main` base already contains the new serial `Phase 1-5` line
- the just-closed `Phase 6` delta was judged against `main`, not against an older local "foundation-first" branch story
- the next serial decision can therefore move forward from a verified `Phase 6` bundle instead of carrying an unresolved proof gap

## Phase 6 Closure Evidence

The current repo state now proves the following `Phase 6` runtime and proof-surface steps:

- `run_eval.py` now exposes a stable profile contract for the local-eval chain again:
  - `resolve_profiles()` exists again
  - `local_compare` resolves to `baseline_rag`, `rag_rerank`, `rag_graph_chunk_backed`
  - `graph_compare` resolves to `baseline_rag`, `rag_graph_chunk_backed`, `rag_graph_chunk_backed_3hop`
  - old names (`rag_graph`, `rag_graph_3hop`) still resolve as compatibility aliases instead of breaking older callers
- `run_stackless_compare_matrix.py` is present again as a real committed Phase 6 entrypoint instead of a missing file referenced only by tests and docs
- the stackless / local-eval helper chain is now self-consistent on this branch:
  - `run_local_embedding_eval.py`
  - `run_stackless_local_eval.py`
  - `run_stackless_compare_matrix.py`
  - `summarize_eval_profiles.py`
  - `local_embedding_server.py`
  - `local_rerank_server.py`
- the domain/runtime support required by that local-eval chain is also now restored on this branch:
  - `services/runtime_registry.py`
  - `services/domain_pack/`
  - `services/graphrag/extractors/`
  - `services/graphrag/retrievers/`
  - `core/graphs/`
  - `core/runtime/`
- the current minimum verification surface for the restored Phase 6 chain is green:
  - `pytest -q src/backend/agentchat/test/test_contract_eval_runner.py src/backend/agentchat/test/test_rag_eval_local_scheme.py src/backend/agentchat/test/test_stackless_compare_matrix.py src/backend/agentchat/test/test_rag_eval_local_launcher.py`
  - latest result on this branch: `24 passed`
- the restored domain-pack / runtime compatibility surface is also green:
  - `pytest -q src/backend/agentchat/test/test_domain_pack_runtime_flow.py src/backend/agentchat/test/test_completion_domain_pack_runtime.py src/backend/agentchat/test/test_workspace_domain_pack_runtime.py src/backend/agentchat/test/test_general_agent_domain_pack_runtime.py`
  - latest result on this branch: `12 passed`
- the broader Phase 6 bundle verification now matches the current worktree truth:
  - `python tools/scripts/verify_docs_surface.py`
  - `python tools/scripts/preview_phase6_bundle_scope.py --summary`
  - `python tools/scripts/verify_phase6_bundle_ready.py`
  - `pytest -q tests/test_docs_surface_consistency.py tests/test_publish_boundary.py tests/test_phase6_bundle_scope.py src/backend/agentchat/test/test_contract_eval_runner.py src/backend/agentchat/test/test_rag_eval_local_scheme.py src/backend/agentchat/test/test_stackless_compare_matrix.py src/backend/agentchat/test/test_rag_eval_local_launcher.py src/backend/agentchat/test/test_domain_pack_runtime_flow.py src/backend/agentchat/test/test_completion_domain_pack_runtime.py src/backend/agentchat/test/test_workspace_domain_pack_runtime.py src/backend/agentchat/test/test_general_agent_domain_pack_runtime.py`
  - latest combined result on this branch: `48 passed`

## What Is Still Not Closed

`Phase 6` is no longer the blocking serial phase.

What still needs to be closed now is the final `Phase 7` surface:

- the final interview-facing runtime / docs / showcase story still needs its own last cleanup pass
- the final `Phase 7` prestage/ready notes still need to become the active closure checklist
- the repository still needs the final `Phase 7` GitHub node after this `Phase 6` merge lands

## Current Phase 6 Bundle Shape

From the current clean branch tip, the realistic `Phase 6` bundled node is:

- `docs_and_contract`
  - `docs/architecture/plans/current-phase-audit.md`
  - `docs/architecture/plans/zuno-refactor-execution-plan.md`
  - `src/backend/agentchat/evals/rag_eval/README.md`
- `logical_phase6_delta`
  - `run_local_embedding_eval.py`
  - `run_stackless_compare_matrix.py`
  - `generate_contract_review_scale_corpus.py`
  - `test_rag_eval_local_launcher.py`
  - `test_stackless_compare_matrix.py`
- `eval_entrypoints`
  - `run_stackless_local_eval.py`
  - `summarize_eval_profiles.py`
  - `local_embedding_server.py`
  - `local_rerank_server.py`
- `runtime_foundations`
  - `services/runtime_registry.py`
  - `services/domain_pack/`
  - `services/graphrag/extractors/`
  - `services/graphrag/retrievers/`
  - `core/graphs/`
  - `core/runtime/`
- `verification_tests`
  - the associated `agentchat/test` proof surface for domain packs, local runtime, retrievers, and stackless eval
- `phase6_node_ops`
  - the grouped preview script
  - the readiness verifier
  - the bundle-scope test
  - the plan notes that describe how to stage this node reproducibly

In the current worktree, that grouped bundle evaluates to:

- `docs_and_contract = 3`
- `logical_phase6_delta = 5`
- `eval_entrypoints = 4`
- `runtime_foundations = 6`
- `verification_tests = 19`
- `phase6_node_ops = 6`
- `total_changed = 43`

This is stricter than the older local note that assumed a separate foundation node had already landed. On the current `main` base, the broader bundled node is the honest contract.

## Current Bundle Commands

Use the grouped preview commands instead of manually guessing the bundle:

- `python tools/scripts/preview_phase6_bundle_scope.py --groups`
- `python tools/scripts/preview_phase6_bundle_scope.py --summary`
- `python tools/scripts/preview_phase6_bundle_scope.py --group logical_phase6_delta`
- `python tools/scripts/preview_phase6_bundle_scope.py --group runtime_foundations --stat`
- `python tools/scripts/preview_phase6_bundle_scope.py --dry-run`
- `python tools/scripts/preview_phase6_bundle_scope.py --stage-command`
- `python tools/scripts/verify_phase6_bundle_ready.py`

## Phase 6 Verification Record

The current minimum `Phase 6` branch checks include:

1. `pytest -q src/backend/agentchat/test/test_contract_eval_runner.py src/backend/agentchat/test/test_rag_eval_local_scheme.py src/backend/agentchat/test/test_stackless_compare_matrix.py src/backend/agentchat/test/test_rag_eval_local_launcher.py`
2. `python tools/scripts/preview_phase6_bundle_scope.py --summary`
3. `python tools/scripts/verify_phase6_bundle_ready.py`

These checks now answer three different questions:

- do the current Phase 6 eval entrypoints and profile contracts actually import and run
- does the grouped bundle still describe the current branch reality
- is the staged-node contract reproducible instead of being a one-off local guess

## Next Exact Step

Stay on `Phase 7`.

The next exact step is:

- use `phase7-final-prestage.md` and `phase7-final-ready.md` as the live closure checklist
- keep the final runtime / docs / publish-boundary proof surface aligned
- prepare the final interview-facing GitHub showcase node
- only then close `Phase 7`
