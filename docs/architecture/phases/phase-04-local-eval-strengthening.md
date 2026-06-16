# Phase 4: Knowledge Config V2 + Local Eval Strengthening

## Goal

Make Knowledge Config V2 and local evaluation the stable proof surface for runtime and retrieval quality.

## Focus

- knowledge config can express:
  - standard index
  - graph index
  - default query mode
  - Local GraphRAG settings
  - Domain Pack binding
  - eval profile
- stackless compare matrix
- stable local evaluation profiles
- retrieval and citation metrics
- GraphRAG-vs-RAG proof surfaces

## Closure Gate

- knowledge config contract is aligned across UI, API, and runtime normalization
- runtime-facing retrieval knobs only expose fields with real consumers
- domain pack binding and eval profile are visible in the knowledge config surface
- local compare runs are reproducible
- key metrics are understandable and stable
- GraphRAG gains can be explained with evidence, not only intuition
- focused eval checks pass
