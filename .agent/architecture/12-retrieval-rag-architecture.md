# Retrieval RAG Architecture

## Purpose

Separate query methods from retrievers.

## Current Evidence

- `RetrievalPlanner` currently resolves modes and internal routes.
- `VectorRetrieverAdapter`, `BM25RetrieverAdapter`, and `GraphRetrieverAdapter`
  already separate vector, keyword, and graph recall.
- `RetrievalFusion` merges documents from multiple sources with
  baseline-preserving metadata.
- `RagHandler` can mix Milvus/vector and Elasticsearch/BM25, then rerank.

## Target Definitions

```text
Query Method = answer strategy / reasoning path
Retriever = recall channel
```

Target query methods:

```text
auto
basic
local
global
drift
```

Target retrievers:

```text
BM25
dense vector
graph
community report
requery
tool
```

## Basic RAG Target

Basic is not weak mode. It is the standard strong baseline:

```text
query normalize / rewrite
BM25 recall
dense vector recall
fusion / RRF
rerank
evidence check
conditional requery
citation answer
```

Basic does not use graph/community assets. Enhanced mode may fall back to basic
when graph or community assets are missing, stale, too expensive, or low
confidence.
