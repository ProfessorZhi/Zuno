# Real Runtime Multihop Eval Results

This audit records the current retrieval-only real runtime evidence for
HotpotQA multihop evaluation after GraphRAG retrieval quality optimization.

## Current Status

Current verified quality-optimization rerun set was executed on June 20, 2026
with:

- dataset: `hotpotqa`
- limit: `5`
- top_k: `10`
- route policy: `auto`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

Quality optimization outcome:

1. `baseline_rag` still runs cleanly on real runtime.
2. `local_graphrag` now matches `baseline_rag` on:
   - `Recall@2`
   - `Recall@5`
   - `Recall@10`
   - `MRR@10`
   - `ChainRecall@5`
   - `FullChainHit@5`
3. `local_graphrag` still keeps `fallback_count = 1`, but no longer underperforms baseline on the sampled metrics.
4. `deep_graphrag` also matches baseline on the same sampled metrics while still activating local graph routing on `4/5` questions.
5. Graph retrieval quality is now baseline-preserving on this sample, with only residual noisy promotions in some top5/top10 positions.

## Auto Route Results

### baseline_rag

- execution mode: `real_runtime`
- requested runtime mode: `rag`
- route policy: `auto`
- `Recall@2 = 0.90`
- `Recall@5 = 1.00`
- `Recall@10 = 1.00`
- `Precision@5 = 0.40`
- `Precision@10 = 0.20`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 1.00`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 1.00`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 16064.76 / 15440.79 / 19005.90 ms`
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
- `Recall@2 = 0.90`
- `Recall@5 = 1.00`
- `Recall@10 = 1.00`
- `Precision@5 = 0.40`
- `Precision@10 = 0.20`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 1.00`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 1.00`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 18503.86 / 15174.18 / 26616.99 ms`
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
  `graph_result_count = 8`, `graph_path_count = 14`, both gold docs remain in top5
- `5a8c7595554299585d9e36b6`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 9`, `graph_path_count = 17`, both gold docs remain in top5
- `5a85ea095542994775f606a8`: fallback to `standard_rag`,
  `graph_worthy = false`, `graph_result_empty`
- `5adbf0a255429947ff17385a`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 9`, `graph_path_count = 24`, both gold docs remain in top5
- `5a8e3ea95542995a26add48d`: `local_graphrag`, `graph_worthy = true`,
  `graph_result_count = 13`, `graph_path_count = 18`, both gold docs remain in top5

Verdict:

- local GraphRAG is now both genuinely activated and baseline-preserving on this
  sample
- this is the first current proof that graph retrieval quality no longer breaks
  the already-strong baseline top5 on the measured sample
- the remaining miss is still one descriptive bridge question that falls back
  to standard retrieval

### deep_graphrag

- execution mode: `real_runtime`
- requested runtime mode: `rag_graph_deep`
- route policy: `auto`
- `Recall@2 = 0.90`
- `Recall@5 = 1.00`
- `Recall@10 = 1.00`
- `Precision@5 = 0.40`
- `Precision@10 = 0.20`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 1.00`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 1.00`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 14576.69 / 14141.65 / 18072.44 ms`
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
- baseline-preserving fusion plus seed/alias/path improvements can recover the
  lost `Recall@5` and `MRR@10` on this sample

Current evidence does not yet prove:

- community-global retrieval quality
- drift-like retrieval quality
- stable improvement over baseline on broader multihop samples
- cross-dataset behavior for 2Wiki or MuSiQue

## Remaining Blocker

One question still fails as a graph route:

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

Current success conditions for this phase:

- `local_graphrag fallback_count <= 1`: passed
- `local_graphrag Recall@5 >= baseline Recall@5`: passed
- `local_graphrag MRR@10 >= baseline MRR@10` or `Recall@2 > baseline`: passed
- `graph_result_count > 0` on at least 4 questions: passed
- `p95 latency <= 2x baseline`: passed

Decision:

- yes, the next allowed step is HotpotQA `limit=10`
- still do not expand to `2Wiki` or `MuSiQue` yet

## Residual Graph-hurts Cases

Current sampled metrics no longer show recall or MRR harm versus baseline.

Residual quality risks still visible in ranking:

- `5a8b57f25542995d1e6f1371`
  - graph promotes `Sinister (film)` into local top5
  - but it no longer pushes out gold support
- `5a8e3ea95542995a26add48d`
  - graph promotes `Great Eastern Conventions` into local top5
  - but both gold docs remain in place

These are now noisy promotions, not metric-breaking failures.

## Required Reading

The scoring contract is defined in:

- [Real Runtime Multihop Eval Standards](./real-runtime-multihop-eval-standards.md)
