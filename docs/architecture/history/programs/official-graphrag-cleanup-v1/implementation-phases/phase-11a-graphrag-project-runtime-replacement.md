# Phase 11A: GraphRAG Project Runtime Replacement

## Goal

Create a project-first knowledge query runtime before deleting legacy runtime
surfaces.

## Status

Complete. Commit `24abdd9` introduced `KnowledgeQueryService`,
`GraphRAGQueryService`, `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult`.
Fresh verification should still be run before using this as dependency evidence.

Fresh status-sync evidence from this docs run:

- `pytest -q tests/test_phase11a_knowledge_query_service.py` passed.
- Code read confirmed the query runtime is in
  `src/backend/zuno/api/services/knowledge_query.py` and
  `src/backend/zuno/services/graphrag/query_service.py`.
- Phase 11C deletion remains blocked; this status does not delete legacy
  runtime surfaces.

## Why This Phase Exists

The old Phase 11 combined replacement and deletion. That made active imports a
global blocker even though the replacement path is the thing that removes those
imports. Phase 11A is allowed to run while legacy code still exists.

## Scope

- Add a single knowledge query Application Service.
- Add a GraphRAG Project query service that uses a project snapshot.
- Reuse `RetrievalPlanner`, `RetrievalOrchestrator`, fusion, retriever adapters,
  evidence, citation, fallback, and trace logic.
- Prove the new query path does not call `DomainPackLoader` or `DomainQAGraph`.

## Non-goals

- Cutting `GeneralAgent` traffic.
- Deleting Domain Pack, `DomainQAGraph`, or compatibility tests.
- Context Orchestrator or memory redesign.

## Candidate Files

- `src/backend/zuno/api/services/knowledge_query.py`
- `src/backend/zuno/services/graphrag/query_service.py`
- `tests/test_phase11a_knowledge_query_service.py`

## Acceptance Criteria

- A project-first query service can be tested independently.
- New query path accepts `graphrag_project_id` and target `query_method` values.
- New query path does not import or call `DomainPackLoader`.
- New query path does not put `domain_pack_id` in retrieval options.
- Unified result includes answer, documents, evidence, citations, requested and
  resolved query method, retrievers, versions, and trace metadata.

## Verification Commands

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py
pytest -q tests/test_graphrag_project_contracts.py tests/test_graphrag_project_loader.py tests/test_graphrag_prompt_registry.py
pytest -q tests/test_standard_retrieval_composition.py tests/test_enhanced_retrieval_composition.py
git diff --check
```

## Evidence Package Required

- failing test output before implementation
- passing targeted test output
- grep proof for new path legacy isolation
- commit hash and push result
