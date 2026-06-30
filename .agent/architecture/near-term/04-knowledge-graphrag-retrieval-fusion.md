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

当前代码已经有 `KnowledgeQueryService`、`GraphRAGQueryService`、
`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。

PHASE08 当前新增并已由测试证明的事实是：

- `GraphRAGExtractorConfig` 能表达 LLM-first extractor config、rule fallback、model / prompt / schema / policy / eval refs。
- `KnowledgeQueryService.build_project_snapshot()` 会把现有 `knowledge_config` JSON 转成 `GraphRAGProjectSnapshot.extractor_config`。
- `GraphRAGQueryService` 和 `RetrievalOrchestrator` 会在 trace metadata 中暴露 `query_method_contract`、`citation_contract` 和 `retrieval_fusion_contract`。
- 显式 `global` 当前走 `community_global`，不与 vector / BM25 chunk-level retrievers 扁平混榜；缺少 chunk/span grounding 时 citation contract 必须保持 `missing`。

仍在 Target 的内容包括生产级 schema-constrained LLM 抽取执行、完整 RRF、成熟 rerank 治理、多套 extractor orchestration 和前端 trace 面板。

## GraphRAG 查询模式

The internal query methods are exactly:

- `basic`
- `local`
- `global`
- `drift`

`auto` is a router. It is not a fifth query mode. Product users should see
普通模式 / 增强模式 / 自动模式 first; only advanced users and traces need the
internal `query_method` labels.

Mode meanings:

```text
basic
  Native BM25 + Vector + RRF + optional rerank

local
  entity / relation / graph neighborhood / source chunks

global
  community reports / global summaries / corpus-level prior

drift
  global community primer -> follow-up questions -> local/basic evidence loop
```

The router records requested method, resolved method, fallback reason, and
method availability. If graph/community assets are not ready, the trace must
show the fallback clearly.

PHASE04 已落地的当前 trace contract 名称：

| 字段 | 当前含义 |
| --- | --- |
| `requested_product_mode` / `resolved_product_mode` | `normal / enhanced / auto` 产品模式。 |
| `router_decision` | `normal_basic` 或 `enhanced_basic|local|global|drift` 路由解释。 |
| `requested_query_method` / `resolved_query_method` | requested 可为 `auto`；resolved 只允许 `basic / local / global / drift`。 |
| `fallback_reason` | graph/community/fallback 触发原因。 |
| `budget_policy` / `fallback_policy` | top-k、rewrite、retry、route broadening 等策略证据。 |
| `citation_coverage` / `retrievers_used` | 证据覆盖率和实际检索器。 |

## 产品模式

```text
普通模式
  fixed low-budget basic path

增强模式
  controlled Agentic RAG path
  may use basic / local / global / drift

自动模式
  router decides direct / basic / enhanced
```

Manual override is allowed for debugging, eval, and advanced UI, but the
default product path should not force users to understand every GraphRAG query
method.

## GraphRAG 实体抽取目标

GraphRAG 建图的 entity / relation discovery 默认走 LLM 抽取。规则、正则和词典不是主路径，只能作为确定格式辅助、预处理、LLM 不可用时的 fallback 或 baseline test。

知识库配置必须能表达：

```text
graph_index_settings.entity_extraction_mode = llm
model_refs.entity_extraction_llm_id = <selected LLM id>
prompt_refs.entity_extraction_prompt_id = <selected prompt id>
schema_refs.entity_extraction_schema_version = <selected schema version>
policy_refs.entity_extraction_cost_latency_profile = <selected policy>
eval_refs.entity_extraction_eval_profile = <selected eval profile>
```

同一个 workspace 可以保留多套知识库配置。每个 GraphRAG Project 或
knowledge base 必须能选择自己的 entity extractor config；这不是 Agent
Memory，也不是全局硬编码正则规则。

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

## Global 与 BM25 的边界

`global` should not be fused with BM25 top-k as if both were the same evidence
type. Global search produces corpus-level or community-level priors. Basic and
local search produce chunk, entity, relation, and source-span evidence.

Target behavior:

```text
global
  -> community reports / global summaries
  -> candidate claims or themes
  -> local/basic evidence grounding when citations are required
```

This means BM25 and vector retrieval are still useful, but they usually appear
after the global primer as evidence grounding, not as a flat RRF list mixed
directly with community reports.

## DRIFT 边界

`drift` is the explicit "global first, local next" path:

```text
community global primer
  -> follow-up questions
  -> local graph expansion
  -> basic BM25/vector evidence backfill
  -> evidence merge
  -> answer synthesis
```

Use drift for architecture diagnosis, migration risk, priority suggestions,
multi-hop explanation, and other tasks where the system needs both broad
context and source-level proof.

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
