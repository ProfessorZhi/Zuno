# Phase 2: GraphRAG Mainline Deepening

## Goal

Make GraphRAG a clean mainline capability instead of a partially hardcoded enhancement path.

## Status

Closed.

## Focus

- `RetrievalOrchestrator` as the unified retrieval entry
- `RetrievalPlanner` explicitly decides `rag / hybrid / graphrag`
- clear retriever mode decisions
- reduced business hardcoding inside GraphRAG internals
- contract-review-specific graph cues move into `Domain Pack retrieval_policy`
- 先把 Local GraphRAG 主线做扎实
- keep Community GraphRAG as a later global-summary layer, not the current default

## Closure Gate

- retrieval orchestration is unified
- graph-specific behavior is explicit rather than accidental
- Local GraphRAG is documented as the current graph mainline
- Community GraphRAG is documented as a later layer on the same graph, not a competing default
- runtime and retrieval docs describe the same GraphRAG model
- focused GraphRAG runtime checks pass
