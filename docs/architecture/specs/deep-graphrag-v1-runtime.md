# Deep GraphRAG V1 Runtime

## Purpose

This spec defines the runtime contract for `增强检索` in the new knowledge product round.

## Product To Runtime Mapping

### Standard Retrieval

Product label:

```text
标准检索
```

Default runtime chain:

```text
query rewrite
  -> vector + bm25
  -> fusion
  -> rerank
  -> citation answer
```

### Enhanced Retrieval

Product label:

```text
增强检索
```

Default internal mode:

```text
rag_graph_deep
```

Enhanced retrieval is not one fixed retriever.
It is a routed runtime umbrella.

## Internal Route Space

The runtime may choose among:

- `hybrid_rag`
- `local_graphrag`
- `community_global`
- `drift_like`

## Router Decision Rules

### Fact Question

Use primarily:

```text
vector + bm25 + rerank
```

### Relation Question

Use primarily:

```text
hybrid entry
  -> entity seed
  -> local graph
  -> cited answer
```

### Global Theme Question

Use primarily:

```text
community reports
  -> global search
  -> aggregated answer
```

### Global Plus Evidence Question

Use primarily:

```text
community reports
  -> broad answer
  -> follow-up questions
  -> local graph evidence search
  -> final answer
```

## Fallback Rules

1. BM25 unavailable
   - degrade to vector-only
   - record `bm25_unavailable`
2. graph unavailable
   - degrade to standard RAG
3. community reports not ready
   - degrade to local graph
4. rerank unavailable
   - degrade to score-based ordering

## Community GraphRAG V1 Scope

1. `level=0` community detection
2. stored community reports
3. community-aware global search
4. stale marking after graph-changing file updates

## DRIFT-like V1 Scope

1. top community selection
2. broad first-pass answer
3. one follow-up round
4. local graph evidence deepening

## Required Trace Metadata

Enhanced retrieval should expose at least:

- `requested_mode`
- `resolved_mode`
- `internal_route`
- `query_variants`
- `enabled_retrievers`
- `used_vector`
- `used_bm25`
- `used_graph`
- `used_communities`
- `used_paths`
- `follow_up_questions`
- `fallback_reason`
- `rerank_info`
- `citation_chunks`
