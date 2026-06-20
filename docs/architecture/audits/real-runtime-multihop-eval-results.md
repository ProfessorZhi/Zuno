# Real Runtime Multihop Eval Results

This audit records the current retrieval-only real runtime evidence for
HotpotQA multihop evaluation after GraphRAG retrieval quality optimization and
the controlled `limit=10` expansion.

Naming note:

- current runner labels still use `baseline_rag`, `local_graphrag`, and
  `deep_graphrag`
- future product-facing reports should translate that comparison to
  `standard_retrieval` vs `enhanced_retrieval`
- `local_graphrag` and `deep_graphrag` should remain internal ablation labels
  unless a report is explicitly diagnostic

Runtime alignment note:

- real runtime runner now accepts `standard_retrieval` and
  `enhanced_retrieval`
- `baseline_rag` remains supported only as a deprecated historical alias

## Product Retrieval Comparison: HotpotQA Limit=10

Current verified product-mode run set was executed on June 20, 2026 with:

- dataset: `hotpotqa`
- limit: `10`
- top_k: `10`
- route policy: `auto`
- product comparison:
  - `standard_retrieval`
  - `enhanced_retrieval`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

### standard_retrieval limit=10

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
- `avg/p50/p95 latency = 12266.23 / 12299.34 / 13362.47 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `retriever_used distribution = {vector: 10}`
  - `vector_used = 10/10`
  - `bm25_available = 0/10`
  - `bm25_used = 0/10`
  - `bm25_fallback_reason = bm25_backend_unavailable`
  - `fusion_used = 10/10`
  - `rerank_used = 10/10`
  - `internal_route distribution = {standard_rag: 10}`

### enhanced_retrieval limit=10

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
- `avg/p50/p95 latency = 11328.32 / 11405.82 / 13185.05 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `standard_floor_used = 10/10`
  - `graph_route_attempted = 4/10`
  - `graph_route_used = 4/10`
  - `graph_result_count > 0 = 4`
  - `graph_path_count > 0 = 4`
  - `requery_available = 10/10`
  - `requery_used = 0/10`
  - `community_available = 0/10`
  - `community_used = 0/10`
  - `drift_available = 0/10`
  - `drift_used = 0/10`
  - `confidence_gated_fusion_used = 10/10`
  - `final_rerank_used = 10/10`
  - `route_selection_reason distribution = {relation_question: 4, standard_question: 6}`
  - `internal_route distribution = {local_graphrag: 4, standard_rag: 6}`
  - `retriever_used distribution = {vector: 10, graph: 4}`

## Per-question Delta Summary

### enhanced_helps cases

No product-level help case was observed on this `limit=10` sample.

That means enhanced retrieval did not beat standard retrieval on:

- `Recall@2`
- `Recall@5`
- `MRR@10`
- `FullChainHit@3`

### enhanced_hurts cases

No hurt case was observed.

Specifically:

- no standard top5 gold document was pushed out by enhanced retrieval
- no `MRR@10` drop was observed
- no `Recall@5` drop was observed

### enhanced_ties cases

All ten sampled questions tied exactly on the tracked retrieval metrics.

Four tied questions still activated the local graph route:

- `5a8b57f25542995d1e6f1371`
- `5a8c7595554299585d9e36b6`
- `5adbf0a255429947ff17385a`
- `5a8e3ea95542995a26add48d`

The remaining six stayed on the standard floor without metric change.

### enhanced_fallback cases

No enhanced fallback case was observed on this run:

- `fallback_count = 0`

## Product Comparison Decision

Decision rules:

1. `enhanced_retrieval Recall@5 >= standard_retrieval Recall@5`
2. `enhanced_retrieval MRR@10 >= standard_retrieval MRR@10`, or stronger early-hit gain
3. `enhanced_retrieval fallback_rate <= 30%`
4. `enhanced_retrieval failure_count = 0`
5. `enhanced_retrieval p95 latency <= standard_retrieval p95 * 2.2`
6. `enhanced_hurts cases <= 2`

Result:

1. passed
2. passed
3. passed
4. passed
5. passed
6. passed

Verdict:

- `enhanced_retrieval` is baseline-preserving on HotpotQA `limit=10`
- it is not better than `standard_retrieval` on this sample
- it is safe enough to continue to HotpotQA `limit=20`
- it is still too early to skip directly to `2Wiki` or `MuSiQue`

## Optional Ablation Status

Optional ablation smoke was not executed in this round.

Reason:

- product comparison already answered the main decision question
- no additional runtime change was needed to explain this sample

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

## HotpotQA Limit=10 Controlled Expansion

Current verified `limit=10` run set was executed on June 20, 2026 with:

- dataset: `hotpotqa`
- limit: `10`
- top_k: `10`
- route policy: `auto`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

### baseline_rag limit=10

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
- `avg/p50/p95 latency = 14672.14 / 14792.11 / 17375.52 ms`
- `fallback_count = 0`
- `failure_count = 0`
- `graph_result_count > 0 = 0`
- `graph_path_count > 0 = 0`
- `internal_route distribution = {standard_rag: 10}`
- `retriever_used distribution = {vector: 10}`

### local_graphrag limit=10

