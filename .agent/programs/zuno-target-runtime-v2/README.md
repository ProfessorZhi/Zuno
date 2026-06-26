# Zuno Target Runtime V2

## Status

Active executable Agent program.

## Purpose

Continue from the closed Zuno Target Architecture Migration V1 baseline into a
controlled first implementation slice of the target runtime architecture.

This program keeps the current Single `GeneralAgent`, GraphRAG Project
mainline, `KnowledgeQueryService`, and `GraphRAGQueryService` intact while
moving low-risk backend ownership toward the target module boundaries,
introducing Context/Memory foundations, and then implementing the target
runtime in linear phases.

## Scope

Completed foundation slice:

- Phase 00 current state gate.
- Phase 01 program setup.
- Phase 02 module boundary audit and verifier.
- Phase 03 first low-risk backend boundary move.
- Phase 04 minimal Context Orchestrator runtime.

Planned execution phases:

- Phase 05 Memory Engine.
- Phase 06 Capability / Tool Retrieval.
- Phase 07 Knowledge Retrieval / Fusion.
- Phase 08 GeneralAgent LangGraph Runtime.
- Phase 09 Product Boundary / Trace / Eval Closure.

Out of scope unless a specific phase explicitly opens it:

- database schema changes.
- dependency upgrades.
- Java services, microservices, event workers, and default multi-agent mode.

## Source References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`

## Active Files

- `README.md`
- `implementation-roadmap.md`
- `current-phase.md`
- `closure-checklist.md`

Detailed Phase 00-04 evidence and old phase files are archived under
`docs/history/programs/zuno-target-runtime-v2/`.

## Verification Rule

Each phase must run the smallest meaningful verification set and record the
current result in the active phase or closure checklist. Bulky phase evidence
belongs under `docs/history/programs/zuno-target-runtime-v2/`.
Do not use this program to promote Target behavior to Current unless current
code and tests prove it.
