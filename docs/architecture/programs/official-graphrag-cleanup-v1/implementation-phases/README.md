# Implementation Phases

These phases split Official GraphRAG Cleanup V1 into execution units that can
be handed to Codex one at a time.

Read first:

1. `../implementation-roadmap.md`
2. `../../../current-architecture.md`
3. `../../../target-architecture.md`
4. `../../../../.agent/architecture/near-term/README.md`
5. `../../../../.agent/architecture/near-term/17-implementation-phase-map.md`

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
11. [Phase 11: Runtime Legacy Deletion](phase-11-runtime-legacy-deletion.md)
12. [Phase 12: Tests / Eval / Trace Closure](phase-12-tests-eval-trace-closure.md)

## Rule

Do not skip phase evidence. If a later phase seems easier, first prove the
dependency phase is complete from the current worktree.
