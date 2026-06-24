# Enhanced Mode Pipeline

## Purpose

Define Enhanced Mode as a pipeline, not a single retriever.

## Current Evidence

- Frontend currently maps enhanced product mode to `rag_graph`.
- Backend normalizes `enhanced_retrieval` and `rag_graph` to deeper internal
  graph routes.
- `RetrievalOrchestrator` already handles vector, BM25, graph, community,
  drift-like, requery, fusion, fallback, and trace metadata.

## Target Definition

```text
Enhanced Mode
  = Auto Query Method Router
  + Query Rewrite
  + Multi-Retriever Recall
  + Fusion / RRF
  + Rerank
  + Evidence Check
  + Conditional Requery
  + Citation Answer
```

## Query Methods

### basic

```text
BM25
dense vector
fusion
rerank
evidence check
conditional requery
citation
```

### local

```text
BM25 / vector
entity linking
graph paths / graph neighbors
chunk backlink
fusion
rerank
citation
```

### global

```text
community reports
optional BM25/vector over reports
map-reduce
citation
```

### drift

```text
community reports primer
follow-up questions
local/basic retrieval per follow-up
evidence merge
reduce
citation
```

## Auto Router Rules

```text
specific entity / clause / amount / date / obligation / liability -> local
dataset-wide summary / overall risk / themes -> global
summary + evidence / multi-step analysis / risk categories -> drift
graph unavailable / community unavailable / simple question -> basic
```

## Fallback

```text
graph not ready -> basic
community reports not ready -> local/basic
evidence insufficient -> conditional requery
citation missing -> supplementary recall
drift too expensive -> local fallback
```
