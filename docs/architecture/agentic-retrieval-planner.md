# Agentic Retrieval Planner

所属运行域：Agent Core、Input & Knowledge、Governance & Observability。

## 定位

Agentic Retrieval Planner 不是用户手动选择一堆 RAG 工具，而是 Single Controller Agent 根据 ContextPack 和任务目标生成 RetrievalPlan，并在检索、Graph expansion、rerank、citation binding 和 reflection 中闭环。

## 模式关系

- standard retrieval：fixed baseline，使用 BM25/vector 和 citation。
- deep retrieval：扩大 query、candidate pool、rerank 和 evidence diagnostics。
- agentic retrieval：在 standard/deep 的 evidence contract 上增加 planning、Graph expansion、reflection、replan、tool observation 和 abstain。

## Contract

```text
ContextPack
-> StrategyDecision
-> RetrievalPlan
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
- P1 retrieval diagnostics 和 citation diagnostics 持久化并可在 trace 中查看。
