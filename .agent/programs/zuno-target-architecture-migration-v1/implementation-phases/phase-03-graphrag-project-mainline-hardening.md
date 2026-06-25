# Phase 03: GraphRAG Project Mainline Hardening

## Goal

Make GraphRAG Project the stable mainline for knowledge query configuration,
query methods, evidence, citation, and trace.

## Dependency

Phase 01 and Phase 02 complete.

Current status: blocked by Phase 01 / Phase 02 for full closure. Safe prework
has started: `/knowledge/search` now routes through `KnowledgeQueryService`
instead of the legacy `RagHandler` search path, while preserving compatibility
response fields for current callers.

## Scope

- Harden `graphrag_project_id` and `query_method` contracts.
- Reuse the existing `GraphRAGProjectSnapshot` and `GraphRAGQueryService`.
- Remove old public names from current docs, API surfaces, frontend labels, and
  eval current paths.

## Files To Change

- `src/backend/zuno/api/services/knowledge_query.py`
- `src/backend/zuno/services/graphrag/`
- `apps/web/src/apis/`
- GraphRAG contract tests
- docs and `.agent/references/`

## Files Not To Change

- Context/Memory runtime.
- A second snapshot or query service.
- Future microservice boundaries.

## Acceptance Gates

- Public query methods are `auto/basic/local/global/drift`.
- Old names remain only in history, migration notes, or explicit compatibility
  tests.
- Query result includes evidence, citation, versions, and trace metadata.

## Verification Commands

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_graphrag_project_contracts.py
pytest -q tests/test_standard_retrieval_composition.py tests/test_enhanced_retrieval_composition.py
git grep -n "domain_pack_id"
git grep -n "rag_graph_deep"
git grep -n "local_graphrag"
git diff --check
```

## Evidence To Return

- contract diff summary
- grep classification
- focused test output
