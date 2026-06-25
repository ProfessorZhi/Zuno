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
- `KnowledgeQueryService`: API-facing query service introduced by Phase 11A.
- `GraphRAGQueryService`: GraphRAG Project query runtime introduced by Phase
  11A.
- `GraphRAGProjectSnapshot`: immutable query-time project/config snapshot.
- `KnowledgeQueryResult`: answer, documents, evidence, citation, version, and
  trace result model.

## Target Terms

- Context & Memory Engine
- Capability System
- GraphRAG Project
- Basic / Local / Global / DRIFT query methods
- Index / Update / Full Rebuild
- Evidence / Citation / Trace / Eval

## Blocked Legacy Terms

- Domain Pack
- `domain_pack_id`
- `DomainQAGraph`
- `MultiAgentSupervisorGraph`

## Retired Holding Areas

- Former `tests/compat/`: retired. Migration compatibility coverage now lives in
  root `tests/` until each test family receives a dedicated naming split.
