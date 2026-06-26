# Context Memory Map

## Purpose

Orient Context/Memory design and implementation work without copying detailed
target architecture into a reference file.

## Current

Typed context contracts are Current under
`src/backend/zuno/services/application/context/`. A minimal pre-call
`ContextOrchestrator` is Current there as the builder for
`ModelContextPacket`, selected context items, dropped item reasons, and
`ContextTrace`.

Memory layer foundation contracts are Current under
`src/backend/zuno/services/memory/layers.py`. The single `GeneralAgent`
runtime now calls the minimal `ContextOrchestrator`, passes `ContextTrace`
metadata into its React loop state, and commits a scoped raw event plus task
summary to the memory layer when memory is enabled.

Context Orchestrator and Post-turn Pipeline are Target, not Current as mature
product behavior. Mature memory extraction/retrieval/consolidation integration
is later phase work. The current runtime still uses existing Agent and memory
surfaces under `src/backend/zuno/`.

## Target References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/18-context-memory-ideal-architecture.md`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/phase-05-context-contract-foundation.md`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/phase-06-memory-layer-foundation.md`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/phase-08-generalagent-runtime-integration.md`

## Rule

Do not implement a second `GraphRAGProjectSnapshot` or `GraphRAGQueryService`.
Future Context/Memory work must reuse the Phase 11A/11B query runtime results
unless fresh verification proves a different dependency boundary.

Phase 05 contract types separate Agent context from GraphRAG project snapshots
and knowledge evidence. Runtime integration belongs to Phase 08; memory storage
layering belongs to Phase 06.

Phase 06 memory layer contracts keep raw events as source of truth, require
source ids for summaries and candidates, scope long-term candidates by
user/agent/project/thread, and require explicit promotion before external
knowledge can become Agent memory.

Phase 08 runtime integration keeps a single `GeneralAgent` path and adds the
minimal current call shape:

```text
prepare_context
  -> ContextOrchestrator.prepare
  -> GeneralAgent React loop
  -> post_turn_commit
```

The old `context-memory-agent-runtime-v1` candidate program is archived under
`docs/history/programs/context-memory-agent-runtime-v1/`.
