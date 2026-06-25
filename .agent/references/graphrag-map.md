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

## Target References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `.agent/programs/zuno-target-architecture-migration-v1/`
- `.agent/programs/official-graphrag-cleanup-v1/`

## Blocked Legacy

Domain Pack surfaces, `DomainQAGraph`, `MultiAgentSupervisorGraph`, and
`tests/compat/` remain Blocked Legacy until Phase 11C active dependency removal
is proved.
