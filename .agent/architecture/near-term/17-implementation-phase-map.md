# Implementation Phase Map

## Purpose

Tell future Codex runs how to execute the near-term GraphRAG implementation
program without drifting into future architecture.

## Formal Program

Use:

- `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-phases/README.md`

## Required Reading For Every Implementation Round

1. `AGENTS.md`
2. `docs/architecture/README.md`
3. `docs/architecture/current-architecture.md`
4. `docs/architecture/target-architecture.md`
5. `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
6. the exact phase file under `implementation-phases/`
7. `.agent/architecture/near-term/README.md`
8. `.agent/architecture/near-term/16-near-term-acceptance-gates.md`
9. `.agent/architecture/decisions/01-locked-near-term-decisions.md`
10. `.agent/architecture/decisions/03-retired-surfaces.md`

## Phase To Surface Map

```text
Phase 01 -> read-only inventory across runtime, frontend, tests, docs, tools
Phase 02 -> docs, specs, Agent references
Phase 03 -> API contracts, DTOs, frontend API payloads
Phase 04 -> GraphRAG Project types and contract tests
Phase 05 -> project loader, settings validation, prompts discovery
Phase 06 -> prompt registry and prompt tuning boundary
Phase 07 -> index/update/full rebuild versioning
Phase 08 -> query method router and trace contract
Phase 09 -> Enhanced Mode pipeline and evidence trace
Phase 10 -> frontend API and UI contract migration
Phase 11 -> old runtime surface deletion after dependency proof
Phase 12 -> final tests, evals, trace, docs, grep closure
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
