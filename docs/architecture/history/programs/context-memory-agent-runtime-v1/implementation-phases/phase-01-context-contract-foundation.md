# Phase 01: Context Contract Foundation

## Goal

Define the typed contracts that make context assembly explicit before changing
runtime behavior.

## Dependency

Phase 00 complete. Runtime implementation begins only if the dependency gate is
open.

## Scope

- Define `AgentExecutionContext`.
- Define `ModelContextPacket`.
- Define `TokenBudgetPolicy`.
- Define `ContextTrace`.
- Add tests proving the contracts serialize, validate, and preserve source ids.

## Files To Change

- backend context/runtime contract modules
- backend contract tests
- Agent docs if names or boundaries change

## Files Not To Change

- GraphRAG query behavior
- frontend UI
- legacy runtime deletion surfaces

## Acceptance Gates

- Contracts distinguish request context, graph state, conversation state,
  knowledge evidence, tool context, persistence state, and trace context.
- `ModelContextPacket` contains only content selected for the current model
  call, not all known memory.
- `ContextTrace` records why each context item was selected or evicted.

## Verification Commands

```powershell
pytest -q tests
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- contract module paths
- tests added or updated
- example `ModelContextPacket` fields
