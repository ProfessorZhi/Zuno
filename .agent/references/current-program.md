# Current Program

The active architecture program is:

- `docs/architecture/programs/official-graphrag-cleanup-v1/`

## Why This Program Exists

The previous Phase 0-6 closure is complete. It should remain a completed historical baseline.

The new work is a separate cleanup and alignment program:

1. standardize `docs/`, `AGENTS.md`, `.agent/`, and `history`
2. clean legacy entrypoints and stale workflow wording
3. retire Domain Pack as the front-path architecture mainline
4. align future GraphRAG work with official GraphRAG Project, Prompt Tuning, and Query Method concepts

## Detailed Target Architecture V0.1

The detailed design-stage architecture working set is:

- `.agent/architecture/`

Its current structure separates near-term and future direction:

- `.agent/architecture/near-term/`
  - detailed next refactor target for Python FastAPI, Service Layer, LangGraph,
    LLM/Tool adapters, RAG/GraphRAG, Enhanced Mode, persistence, frontend API,
    observability, and near-term migration
- `.agent/architecture/future/`
  - horizon planning for Java business services, microservices, event-driven
    workers, and multi-agent mode
- `.agent/architecture/decisions/`
  - locked near-term choices, open questions, and retired surfaces

Future material is not an implementation-complete claim and is not a near-term
acceptance target. The current program remains focused on GraphRAG official
alignment, Enhanced Mode, Domain Pack retirement, and legacy cleanup.

## Current Rule

Do not rewrite completed Phase 0-6 files as incomplete.

Do not keep superseded programs in the front path. Move them under `docs/architecture/history/programs/` and link them as archived context only.
