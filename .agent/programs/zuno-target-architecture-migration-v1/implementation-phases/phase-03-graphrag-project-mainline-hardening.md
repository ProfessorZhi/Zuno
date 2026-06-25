# Phase 03: GraphRAG Project Mainline Hardening

## Goal

Make GraphRAG Project the stable mainline for knowledge query configuration,
query methods, evidence, citation, and trace.

## Dependency

Phase 01 and Phase 02 complete.

Current status: blocked by Phase 01 / Phase 02 for full closure. Safe prework
has started: `/knowledge/search` now routes through `KnowledgeQueryService`
instead of the legacy `RagHandler` search path, while preserving compatibility
response fields for current callers. Contract Review eval project assets now
use `to_project_payload()` as the main GraphRAG Project payload API, and
Structured/Cached graph extractors expose `project_payload` as their primary
payload parameter while keeping `domain_pack` as a migration alias. Contract
Review and stackless local eval graph extraction calls now use
`project_payload=project_payload`. Stackless eval entrypoints prefer `graphrag_project_id` /
`--graphrag-project-id` while retaining `domain_pack_id` only as migration
compatibility. Stable active architecture specs now frame retrieval governance,
LangGraph runtime, enhanced retrieval, platform direction, eval, and knowledge
config impact around GraphRAG Project / query policy instead of Domain Pack as
the target driver. Active near-term target docs now also classify retired
`DomainQAGraph`, retired Domain Pack endpoint/page wrappers, and bare
`domain_pack_id` query-policy wording as legacy or migration evidence instead
of current GraphRAG Project target evidence.

`GraphRetrieverAdapter` maps GraphRAG Project scope
(`scope_policy.graphrag_project_id`) to the current legacy graph storage filter
field (`domain_pack_id`). This is current compatibility with the existing
storage model, not a target endorsement of Domain Pack as the public contract.

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
- Active stable specs do not reintroduce Domain Pack as the GraphRAG Project
  mainline driver.

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
