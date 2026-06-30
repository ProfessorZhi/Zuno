# PHASE09 agentic-retrieval-evidence-citation-runtime

status: completed

## 目标

让 ProductMode、QueryMethod、AgenticRetrievalRouter、StagedFusionPlan、EvidenceBundle、CitationBuilder 和 UnsupportedClaimChecker 真正消费新的 ingestion/index runtime。

## 范围

- 接通 normal / enhanced / auto 用户模式与 basic / local / global / drift 内部方法。
- 实现 fusion/rerank、citation-rich answer、unsupported claim guard。
- 推进 graph extraction、community report 和 index manifest runtime。

## 禁止范围

- 不把 query method contract 当作成熟 GraphRAG。
- 不把 global community prior 和 chunk-level evidence 混成不可解释排序。
- 不输出无 citation 的企业知识答案作为成功路径。

## 验收闸门

- e2e retrieval test 能从上传文档产生 citation-rich answer。
- Evidence coverage、citation coverage、unsupported claim check 进入 trace/eval。
- fallback reason 可断言。

## 完成证据

- `AgenticRetrievalRuntime` 已接通 `KnowledgeIndexRuntime.to_retrieval_payload()`，能按 ProductMode / QueryMethod 生成 EvidenceBundle、CitationBuilder 输出和 unsupported claim check，并覆盖 normal/basic、enhanced local/global、auto drift 与 zero-evidence fallback。
- Workspace task runtime 已把 upload -> ingest -> index -> task -> retrieval -> cited artifact 串成同一条 API 路径，并在 retrieval event 中记录 `resolved_methods`、`citation_ids`、coverage、router decision、retrievers_used、ACL dropped evidence、evidence verdict、runtime trace event ids 和 artifact manifest。
- PHASE09 仍严格把生产级 community report、语义 rerank、语义 unsupported-claim checker、durable external index store 写作 Target；Current 只声明本地 deterministic runtime 闭环。
- 前端 workspace API 类型已暴露文件 `content` 字段和工具审批事件字段，便于 PHASE11 UI 闭环继续消费。
- 验证：`pytest -q tests\agent\test_agentic_retrieval_runtime.py tests\agent\test_agentic_graphrag_contract.py tests\agent\test_knowledge_graphrag_runtime_contracts.py tests\agent\test_hooks_evidence_trace_artifacts.py tests\retrieval tests\graphrag tests\evals\test_multihop_eval_route_policy.py tests\api\test_workspace_task_runtime.py tests\agent\test_knowledge_layer_surfaces.py tests\frontend\test_workspace_product_loop_types.py tests\repo\test_backend_facade_layers.py tests\repo\test_lazy_facade_static_exports.py -p no:cacheprovider` 通过，176 passed。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_agentic_graphrag_contract.py tests/retrieval tests/graphrag tests/evals -p no:cacheprovider
```
