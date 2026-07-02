# Agentic Retrieval 数据看板观测实现记录

## 目标

在现有数据看板中增加 Agentic Retrieval 观测面板，用于比较 `standard`、`deep` 和 `deep_without_graph` 的实际运行效果。

## 当前边界

当前实现只聚合本地 `WorkspaceTaskRuntimeService` 已经保存的 task、retrieval plan、eval 和 cost summary，不新增数据库表，不接外部 observability sink，也不把尚未接入的生产级指标平台写成 Current。

产品侧展示知识库检索 profile 的观测事实：运行数、引用覆盖率、图谱参与率、replan 比率、成本差和最近运行。数据看板还必须展示 Benchmark Metrics，包括 Recall@5、Precision@5、MRR、NDCG、Answer Correctness、Citation Coverage、Source Span Accuracy、Unsupported Claim Rate、Latency p50/p95 和 Estimated Cost。用户仍只在知识库层选择标准检索或深度检索，GraphRAG、rerank、re-query 和 fallback 由 Single Controller Agent 内部规划。

Benchmark Metrics 必须区分三种状态：

- `measured`：来自固定 eval dataset 的真实评测结果。
- `runtime_observed`：来自当前 workspace runtime 的运行观测，例如 citation coverage、latency、cost。
- `missing_dataset`：固定数据集尚未提供，不能伪造成已评测。

## 已完成事项

- [x] 新增 focused test：`tests/api/test_workspace_retrieval_observability_dashboard.py`。
- [x] 新增后端聚合：`WorkspaceTaskRuntimeService.retrieval_observability_summary()`。
- [x] 新增接口：`GET /api/v1/workspace/retrieval-observability`。
- [x] 同步前端 API 类型与调用：`apps/web/src/apis/workspace.ts`。
- [x] 在 `apps/web/src/pages/dashboard/dashboard.vue` 增加 Agentic Retrieval 面板。
- [x] 面板展示 `standard / deep / deep_without_graph`、`citation_coverage`、`graph_used_rate` 和 `cost_delta`。
- [x] 面板展示 Benchmark Metrics，并明确区分 `measured / runtime_observed / missing_dataset`。

## 验收命令

```powershell
pytest -q tests/api/test_workspace_retrieval_observability_dashboard.py -p no:cacheprovider
pytest -q tests/api/test_workspace_agentic_product_contract.py tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/evals/test_agentic_graphrag_product_baseline.py -p no:cacheprovider
npm --prefix apps/web run lint
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 后续扩展

后续如果要推进到 Production Scale，需要把当前 in-process summary 替换或旁路同步到统一 metrics sink，形成 conversation/stage 级长期指标；当前文件不把该目标伪装成已完成事实。
