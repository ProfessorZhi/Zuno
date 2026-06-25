# Runtime Call Chain

## Purpose

Summarize the current backend call direction.

## Current Shape

```text
HTTP route
  -> application/service function
  -> core/runtime orchestration
  -> retrieval, GraphRAG, memory, tools, storage
  -> response DTO
```

## Rule

Lower layers do not depend backward on the API layer.

## Known Limitations

Domain Pack and `DomainQAGraph` remain Blocked Legacy until Phase 11 proves
safe deletion.
