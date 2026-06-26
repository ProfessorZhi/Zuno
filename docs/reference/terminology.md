# Terminology

## Purpose

Keep public architecture terms stable and short. Detailed target contracts stay
in `.agent/architecture/near-term/`.

## Status Labels

- Current: current code and tests prove it.
- Target: near-term desired architecture that is not fully implemented.
- Future: longer-term direction such as Java services, microservices,
  event-driven workers, product-level multi-agent mode, or Coding Agent mode.
- History: superseded material retained for evidence.
- Blocked Legacy: should exit the front path, but still has active dependency.

## Current Terms

- `GeneralAgent single loop`: current knowledge-answering conversation path.
- `KnowledgeQueryService`: application knowledge query service introduced by
  Phase 11A and moved to the application boundary in Target Runtime V2.
- `GraphRAGQueryService`: GraphRAG Project query runtime introduced by Phase
  11A.
- `GraphRAGProjectSnapshot`: immutable query-time project/config snapshot.
- `KnowledgeQueryResult`: answer, documents, evidence, citation, version, and
  trace result model.

## Target Terms

- Context & Memory Engine
- Summary Compression
- Structured Extraction
- ToolCard
- Capability / Tool Retrieval
- Native BM25
- Optional vector tool search
- Multi-query retrieval
- Multi-retriever recall
- RRF fusion
- Optional rerank
- GraphRAG Project
- Basic / Local / Global / DRIFT query methods
- `auto` router
- Index / Update / Full Rebuild
- Evidence / Citation / Trace / Eval

## Target Term Boundaries

- Native BM25: local BM25 ranking algorithm. Elasticsearch may expose BM25
  scoring as an external adapter, but Elasticsearch is not the algorithm
  itself.
- ToolCard: compact retrievable metadata for a tool, MCP connector, skill, or
  knowledge capability. It is not the full injected tool schema.
- RRF fusion: coarse result fusion, default `k = 60`, followed by optional
  rerank when enabled.
- `auto` router: chooses `basic`, `local`, `global`, or `drift`; it is not a
  fifth GraphRAG query mode.
- External Knowledge: RAG/GraphRAG/file/web evidence. It is not Agent Memory.

## Blocked Legacy Terms

- Domain Pack
- `domain_pack_id`
- `DomainQAGraph`
- `MultiAgentSupervisorGraph`

## Retired Holding Areas

- Former `tests/compat/`: retired. Migration compatibility coverage now lives in
  root `tests/` until each test family receives a dedicated naming split.
