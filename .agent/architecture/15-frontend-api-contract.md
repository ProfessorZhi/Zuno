# Frontend API Contract

## Purpose

Define the target product-facing API contract.

## Current Evidence

- `apps/web/src/utils/retrieval.ts` exposes `standard` as `rag` and enhanced as
  `rag_graph`, while mapping `rag_graph_deep` back to the product label.
- `apps/web/src/apis/knowledge.ts` includes `domain_pack_id`,
  `index_capability`, `graph_index_settings`, and retrieval modes such as
  `rag_graph_deep`.
- `apps/web/src/utils/knowledge-config.ts` creates standard/enhanced product
  configs and still carries `domain_pack_id`.

## Target Product Layer

```text
Standard Mode
Enhanced Mode
Advanced Settings: Auto / Basic / Local / Global / DRIFT
Index Status
GraphRAG Project Status
Prompt Version
Index Version
Trace
Evidence / Citation
```

## Target API Config

```text
graphrag_project_id
prompt_version
index_version
query_method
enhanced_mode_enabled
retrieval_trace_enabled
```

## Retired Fields

```text
domain_pack_id
domain_pack
rag_graph_deep
local_graphrag
community_global
drift_like
```

## Trace Contract

Backend trace should expose:

- requested query method
- resolved query method
- fallback reason
- retrievers used
- graph paths used
- community reports used
- citation coverage
- latency and cost metadata

Frontend may keep standard/enhanced simple by default. Advanced users can opt
into explicit query methods.
