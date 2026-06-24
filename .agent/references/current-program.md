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

It expands the target program into C4-style context/container/component/runtime
views, layered runtime boundaries, GraphRAG Project design, Enhanced Mode,
future Java business service integration, microservices readiness, multi-agent
mode, observability, migration, decisions, and open questions.

This directory is not an implementation-complete claim. Future sections must be
treated as target/proposed until runtime code and formal docs prove them.

## Current Rule

Do not rewrite completed Phase 0-6 files as incomplete.

Do not keep superseded programs in the front path. Move them under `docs/architecture/history/programs/` and link them as archived context only.
