# Implementation Phase Map

## Purpose

Tell future Codex runs how to execute the near-term target architecture
migration program without drifting into future architecture.

## Formal Program

Use:

- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md`
- `docs/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/history/programs/official-graphrag-cleanup-v1/implementation-phases/README.md`
  as archived dependency history; final tests/eval/trace closure now belongs
  to target migration Phase 09

## Required Reading For Every Implementation Round

1. `AGENTS.md`
2. `docs/architecture/README.md`
3. `docs/architecture/current-architecture.md`
4. `docs/architecture/target-architecture.md`
5. `docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
6. the exact target migration phase file under `implementation-phases/`
7. `.agent/architecture/near-term/README.md`
8. `.agent/architecture/near-term/16-near-term-acceptance-gates.md`
9. `.agent/architecture/decisions/01-locked-near-term-decisions.md`
10. `.agent/architecture/decisions/03-retired-surfaces.md`

## Phase To Surface Map

```text
Phase 00 -> current-state and dependency gate
Phase 01 -> official cleanup 11C active dependency removal
Phase 02 -> Contract Review asset migration
Phase 03 -> GraphRAG Project mainline hardening
Phase 04 -> repository layout cleanup
Phase 05 -> context contract foundation
Phase 06 -> memory layer foundation
Phase 07 -> capability system
Phase 08 -> GeneralAgent runtime integration
Phase 09 -> final tests, evals, trace, docs, grep closure
```

## Scope Boundary

Near-term implementation may modify Python FastAPI, LangGraph, RAG/GraphRAG,
persistence, frontend API contracts, tests, tools, docs, and Agent references
only when the active phase authorizes those paths.

Near-term implementation must not make Java services, microservices,
event-driven workers, or default multi-agent mode acceptance requirements.

## Verification Pattern

Every modification phase must:

1. show initial branch, status, and last commit
2. run the phase-specific tests
3. run `git diff --check`
4. stage only phase-relevant files
5. commit with the phase-specific message
6. push
7. return the evidence package named by the phase

If validation fails, do not push.
