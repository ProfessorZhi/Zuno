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

## Verification Commands

```powershell
pytest -q tests/test_context_contracts.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- contract API summary
- failing-then-passing test output
