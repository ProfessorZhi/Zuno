# Architecture Decisions

## Purpose

Keep Agent-side architecture choices concise. Formal human-facing ADRs remain
under `docs/architecture/decisions/`.

## Locked Near-Term Decisions

- Keep one `GeneralAgent` conversational runtime.
- Treat GraphRAG Project as the target knowledge project boundary.
- Keep Domain Pack terms as history, migration compatibility, or retirement
  guards only.
- Keep `.agent/architecture/near-term/` as Target design, not Current Truth.
- Keep Java, microservices, event workers, Coding Agent mode, and product-level
  multi-agent mode in future horizon unless a separate program opens them.

## Open Questions

- Exact persistence model for mature structured long-term memory.
- Whether ToolCard vector retrieval is needed before Native BM25 proves
  insufficient.
- When to split async indexing workers into a separately deployable service.
- Whether the full GeneralAgent runtime graph should be explicit LangGraph nodes
  or a thinner LangGraph wrapper around the existing loop.

## Retired Surfaces

- `DomainQAGraph`
- `MultiAgentSupervisorGraph`
- `AgentRuntime` facade
- active Domain Pack runtime and frontend pages
- root `domain-packs/`
- old fragmented near-term 01-19 target docs as active source
