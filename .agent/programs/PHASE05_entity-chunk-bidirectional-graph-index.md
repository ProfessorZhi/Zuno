# PHASE05 Entity-Chunk Bidirectional Graph Index

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE05_entity-chunk-bidirectional-graph-index
status: completed
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

- [x] graph context 能输出 source chunk ids 和 source span ids。
- [x] entity / relation / community summary 能回到 evidence span。
- [x] 无 source refs 的 graph context 不能算 strict citation。

## 完成事实

PHASE05 已完成 local deterministic graph evidence lineage，不表示 external graph DB 已接入，也不表示 PHASE06 reranker 已完成。

Current 已实现：

- `production_graphrag.graph_extraction.entity_index` 输出 `entity -> supporting_chunk_ids / supporting_span_ids`。
- `production_graphrag.graph_extraction.relation_index` 输出 `relation -> supporting_chunk_ids / evidence_span_ids`。
- `community_report.reports` 输出 `source_chunk_ids` 和 `source_span_ids`。
- `chunk_entity_index` 和 `span_entity_index` 保留 chunk / span 到 entities 的反向索引。
- 无 source span 的 graph summary 仍会被 `CitationBuilder` 排除在 strict citation 外。

边界：

- External graph index service 仍是 `target_blocked`。
- 当前 entity extraction 是 local regex deterministic baseline，不声明生产级 entity resolution。

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
