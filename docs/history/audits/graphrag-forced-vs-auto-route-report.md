# GraphRAG Forced Vs Auto Route Report

This audit compares `route_policy = auto` and `route_policy = force_graph` for
HotpotQA `limit=5` on `local_graphrag`.

Important boundary:

- `force_graph` is eval-only
- it is not a product route
- it must not be reported as product automatic routing quality

## Compared Runs

Shared settings:

- dataset: `hotpotqa`
- limit: `5`
- mode: `local_graphrag`
- top_k: `10`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

Compared route policies:

1. `auto`
2. `force_graph`

## Direct Comparison

### auto

- `Recall@2 = 0.60`
- `Recall@5 = 0.80`
- `Recall@10 = 1.00`
- `MRR@10 = 0.80`
- `avg/p50/p95 latency = 15806.78 / 13326.67 / 23182.03 ms`
- `fallback_count = 1`
- `internal_route distribution = {local_graphrag: 4, standard_rag: 1}`
- `graph_result_count > 0 = 4`
- `graph_path_count > 0 = 4`

### force_graph

- `Recall@2 = 0.60`
- `Recall@5 = 0.80`
- `Recall@10 = 1.00`
- `MRR@10 = 0.90`
- `avg/p50/p95 latency = 15196.90 / 11664.02 / 23333.78 ms`
- `fallback_count = 1`
- `internal_route distribution = {local_graphrag: 4, standard_rag: 1}`
- `graph_result_count > 0 = 4`
- `graph_path_count > 0 = 4`

## Required Questions

### 1. Did `force_graph` produce entity/path output?

Yes, but only on the same 4 questions already activated by `auto`.

Evidence:

- `graph_result_count > 0 = 4`
- `graph_path_count > 0 = 4`

### 2. Did `force_graph` improve `Recall@2` or `MRR`?

- `Recall@2`: no change, still `0.60`
- `MRR@10`: small improvement from `0.80` to `0.90`

Interpretation:

- forcing the planner is not unlocking a new large retrieval surface
- it only changes ranking behavior slightly on the already activated subset

### 3. Did `force_graph` significantly increase latency?

No meaningful increase.

- auto `avg_latency_ms = 15806.78`
- force `avg_latency_ms = 15196.90`

The p95 values are in the same range, so there is no evidence of a major forced
route latency penalty at this sample size.

### 4. Can `auto` already activate graph routing?

Yes.

Evidence:

- `internal_route = local_graphrag` on 4 of 5 sampled questions
- `retriever_used` includes `graph` on those 4 questions
- non-empty graph documents and graph paths are present on those 4 questions

### 5. If `force_graph` helps but `auto` does not, what next?

That condition is no longer the main issue.

`auto` already activates graph routing for the graph-worthy subset.

### 6. If `force_graph` also does not help, what next?

That is the remaining issue for the fifth question.

The unresolved blocker is now:

- descriptive bridge question recognition
- graph-worthiness / seed quality for
  `The Hork-Bajir Chronicles -> Animorphs` style parent-series linkage

So the next tuning target is not planner-level route activation anymore. It is
graph seed and graph-worthiness quality for descriptive bridge questions.

## Bottom Line

`force_graph` is available and correctly labeled as eval-only, but it does not
materially outperform `auto` on the current sample.

That means:

- planner gating is mostly fixed for this smoke set
- the remaining miss has moved deeper into graph-worthiness and graph-retrieval
  quality for one specific question shape
