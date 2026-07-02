# Agentic Retrieval Planner

本文说明 Zuno 企业知识库问答里的检索规划边界。它不是旧 RAG 模式列表，也不把内部算法名暴露成最终产品下拉。

## 产品口径

用户在知识库选择时只看到：

- 标准检索：适合单文档事实、明确引用、低成本回答。
- 深度检索：适合跨文档分析、多步问题、需要 agentic planning / graph fallback 的任务。

内部可以使用 BM25、vector、re-query、rerank、GraphRAG、deep_without_graph fallback、Skill 和 Tool，但这些是 Single Controller Agent 的内部规划，不是用户手动选择的产品模式。

## Current Local Slice

当前已证明：

- `src/backend/zuno/agent/contracts.py` 固定 `RetrievalProfile`、`RetrievalDecision`、`EvidenceBundle`、`CitationLineage`、`RetrievalPlan` 和 `PlanningMetrics` 等共享契约。
- Program 3 Mega PHASE04 已让 `standard` 落到 BM25 + vector light fusion。
- `deep` 在本地图索引不可用时会降级为 `deep_without_graph`，并记录 fallback reason。
- trace 记录 requested/effective profile、retrievers_used、evidence_count、citation_coverage、ACL 和 sensitivity。
- PHASE12 E2E 已证明 standard single-document fact、deep cross-document analysis、deep_without_graph fallback、citation lineage、dynamic replan 和 cited artifact。
- PHASE13 regression summary 已把 retrieval_rounds、retrievers_used、evidence_count、citation_count、citation_coverage 和 source_span_accuracy 汇总成可回归指标。

对应测试包括 `tests/agent/test_knowledge_graphrag_runtime_contracts.py`、`tests/agent/test_agentic_retrieval_runtime.py`、`tests/evals/test_agentic_graphrag_product_baseline.py` 和 `tests/evals/test_agentic_graphrag_regression_summary.py`。

## 规划链路

```text
KnowledgeSpaceConfig / task request
  -> requested profile: standard / deep
  -> RetrievalPlan
  -> RetrievalDecision
  -> EvidenceBundle
  -> citation lineage
  -> ReflectionVerdict
  -> ReplanDecision when retrieval_empty or citation_coverage_low
```

Replan 必须改变后续 retrieval / tool trajectory，否则只是静态重试，不算 dynamic replan。

## Launchable Prototype Target

- 正式文档和归档能说明 standard / deep 是产品语义，basic_rag / static_graphrag / agentic_graphrag 是 eval baseline labels。
- E2E 和 regression summary 作为 PHASE15 release evidence。
- KnowledgeSpaceConfig 的默认 profile、可用 profile 和 change impact preview 保持可解释。

## Production Scale Target

以下仍是 Target：

- 生产级 LLM entity / relation extraction。
- 真实 community report pipeline。
- 生产 reranker 服务。
- 外部 Elasticsearch / Milvus / Neo4j / graph index platform。
- 大规模 retrieval eval dataset 和 online eval。

## 不变量

- 不把 basic / local / global / drift 写成用户产品模式。
- 不把 graph index 缺失写成 deep success；必须记录 `deep_without_graph` fallback。
- citation coverage 低或 retrieval empty 时必须进入 reflection / replan 证据，而不是生成无来源答案。
