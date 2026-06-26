# Phase 04 Context Orchestrator Minimal Runtime

## Goal

Promote the current context foundation into a callable, focused
`ContextOrchestrator` without rewriting `GeneralAgent` streaming.

## Status

Complete for this first runtime slice. This phase adds callable pre-call
context preparation only; mature memory extraction/retrieval/consolidation,
the full Post-turn Pipeline, and full LangGraph runtime graph remain later
phase targets.

## Required Behavior

- `ContextOrchestrator`
- `ContextPreparationInput`
- `ContextPreparationResult`
- `RecentWindowSelector`
- `TokenBudgetPolicy.apply(...)`
- Context trace with selection and eviction reason
- `ModelContextPacket` builder
- tool call/result group protection
- explicit user constraint priority
- Knowledge Evidence and Memory context separation
- no memory / no knowledge fallback

## Non-Goals

- live LLM summarization.
- long-term memory extraction.
- database schema changes.
- full Post-turn Pipeline.
- frontend UI.
- full LangGraph runtime graph.

## Verification

```powershell
pytest -q tests/test_context_orchestrator.py -p no:cacheprovider
pytest -q tests/test_phase11b_single_generalagent_cutover.py -p no:cacheprovider
pytest -q tests/test_agent_system.py tests/test_repo_hygiene.py -p no:cacheprovider
python .agent/scripts/verify_module_boundaries.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence

- `src/backend/zuno/services/application/context/orchestrator.py`
- `tests/test_context_orchestrator.py`
- `docs/architecture/current-architecture.md`
- `.agent/references/context-memory-map.md`
