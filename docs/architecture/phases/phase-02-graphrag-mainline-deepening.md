# Phase 2: GraphRAG Mainline Deepening

## Goal

Make GraphRAG a clean mainline capability instead of a partially hardcoded enhancement path.

## Focus

- `RetrievalOrchestrator` as the unified retrieval entry
- explicit retrieval planning
- clear retriever mode decisions
- reduced business hardcoding inside GraphRAG internals

## Closure Gate

- retrieval orchestration is unified
- graph-specific behavior is explicit rather than accidental
- runtime and retrieval docs describe the same GraphRAG model
- focused GraphRAG runtime checks pass
