# Official GraphRAG Cleanup V1

## Goal

This is a new architecture program. It does not overwrite the completed Phase 0-6 closure truth.

The program standardizes the documentation and Agent workflow system, cleans legacy surfaces, retires Domain Pack as the front-path architecture mainline, and aligns the next GraphRAG work with official GraphRAG Project, Prompt Tuning, and Query Method concepts.

## Program Boundary

Formal truth lives in `docs/`. Agent workflow aids live in `.agent/`. Superseded material moves to `docs/architecture/history/`.

## Detailed Target Architecture V0.1

The detailed design-stage target architecture working set lives at:

- `.agent/architecture/`
- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
  as the canonical Target / Proposed visual blueprint, not Current Truth

It is split into:

- `.agent/architecture/near-term/`
  - detailed next refactor target for the current Python AI Runtime
  - FastAPI, Service Layer, LangGraph, LLM/Tool adapters, RAG/GraphRAG,
    Enhanced Mode, persistence, frontend API, observability, and migration
- `.agent/architecture/future/`
  - horizon planning for Java business services, microservices, event-driven
    workers, and multi-agent mode
  - not a current program acceptance target
- `.agent/architecture/decisions/`
  - locked near-term choices, open questions, and retired surfaces

The current program should not treat Java, microservices, event-driven workers,
or default multi-agent mode as near-term implementation work.

## Execution Order

The executable implementation breakdown for moving code toward the near-term
target architecture is the current execution source:

- [Implementation Roadmap](implementation-roadmap.md)
- [Implementation Phases](implementation-phases/README.md)

Use those files for target-mode implementation. They start with Phase 01 legacy
surface audit, then Phase 02 docs/spec cleanup, then Phase 03 Domain Pack
contract retirement.

## Current Status

- Phase 11A is complete; commit `24abdd9` introduced the project query runtime.
- Phase 11B is complete; commit `b160c4b` unified knowledge queries under the
  single `GeneralAgent` path.
- Phase 11C is in progress and still blocked overall. The current FastAPI
  router no longer mounts `/domain-packs`, and active Vue knowledge
  routes/pages no longer open Domain Pack entrypoints. Workspace knowledge
  prefetch/tools now use `KnowledgeQueryService`, not `AgentRuntime` or
  `_run_domain_pack_query`. The standalone `AgentRuntime` facade has been
  removed from current backend source and exports. The direct
  `MultiAgentSupervisorGraph` source has also retired from current backend.
  `DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer current core
  package public exports. `KnowledgeService.get_runtime_settings` preserves
  `domain_pack_id` without auto-loading `DomainPackLoader`. Domain Pack
  runtime services/assets, `GraphRetriever`/eval loader paths, direct
  `DomainQAGraph` source/dependencies, Docker surfaces, and `tests/compat/`
  still block closure. Domain Pack backend endpoint/API-service wrappers and
  frontend API/page files are retired from current source.
- Phase 12 is partially complete / not closed. Do not claim final full `pytest`
  or Eval baseline comparison until fresh evidence exists.

## Original Program Outline

The original program phases below are a high-level outline only. They are kept
as program context and must not override the executable implementation phases.

1. [Phase 00: Docs And Agent Workflow](phase-00-docs-and-agent-workflow.md)
2. [Phase 01: Legacy Cleanup](phase-01-legacy-cleanup.md)
3. [Phase 02: GraphRAG Project Settings](phase-02-graphrag-project-settings.md)
4. [Phase 03: Prompt Tuning And Indexing](phase-03-prompt-tuning-indexing.md)
5. [Phase 04: Query Method Router](phase-04-query-method-router.md)
6. [Phase 05: Storage Versioning](phase-05-storage-versioning.md)
7. [Phase 06: Frontend API Surface](phase-06-frontend-api-surface.md)
8. [Phase 07: Tests Eval Closure](phase-07-tests-eval-closure.md)

Additional near-term roadmap notes are in
`.agent/architecture/near-term/15-near-term-migration-roadmap.md`; they do not
replace the phase files above.

The implementation phases do not expand near-term scope into Java business
services, microservices, event-driven workers, or default multi-agent mode.

## Acceptance Rule

Each phase must define:

- Goal
- Scope
- Files to change
- Files not to change
- Acceptance gates
- Verification commands
- Evidence to return

## Superseded Material

The previous knowledge-product program is archived under:

- `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/`
