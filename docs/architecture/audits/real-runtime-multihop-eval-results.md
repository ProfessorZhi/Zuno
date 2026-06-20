# Real Runtime Multihop Eval Results

This audit records the current retrieval-only real runtime evidence for
HotpotQA multihop evaluation after GraphRAG route activation calibration.

## Current Status

Current verified run set was executed on June 20, 2026 with:

- dataset: `hotpotqa`
- limit: `5`
- top_k: `10`
- route policy: `auto`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

Calibration outcome:

1. `baseline_rag` still runs cleanly on real runtime.
2. `local_graphrag` no longer falls back `5/5`.
3. `deep_graphrag` no longer stays `5/5` on `standard_rag`.
4. The current HotpotQA smoke sample now activates graph routing on `4/5`
   questions.
5. The remaining miss is no longer "planner never tries graph". It is one
   specific question that still fails graph-worthiness / graph-result
   production.

## Auto Route Results

### baseline_rag

- execution mode: `real_runtime`
- requested runtime mode: `rag`
- route policy: `auto`
- `Recall@2 = 0.70`
- `Recall@5 = 1.00`
- `Recall@10 = 1.00`
- `Precision@5 = 0.40`
- `Precision@10 = 0.20`
- `MRR@10 = 0.90`
- `ChainRecall@5 = 1.00`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 1.00`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 12148.21 / 11776.82 / 13803.59 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `graph_worthy_count = 4`
  - `graph_result_count > 0 = 0`
  - `graph_path_count > 0 = 0`
  - `internal_route distribution = {standard_rag: 5}`
  - `retriever_used distribution = {vector: 5}`

Verdict:

- baseline remains the clean control run
- graph-worthiness can now be diagnosed even when the mode is standard RAG
- baseline does not use graph retrieval, as expected

### local_graphrag

- execution mode: `real_runtime`
- requested runtime mode: `local_graphrag`
- route policy: `auto`
- `Recall@2 = 0.60`
- `Recall@5 = 0.80`
- `Recall@10 = 1.00`
- `Precision@5 = 0.32`
- `Precision@10 = 0.20`
- `MRR@10 = 0.80`
- `ChainRecall@5 = 0.80`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 0.60`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 15806.78 / 13326.67 / 23182.03 ms`
- `fallback_count = 1`
- `failure_count = 0`
- route diagnostics:
  - `graph_worthy_count = 4`
  - `graph_result_count > 0 = 4`
  - `graph_path_count > 0 = 4`
  - `internal_route distribution = {local_graphrag: 4, standard_rag: 1}`
  - `fallback_reason distribution = {graph_result_empty: 1}`
  - `retriever_used distribution = {vector: 5, graph: 4}`

Per-question route summary:

- `5a8b57f25542995d1e6f1371`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 8`, `graph_path_count = 14`
- `5a8c7595554299585d9e36b6`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 7`, `graph_path_count = 10`
- `5a85ea095542994775f606a8`: fallback to `standard_rag`,
  `graph_worthy = false`, `graph_result_empty`
- `5adbf0a255429947ff17385a`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 9`, `graph_path_count = 24`
- `5a8e3ea95542995a26add48d`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 8`, `graph_path_count = 15`

Verdict:

- local GraphRAG is now genuinely activated on most of the sample
- this is the first current proof that route calibration changed runtime
  behavior instead of only adding diagnostics
- there is still one remaining miss, so this is not yet a full clean sweep

### deep_graphrag

- execution mode: `real_runtime`
- requested runtime mode: `rag_graph_deep`
- route policy: `auto`
- `Recall@2 = 0.60`
- `Recall@5 = 0.80`
- `Recall@10 = 1.00`
- `Precision@5 = 0.32`
- `Precision@10 = 0.20`
- `MRR@10 = 0.90`
- `ChainRecall@5 = 0.80`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 0.60`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 13595.57 / 13009.20 / 16923.67 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `graph_worthy_count = 4`
  - `graph_result_count > 0 = 4`
  - `graph_path_count > 0 = 4`
  - `internal_route distribution = {local_graphrag: 4, standard_rag: 1}`
  - `fallback_reason distribution = {none: 5}`
  - `retriever_used distribution = {vector: 5, graph: 4}`

Verdict:

- `deep_graphrag` no longer behaves like pure standard retrieval on all 5
  samples
- on this current sample it resolves to local graph routing for the same 4
  graph-worthy questions
- this is still not proof of community or drift quality because no community
  route was activated in this smoke

## Interpretation

Current evidence now proves:

- route activation calibration worked
- real runtime graph routing is no longer blocked at planner level for most of
  the sampled HotpotQA questions
- local graph retrieval can return entities, graph documents, and graph paths on
  current eval artifacts
- `deep_graphrag` can enter graph-backed routing on the same subset of
  graph-worthy questions

Current evidence does not yet prove:

- community-global retrieval quality
- drift-like retrieval quality
- stable improvement over baseline on broader multihop samples
- cross-dataset behavior for 2Wiki or MuSiQue

## Remaining Blocker

One question still fails:

- `5a85ea095542994775f606a8`
- `What science fantasy young adult series, told in first person, has a set of companion books narrating the stories of enslaved worlds and alien species?`

Current behavior:

- `graph_worthy = false`
- `internal_route = standard_rag`
- `local_graphrag` fallback reason = `graph_result_empty`

Root-cause summary:

- this is no longer a global route-activation failure
- this is a narrower descriptive bridge-question miss
- the next tuning target is graph-worthiness / seed quality for descriptive
  parent-series questions

## Decision

Current stop condition from the earlier debug phase has been cleared.

New decision:

- allowed next step: expand to HotpotQA `limit=10`
- still hold: `2Wiki` and `MuSiQue`

Why:

- `local_graphrag` is no longer fallback `5/5`
- `deep_graphrag` is no longer `standard_rag` `5/5`
- but community and drift routes are still unproven, so broader dataset
  expansion is premature

## Required Reading

The scoring contract is defined in:

- [Real Runtime Multihop Eval Standards](./real-runtime-multihop-eval-standards.md)
