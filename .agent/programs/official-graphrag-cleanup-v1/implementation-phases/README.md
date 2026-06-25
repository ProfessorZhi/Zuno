# Implementation Phases

These phases split Official GraphRAG Cleanup V1 into execution units that can
be handed to Codex one at a time.

Read first:

1. `../implementation-roadmap.md`
2. `../../../current-architecture.md`
3. `../../../target-architecture.md`
4. `../../../../.agent/architecture/near-term/README.md`
5. `../../../../.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
6. `../../../../.agent/architecture/near-term/17-implementation-phase-map.md`

## Phase List

1. [Phase 01: Legacy Surface Audit](phase-01-legacy-surface-audit.md)
2. [Phase 02: Docs / Spec / Current Truth Cleanup](phase-02-docs-spec-current-truth-cleanup.md)
3. [Phase 03: Domain Pack Contract Retirement](phase-03-domain-pack-contract-retirement.md)
4. [Phase 04: GraphRAG Project Contracts](phase-04-graphrag-project-contracts.md)
5. [Phase 05: GraphRAG Project Loader / Settings](phase-05-graphrag-project-loader-settings.md)
6. [Phase 06: Prompt Registry And Tuning Boundary](phase-06-prompt-registry-and-tuning-boundary.md)
7. [Phase 07: Index / Update / Versioning](phase-07-index-update-versioning.md)
8. [Phase 08: Query Method Router](phase-08-query-method-router.md)
9. [Phase 09: Enhanced Mode Pipeline](phase-09-enhanced-mode-pipeline.md)
10. [Phase 10: Frontend API Contract Migration](phase-10-frontend-api-contract-migration.md)
11. [Phase 11A: GraphRAG Project Runtime Replacement](phase-11a-graphrag-project-runtime-replacement.md)
12. [Phase 11B: Single GeneralAgent Cutover](phase-11b-single-generalagent-cutover.md)
13. [Phase 11C: Runtime Legacy Deletion](phase-11c-runtime-legacy-deletion.md)
14. [Phase 12: Tests / Eval / Trace Closure](phase-12-tests-eval-trace-closure.md)

## Current Status

- Phase 01 is complete as read-only evidence.
- Phase 02 is the docs/spec/current-truth cleanup step that removes misleading
  Domain Pack-era target language from current entrypoints.
- Phase 03 introduces `graphrag_project_id` at the public contract edge and
  keeps `domain_pack_id` as bounded compatibility input for the existing
  runtime.
- Phase 04 adds first-class GraphRAG Project contract fields without claiming a
  loader.
- Phase 05 adds project settings loading, prompt discovery, and readiness
  metadata without changing retrieval behavior.
- Phase 06 adds Prompt Registry categories and prompt-version impact rules
  without implementing automatic tuning.
- Phase 07 adds index version, hash flow, full rebuild boundary, and stale-index
  trace detection without database migration.
- Phase 08 adds the public backend Query Method Router for
  `auto/basic/local/global/drift`, with compatibility mapping to current
  internal runtime routes and explicit fallback trace.
- Phase 09 hardens Enhanced Mode pipeline trace for query method routing,
  multi-retriever recall, fusion/rerank, evidence, requery, citation coverage,
  and standard-floor preservation.
- Phase 10 migrates frontend API/types/config utilities to GraphRAG Project and
  public query-method trace fields, and removes old runtime route names from
  `apps/web`.
- Phase 11A is complete; commit `24abdd9` introduced the project query runtime.
- Phase 11B is complete; commit `b160c4b` unified knowledge queries under the
  single `GeneralAgent` path.
- Phase 11C is blocked by active Domain Pack, `DomainQAGraph`,
  `MultiAgentSupervisorGraph`, Docker/eval/frontend/API, and `tests/compat/`
  dependencies.
- Phase 12 is partially complete / not closed.

## Rule

Do not skip phase evidence. If a later phase seems easier, first prove the
dependency phase is complete from the current worktree.
