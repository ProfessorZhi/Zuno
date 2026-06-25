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

Domain Pack assets/services and compatibility tests remain Blocked Legacy until
Phase 11C proves safe deletion. The direct `DomainQAGraph` backend source is
already retired from the current call chain.
