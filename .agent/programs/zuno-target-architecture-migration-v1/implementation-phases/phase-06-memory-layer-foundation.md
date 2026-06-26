# Phase 06: Memory Layer Foundation

## Goal

Introduce memory layers with raw events as the source of truth.

## Dependency

Phase 05 complete.

## Scope

- Separate working context, short-term state, task memory, long-term memory, and
  external knowledge.
- Add append-only raw event logging or an approved adapter over the existing
  event source.
- Add source-linked summaries and memory candidate records.

## Files To Change

- memory service modules under `src/backend/zuno/services/memory/`
- runtime state/checkpoint adapters
- focused memory tests

## Files Not To Change

- GraphRAG Project query runtime.
- Domain Pack compatibility surfaces.
- Database schema unless separately approved.

## Acceptance Gates

- Raw events are not deleted by compaction.
- Task summaries include source event ids.
- Long-term memory writes are scoped and traceable.
- External knowledge is not stored as Agent memory without an explicit
  promotion path.

## 2026-06-26 Closure Evidence

Memory layer foundation contracts live under:

- `src/backend/zuno/services/memory/layers.py`

The layer API defines:

- `MemoryLayer`: working context, short-term, task memory, long-term, and
  external knowledge.
- `MemoryScope`: `user_id`, `agent_id`, `project_id`, and `thread_id`.
- `RawMemoryEvent`: append-only raw event record.
- `TaskMemorySummary`: source-linked task/session summary.
- `MemoryCandidate`: scoped long-term memory candidate with confidence,
  `source_event_ids`, `dedupe_key`, and retention policy.
- `ExternalKnowledgeRecord`: knowledge evidence that requires explicit
  promotion before becoming Agent memory.
- `RetentionPolicy`: TTL and privacy deletion boundary.
- `InMemoryLayerStore`: testable adapter proving summaries do not delete raw
  events.

Existing `memory_client` persistence remains unchanged. No database schema,
GraphRAG query runtime, Domain Pack compatibility surface, or GeneralAgent
runtime integration changed in this phase.

## Verification Commands

```powershell
pytest -q tests/test_memory_layers.py
pytest -q tests/test_context_contracts.py
git diff --check
```

## Evidence To Return

- memory layer table
- test output
- migration notes
