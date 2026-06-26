# GraphRAG Map

## Purpose

Orient GraphRAG boundary work without duplicating detailed target architecture.

## Current

The current GraphRAG Project Query Runtime includes:

- `src/backend/zuno/services/application/knowledge/query_service.py`
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

GraphRAG Project scope currently reaches graph storage through
`graphrag_project_id`: `GraphRetrieverAdapter`, `GraphRetriever`,
`GraphWriter`, structured graph extraction, pipeline graph indexing, and the
Neo4j client use it as the primary graph scope. Neo4j queries dual-read legacy
`domain_pack_id` properties with `COALESCE` until the backfill helper is
applied. This must not be described as Domain Pack being the target public
contract.

## Target References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `examples/graphrag-projects/contract_review/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`

`examples/graphrag-projects/contract_review/` is the Target asset copy for
Contract Review schema, prompts, retrieval policy, and eval fixture. It is not
proof that all runtime paths no longer need `DomainPackLoader`;
`KnowledgeService.get_runtime_settings` and `GraphRetriever` policy resolution
no longer auto-load it. Stackless local eval and the dedicated Contract Review
eval can build from GraphRAG Project assets. The dedicated Contract Review eval
is cut over from `DomainQAGraph`; the direct `DomainQAGraph` source and
`src/backend/zuno/services/domain_pack/` runtime service package are retired.
Root Domain Pack assets are archived under
`docs/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. Stackless local eval now requires
GraphRAG Project assets when an id is provided. Contract Review and stackless
local graph extraction calls use `project_payload=project_payload`; active
pipeline graph extraction also passes `project_payload`, and graph extractors
no longer expose a `domain_pack` payload parameter alias. Extracted graph
items now carry `graphrag_project_id`; `domain_pack_id` remains only as a
legacy input/backfill/eval compatibility surface where explicitly tested.

## Blocked Legacy

Remaining migration compatibility references in root `tests/` are bounded to
storage/eval/DB alias roles. The former
`tests/compat/` holding area is retired. The graph classes are no longer public
exports from `zuno.core` or `zuno.core.graphs`; the direct `DomainQAGraph` and
`MultiAgentSupervisorGraph` sources are retired from current backend source,
and the Domain Pack runtime service source is retired too. Those retired
sources and root asset/Docker surfaces must stay absent while remaining
compatibility blockers are closed.
