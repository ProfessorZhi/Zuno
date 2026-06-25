# Phase 08: GeneralAgent Runtime Integration

## Goal

Integrate Context Orchestrator, Memory layers, Capability System, and GraphRAG
Project query capability into the single `GeneralAgent` runtime.

## Dependency

Phase 05 through Phase 07 complete.

## Scope

- Prepare context before each model call.
- Commit raw events and derived memory after each turn.
- Route knowledge access through the existing `KnowledgeQueryService`.
- Keep the single `GeneralAgent` conversation path.

## Files To Change

- `src/backend/zuno/core/agents/general_agent.py`
- runtime/context/memory/capability modules
- Agent runtime tests

## Files Not To Change

- Retired Domain Pack runtime source or remaining root Domain Pack blockers.
- A second chat runtime.
- Product-level multi-agent default mode.

## Acceptance Gates

- One conversation path remains.
- Context trace records what entered the model call.
- Post-turn pipeline records raw events and derived updates.
- GraphRAG Project query returns Knowledge Evidence to the Agent.

## Verification Commands

```powershell
pytest -q tests/test_generalagent_context_memory_runtime.py
pytest -q tests/test_phase11b_single_generalagent_cutover.py
git diff --check
```

## Evidence To Return

- runtime call chain
- trace example
- focused test output
