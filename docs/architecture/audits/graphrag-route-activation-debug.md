# GraphRAG Route Activation Debug

This audit explains why the current real runtime multihop runs do not yet prove
GraphRAG effectiveness.

## Scope

Investigated files:

- `tools/evals/zuno/multihop_eval/run_real_runtime_eval.py`
- `tools/evals/zuno/multihop_eval/ingestion/ingest_to_knowledge.py`
- `tools/evals/zuno/multihop_eval/ingestion/build_corpus.py`
- `src/backend/zuno/services/retrieval/planner.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/graphrag/retriever.py`
- `src/backend/zuno/services/rag/handler.py`
- `tests/test_phase3_community_graphrag_v1.py`
- `tests/test_phase4_global_drift_v1.py`
- `tests/test_phase5_deep_graphrag_eval_surface.py`

Current runtime evidence source:

- gitignored real runtime reports under `reports/evals/multihop/real_runtime/`
- direct inspection of the first 5 HotpotQA question features and graph seed
  analysis

## Short Answer

1. `local_graphrag` **does call** the graph route on round 1.
2. The current `graph_result_empty` is primarily caused by the local
   `GraphRetriever` deciding these HotpotQA questions are **not graph-worthy**,
   so it returns empty entities, empty paths, and no graph documents.
3. `deep_graphrag` stays on `standard_rag` because the current `QueryProcessor`
   marks these 5 HotpotQA questions as neither relation, nor global, nor
   evidence-required queries.
4. The real runtime runner already captures enough metadata to prove those two
   facts, but not enough to expose seed entities, graph result counts, or
   community counts directly per question.
5. The current real runtime runner does **not** build a persisted eval graph
   index. It builds an in-memory local graph retriever from corpus chunks and
   registers it in the runtime registry.

## Root Cause: local_graphrag `graph_result_empty`

### Was the graph retriever really called?

Yes.

Evidence from current local-graphrag report:

- round 1 metadata shows:
  - `mode = local_graphrag`
  - `internal_route = local_graphrag`
  - `quality_reason = graph_result_empty`
- round 2 then switches to:
  - `mode = hybrid_rag`
  - `internal_route = standard_rag`
  - `trigger = query_rewrite_retry`

That means the runtime did attempt a graph-first pass before degrading.

### Why did round 1 return empty graph evidence?

Primary root cause:

- `src/backend/zuno/services/graphrag/retriever.py`
- `GraphRetriever.retrieve()` immediately returns empty graph output when
  `_is_graph_worthy_query(query, seed_entities, query_policy)` is false.

Current HotpotQA first-5 evidence:

- all 5 questions produce `graph_worthy = false`
- all 5 questions produce:
  - `relation_question = false`
  - `global_question = false`
  - `evidence_required = false`

So the current runtime behavior is:

1. planner allows a local graph round because requested mode is
   `local_graphrag`
2. graph retriever receives the query
3. graph retriever rejects the query as not graph-worthy
4. graph result has:
   - `entities = []`
   - `paths = []`
   - `documents = []`
5. orchestrator marks first-pass quality as `graph_result_empty`
6. fallback policy retries with `hybrid_rag`

### What this is **not**

Current evidence does **not** prove that the first blocker is:

- missing graph index in Neo4j
- missing entity extraction pipeline writeback
- wrong `graph_hop_limit`
- wrong `doc_id` / `chunk_id` backlink
- runtime registry failure to register graph retriever

Why not:

- the current eval runner does not depend on persisted Neo4j graph artifacts
  first
- it injects an in-memory `graph_retriever` through runtime registry
- the degradation happens before any meaningful graph evidence is returned
- metadata already shows `entity_count = 0` and `path_count = 0` on round 1

So the first actionable root cause is **query gating**, not storage wiring.

## Root Cause: deep_graphrag stayed on `standard_rag`

Primary root cause:

- `src/backend/zuno/services/retrieval/planner.py`

For `rag_graph_deep`, planner only selects:

- `local_graphrag` when `relation_question = true`
- `community_global` when `global_question = true`
- `drift_like` when both `global_question = true` and
  `evidence_required = true`
- otherwise it stays on `standard_rag`

Current HotpotQA first-5 evidence:

- `relation_question = false`
- `global_question = false`
- `evidence_required = false`

Therefore:

- `requested_mode = rag_graph_deep`
- `resolved_mode = rag_graph_deep`
- but `internal_route = standard_rag`
- and route trace reports:
  - `graph_required = false`
  - `community_required = false`
  - `local_graph_required = false`

This is not a runtime failure.
It is the current planner policy doing exactly what it was coded to do.

## Eval Runner And Corpus Reality

### Does the runner build a real persisted graph index?

No.

Current real runtime runner:

- builds text chunks from benchmark corpus rows
- indexes vectors into the temporary eval knowledge
- builds a local in-memory graph retriever from those chunks
- registers that retriever in `runtime_registry`

It does **not** currently:

- call `ingest_to_knowledge.py`
- write a persistent eval graph index to Neo4j as a required step
- build community reports for the eval knowledge

### Is `ingest_to_knowledge.py` part of the active path?

No.

Current file status:

- `tools/evals/zuno/multihop_eval/ingestion/ingest_to_knowledge.py`
- still returns `status = not_implemented`

So the active real runtime path is:

- corpus rows
- local temporary knowledge
- vector index
- injected local graph retriever

not:

- benchmark corpus -> persisted eval knowledge -> persisted graph index

## Route Metadata Sufficiency

Current runner metadata is already strong enough to prove:

- requested mode
- resolved mode
- internal route
- fallback triggered or not
- fallback reason
- round-by-round mode transitions
- path count and entity count per round

Current metadata is still missing convenient top-level per-question fields for:

- graph result count
- seed entities
- seed entity count
- community report count
- drift follow-up count
- explicit retriever-used summary

That is why a dedicated diagnostics expansion is still justified.

## Minimal Next Step

The smallest aligned next step is:

1. expand real runtime runner diagnostics
2. expose seed entities and graph result counts directly
3. add a graph index smoke script for the eval corpus path
4. only then rerun HotpotQA limit 5

This keeps the current GraphRAG runtime stable while making the blocker visible
enough to debug.

## Bottom Line

Current blocker summary:

- `local_graphrag`: graph route is attempted, but query gating in
  `GraphRetriever` rejects these questions as not graph-worthy, producing
  `graph_result_empty`
- `deep_graphrag`: planner never routes these questions into local graph or
  community flow because the current query features classify them as plain
  factual queries

So the immediate problem is **route activation policy visibility**, not yet
proof of a broken storage layer.
