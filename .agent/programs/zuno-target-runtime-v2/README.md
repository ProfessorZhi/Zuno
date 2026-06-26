# Zuno Target Runtime V2

## Status

Active executable Agent program.

## Purpose

Continue from the closed Zuno Target Architecture Migration V1 baseline into a
controlled first implementation slice of the target runtime architecture.

This program keeps the current Single `GeneralAgent`, GraphRAG Project
mainline, `KnowledgeQueryService`, and `GraphRAGQueryService` intact while
moving low-risk backend ownership toward the target module boundaries and
introducing a minimal callable Context Orchestrator.

## Scope

In scope:

- Phase 00 current state gate.
- Phase 01 program setup.
- Phase 02 module boundary audit and verifier.
- Phase 03 first low-risk backend boundary move.
- Phase 04 minimal Context Orchestrator runtime.

Out of scope for this first slice:

- mature Memory Engine implementation.
- mature Dynamic Capability Selector implementation.
- full `GeneralAgent` LangGraph runtime rewrite.
- frontend feature-boundary migration.
- database schema changes.
- dependency upgrades.
- Java services, microservices, event workers, and default multi-agent mode.

## Source References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/18-context-memory-ideal-architecture.md`
- `.agent/architecture/near-term/19-repository-layout-and-module-boundaries.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`

## Verification Rule

Each phase must run the smallest meaningful verification set and record the
result under `evidence/` or the phase document. Do not use this program to
promote Target behavior to Current unless current code and tests prove it.
