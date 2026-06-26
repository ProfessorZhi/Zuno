# Eval Graph Index Persistence Plan

This audit explains why the current multihop real runtime eval still reports
`graph_index_missing = true` for persisted graph runtime reuse.

## Short Answer

The current missing persisted graph state is caused by an execution-path split:

1. real runtime multihop eval builds a temporary local graph retriever from
   corpus rows
2. that retriever is injected through runtime registry
3. the runtime registry is cleared after each eval run
4. the separate benchmark ingestion script for persisted eval knowledge is still
   `not_implemented`

So the current eval path proves local rebuilt graph capability, but it does not
yet prove durable persisted graph indexing for eval knowledge IDs.

## Required Questions

### 1. Why is `persisted eval runtime graph_index_missing = true`?

Because current smoke checks persisted runtime availability via
`runtime_registry`, and the multihop real runtime runner clears that local
registration after each run.

Also, there is no active benchmark-eval ingestion flow that writes eval corpus
documents into the normal persisted knowledge pipeline and then leaves them in a
reusable graph-indexed state.

### 2. Does corpus ingest trigger entity extraction?

Not in the current benchmark-eval ingestion path.

Evidence:

- `tools/evals/zuno/multihop_eval/ingestion/ingest_to_knowledge.py` still
  returns `status = not_implemented`
- current multihop real runtime runner instead calls:
  - `build_chunks_from_corpus(...)`
  - `_build_local_graph_retriever(chunks)`

That local rebuilt path does perform extraction in memory, but not through the
persisted ingestion script.

### 3. Is relation extraction persisted?

Not through the current benchmark-eval ingestion path.

The normal product pipeline can persist graph data when the pipeline manager
runs graph extraction with Neo4j enabled:

- `src/backend/zuno/services/pipeline/manager.py`
- uses `CachedGraphExtractor`
- then `GraphWriter`
- then `Neo4jClient.upsert_entity(...)`
- then `Neo4jClient.upsert_relation(...)`

But the current eval workflow is not executing that persisted pipeline path for
the benchmark corpus.

### 4. Is chunk backlink persisted?

The normal runtime graph writer supports it.

Evidence:

- `Neo4jClient.upsert_relation(...)` writes `r.chunk_id`
- `Neo4jClient.fetch_relation_edges(...)` returns `chunk_ids`
- `Neo4jClient.count_knowledge_graph(...)` now counts persisted backlinks

But again, the current benchmark eval path does not route through this persisted
writer, so persisted backlink availability for eval knowledge remains unproven.

### 5. Which graph store does real runtime GraphRetriever query?

Current production/default `GraphRetriever` uses `Neo4jClient.query_neighbors`.

But during multihop real runtime eval, the runner registers a local graph
retriever built from the eval corpus. So the active query target becomes:

- local rebuilt in-memory graph client during eval runtime

not:

- persisted Neo4j graph for the eval knowledge

### 6. What is the difference between local rebuilt graph and persisted graph?

Local rebuilt graph:

- built from corpus rows at eval time
- extracted in memory from chunks
- registered temporarily in runtime registry
- deleted from runtime registry after run

Persisted graph:

- should be created by the normal ingestion / pipeline manager path
- written to Neo4j with entities, relations, and chunk backlinks
- queryable by knowledge ID after the eval run ends

This is the current architectural gap.

### 7. What is the smallest fix?

The smallest aligned fix is not to rewrite GraphRAG retrieval first.

It is to add a real benchmark ingestion path that:

1. creates eval knowledge through the normal ingestion/pipeline path
2. waits for graph extraction and graph indexing completion
3. records the persisted knowledge ID
4. reuses that knowledge ID in real runtime eval and smoke scripts

Before that exists, the correct truth is:

- local rebuilt graph: available
- persisted eval graph: not yet proven

## Smoke Output Improvement

`check_graph_index_smoke.py` now distinguishes:

- `persisted_entity_count`
- `persisted_relation_count`
- `persisted_backlink_count`
- `local_rebuilt_entity_count`
- `local_rebuilt_relation_count`
- `mismatch_reason`

This makes the smoke useful even when Neo4j is disabled or the eval knowledge
was never persisted.
