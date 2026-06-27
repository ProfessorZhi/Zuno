# 知识、GraphRAG 与检索融合

## 用途

Define the canonical target for Knowledge Query, GraphRAG query modes,
multi-query retrieval, multi-retriever recall, fusion, rerank, evidence,
citation, and trace.

## 知识边界

The target query path is:

```text
GeneralAgent
  -> Knowledge Capability
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> Retrieval / Fusion / Evidence
  -> Knowledge Evidence
  -> GeneralAgent answer with citations
```

Current code already has `KnowledgeQueryService`, `GraphRAGQueryService`,
`GraphRAGProjectSnapshot`, and `KnowledgeQueryResult`. The target architecture
extends this with clearer retrieval/fusion components and stronger traces.

## GraphRAG 查询模式

The real query modes are exactly:

- `basic`
- `local`
- `global`
- `drift`

`auto` is a router. It is not a fifth query mode.

Mode meanings:

```text
basic
  Native BM25 + Vector + RRF + optional rerank

local
  entity / relation / graph neighborhood / source chunks

global
  community reports / global summaries

drift
  global community primer -> local follow-up retrieval -> evidence merge
```

The router records requested method, resolved method, fallback reason, and
method availability. If graph/community assets are not ready, the trace must
show the fallback clearly.

## GraphRAG 实体抽取目标

GraphRAG 建图的 entity / relation discovery 默认走 LLM 抽取。规则、正则和词典不是主路径，只能作为确定格式辅助、预处理、LLM 不可用时的 fallback 或 baseline test。

知识库配置必须能表达：

```text
graph_index_settings.entity_extraction_mode = llm
model_refs.entity_extraction_llm_id = <selected LLM id>
```

LLM 抽取输出必须是 schema-constrained JSON，并至少包含：

- entity name
- entity type
- relation type
- source chunk id
- source span
- confidence
- prompt version
- schema version
- fallback reason when applicable

日期、金额、条款号、编号等确定格式可以由规则层辅助抽取，但这些辅助结果必须进入同一 evidence / trace，而不能绕过 GraphRAG extraction trace。

## 多查询与多检索器流程

Target enhanced retrieval:

```text
User Query
  -> Query Understanding
  -> Query Variants
  -> Multi-retriever Recall
       Native BM25
       Dense Vector
       Graph Local
       Community Global
  -> Deduplication
  -> RRF Fusion
  -> Optional Rerank
  -> Evidence Check
  -> Citation Builder
  -> Trace
```

Query variants are enhanced / expensive mode. They are not enabled by default
for every query. The original query must always be preserved in the trace and
included in the candidate set.

## 面向知识的 Native BM25

Native BM25 is the local lexical baseline. Elasticsearch can be an optional
adapter, but it is not the BM25 algorithm itself.

Target components:

```text
NativeBM25Index
  tokenizer
  inverted_index
  term_freq
  doc_freq
  doc_len
  avg_doc_len
  idf

NativeBM25Retriever
  build(documents)
  search(query, top_k)
  explain_score(query, doc_id)
```

Formula:

```text
score(q,d) =
Σ idf(t) * tf(t,d) * (k1 + 1)
 / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl))
```

Defaults:

```text
k1 = 1.2 ~ 1.5
b = 0.75
```

## 去重

Deduplication uses stable ids:

- `chunk_id`
- `document_id + span`
- `graph_node_id`
- `community_report_id`

The same evidence may arrive from BM25, vector, graph, and community recall.
It must be merged before fusion/rerank to avoid over-counting one source.

## RRF 融合

RRF is the default coarse-rank fusion method:

```text
score(d) = Σ 1 / (k + rank_i(d))
```

Default:

```text
k = 60
```

RRF produces a fused candidate list across retrievers and query variants.
Optional rerank may run after RRF. RRF is not a final answer verifier.

## 证据与引用

The answer path must output:

- evidence bundle
- citation ids and source spans
- citation coverage
- retrievers used
- fusion trace
- optional rerank trace
- prompt version
- query prompt version
- index version
- community version
- latency
- cost when available

## 与 Agent 上下文的边界

Do not confuse:

```text
Agent Context
GraphRAGProjectSnapshot
Knowledge Evidence
```

`GraphRAGProjectSnapshot` is internal query configuration. Knowledge Evidence is
what returns to the Agent. Agent Context is what the model sees after
ContextOrchestrator selection.
