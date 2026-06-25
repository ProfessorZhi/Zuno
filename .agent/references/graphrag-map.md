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
still executes through `DomainQAGraph`; direct `DomainQAGraph` id-only fallback
and generic legacy eval fallback paths remain Blocked Legacy until the
runtime/eval cutover is complete.

## Blocked Legacy

Domain Pack surfaces, `DomainQAGraph`, and `tests/compat/` remain Blocked
Legacy until Phase 11C active dependency removal is proved. The graph classes
are no longer public exports from `zuno.core` or `zuno.core.graphs`; the direct
`MultiAgentSupervisorGraph` source is retired, while the direct
`DomainQAGraph` module still exists for Blocked Legacy coverage and eval
dependencies.
