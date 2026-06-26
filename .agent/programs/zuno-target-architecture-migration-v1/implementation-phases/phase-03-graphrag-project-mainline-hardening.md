# Phase 03: GraphRAG Project Mainline Hardening

## Goal

Make GraphRAG Project the stable mainline for knowledge query configuration,
query methods, evidence, citation, and trace.

## Dependency

Phase 01 and Phase 02 complete.

Current status: complete for public GraphRAG Project mainline hardening.
Internal retrieval/eval labels such as `rag_graph_deep` and `local_graphrag`
remain classified as implementation or ablation labels, not public query
methods. `/knowledge/search` now routes through `KnowledgeQueryService`
instead of the legacy `RagHandler` search path, while preserving compatibility
response fields for current callers. Contract Review eval project assets now
use `to_project_payload()` as the main GraphRAG Project payload API, and
Structured/Cached graph extractors expose `project_payload` as their payload
parameter without the old `domain_pack` payload alias. Contract Review,
stackless local eval, active pipeline graph extraction, and extractor contract
tests now use `project_payload=project_payload`. Stackless eval entrypoints prefer `graphrag_project_id` /
`--graphrag-project-id` while retaining `domain_pack_id` only as migration
compatibility. Runtime settings now expose GraphRAG Project payload state under
`project_payload`; the old `domain_pack` runtime payload key is accepted only
as a migration fallback where older producers still exist. Stable active
architecture specs now frame retrieval governance,
LangGraph runtime, enhanced retrieval, platform direction, eval, and knowledge
config impact around GraphRAG Project / query policy instead of Domain Pack as
the target driver. Active near-term target docs now also classify retired
`DomainQAGraph`, retired Domain Pack endpoint/page wrappers, and bare
`domain_pack_id` query-policy wording as legacy or migration evidence instead
of current GraphRAG Project target evidence.

`GraphRetrieverAdapter`, `GraphRetriever`, `GraphWriter`, structured graph
extraction, pipeline graph indexing, and the Neo4j client now use
`graphrag_project_id` as the primary graph scope. Neo4j query filters dual-read
old `domain_pack_id` properties with `COALESCE` only for pre-backfill data.
This is migration compatibility, not a target endorsement of Domain Pack as
the public contract.

Stackless Contract Review local eval coverage now lives in
`tests/test_stackless_local_eval_contract_project_query_policy.py`, which
builds from `graphrag_project_id="contract_review"` and explicit GraphRAG
Project `query_policy`.

## 2026-06-26 Closure Evidence

- `GraphRAGProjectContract` accepts public query methods
  `auto/basic/local/global/drift` and rejects legacy method names such as
  `community_global`.
- Normalized public knowledge config keeps `graphrag_project_id` and no longer
  emits `domain_pack_id`.
- `KnowledgeQueryService` and `GraphRAGQueryService` remain the GraphRAG
  Project query mainline and preserve evidence/citation/version/trace metadata.
- Standard/enhanced retrieval composition tests cover the public composition
  path while `rag_graph_deep` and `local_graphrag` remain internal route/eval
  labels.
- Grep gates for `domain_pack_id`, `rag_graph_deep`, and `local_graphrag` are
  classified as migration aliases, internal implementation labels, eval
  ablations, audits, or history.

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
