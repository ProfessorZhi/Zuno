# PHASE04 Query Router Mode Policy

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

普通 / 增强 / 自动三种产品模式如果没有 runtime contract，会让 Agentic RAG、GraphRAG 和 fallback 都变成 prompt 习惯。先固定模式和内部方法，后续 memory、tool、knowledge 才有稳定入口。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- 产品模式：`normal`、`enhanced`、`auto`。
- 内部方法：`basic`、`local`、`global`、`drift`。
- `auto` 只做 router，不成为第五种 retrieval 方法。

## 执行步骤

1. 审计现有请求 DTO、AgentRuntime、GeneralAgent 和 knowledge query path。
2. 设计 mode / query_method / fallback / budget / evidence coverage contract。
3. 实现最小破坏的 router policy 和 trace 字段。
4. 增加 focused tests，证明旧请求兼容、新模式可解释。
5. 同步 architecture docs 和 eval contract。

## 验收

- 模式选择和内部 query_method 能在 trace 中解释。
- `auto` 的路由结果可测试，fallback 可追踪。
- 不改变既有 API response shape，除非本 phase 明确补 contract 和兼容测试。
- docs 只把已实现字段写入 Current。

## 完成摘要

- 多 agent 使用情况：已启用线程内多 agent 协作。Architecture / Docs、Runtime / Code、Verification、Integration Reviewer 四个子 agent 均执行只读审计；主线程完成最终实现、diff 审查和验证。未禁用多 agent。
- Runtime contract：`product_mode = normal | enhanced | auto` 已贯通 `CompletionReq`、`AgentConfig`、`KnowledgeQueryService`、`GraphRAGQueryService`、`RetrievalRequest`、`RetrievalPlan`、`RetrievalPlanner` 和 `RetrievalOrchestrator`。
- Query method contract：`requested_query_method` 可为 `auto`，但 `resolved_query_method` 只落到 `basic | local | global | drift`；`auto` 在 trace 中只代表 router。
- Trace / eval contract：trace metadata 已包含 requested/resolved product mode、router decision、requested/resolved query method、fallback reason、budget policy、fallback policy、pipeline trace、retrievers used 和 citation coverage；eval metadata 保留旧 `standard_retrieval / enhanced_retrieval`，并新增 `normal / enhanced / auto`。
- 文档边界：Current 只写已实现的 mode/query_method/trace foundation；完整 retrieval fusion、产品 UI 三模式统一和生产级 GraphRAG 能力仍留在 Target 或后续 phase。

## 验证证据

```powershell
pytest -q tests/retrieval/test_retrieval_planner.py tests/agent/test_completion_agent_config_compatibility.py tests/agent/test_general_agent_project_query_runtime.py tests/api/test_knowledge_api_contract.py tests/legacy_guards/test_phase11a_knowledge_query_service.py tests/retrieval/test_retrieval_mode_semantics.py -p no:cacheprovider
pytest -q tests/retrieval/test_retrieval_orchestrator.py tests/retrieval/test_enhanced_retrieval_composition.py tests/retrieval/test_standard_retrieval_composition.py tests/retrieval/test_retrieval_mode_semantics.py tests/frontend/test_product_wiring_v1_api_contract.py tests/evals/test_contract_eval_runner.py tests/evals/test_stackless_compare_matrix.py tests/evals/test_stackless_local_eval_contract_project_query_policy.py tests/legacy_guards/test_phase5_retrieval_modes.py tests/agent/test_knowledge_layer_surfaces.py tests/repo/test_backend_facade_layers.py -p no:cacheprovider
```

## PR 边界

本 phase 作为单独 stacked PR：contract/docs、runtime policy、trace/eval 和 focused tests 一起收口。
