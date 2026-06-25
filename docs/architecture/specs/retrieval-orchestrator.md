# Retrieval Orchestrator

## Goal

Make retrieval run through one clean control plane instead of letting `rag`, `hybrid`, and `graphrag` branch implicitly inside multiple runtime layers.

## Phase 2 Position

This document only defines the current mainline:

- `RetrievalPlanner` explicitly decides `rag / hybrid / graphrag`
- `RetrievalOrchestrator` is the unified retrieval entry
- `Local GraphRAG` is the current graph mainline
- `Community GraphRAG` and `DRIFT-like` search remain later layers

## Runtime Shape

```text
Query
  -> QueryProcessor
  -> RetrievalPlanner
  -> Retriever Adapters
  -> RetrievalFusion
  -> Final Context + Trace
```

## Responsibilities

### `RetrievalPlanner`

Planner owns retrieval mode resolution.

It takes:

- requested mode
- query features
- knowledge capability
- scope and index health
- GraphRAG Project `query_policy` and retrieval policy inputs

It outputs:

- resolved mode
- enabled retrievers
- fallback policy
- trace policy
- budget policy

### `RetrievalOrchestrator`

Orchestrator is the only retrieval entry.

It:

- runs query processing
- calls planner
- dispatches vector / keyword / graph retrievers
- fuses evidence
- records `retriever_runs`, `rounds`, and final retrieval trace

It must not bypass planner with extra mode hardcoding.

### `GraphRetriever`

Graph retriever is a graph evidence backend, not a business scenario plugin.

It is responsible for:

- entity seed extraction
- graph neighbor and path lookup
- chunk hydration
- graph evidence formatting

It must not hardcode contract-review-only rules.
Domain-specific graph cues belong in GraphRAG Project `query_policy` /
`retrieval_policy.yaml`, not in a restored Domain Pack runtime.

## Mode Semantics

External compatibility may still accept legacy aliases such as `rag_graph` and `auto`.
Internal runtime must resolve to exactly three modes:

- `rag`
- `hybrid`
- `graphrag`

## GraphRAG Layering

Current mainline:

```text
Local GraphRAG
  -> entity seeds
  -> graph path retrieval
  -> chunk hydration
  -> evidence fusion
  -> citation-checked answer
```

Later layers:

- `Community GraphRAG`
- `DRIFT-like hybrid graph search`

That later hybrid direction is still:

```text
global overview + local deep dive
```

Those later layers do not redefine the current default retrieval mainline.
