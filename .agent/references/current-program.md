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

## Implementation Program

The executable near-term implementation breakdown lives in:

- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

Use these files when the user asks to implement the near-term ideal
architecture in target mode. They split the work into phases for legacy audit,
docs cleanup, Domain Pack contract retirement, GraphRAG Project contracts,
settings loading, prompt registry, index versioning, query method routing,
Enhanced Mode, frontend migration, runtime legacy deletion, and final
tests/eval/trace closure.

Do not use the implementation phases to pull Java, microservices,
event-driven workers, or default multi-agent mode into near-term acceptance.

## Current Implementation Status

- Phase 01 legacy surface audit is complete as read-only evidence.
- Phase 02 cleans docs, specs, and Agent references so current entrypoints point
  toward GraphRAG Project, Query Method, and Enhanced Mode rather than Domain
  Pack-era target language.
- Phase 03 adds `graphrag_project_id` as the preferred public config field and
  keeps `domain_pack_id` as bounded migration/runtime compatibility.
- Phase 04 adds first-class GraphRAG Project contract fields without claiming a
  loader.
- Phase 05 adds GraphRAG Project `settings.yaml` loading, prompt discovery, and
  readiness metadata without changing retrieval behavior.
- Phase 06 adds Prompt Registry categories and prompt-version impact rules
  without implementing automatic tuning.
- Phase 07 adds index version, hash flow, full rebuild boundary, and stale-index
  trace detection without database migration.
- Phase 08 adds the backend Query Method Router for
  `auto/basic/local/global/drift`, compatibility maps old route names, and
  exposes requested/resolved method plus fallback reason in trace metadata.
- Phase 09 hardens Enhanced Mode pipeline trace for query method routing,
  multi-retriever recall, fusion/rerank, evidence bundle, conditional requery,
  citation coverage, and standard-floor preservation.
- Phase 10 migrates frontend API/types/config utilities to GraphRAG Project and
  public query-method trace fields, and removes old runtime route names from
  `apps/web`.
- Phase 11 is next: Runtime Legacy Deletion.

## Current Rule

Do not rewrite completed Phase 0-6 files as incomplete.

Do not keep superseded programs in the front path. Move them under `docs/architecture/history/programs/` and link them as archived context only.
