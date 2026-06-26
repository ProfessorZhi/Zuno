# Runtime Call Chain

## Purpose

Summarize the current backend call direction.

## Current Shape

```text
HTTP route
  -> application/service function
  -> core/runtime orchestration
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
that runtime integration belongs to Phase 08.

## Known Limitations

Root Domain Pack assets are archived under
`docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. Compatibility tests remain Blocked
Legacy until Phase 11C proves replacement or deletion. The direct
`DomainQAGraph` backend source and Domain Pack runtime service package are
already retired from the current call chain.
