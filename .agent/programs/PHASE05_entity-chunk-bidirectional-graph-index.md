# PHASE05 Entity-Chunk Bidirectional Graph Index

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE05_entity-chunk-bidirectional-graph-index
status: pending
owner: GraphRAG

## 目标

让 graph retrieval 必须能回到 source chunk / evidence span，而不是只返回 summary 或 abstract graph context。

## 范围

需要支持：

- `entity -> relation -> supporting_chunk_ids`
- `relation -> evidence_span_ids`
- `community_summary -> source_chunk_ids`
- `chunk -> entities`
- `chunk -> relations`

## 禁止范围

- 不接 external graph DB。
- 不把 deterministic local graph 写成 production graph platform。
- 不让 graph summary 替代 source evidence。

## 验收闸门

- graph context 能输出 source chunk ids。
- graph-added evidence 能区分 gold / non-gold。
- `graph_context_non_gold` 可诊断。

## 验证命令

```powershell
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/evals/test_enterprise_rag_paired_benchmark.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/agentic_graphrag.py`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `tools/evals/zuno/rag_eval/**`

## 需要修改的文件

预计修改范围：

- `src/backend/zuno/knowledge/**`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `tests/evals/**`

## 执行拆解

1. 审计 current graph context 的 source provenance。
2. 增加 entity / relation / chunk 双向映射。
3. 更新 GraphRAG trace 和 eval diagnostics。

## 多 agent 分工

默认单线程，避免 graph contract 分裂。

## 需要返回的证据

- graph context 到 source span 的示例。
- graph-added gold evidence 统计。
- focused tests。

## 停止条件

只有 graph result 可回到 source span 后才能关闭。
