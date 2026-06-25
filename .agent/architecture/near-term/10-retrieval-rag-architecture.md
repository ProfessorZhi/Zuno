# Retrieval RAG Architecture

## Purpose

Separate query methods from retrievers and define Basic RAG.

## Current Evidence

- `RetrievalPlanner` resolves current modes and internal routes.
- `VectorRetrieverAdapter`, `BM25RetrieverAdapter`, and `GraphRetrieverAdapter`
  separate vector, keyword, and graph recall.
- `RetrievalFusion` merges evidence with baseline-preserving metadata.
- `RagHandler` mixes Milvus/vector and Elasticsearch/BM25 when available, then
  reranks.
- `RetrievalOrchestrator` records `pipeline_trace`, `evidence_bundle`,
  `citation_coverage`, and `retrievers_used` for Basic and Enhanced pipeline
  proof.

## Target Definitions

```text
Query Method = answering strategy / reasoning path
Retriever = recall channel
```

Near-term query methods:

```text
auto
basic
local
global
drift
```

Near-term retrievers:

```text
BM25
dense vector
graph
community report
requery
```

## Basic RAG

```text
Basic RAG
  = query rewrite
  + BM25
  + dense vector
  + fusion / RRF
  + rerank
  + evidence check
  + conditional requery
  + citation answer
```

Basic is not a weak fallback. It is the strong non-graph baseline. It does not
use graph or community assets.

## Migration Notes

Current names like `rag`, `rag_graph`, `rag_graph_deep`, and `hybrid` should be
mapped toward public query methods. Internal compatibility names must not leak
into frontend product contracts after the migration.

## Acceptance Direction

Tests should prove Basic uses BM25 when available, dense vector recall, fusion,
rerank or score fallback, citation metadata, and traceable fallback. Current
backend tests cover this through the orchestrator trace contract; frontend
contract migration remains a later phase.
