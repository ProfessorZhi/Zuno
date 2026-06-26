# Current Phase Audit

## Status Snapshot (2026-06-10)

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: completed
- `Phase 4`: completed
- `Phase 5`: completed
- `Phase 6`: completed
- `Phase 7`: current default phase

## Phase 4 Closure Evidence

The highest-value `api/v1` controller routes now delegate runtime orchestration through `api/services` instead of importing lower-level runtime and infrastructure modules directly:

- `user`, `knowledge`, `knowledge_file`
- `upload`, `completion`, `wechat`
- `mcp_server`, `workspace`
- `capability`, `tool`

Current audit evidence from the repo state:

- `src/backend/zuno/api/v1` no longer directly imports `zuno.services.*`, `zuno.core.*`, or `zuno.tools.*`
- `tests/test_layered_api_boundaries.py`
- `tests/test_zuno_runtime_chain_guard.py`
- targeted `tests/test_zuno_public_entrypoints.py` checks for `workspace`, `mcp_server`, `capability`, and `tool`
- `import zuno.main` + `create_app` smoke

## Phase 3 Closure Evidence

The public documentation surface is now explicitly split between first-time readers and maintainers:

- `README.md` exposes a short first-read path and a separate maintainer-only release workflow section.
- `docs/README.md` stops the public reading order at the public demo path and moves maintainer docs into a separate entrypoint section.
- `docs/development/README.md` is explicitly marked as maintainer-facing and not part of the first-read public path.

Phase 3 minimum checks passed with the current repo state:

- `python tools/scripts/verify_docs_entrypoints.py`
- `pytest -q tests/test_docs_entrypoints.py`
- `python tools/scripts/verify_public_demo_docs.py`
- `pytest -q tests/test_publish_boundary.py tests/test_repo_structure_consistency.py`

## Next Default Step

Proceed to `Phase 7`: do the final interview-facing total cleanup on top of the now-published `Phase 6` evidence bundle, keeping code, structure, docs, evaluation, and presentation story aligned.

## Phase 6 Current Evidence

`Phase 6` is now technically mature enough for closure from the current repo state, and this run now also has a standalone local phase node:

- local isolated commit formed: `01d3db0 phase6: solidify eval evidence bundle`
- this closes the earlier "node not formed yet" process gap inside the local repository state
- the remaining gap is narrower now: remote GitHub push has not yet been completed from this environment, and `Phase 7` should still wait until that serial publish step is handled

- the `contract_review_eval` demo profile no longer drops graph-path evidence when a clause heading and clause body live on the same line
  - root cause was in `StructuredGraphExtractor._find_clause_sections()`, which previously ignored inline clause bodies such as `第八条 违约责任：...`
  - the extractor now keeps inline clause content, so structured extraction can emit `Clause` / `Risk` relations for the demo contract path
- the local embedding preflight path no longer hangs on avoidable heavyweight imports and avoidable DB access
  - `run_local_embedding_eval.py` now lazy-loads the embedding runtime instead of importing the full embedding stack at module import time
  - explicit `text_embedding_model_id` no longer forces `resolve_embedding_model_id() -> list_llm_candidates() -> LLMDao.get_all_llm()` before validation
- the Phase 6 candidate test surface now has a green baseline:
  - `tests/compat/test_contract_eval_runner.py`
  - `tests/compat/test_rag_eval_local_scheme.py`
  - `tests/compat/test_stackless_compare_matrix.py`
  - `tests/compat/test_rag_eval_local_launcher.py`
  - latest combined result: `22 passed`
- the public demo verification layer is now green as a whole instead of only partially sampled:
  - `python tools/scripts/verify_public_demo_runtime.py`
  - `python tools/scripts/verify_public_demo_strict_grounding.py`
  - targeted `pytest -q tests/test_publish_boundary.py -k "public_demo_runtime_verifier_script_mentions_contract_review_smoke_expectations or public_readme_explains_why_contract_review_needs_graphrag"`
  - latest result: verifier scripts passed and the targeted publish-boundary checks passed
