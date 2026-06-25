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

Root Domain Pack assets are archived under
`docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. Compatibility tests remain Blocked
Legacy until Phase 11C proves replacement or deletion. The direct
`DomainQAGraph` backend source and Domain Pack runtime service package are
already retired from the current call chain.