- `Recall@2 = 0.95`
- `Recall@5 = 1.00`
- `Recall@10 = 1.00`
- `Precision@5 = 0.40`
- `Precision@10 = 0.20`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 1.00`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 1.00`
- `FullChainHit@10 = 1.00`
- `avg/p50/p95 latency = 19783.35 / 21054.74 / 26643.14 ms`
- `fallback_count = 6`
- `failure_count = 0`
- `graph_result_count > 0 = 4`
- `graph_path_count > 0 = 4`
- `internal_route distribution = {local_graphrag: 4, standard_rag: 6}`
- `retriever_used distribution = {vector: 10, graph: 4}`

### deep_graphrag limit=10

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
- `avg/p50/p95 latency = 14559.42 / 14885.93 / 16528.08 ms`
- `fallback_count = 0`
- `failure_count = 0`
- `graph_result_count > 0 = 4`
- `graph_path_count > 0 = 4`
- `internal_route distribution = {local_graphrag: 4, standard_rag: 6}`
- `retriever_used distribution = {vector: 10, graph: 4}`

## Per-question Delta Summary

### graph_helps cases

Current clear metric help case versus baseline:

- `5abd94525542992ac4f382d2`
  - question: `2014 S/S is the debut album of a South Korean boy group that was formed by who?`
  - local GraphRAG improved `Recall@2` over baseline
  - but this happened on a fallback-to-standard path, not on a graph-activated path
  - treat it as a retrieval help, not a proof of graph path quality

### graph_hurts cases

No metric-breaking graph-hurt case was observed at `limit=10`.

Specifically:

- no question lost `Recall@5` versus baseline
- no question lost `MRR@10` versus baseline
- no gold support document was pushed out of local top5 relative to baseline

Residual noisy promotions still exist, but they did not break the measured
retrieval metrics in this sample.

### graph_neutral cases

Nine of the ten sampled questions were metric-neutral against baseline on the
tracked retrieval metrics.

That means:

- GraphRAG is still baseline-preserving
- but it is not yet stably outperforming baseline on this broader sample

### fallback cases

Current local GraphRAG fallback cases:

1. `5a85ea095542994775f606a8`
   - `What science fantasy young adult series, told in first person, has a set of companion books narrating the stories of enslaved worlds and alien species?`
   - fallback reason: `graph_result_empty`

2. `5abd94525542992ac4f382d2`
   - `2014 S/S is the debut album of a South Korean boy group that was formed by who?`
   - fallback reason: `graph_result_empty`

3. `5a85b2d95542997b5ce40028`
   - `Who was known by his stage name Aladin and helped organizations improve their performance as a consultant?`
   - fallback reason: `graph_result_empty`

4. `5a87ab905542996e4f3088c1`
   - `The arena where the Lewiston Maineiacs played their home games can seat how many people?`
   - fallback reason: `graph_result_empty`

5. `5a7bbb64554299042af8f7cc`
   - `Who is older, Annie Morton or Terry Richardson?`
   - fallback reason: `graph_result_empty`

6. `5a8db19d5542994ba4e3dd00`
   - `Are Local H and For Against both from the United States?`
   - fallback reason: `graph_result_empty`

### standard_rag fallback but still correct cases

All six fallback cases still returned correct top5 gold support under the
current retrieval metrics.

This is good for robustness, but it also proves that graph coverage on the
expanded sample is still too narrow.

## H3 Decision Check

Required rules:

1. `local_graphrag Recall@5 >= baseline Recall@5`
2. `local_graphrag MRR@10 >= baseline MRR@10`, or `Recall@2 > baseline`
3. `local_graphrag fallback_rate <= 30%`
4. `graph_result_count > 0` question ratio `>= 60%`
5. `p95 latency <= baseline p95 * 2`
6. `graph_hurts cases <= 2`

Result:

1. passed
2. passed
3. failed
4. failed
5. passed
6. passed

Why it fails overall:

- fallback rate is `6/10 = 60%`
- graph-active coverage is `4/10 = 40%`

So the current `limit=10` expansion does **not** pass the controlled expansion
gate, even though the top-line retrieval metrics are strong.

## Decision

Do **not** expand to:

- HotpotQA `limit=20`
- `2Wiki` small smoke

Reason:

- GraphRAG is baseline-preserving
- GraphRAG does not underperform baseline on current `limit=10`
- but graph coverage and fallback rate still fail the explicit expansion rules

The next loop should return to:

- seed quality
- alias quality
- path ranking
- graph-worthiness for the six fallback question shapes

## Next-Round Eval Contract

The next HotpotQA `limit=10` comparison should prioritize product semantics:

1. `standard_retrieval`
2. `enhanced_retrieval`

Optional internal analysis:

3. `local_graphrag_ablation`
4. `vector_only_ablation`
5. `deep_route_ablation`

Rules for that next round:

- `standard_retrieval` is the product baseline
- `enhanced_retrieval` is the product enhanced mode
- `local_graphrag` is allowed only as a graph-module attribution view
- `deep_graphrag` is allowed only as a deep-route attribution view
- `force_graph` is diagnostic only and must not be presented as product score

Required reporting fields for the next product comparison:

- `Recall@2 / Recall@5 / Recall@10`
- `Precision@5 / Precision@10`
- `MRR@10`
- `FullChainHit@2 / FullChainHit@3 / FullChainHit@5`
- hard-subset metrics
- latency
- fallback
- route distribution
- `retriever_used` distribution

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
