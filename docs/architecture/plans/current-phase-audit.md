# Current Phase Audit

## Status Snapshot (2026-06-11)

- `Phase 1`: completed
- `Phase 2`: next serial phase
- `Phase 3`: pending
- `Phase 4`: pending
- `Phase 5`: pending
- `Phase 6`: pending
- `Phase 7`: pending

## Phase 1 Closure Evidence

This branch closes the new serial `Phase 1` gate from `origin/main` by establishing a real `zuno` runtime entrypoint and switching the highest-value public/runtime surfaces onto that path.

Current evidence from the repo state:

- `src/backend/zuno/` now exists on the branch as the runtime-facing package root
- `README.md` local backend start path now uses `uvicorn zuno.main:app`
- `infra/docker/Dockerfile`, `infra/docker/docker-compose.yml`, and `infra/docker/docker-compose.dev.yml` now point backend and worker startup/config mounts to `zuno`
- `src/backend/agentchat/main.py` keeps a backward-compatible bridge, but its direct CLI entry now forwards to `zuno.main:app`
- `src/backend/agentchat/settings.py` now prefers `ZUNO_CONFIG` and resolves `zuno/config.yaml` plus `/app/zuno/config.yaml`
- `src/backend/agentchat/config/mcp_server.json` and `src/backend/agentchat/tools/send_email/manifest.yaml` no longer point their runtime entrypaths at the old `agentchat` locations

## Phase 1 Minimum Verification

The Phase 1 minimum gate now passes on this branch:

1. `pytest -q tests/test_zuno_public_entrypoints.py`
   - latest result: `36 passed`
2. `pytest -q src/backend/agentchat/test/test_zuno_alias_imports.py`
   - latest result: `7 passed`
3. `pytest -q tests/test_zuno_runtime_chain_guard.py`
   - latest result: `2 passed`
4. minimal `import zuno.main` smoke with `src/backend` on `sys.path`
   - latest result: `module_ok True`, `app_attr True`

## Next Default Step

Proceed to `Phase 2`: project folder and structure hard governance.

The default next action is:

- keep the new `zuno` runtime path stable
- start separating application entrypoints, core capability directories, docs, tooling, and infrastructure surfaces
- keep later `Phase 3-7` goals as pending, not pre-claimed

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
  - `src/backend/agentchat/test/test_zuno_alias_imports.py`
- `zuno.main` 的最小 import / create-app smoke 已通过

这意味着“运行时收口与可运行恢复”已经不再是当前主战场。

## 为什么 `Phase 2` 现在可以视为完成

`Phase 2` 的目标不是继续扩大运行时迁移，而是把项目结构治理清楚：

- 清理混乱入口、历史残留、过时目录与过时文档引用
- 明确应用入口、核心能力、评测、文档、工具、基础设施、测试边界
- 收紧 `src/backend`、`src/frontend`、`apps/desktop`、`docs/`、`infra/`、`tools/`、`tests/` 的职责说明
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
