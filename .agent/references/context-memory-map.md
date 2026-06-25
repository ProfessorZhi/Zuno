# Context Memory Map

## Purpose

Orient Context/Memory design and implementation work without copying detailed
target architecture into a reference file.

## Current

Context Orchestrator and new Memory layering are Target, not Current. The
current runtime still uses existing Agent and memory surfaces under
`src/backend/zuno/`.

## Target References

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/18-context-memory-ideal-architecture.md`
- `.agent/programs/context-memory-agent-runtime-v1/`

## Rule

Do not implement a second `GraphRAGProjectSnapshot` or `GraphRAGQueryService`.
Future Context/Memory work must reuse the Phase 11A/11B query runtime results
unless fresh verification proves a different dependency boundary.