- the local embedding preflight path is now also proven with a real local request instead of only monkeypatched tests:
  - `local_embedding_server.py` was started locally
  - `run_local_embedding_eval.py --validate-only --local-embedding-model-name zuno-local-embedding-dev --local-embedding-base-url http://127.0.0.1:11434/v1`
  - latest result: a real embedding probe completed with `dimension = 64`
- the compare-matrix proof surface now has a real stackless contract-review run artifact:
  - `run_stackless_compare_matrix.py` completed against `contract_review_graph_relation_small.jsonl`
  - output root: `.local/evals/agentchat/rag_eval/runs/stackless-contract-review-phase6`
  - the five retrieval metrics plus faithfulness / citation accuracy are now written to `summary.json` and `summary.md`
  - current acceptance surface is informative but not yet a closure proof: `prefer_rerank_when_tied = no` while the other three matrix gates are `yes`
- the compare-matrix surface now exposes coverage metadata so a tiny slice cannot masquerade as a system-level conclusion:
  - the earlier `sample_limit = 3` run only covered `3` sampled questions, `2` referenced files, and `2` indexed chunks
  - `summary.md` / `summary.json` now show sampled-question count, unique referenced file count, chunk count, and a low-coverage warning
  - this turns the earlier flat `s3` result into a debuggable evidence artifact instead of a misleading headline
- the larger contract-review matrix run now gives a stronger baseline for interpretation:
  - output root: `.local/evals/agentchat/rag_eval/runs/stackless-contract-review-phase6-s12`
  - current run covers `12` sampled questions and `8` indexed chunks
  - current result: GraphRAG is not worse than baseline and improves `MRR` / `NDCG` over baseline, but it still does not beat the `rag_rerank` line on the default acceptance story
- the scaled-corpus hypothesis has now been verified with a harder local corpus instead of staying as a README suggestion:
  - `generate_contract_review_scale_corpus.py --copies-per-file 4` produced `40` local contract files under `contract_review_scale_phase6`
  - the scaled matrix run at `.local/evals/agentchat/rag_eval/runs/stackless-contract-review-scale-phase6-s12` covers `12` sampled questions, `8` referenced gold files, and `40` indexed chunks
  - on this harder corpus, `rag_graph_chunk_backed` now clearly beats both `baseline_rag` and `rag_rerank`
    - vs `baseline_rag`: recall `0.5000 > 0.3333`, MRR `0.5000 > 0.2153`, NDCG `0.5000 > 0.2442`, citation accuracy `0.5000 > 0.3333`
    - vs `rag_rerank`: recall `0.5000 > 0.2500`, MRR `0.5000 > 0.1944`, NDCG `0.5000 > 0.2083`, citation accuracy `0.5000 > 0.2500`
  - the matrix acceptance layer is now fully green on the scaled corpus, including `prefer_rerank_when_tied = yes`
  - this closes the earlier ambiguity: the flat result on the smaller corpus was largely a data-volume / distractor-pressure issue, not proof that GraphRAG had no local value
- the one-command local embedding eval entry now has a real runnable fallback instead of failing hard when the local database is absent:
  - root cause of the previous failure was not the embedding endpoint itself, but the database-backed `LLMDao` / ingest path trying to connect to `localhost:5432`
  - `run_local_embedding_eval.py` now falls back to `run_stackless_local_eval` when a direct local embedding target is provided and the DB-backed registration / ingest path is unavailable
  - the fallback preserves one-command local-eval semantics and writes the usual `summary.json` / `summary.md`
  - real proof run: `.local/evals/agentchat/rag_eval/runs/local-embedding-phase6-contract-review-fallback`
  - current full-command result on the contract-review dataset is strong:
    - `rag_graph_chunk_backed` recall `1.0000`
    - `rag_graph_chunk_backed` MRR `0.9583`
    - `rag_graph_chunk_backed` NDCG `0.9692`
    - `rag_graph_chunk_backed` citation accuracy `1.0000`
    - baseline / rerank both stay at recall `0.9167`, MRR `0.6528`, NDCG `0.7212`, citation accuracy `0.9167`
- the contract-review public demo runtime path is now also re-proven from the live script output:
  - `run_contract_eval.py --profile demo`
  - latest result includes `path_count = 4` and `trace_node_count = 7`

What is still not proven closed for `Phase 6`:

