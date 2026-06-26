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

- Complete. One conversation path remains: `GeneralAgent.astream()` still
  drives the single React loop.
- Complete. `prepare_context()` records a `ModelContextPacket` and
  `ContextTrace` before the model call, then passes both into the loop state.
- Complete. `post_turn_commit()` records a scoped raw event and task summary
  into the memory layer when memory is enabled.
- Complete. GraphRAG Project knowledge access still routes through
  `search_knowledge_base -> KnowledgeQueryService`.

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

## Closure Evidence

- Runtime call chain:
  `prepare_context -> GeneralAgent React loop -> post_turn_commit`.
- Trace example:
  `context_trace.selected_item_ids` includes recent message items and selected
  capability schema item ids such as `search_knowledge_base`.
- Memory example:
  `RawMemoryEvent(layer=WORKING, event_type=agent_turn)` and
  `TaskMemorySummary(layer=TASK, source_event_ids=(raw_event_id,))`.
- Focused tests:
  `python -m pytest -q tests/test_generalagent_context_memory_runtime.py`
  passed.
