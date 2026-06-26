# Phase 05: Context Contract Foundation

## Goal

Define typed context boundaries before changing memory persistence or Agent
runtime behavior.

## Dependency

Phase 04 complete.

## Scope

- Define `AgentExecutionContext`, `ModelContextPacket`, `TokenBudgetPolicy`,
  and `ContextTrace`.
- Keep Agent Context separate from `GraphRAGProjectSnapshot` and Knowledge
  Evidence.
- Add tests for construction, serialization, and trace fields.

## Files To Change

- new or existing context contract modules under `src/backend/zuno/`
- focused context tests
- `.agent/references/context-memory-map.md`

## Files Not To Change

- Long-term memory stores.
- GraphRAG query service implementation.
- Frontend UI.

## Acceptance Gates

- Context packet can be built without mutating GraphRAG snapshot.
- Token budget decisions are traceable.
- No second GraphRAG query runtime is introduced.

## 2026-06-26 Closure Evidence

Current context contracts live under:

- `src/backend/zuno/services/application/context/contracts.py`

The contract API defines:

- `AgentExecutionContext`
- `ModelContextPacket`
- `TokenBudgetPolicy`
- `ContextTrace`
- `ContextItem`
- `ContextSource`
- `ContextSelectionReason`

`ModelContextPacket` serializes the execution context, selected context items,
token budget, and trace without embedding or mutating
`GraphRAGProjectSnapshot`. `ContextTrace.from_items(...)` records selected and
dropped item ids, selection reasons, used tokens, and remaining budget. The
module exports contract types only and does not define a second
`GraphRAGProjectSnapshot` or `GraphRAGQueryService`.

## Verification Commands

```powershell
pytest -q tests/test_context_contracts.py
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_graphrag_project_contracts.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- contract API summary
- failing-then-passing test output