- no remaining local closure gap is left inside `Phase 6`
- the phase already has technical evidence, a standalone node, and a remote GitHub push

## Phase 7 Next Exact Step

Keep the finished `Phase 1-6` evidence stable and switch all remaining public-facing surfaces to the final interview-ready story.

The highest-value next action is now the first real `Phase 7` gate:

- remove stale `Phase 6` wording from public README / architecture indexes / phase summary surfaces
- define the final interview-facing reading path and smoke verification path
- keep the final public story aligned with code, structure, evaluation evidence, and GitHub presentation
- use `python tools/scripts/verify_phase7_readiness.py` as the final low-cost unified readiness entry once the public path is aligned
- use `python tools/scripts/preview_phase6_bundle_scope.py --dry-run` to print the full grouped stage dry-run before forming the GitHub node
- use `python tools/scripts/preview_phase6_bundle_scope.py --stage-command` to print the canonical `git add` command for the full bundled node
- use `python tools/scripts/verify_phase6_bundle_ready.py` for the current one-command go/no-go check
- use `python tools/scripts/preview_phase6_bundle_scope.py --groups` to list the grouped Phase 6 bundle slices
- use `python tools/scripts/preview_phase6_bundle_scope.py --summary` to print the current Phase 6 bundle summary
- use `python tools/scripts/preview_phase6_bundle_scope.py --group logical_phase6_delta` to inspect the logical delta slice
- use `python tools/scripts/preview_phase6_bundle_scope.py --group runtime_foundations --stat` to inspect the runtime foundations slice with stats
- see `./phase6-bundle-prestage.md` and `./phase6-bundle-ready.md` for the current operational staging contract

## Phase 6 Minimal Standalone Node Scope

There are two different notions of "minimal scope" here, and the current branch state matters:

1. logical `Phase 6` delta
2. self-contained GitHub node on top of the current branch tip

If the branch you are pushing from already contains the required `Phase 1-5` foundations, then the logical `Phase 6` delta can prioritize the files that directly carry the newly-proven evaluation and evidence-chain contract:

- `docs/architecture/plans/current-phase-audit.md`
- `docs/architecture/plans/zuno-refactor-execution-plan.md`
- `tools/evals/zuno/rag_eval/README.md`
- `tools/evals/zuno/rag_eval/run_local_embedding_eval.py`
- `tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py`
- `tools/evals/zuno/rag_eval/generate_contract_review_scale_corpus.py`
- `tests/compat/test_rag_eval_local_launcher.py`
- `tests/compat/test_stackless_compare_matrix.py`

These files are the smallest current slice that explains and verifies the Phase 6 delta:

- local embedding preflight and one-command fallback behavior
- compare-matrix coverage visibility
- scaled-corpus local evidence for GraphRAG value
- architecture-plan status sync for the new evidence

However, that slice is not yet self-contained on the current branch tip. In the current worktree, the `Phase 6` eval entrypoints still depend on several untracked foundation files, including:

- `tools/evals/zuno/rag_eval/run_stackless_local_eval.py`
- `tools/evals/zuno/rag_eval/summarize_eval_profiles.py`
- `tools/evals/zuno/rag_eval/local_embedding_server.py`
- `tools/evals/zuno/rag_eval/local_rerank_server.py`
- `src/backend/zuno/legacy/agentchat/services/runtime_registry.py`
- `src/backend/zuno/legacy/agentchat/services/domain_pack/`
- `src/backend/zuno/legacy/agentchat/services/graphrag/extractors/`
- `src/backend/zuno/legacy/agentchat/services/graphrag/retrievers/`
- `src/backend/zuno/legacy/agentchat/core/graphs/`
- `src/backend/zuno/legacy/agentchat/core/runtime/`

So the real process conclusion is stricter than before:

- if `Phase 1-5` foundations are already present on the branch base, the logical `Phase 6` slice above is enough
- if they are not present on the branch base, then a truly standalone `Phase 6` node cannot be cut from the current tip without also bundling earlier foundational files or first rebasing onto a branch where those foundations already exist

For the current branch tip specifically, the smallest realistic bundled scope now looks more like:

