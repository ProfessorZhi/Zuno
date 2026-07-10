# Agentic Retrieval Planner

所属运行域：Agent Core、Input & Knowledge、Governance & Observability。

## 定位

Agentic Retrieval Planner 不是用户手动选择一堆 RAG 工具，而是 Single Controller Agent 根据 ContextPack 和任务目标生成 RetrievalPlan，并在检索、Graph expansion、rerank、citation binding 和 reflection 中闭环。

RAG 的目标设计已经清楚：离线侧完成 SourceObject、Document IR、Chunk、Embedding/Index 和 Graph evidence；在线侧完成 Query strategy、粗召回、fusion/rerank、EvidenceBundle、claim binding 和 grounded answer。当前主要缺口不是“有没有 GraphRAG”，而是 agentic re-retrieval 是否由统一 Agent Core loop 驱动，以及 fixed benchmark 是否证明 evidence-span、citation 和 answer correctness 增益。

## 模式关系

- standard retrieval：fixed baseline，使用 BM25/vector 和 citation。
- deep retrieval：扩大 query、candidate pool、rerank 和 evidence diagnostics。
- agentic retrieval：在 standard/deep 的 evidence contract 上增加 planning、Graph expansion、reflection、replan、tool observation 和 abstain。

短期 RetrievalPlan 的 query strategy contract 至少应能表达：

- Query Rewrite：把用户问题改写为检索友好查询。
- Multi Query：为同一问题生成多个互补查询。
- Step-back Query：先抽象上位问题，再回到具体证据。
- HyDE：在合适任务上生成假设性答案/段落辅助召回。

这些策略是 RetrievalPlan 的字段或 step，不是用户手动选择的产品模式。是否启用由 StrategySelector、ContextPack、budget、evidence diagnostics 和 reflection 共同决定。

## Contract

```text
ContextPack
-> StrategyDecision
-> RetrievalPlan
   -> Query Rewrite / Multi Query / Step-back / HyDE
-> BM25 / Vector / Graph retrieval
-> Fusion / Rerank
-> EvidenceBundle
-> ClaimBinding
-> ReflectionDecision
```

EvidenceBundle 必须包含 source document、source span、citation label 和 retriever/rerank diagnostics。Graph evidence 必须回到 source span；doc-only evidence 不得作为 strict citation。

## Failure Buckets

- doc_miss
- doc_hit_text_miss
- text_hit_citation_miss
- citation_hit_answer_wrong
- unavailable_due_to_missing_trace_fields

缺少 trace 字段时必须输出 unavailable，不得编造 bucket。

## 质量门

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

Current：

```text
implementation available
measurement blocked
quality not yet proven
```

Short-term：

- P0 完整跑通 fixed EnterpriseRAG paired benchmark。
- P0 release gate 只在 measured profile 完整时判断通过或失败。
- P0 agentic re-retrieval 由统一 Agent Core loop 驱动，Reflection 的 RETRIEVE_MORE 必须回到 RetrievalPlan / execute_step，而不是停留在诊断文本。
- P1 retrieval diagnostics 和 citation diagnostics 持久化并可在 trace 中查看。
