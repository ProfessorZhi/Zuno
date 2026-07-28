# Goal04 PHASE18 KnowledgeRetrievalGraph Contract Evidence

updated: 2026-07-28
phase: PHASE18 Agentic GraphRAG Inner Loop
pr: PR D / #49
status: implementation-evidence
production_readiness: not established

## 目标

本证据记录 PHASE18 的第一块实现增量：把 Knowledge 内层检索从“corrective wrapper trace”推进为显式固定 `KnowledgeRetrievalGraph` contract，并把 Knowledge 产出的 `KnowledgeControlProposal` 暴露给 Agent Core observation。

本文件不是 PHASE18 closure approval，不把 PHASE18 标记为 completed。

## 实现范围

- 新增固定节点 contract：`validate -> pin_snapshot -> scope -> interpret -> select_profile -> plan_round -> admit -> dispatch -> normalize -> fuse_rerank -> evidence_ledger -> evaluate -> corrective_decision`。
- 新增内部 profile contract：`standard/local/global/drift/deep/agentic`。
- 新增 `RetrievalPlan` 与 `RetrieverDispatchPlan`，将 profile、query strategy、knowledge scope、round budget、timeout 和 parallel group 固化到 `plan_round/admit/dispatch` trace。
- `admit` 节点在 scope 为空、预算耗尽或 retriever set 为空时阻断 dispatch，并通过 `KnowledgeControlProposal` 交给 Agent Core gate。
- 新增 `RetrieverAttemptResult`，记录 required retriever timeout / index unavailable、budget exhausted 和 late result fencing；BM25/Vector 这类 required retriever 失败会阻断 normalize，optional graph late result 被 fence 后不进入 EvidenceLedger。
- `DurableKnowledgeRetrievalPort` 使用稳定 `query_run_id` / `round_id` 执行 idempotent replay：重复请求会读取已存在 strict evidence，跳过重复 `commit_evidence`，保留 citation lineage 幂等确认，并在 trace 中输出 `idempotent_replay`。
- 新增 `EvidenceFrontier` / `EvidenceCoverageSummary`，从 EvidenceLedger 计算 claim coverage、strict citation coverage、authority、temporal versions、conflict groups、missing strict citation 和 stop reasons，并写入 `evidence_ledger`、`evaluate` 与 proposal trace。
- `CorrectiveRetrievalPolicy` 消费 `EvidenceFrontier.stop_reasons`：即使单轮 evidence verdict 为 `relevant`，存在 coverage gap、strict citation 缺失或 unresolved conflict 时，也不能直接输出 `accept_evidence`。
- 新增 `KnowledgeControlProposal`，默认要求 Agent Core 显式接受或拒绝，Knowledge 不直接修改 Agent PlanVersion、不问用户、不调用外部 Tool。
- `CorrectiveAgenticRetrievalRuntime` 每次检索生成 `knowledge_retrieval_graph` trace。
- 新增 `CorrectiveAgenticGraphRAGRuntime` 兼容入口：外部仍返回 `AgenticRetrievalRuntimeResult`，内部先执行 PHASE18 `CorrectiveAgenticRetrievalRuntime`，再把 `phase18_default_path`、`knowledge_retrieval_graph`、`knowledge_control_proposal`、`evidence_frontier` 和 corrective rounds 写入旧结果的 `trace_metadata`。
- `WorkspaceTaskRuntimeService` 默认 `_agentic_retrieval_runtime` 和 test reset 默认入口从旧 `AgenticRetrievalRuntime` 切到 `CorrectiveAgenticGraphRAGRuntime`。
- `product_baseline.py` 的标准/Deep retrieval probe 使用 PHASE18 兼容入口生成基线证据，不再直接构造旧 GraphRAG runtime。
- `KnowledgeQueryService.query()` 保留 `KnowledgeQueryResult` 应用层返回形状，但在 metadata 中加入 `phase18_application_query_path`、固定 `knowledge_retrieval_graph`、`knowledge_control_proposal` 和 `evidence_frontier`，使 workspace/simple agent 与 general agent 的 `search_knowledge_base` 工具不再成为无 PHASE18 trace 的旧旁路。
- `KnowledgeStepExecutor` 把 graph trace 和 proposal 放入 observation metadata，供 Agent Core 后续 gate 消费。
- `KnowledgeStepExecutor` 增加 deterministic proposal gate：只有 `accept_evidence` 被接受为 completed；`abstain`、ask-user、external-tool、agent-replan 和 unresolved corrective proposal 均转为 blocked observation，不由 Knowledge 越权完成 Agent 决策。

## 验证

```powershell
python -m py_compile src\backend\zuno\knowledge\agentic\contracts.py src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\agent\runtime\execution\knowledge_step.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\agent\runtime\execution\knowledge_step.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\contracts.py src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\knowledge\agentic\__init__.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\durable.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py -q -p no:cacheprovider --tb=short
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\contracts.py src\backend\zuno\knowledge\agentic\evidence_ledger.py src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\knowledge\agentic\__init__.py tests\knowledge\test_evidence_ledger.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_evidence_ledger.py tests\knowledge\test_corrective_retrieval_runtime.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\corrective.py src\backend\zuno\knowledge\agentic\runtime.py tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\contracts.py src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\knowledge\agentic\__init__.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\knowledge\agentic\__init__.py src\backend\zuno\api\services\workspace_task_runtime.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m pytest tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_resets_to_phase18_agentic_graphrag_default_path tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
python -m py_compile src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\knowledge\agentic\__init__.py src\backend\zuno\api\services\workspace_task_runtime.py src\backend\zuno\agent\product_baseline.py tests\knowledge\test_corrective_retrieval_runtime.py tests\api\test_workspace_task_runtime.py
python -m py_compile src\backend\zuno\platform\services\application\knowledge\query_service.py tests\agent\test_knowledge_graphrag_runtime_contracts.py
python -m pytest tests\agent\test_knowledge_graphrag_runtime_contracts.py::test_application_knowledge_query_service_emits_phase18_graph_metadata -q -p no:cacheprovider --tb=short
python -m pytest tests\agent\test_knowledge_graphrag_runtime_contracts.py tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_resets_to_phase18_agentic_graphrag_default_path tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
```

结果：

```text
11 passed in 48.15s
9 passed in 12.27s
14 passed in 12.84s
16 passed in 12.09s
14 passed in 15.19s
17 passed in 13.23s
18 passed in 24.62s
19 passed in 21.95s
20 passed in 24.06s
21 passed in 29.05s
1 passed in 8.76s
26 passed in 48.85s
```

未计入通过的环境/fixture 漂移：

```text
command: python -m pytest tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_resets_to_phase18_agentic_graphrag_default_path tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py tests\evals\test_agentic_graphrag_product_baseline.py -q -p no:cacheprovider --tb=short
test: tests\evals\test_agentic_graphrag_product_baseline.py::test_launchable_agentic_graphrag_product_baseline_generates_shareable_summaries
exception: RuntimeError
first relevant stack frame: src\backend\zuno\agent\product_baseline.py:423
message: blocked file did not block: file_phase12_docx
environment signature: local parser dependency state no longer blocks docx before PHASE18 retrieval probe
```

## 剩余范围

PHASE18 尚未完成。后续仍需继续实现和验证 Migration / integration / fault / security gate，以及 closure approval。