- the logical `Phase 6` files listed above
- the stackless local-eval runtime helpers:
  - `tools/evals/zuno/rag_eval/run_stackless_local_eval.py`
  - `tools/evals/zuno/rag_eval/summarize_eval_profiles.py`
  - `tools/evals/zuno/rag_eval/local_embedding_server.py`
  - `tools/evals/zuno/rag_eval/local_rerank_server.py`
- the domain/runtime foundations that those helpers import directly:
  - `src/backend/zuno/legacy/agentchat/services/runtime_registry.py`
  - `src/backend/zuno/legacy/agentchat/services/domain_pack/`
  - `src/backend/zuno/legacy/agentchat/services/graphrag/extractors/`
  - `src/backend/zuno/legacy/agentchat/services/graphrag/retrievers/`
  - `src/backend/zuno/legacy/agentchat/core/graphs/`
  - `src/backend/zuno/legacy/agentchat/core/runtime/`
- the associated local-eval / domain-pack / contract tests that verify this bundled runtime

The grouped preview tool now mirrors that split directly:

- `docs_and_contract`
  - docs sync and architecture-plan sync for the closure claim
- `logical_phase6_delta`
  - the smallest direct code/test delta that carries the newly-proven Phase 6 behavior
- `eval_entrypoints`
  - stackless/local-eval helpers that the logical delta still imports on the current branch tip
- `runtime_foundations`
  - domain/runtime foundations required when the branch base does not already contain the earlier phases
- `verification_tests`
  - the associated test bundle that proves this broader node still works as one phase closure
- `phase6_node_ops`
  - the local docs/scripts/tests that make the bundle staging contract reproducible

That means the current branch tip is still not ready for a "pure Phase 6 only" node. It is ready either for:

- a branch-base switch onto a history that already contains those foundations
- or a broader bundled node that explicitly carries them

Current local git evidence makes the first option weak in this repository snapshot:

- the critical foundation files above currently have no local commit history in the visible branches
- `main`, `codex/zuno-bm25-retrieval-modes`, and the other locally visible branches do not currently provide a better recorded base for those files

So unless a different external branch/history is introduced later, the practical path from the current repo state is the broader bundled node, not a clean local branch-base switch.

## Phase 5 Closure Evidence

`Phase 5` is now treated as closed. The current repo state proves the four closure gates in `zuno-refactor-execution-plan.md` instead of only matching them by wording:

- GraphRAG dynamic update has moved past file-level replacement:
  - parser chunks now carry `document_hash`, `chunk_hash`, and stable `source_chunk_id`
  - graph extraction and graph writing preserve those runtime identity fields
  - graph indexing now deletes prior graph state by `source_chunk_id` before rewriting the chunk path
- normal / enhanced retrieval experience now has an explicit minimum contract:
  - normal mode stays on the vector + keyword path
  - enhanced mode enables graph retrieval when graph capability is healthy
  - enhanced mode degrades back to normal retrieval when graph health is unavailable
  - Domain QA runtime still forwards the knowledge default retrieval mode into the retrieval runner
- LangGraph / Domain Pack import path is now harder than before:
  - `zuno.api` and `zuno.api.services` no longer eagerly import the full router / service tree during package initialization
  - `zuno.core.graphs.domain_qa_graph` can now be imported directly from the current `zuno` mainline without tripping the previous circular import chain
  - `contract_review` Domain Pack assets now live under `src/backend/zuno/domain_packs/contract_review`, so the default `zuno` loader path resolves the pack without falling back to the legacy tree
- contract-review Domain Pack now has direct zuno-side value evidence:
  - the `contract_review` pack loads from the `zuno` runtime path and is listed by the `zuno` registry
  - the structured graph extractor uses the Domain Pack schema to emit contract-specific entities and typed relations
  - the graph retriever can answer a Chinese contract-risk question through the Domain Pack graph path instead of only generic vector recall
- contract-review main runtime path now also has zuno-side checks:
  - `AgentRuntime` stays on the single-agent graph by default and switches to the multi-agent graph when the Domain Pack enables it
  - `GeneralAgent` imported through the `zuno` entrypoint prefers the domain-pack runtime path for both knowledge-tool execution and streamed answer generation
  - these checks now run from the `zuno` test surface instead of only the legacy `agentchat/test` tree
