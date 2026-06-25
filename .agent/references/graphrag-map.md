# GraphRAG Map

## Purpose

Orient GraphRAG boundary work without duplicating detailed target architecture.

## Current

The current GraphRAG Project Query Runtime includes:

- `src/backend/zuno/api/services/knowledge_query.py`
- `src/backend/zuno/services/graphrag/query_service.py`
- `GraphRAGProjectSnapshot`
- `GraphRAGQueryService`
- `KnowledgeQueryResult`

`GeneralAgent` reaches this runtime through `search_knowledge_base` and
`KnowledgeQueryService`.

Workspace knowledge prefetch and the Workspace `search_knowledge_base` tool
also reach this runtime through `KnowledgeQueryService`; they no longer call
`AgentRuntime` or `DomainQAGraph`.

The `/knowledge/search` API service path also reaches this runtime through
`KnowledgeQueryService`; it no longer calls the legacy `RagHandler` search
path directly.

## Target References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `examples/graphrag-projects/contract_review/`
- `.agent/programs/zuno-target-architecture-migration-v1/`
- `.agent/programs/official-graphrag-cleanup-v1/`

`examples/graphrag-projects/contract_review/` is the Target asset copy for
Contract Review schema, prompts, retrieval policy, and eval fixture. It is not
proof that all runtime paths no longer need `DomainPackLoader`;
`KnowledgeService.get_runtime_settings` and `GraphRetriever` policy resolution
no longer auto-load it. Stackless local eval and the dedicated Contract Review
eval can build from GraphRAG Project assets. The dedicated Contract Review eval
is cut over from `DomainQAGraph`; the direct `DomainQAGraph` source and
`src/backend/zuno/services/domain_pack/` runtime service package are retired.
Root Domain Pack assets are archived under
`docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. Stackless local eval now requires
GraphRAG Project assets when an id is provided.

## Blocked Legacy

Remaining migration compatibility dependencies in root `tests/` remain Blocked
Legacy until Phase 11C active dependency removal is proved. The former
`tests/compat/` holding area is retired. The graph classes are no longer public
exports from `zuno.core` or `zuno.core.graphs`; the direct `DomainQAGraph` and
`MultiAgentSupervisorGraph` sources are retired from current backend source,
and the Domain Pack runtime service source is retired too. Those retired
sources and root asset/Docker surfaces must stay absent while remaining
compatibility blockers are closed.
