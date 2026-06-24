# Enhanced Mode Pipeline

## Purpose

Define Enhanced Mode as a pipeline, not a single retriever.

## Current Evidence

- `apps/web/src/utils/retrieval.ts` exposes standard/enhanced product language.
- Backend mode normalization maps enhanced style names into deeper graph routes.
- `RetrievalOrchestrator` handles vector, BM25, graph, community, drift-like,
  requery, fusion, fallback, and trace metadata.

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
BM25 + dense vector + fusion + rerank + evidence check
  + conditional requery + citation
```

### local

```text
BM25/vector + entity linking + graph paths/neighbors + chunk backlink
  + fusion + rerank + citation
```

### global

```text
community reports + optional BM25/vector over reports + map-reduce + citation
```

### drift

```text
community reports primer + follow-up questions
  + local/basic retrieval per follow-up + evidence merge + reduce + citation
```

## Auto Router

```text
specific clause / entity / amount / date / obligation / liability -> local
overall risk / theme summary / dataset-level question -> global
summary then evidence / multiple risk categories / multi-step analysis -> drift
graph unavailable / community unavailable / normal fact QA -> basic
```

## Fallback

```text
graph not ready -> basic
community reports not ready -> local/basic
evidence insufficient -> conditional requery
citation missing -> supplementary recall
drift too expensive -> local fallback
```

## Migration Notes

Keep product labels as Standard and Enhanced. Advanced settings may expose
Auto, Basic, Local, Global, and DRIFT. Do not expose `local_graphrag`,
`community_global`, or `drift_like` to normal users.

## Acceptance Direction

Enhanced Mode is ready when trace proves requested method, resolved method,
retrievers used, fallback reason, evidence bundle, and citation coverage.