- `DomainQAGraph` itself now has zuno-side offline integration coverage:
  - the contract-review retrieval result is wired through `retrieve_evidence -> draft_answer -> citation_check -> finalize`
  - support verdict, evidence bundle, graph paths, and runtime trace metadata are all asserted from the `zuno` test surface
  - failure flow is also covered, including `retrieve_evidence` failure metadata and finalize behavior
- `MultiAgentSupervisorGraph` now also has zuno-side offline integration coverage:
  - the supervisor graph runs the actual `zuno` `DomainQAGraph` subgraph path instead of only a fake specialist stub
  - planner -> domain_qa_specialist -> citation_verifier_specialist -> finalize trace is asserted from the `zuno` test surface
  - citation dedup, support verdict carry-over, and failure finalize behavior are now covered on the multi-agent line too
- the public high-value agent entrypoint now also has real zuno-side graph-chain coverage:
  - `zuno.core.agents.general_agent` can drive the real `DomainQAGraph` path from the public knowledge-tool entrypoint without stubbing `run_domain_qa`
  - `GeneralAgent -> AgentRuntime -> MultiAgentSupervisorGraph -> DomainQAGraph` now runs from the public `astream` path with only the retrieval backend faked
  - the multi-agent public-path trace is asserted as `plan_specialists -> domain_qa_specialist -> citation_verifier_specialist -> finalize`
- public runtime exits now preserve contract-review evidence semantics instead of dropping them:
  - `GeneralAgent` domain-pack events now expose `support_verdict` and `evidence_bundle`
  - `WorkSpaceSimpleAgent` prefetch/runtime payloads now preserve `domain_pack_support_verdict` and `domain_pack_evidence_bundle`
  - supported vs `insufficient_evidence` contract-review outcomes are both asserted from the `zuno` test surface
- Chinese contract-review query alignment is now stricter and more realistic:
  - query-aware support checks no longer treat the full Chinese question sentence as one opaque token
  - filler phrases such as `这份合同` / `是否` / `约定` are stripped before overlap checks
  - this closes the earlier false negative where real `违约责任` evidence could still be marked `evidence_not_query_aligned`

Current Phase 5 minimum evidence in the repo state:

- `tests/test_phase5_graphrag_index_filters.py`
- `tests/test_phase5_contract_review_domain_pack.py`
- `tests/test_phase5_domain_qa_graph_runtime.py`
- `tests/test_phase5_multi_agent_supervisor_runtime.py`
- `tests/test_phase5_general_agent_real_runtime_flow.py`
- `tests/test_phase5_workspace_real_runtime_flow.py`
- `tests/test_phase5_domain_runtime_paths.py`
- `tests/test_phase5_retrieval_modes.py`
- `tests/test_phase5_langgraph_runtime_imports.py`
- targeted `tests/test_zuno_public_entrypoints.py` checks covering the high-value `zuno` service path
- targeted `tests/test_layered_api_boundaries.py` guard for the knowledge file controller path

Latest focused verification set:

1. `pytest -q tests/test_phase5_retrieval_modes.py`
2. `pytest -q tests/test_phase5_langgraph_runtime_imports.py`
3. `pytest -q tests/test_phase5_contract_review_domain_pack.py`
4. `pytest -q tests/test_phase5_domain_runtime_paths.py`
5. `pytest -q tests/test_phase5_domain_qa_graph_runtime.py`
6. `pytest -q tests/test_phase5_multi_agent_supervisor_runtime.py`
7. `pytest -q tests/test_phase5_general_agent_real_runtime_flow.py`
8. `pytest -q tests/test_phase5_workspace_real_runtime_flow.py`
9. `pytest -q tests/test_phase5_general_agent_real_runtime_flow.py tests/test_phase5_workspace_real_runtime_flow.py tests/test_phase5_multi_agent_supervisor_runtime.py tests/test_phase5_domain_qa_graph_runtime.py tests/test_phase5_domain_runtime_paths.py tests/test_phase5_contract_review_domain_pack.py tests/test_phase5_langgraph_runtime_imports.py tests/test_phase5_retrieval_modes.py tests/test_phase5_graphrag_index_filters.py`
10. `pytest -q tests/test_phase5_general_agent_real_runtime_flow.py tests/test_phase5_workspace_real_runtime_flow.py tests/test_phase5_multi_agent_supervisor_runtime.py tests/test_phase5_domain_qa_graph_runtime.py tests/test_phase5_domain_runtime_paths.py tests/test_phase5_contract_review_domain_pack.py tests/test_phase5_langgraph_runtime_imports.py tests/test_phase5_retrieval_modes.py tests/test_phase5_graphrag_index_filters.py tests/test_zuno_public_entrypoints.py::test_high_value_service_modules_prefer_local_zuno_contracts tests/test_zuno_public_entrypoints.py::test_public_worker_entrypoints_and_manifest_prefer_zuno tests/test_layered_api_boundaries.py::test_knowledge_file_controller_avoids_direct_storage_imports`

