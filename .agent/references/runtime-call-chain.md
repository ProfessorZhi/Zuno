# Runtime Call Chain

## Purpose

Summarize the current backend call direction.

## Current Shape

```text
HTTP route
  -> application/service function
  -> core/runtime orchestration
  -> GeneralAgent prepare_context
  -> GeneralAgent React loop
  -> post_turn_commit
  -> retrieval, GraphRAG, context contracts, memory, capabilities, tools, storage
  -> response DTO
```

## Rule

Lower layers do not depend backward on the API layer.

## Capability Boundary

Capability foundation code lives under
`src/backend/zuno/services/application/capabilities/`. It defines the current
metadata contract for Knowledge, ActionTool, MCPTool, MCPResource, MCPPrompt,
and Skill capabilities, plus a minimal selector that can return only relevant
schemas for a task. The existing API capability search service preserves its
previous response keys while also exposing the unified metadata fields.

GeneralAgent does not yet inject selected capabilities into every model turn;
full product-level capability orchestration remains Phase 09/future closure.

## GeneralAgent Context Runtime

`GeneralAgent.astream()` now prepares a `ModelContextPacket`, passes
`context_trace` and `model_context_packet` into the single React loop state,
and commits a scoped memory raw event plus task summary after the turn when
memory is enabled.

Detailed target behavior belongs in:

- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

## Known Limitations

Root Domain Pack assets are archived under
`docs/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. Compatibility tests remain Blocked
Legacy until Phase 11C proves replacement or deletion. The direct
`DomainQAGraph` backend source and Domain Pack runtime service package are
already retired from the current call chain.
