# Frontend API Contract

## Purpose

Define the near-term frontend/backend contract.

## Current Evidence

- `apps/web/src/utils/retrieval.ts` maps `rag` to Standard Mode and `rag_graph`
  to Enhanced Mode.
- `apps/web/src/apis/knowledge.ts` now exposes `graphrag_project_id` as the
  preferred public field while retaining `domain_pack_id` as migration
  compatibility.
- `apps/web/src/apis/knowledge.ts` also exposes `graphrag_project` with
  settings path, prompt/index/query/community versions, document/chunk hashes,
  query method, and project status.
- `apps/web/src/utils/knowledge-config.ts` creates standard/enhanced product
  configs, creates a GraphRAG Project contract object only when a project id
  exists, and writes Enhanced Mode as `rag_graph` plus
  `graphrag_project.query_method=auto`.
- `apps/web/src/apis/knowledge.ts` types requested/resolved query method,
  retrievers, evidence bundle, citation coverage, and pipeline trace metadata.
- Old query route names no longer appear under `apps/web`; remaining Domain
  Pack pages are migration/runtime surfaces for the runtime deletion phase.

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

## Target Fields

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

## Trace Fields

Frontend may display:

- requested query method
- resolved query method
- fallback reason
- retrievers used
- graph paths used
- community reports used
- citation coverage
- index and prompt versions

## Migration Notes

Keep the simple Standard/Enhanced UX. Move advanced GraphRAG details into an
advanced panel or trace view.

## Acceptance Direction

Frontend API tests should prove old internal route names do not appear in new
public product contracts except in explicit migration/retired terminology docs.

Current frontend contract satisfies this for `apps/web`. Runtime compatibility
deletion remains a later phase.