Latest whole-set closure proof:

- the full phase minimum integration set now passes as a whole from the `zuno` test surface
- latest whole-set command result: `42 passed`

这份文档只回答一件事：

```text
当前到底推进到哪个 phase，为什么这样判断，下一步先做什么
```

它不是稳定架构定义，也不替代 `spec` 或完整执行计划。

## 当前结论

- `Phase 1` 已完成
- `Phase 2` 已完成
- `Phase 3` 已完成
- `Phase 4` 已完成
- `Phase 5` 已完成
- `Phase 6` 已完成
- `Phase 7` 是当前默认下一阶段

## 为什么 `Phase 1` 已完成

当前判断依据是已经有代码和最小验证支撑，而不是只靠口头状态：

- `src/backend/zuno` 下 direct `agentchat` import 已清零
- `zuno.main` 已成为主运行入口
- 最小测试集已经通过：
  - `tests/test_zuno_public_entrypoints.py`
  - `tests/test_zuno_runtime_chain_guard.py`
  - `tests/compat/test_zuno_alias_imports.py`
- `zuno.main` 的最小 import / create-app smoke 已通过

这意味着“运行时收口与可运行恢复”已经不再是当前主战场。

## 为什么 `Phase 2` 现在可以视为完成

`Phase 2` 的目标不是继续扩大运行时迁移，而是把项目结构治理清楚：

- 清理混乱入口、历史残留、过时目录与过时文档引用
- 明确应用入口、核心能力、评测、文档、工具、基础设施、测试边界
- 收紧 `src/backend`、`apps/web`、`apps/desktop`、`docs/`、`infra/`、`tools/`、`tests/` 的职责说明
- 保持当前可运行结构，不做高风险全仓路径革命

这轮已经补齐了对应的最小结构门禁：

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/test_repo_structure_consistency.py tests/test_publish_boundary.py`
- `python tools/scripts/verify_docs_and_readme_ready.py`
- `zuno.main` 最小 import / create-app smoke

这些检查现在都已经通过，所以“结构解释力”和“目录职责一致性”已经有了最小可验证支撑，而不是只停留在文档说法上。

## `Phase 2` 当前最小验收思路

这阶段至少要能稳定回答下面四个问题：

1. 仓库顶层目录职责能不能一眼讲清楚
2. `src/backend/zuno` 内部的控制层 / 服务层 / DAO 层 / 基础设施层边界是不是和文档一致
3. README、`docs/README.md`、`docs/architecture/`、publish boundary 文档是不是在讲同一套结构
4. 有没有把结构治理偷偷做成高风险全仓路径革命

## `Phase 2` 当前最小检查

当前建议的最小检查是：

1. `python tools/scripts/verify_repo_structure.py`
2. `pytest -q tests/test_repo_structure_consistency.py tests/test_publish_boundary.py`
3. 最小 import smoke

这些检查已经稳定通过，因此 `Phase 2` 可以正式收尾，并把默认主线切到 `Phase 3`。

## 下一步默认顺序

接下来默认继续按这个顺序推进：

1. 进入 `Phase 3`
2. 继续压缩首次阅读路径里的冗余和历史噪音
3. 把 README、`docs/README.md`、`docs/architecture/`、`docs/development/` 的展示口径继续收齐
4. 跑 `Phase 3` 最小检查
5. 形成单独 GitHub 节点
