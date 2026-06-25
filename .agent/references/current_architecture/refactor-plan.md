# Refactor Plan

## Completed Baseline

Phase 0-6 closure is complete and remains completion truth.

## Active Program

The current program is `official-graphrag-cleanup-v1`.

Its executable stages are defined by:

- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-phases/README.md`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

The current implementation sequence is:

1. Legacy Surface Audit
2. Docs / Spec / Current Truth Cleanup
3. Domain Pack Contract Retirement
4. GraphRAG Project Contracts
5. GraphRAG Project Loader / Settings
6. Prompt Registry And Tuning Boundary
7. Index / Update / Versioning
8. Query Method Router
9. Enhanced Mode Pipeline
10. Frontend API Contract Migration
11. Runtime Legacy Deletion
12. Tests / Eval / Trace Closure

## Current Phase

Phase 01 legacy surface audit and Phase 02 docs/spec cleanup are complete.
Phase 03 has introduced `graphrag_project_id` at the public contract edge while
keeping `domain_pack_id` as bounded compatibility input. The next phase is
Phase 04: GraphRAG Project Contracts.
