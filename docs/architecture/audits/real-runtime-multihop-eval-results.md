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

## Product Retrieval Comparison: HotpotQA Limit=20

Current verified product-mode `limit=20` run set was rerun on June 20, 2026
after comparison-chain fusion tuning, with:

- dataset: `hotpotqa`
- limit: `20`
- top_k: `10`
- route policy: `auto`
- product comparison:
  - `standard_retrieval`
  - `enhanced_retrieval`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

### standard_retrieval limit=20

- `Recall@2 = 0.90`
- `Recall@5 = 0.975`
- `Recall@10 = 0.975`
- `Precision@5 = 0.39`
- `Precision@10 = 0.195`
- `MRR@10 = 1.00`
- derived `ChainRecall@2 = 0.90`
- derived `ChainRecall@3 = 0.95`
- `ChainRecall@5 = 0.975`
- `ChainRecall@10 = 0.975`
- derived `FullChainHit@2 = 0.80`
- derived `FullChainHit@3 = 0.90`
- `FullChainHit@5 = 0.95`
- `FullChainHit@10 = 0.95`
- `avg/p50/p95 latency = 13763.89 / 13563.89 / 18021.79 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `retriever_used distribution = {vector: 20}`
  - `vector_used = 20/20`
  - `bm25_available = 0/20`
  - `bm25_used = 0/20`
  - `bm25_fallback_reason = bm25_backend_unavailable`
  - `fusion_used = 20/20`
  - `rerank_used = 20/20`
  - `internal_route distribution = {standard_rag: 20}`

### enhanced_retrieval limit=20

- `Recall@2 = 0.90`
- `Recall@5 = 0.975`
- `Recall@10 = 0.975`
- `Precision@5 = 0.39`
- `Precision@10 = 0.195`
- `MRR@10 = 1.00`
- derived `ChainRecall@2 = 0.90`
- derived `ChainRecall@3 = 0.95`
- `ChainRecall@5 = 0.975`
- `ChainRecall@10 = 0.975`
- derived `FullChainHit@2 = 0.80`
- derived `FullChainHit@3 = 0.90`
- `FullChainHit@5 = 0.95`
- `FullChainHit@10 = 0.95`
- `avg/p50/p95 latency = 12989.80 / 12040.78 / 17307.62 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `standard_floor_used = 20/20`
  - `graph_route_attempted = 4/20`
  - `graph_route_used = 4/20`
  - `graph_result_count > 0 = 4`
  - `graph_path_count > 0 = 4`
  - `requery_available = 20/20`
  - `requery_used = 0/20`
  - `community_available = 0/20`
  - `community_used = 0/20`
  - `drift_available = 0/20`
  - `drift_used = 0/20`
  - `confidence_gated_fusion_used = 20/20`
  - `final_rerank_used = 20/20`
  - `route_selection_reason distribution = {relation_question: 4, standard_question: 16}`
  - `internal_route distribution = {local_graphrag: 4, standard_rag: 16}`
  - `retriever_used distribution = {vector: 20, graph: 4}`

## Per-question Delta Summary: Limit=20

### enhanced_helps cases

No help case was observed on the rerun `limit=20` product sample.

Enhanced retrieval did not improve headline retrieval metrics beyond standard,
but it no longer regresses the hard comparison subset.

### enhanced_hurts cases

No hurt case was observed on the rerun `limit=20` product sample.

The previously failing comparison question:

- `5a8b57f25542995d1e6f1371`
- question: `Were Scott Derrickson and Ed Wood of the same nationality?`
- current standard top3:
  - `Scott Derrickson`
  - `Ed Wood (film)`
  - `Ed Wood`
- current enhanced top3:
  - `Scott Derrickson`
  - `Ed Wood (film)`
  - `Ed Wood`
- current effect:
  - standard derived `FullChainHit@3 = 1.0`
  - enhanced derived `FullChainHit@3 = 1.0`
- current route:
  - `internal_route = local_graphrag`
  - `graph_result_count = 14`
  - `graph_path_count = 24`
  - `fusion_metadata.comparison_seed_entities = [scott derrickson, ed wood]`

### enhanced_ties cases

The remaining nineteen sampled questions tied on the tracked product metrics.

### enhanced_fallback cases

No enhanced fallback case was observed:

- `fallback_count = 0`

## Hard Multihop Subset Analysis

Question-text-only hard subset rule matched three questions:

- comparison: `2`
- bridge relation: `1`
- multi-entity relation: `0`

### Hard subset metrics

standard:

- `hard_subset_count = 3`
- derived `ChainRecall@2 = 0.8333`
- derived `ChainRecall@3 = 1.0000`
- `ChainRecall@5 = 1.0000`
- derived `FullChainHit@2 = 0.6667`
- derived `FullChainHit@3 = 1.0000`
- `FullChainHit@5 = 1.0000`
- `graph_activation_rate = 0.0000`

enhanced:

- `hard_subset_count = 3`
- derived `ChainRecall@2 = 0.8333`
- derived `ChainRecall@3 = 1.0000`
- `ChainRecall@5 = 1.0000`
- derived `FullChainHit@2 = 0.6667`
- derived `FullChainHit@3 = 1.0000`
- `FullChainHit@5 = 1.0000`
- `graph_activation_rate = 1.0000`

hard subset outcome:

- `enhanced_win_count = 0`
- `enhanced_tie_count = 3`
- `enhanced_loss_count = 0`

Verdict on hard subset:

- enhanced retrieval recovered the former comparison regression
- enhanced retrieval now matches standard retrieval on the current hard subset
- enhanced retrieval is still not superior on the current hard subset

## Product Comparison Decision: Limit=20

Decision rules:

1. `Recall@5 >= standard Recall@5`
2. `failure_count = 0`
3. `fallback_rate <= 30%`
4. `p95 latency <= standard p95 * 2.2`
5. `enhanced_hurts cases <= 2`

Result:

1. passed
2. passed
3. passed
4. passed
5. passed

Win conditions:

- `Recall@2 > standard`: failed
- `MRR@10 > standard`: failed
- `FullChainHit@2 > standard`: failed
- `FullChainHit@3 > standard`: failed
- hard subset recall / MRR / chain hit win: failed

Final verdict:

- `enhanced_retrieval` recovers the hard-subset regression and is baseline-preserving enough to continue evaluation
- `enhanced_retrieval` is not yet superior
- current evidence is strong enough to allow `HotpotQA limit=50`
- current evidence still does **not** justify direct expansion to `2Wiki`

Recommended next step:

- proceed to `HotpotQA limit=50`
- keep a follow-up audit on whether enhanced can create genuine help cases
- keep `2Wiki small smoke` as a later option, not the immediate next move

## Product Retrieval Comparison: HotpotQA Limit=50

Current verified product-mode `limit=50` run set was executed on June 21, 2026
with:

- dataset: `hotpotqa`
- limit: `50`
- top_k: `10`
- route policy: `auto`
- product comparison:
  - `standard_retrieval`
  - `enhanced_retrieval`
- conversation model: `deepseek-v4-flash`
- text embedding model: `text-embedding-v4`
- rerank model: `gte-rerank-v2`

### standard_retrieval limit=50

- `Recall@2 = 0.85`
- `Recall@5 = 0.97`
- `Recall@10 = 0.97`
- `Precision@5 = 0.388`
- `Precision@10 = 0.194`
- `MRR@10 = 1.00`
- derived `ChainRecall@2 = 0.85`
- derived `ChainRecall@3 = 0.93`
- `ChainRecall@5 = 0.97`
- `ChainRecall@10 = 0.97`
- derived `FullChainHit@2 = 0.70`
- derived `FullChainHit@3 = 0.86`
- `FullChainHit@5 = 0.94`
- `FullChainHit@10 = 0.94`
- `avg/p50/p95 latency = 12788.60 / 12434.31 / 15647.17 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `retriever_used distribution = {vector: 50}`
  - `vector_used = 50/50`
  - `bm25_available = 0/50`
  - `bm25_used = 0/50`
  - `bm25_fallback_reason = bm25_backend_unavailable`
  - `fusion_used = 50/50`
  - `rerank_used = 50/50`
  - `internal_route distribution = {standard_rag: 50}`

### enhanced_retrieval limit=50

- `Recall@2 = 0.84`
- `Recall@5 = 0.97`
- `Recall@10 = 0.97`
- `Precision@5 = 0.388`
- `Precision@10 = 0.194`
- `MRR@10 = 1.00`
- derived `ChainRecall@2 = 0.84`
- derived `ChainRecall@3 = 0.93`
- `ChainRecall@5 = 0.97`
- `ChainRecall@10 = 0.97`
- derived `FullChainHit@2 = 0.68`
- derived `FullChainHit@3 = 0.86`
- `FullChainHit@5 = 0.94`
- `FullChainHit@10 = 0.94`
- `avg/p50/p95 latency = 12586.02 / 11964.68 / 16617.77 ms`
- `fallback_count = 0`
- `failure_count = 0`
- route diagnostics:
  - `standard_floor_used = 50/50`
  - `graph_route_attempted = 5/50`
  - `graph_route_used = 5/50`
  - `graph_result_count > 0 = 5`
  - `graph_path_count > 0 = 5`
  - `requery_available = 50/50`
  - `requery_used = 0/50`
  - `community_available = 0/50`
  - `community_used = 0/50`
  - `drift_available = 0/50`
  - `drift_used = 0/50`
  - `confidence_gated_fusion_used = 50/50`
  - `final_rerank_used = 50/50`
  - `route_selection_reason distribution = {relation_question: 5, standard_question: 45}`
  - `internal_route distribution = {local_graphrag: 5, standard_rag: 45}`
  - `retriever_used distribution = {vector: 50, graph: 5}`

## Per-question Delta Summary: Limit=50

### enhanced_helps cases

One help case was observed:

1. `5ae4a3265542995ad6573de5`
   - question: `Hayden is a singer-songwriter from Canada, but where does Buck-Tick hail from?`
   - standard top5:
     - `Buck-Tick`
     - `Atsushi Sakurai`
     - `Masami Tsuchiya`
     - `Kyo (musician)`
     - `Mick (DJ)`
   - enhanced top5:
     - `Buck-Tick`
     - `Hayden (musician)`
     - `Atsushi Sakurai`
     - `Masami Tsuchiya`
     - `Skyscraper National Park`
   - effect:
     - `Recall@2: 0.5 -> 1.0`
     - `Recall@5: 0.5 -> 1.0`
     - `FullChainHit@2: 0 -> 1`
     - `FullChainHit@3: 0 -> 1`
   - route:
     - `internal_route = standard_rag`
     - `graph_used = false`
   - likely reason:
     - enhanced product path improved baseline retrieval ordering even without
       graph activation

### enhanced_hurts cases

Two hurt cases were observed:

1. `5a828c8355429966c78a6a50`
   - question: `Kaiser Ventures corporation was founded by an American industrialist who became known as the father of modern American shipbuilding?`
   - standard top5:
     - `Henry J. Kaiser`
     - `Kaiser Ventures`
     - `Kaiser Shipyards`
     - `Edgar Kaiser Sr.`
     - `Edgar Kaiser Jr.`
   - enhanced top5:
     - `Henry J. Kaiser`
     - `Cho Kyuhyun`
     - `Kaiser Ventures`
     - `Method Man`
     - `Kaiser Shipyards`
   - effect:
     - `FullChainHit@2: 1 -> 0`
     - `FullChainHit@3: 1 -> 1`
   - route:
     - `internal_route = local_graphrag`
     - `graph_used = true`
   - likely reason:
     - graph route introduced noisy rank-2 distraction before the second gold
       document

2. `5a7571135542992d0ec05f98`
   - question: `Ralph Hefferline was a psychology professor at a university that is located in what city?`
   - standard top5:
     - `Ralph Hefferline`
     - `Columbia University`
     - `Virginia Commonwealth University`
     - `University of the Incarnate Word`
     - `University of Kansas`
   - enhanced top5:
     - `Ralph Hefferline`
     - `Virginia Commonwealth University`
     - `University of the Incarnate Word`
     - `University of Kansas`
     - `Amherst, Massachusetts`
   - effect:
     - `Recall@2: 1.0 -> 0.5`
     - `Recall@5: 1.0 -> 0.5`
     - `FullChainHit@2: 1 -> 0`
     - `FullChainHit@3: 1 -> 0`
   - route:
     - `internal_route = standard_rag`
     - `graph_used = false`
   - likely reason:
     - baseline ordering changed and dropped `Columbia University` out of top5

### enhanced_ties cases

The remaining forty-seven sampled questions tied on the tracked product
metrics.

### standard_gap_cases

Seven standard gap cases were observed.

- one gap was improved by enhanced retrieval:
  - `5ae4a3265542995ad6573de5`
- six gap cases remained missed opportunities:
  - `5ab6d09255429954757d337d`
  - `5a75e05c55429976ec32bc5f`
  - `5ae0d4c9554299603e418468`
  - `5adddccd5542997dc7907069`
  - `5a79311755429970f5fffe67`
  - `5abbf698554299114383a0b5`

### missed_opportunity_cases

Enhanced retrieval failed to improve six cases where standard retrieval still
had a gap.

Pattern:

- all six stayed on `standard_rag`
- none used graph, community, or drift
- none used requery

This means the current missed-opportunity ceiling is mostly in the standard
baseline path, not in graph route under-activation alone.

### enhanced_fallback cases

No enhanced fallback case was observed:

- `fallback_count = 0`

## Hard Multihop Subset Analysis: Limit=50

Question-text-only hard subset rule again matched three questions:

- comparison: `2`
- bridge relation: `1`
- multi-entity relation: `0`

### Hard subset metrics

standard:

- `hard_subset_count = 3`
- `Recall@2 = 0.8333`
- `Recall@5 = 1.0000`
- `MRR@10 = 1.0000`
- `FullChainHit@2 = 0.6667`
- `FullChainHit@3 = 1.0000`
- `FullChainHit@5 = 1.0000`
- `graph_activation_rate = 0.0000`

enhanced:

- `hard_subset_count = 3`
- `Recall@2 = 0.8333`
- `Recall@5 = 1.0000`
- `MRR@10 = 1.0000`
- `FullChainHit@2 = 0.6667`
- `FullChainHit@3 = 1.0000`
- `FullChainHit@5 = 1.0000`
- `graph_activation_rate = 1.0000`

hard subset outcome:

- `enhanced_win_count = 0`
- `enhanced_tie_count = 3`
- `enhanced_loss_count = 0`
- `hard_subset_helps = 0`
- `hard_subset_hurts = 0`
- `hard_subset_missed_opportunities = 0`

Verdict on hard subset:

- enhanced retrieval still preserves the repaired hard subset
- enhanced retrieval does not yet beat standard retrieval on the hard subset

## Product Comparison Decision: Limit=50

Decision rules:

1. `Recall@5 >= standard Recall@5`
2. `failure_count = 0`
3. `fallback_rate <= 30%`
4. `p95 latency <= standard p95 * 2.2`
5. `enhanced_hurts cases <= 2`

Result:

1. passed
2. passed
3. passed
4. passed
5. passed

Win conditions:

- `Recall@2 > standard`: failed
- `MRR@10 > standard`: failed
- `FullChainHit@2 > standard`: failed
- `FullChainHit@3 > standard`: failed
- hard subset Recall@5 > standard: failed
- hard subset MRR@10 > standard: failed
- hard subset FullChainHit@2/3 > standard: failed
- `enhanced_helps_count > enhanced_hurts_count`: failed

Final verdict:

- `enhanced_retrieval` remains baseline-preserving at `limit=50`
- `enhanced_retrieval` is still not yet superior
- one genuine help case appeared, but two hurt cases remain
- current evidence does **not** justify direct expansion to `2Wiki`

Recommended next step:

- keep `HotpotQA` as the active dataset
- target the two `limit=50` hurt cases and the six missed-opportunity cases
- do not start `2Wiki small smoke` yet

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

## HotpotQA Limit=50 Post-tuning Rerun

Current verified post-tuning rerun was executed on June 21, 2026 after:

- standard floor invariance
- bridge relation graph guardrail
- proactive requery activation for bridge / attribute questions

Compared reports:

- `hotpotqa_standard_retrieval_limit50_post_tuning.json`
- `hotpotqa_enhanced_retrieval_limit50_post_tuning_v3.json`

### standard_retrieval

- `Recall@2 = 0.84`
- `Recall@5 = 0.96`
- `Recall@10 = 0.96`
- `MRR@10 = 1.00`
- derived `ChainRecall@2/3/5 = 0.84 / 0.92 / 0.96`
- derived `FullChainHit@2/3/5 = 0.68 / 0.84 / 0.92`
- `avg/p50/p95 latency = 13340.82 / 13001.57 / 19170.42 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.86`
- `Recall@5 = 0.97`
- `Recall@10 = 0.98`
- `MRR@10 = 1.00`
- derived `ChainRecall@2/3/5 = 0.86 / 0.94 / 0.97`
- derived `FullChainHit@2/3/5 = 0.72 / 0.88 / 0.94`
- `avg/p50/p95 latency = 14615.90 / 13099.89 / 23663.10 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Route Diagnostics

- `internal_route distribution = {standard_rag: 42, local_graphrag: 8}`
- `route_selection_reason distribution = {standard_question: 42, relation_question: 8}`
- `graph_used = 8/50`
- `requery_used = 9/50`
- `requery_fallback_to_floor = 0/50`
- `community_used = 0/50`
- `drift_used = 0/50`
- `p95 latency ratio vs standard = 1.23x`

### Per-question Delta Summary

- `enhanced_helps cases = 2`
  - `5a8e3ea95542995a26add48d`
  - `5ae4a3265542995ad6573de5`
- `enhanced_hurts cases = 1`
  - `5a79311755429970f5fffe67`
- `enhanced_ties cases = 47`
- `standard_gap_cases = 4`
- `missed_opportunity_cases = 0`

Help shape:

- `Big Stone Gap` now reaches both gold docs at `top2` through
  `local_graphrag + requery`
- `Buck-Tick hail from` now promotes `Hayden (musician)` into the early ranks
  through `local_graphrag + requery`

Remaining hurt shape:

- `5a79311755429970f5fffe67`
- current issue is no longer graph noise
- it is a narrow false-positive requery case on
  `written and illustrated by someone born in what year`

### Decision

This rerun passes the current closure gates:

1. `enhanced Recall@5 >= standard Recall@5`
2. `enhanced FullChainHit@3 >= standard FullChainHit@3`
3. `enhanced_hurts cases <= 1`
4. `enhanced_helps_count >= enhanced_hurts_count`
5. `requery_used > 0`
6. `missed_opportunity_cases` reduced
7. `p95 latency <= standard p95 * 2.2`
8. `fallback_count = 0`
9. `failure_count = 0`

Verdict:

- `enhanced_retrieval` now beats the rerun `standard_retrieval` baseline on the
  main HotpotQA `limit=50` retrieval surface
- M2 to M4 closed the previous missed-opportunity ceiling
- this is strong enough to allow a cautious `2Wiki small smoke`
- the next precision cleanup target is the single remaining false-positive
  requery hurt case

## HotpotQA Limit=50 Post-cleanup V2

Current verified cleanup rerun was executed on June 21, 2026 after the
dedicated requery precision gate blocked generic same-domain requery promotion.

Compared reports:

- `hotpotqa_standard_retrieval_limit50_post_cleanup.json`
- `hotpotqa_enhanced_retrieval_limit50_post_cleanup_v2.json`

### standard_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.97`
- `Recall@10 = 0.97`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.97`
- `FullChainHit@5 = 0.94`
- `avg/p50/p95 latency = 13291.03 / 12854.74 / 17251.26 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.98`
- `Recall@10 = 0.99`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.98`
- `FullChainHit@5 = 0.96`
- `avg/p50/p95 latency = 13823.47 / 12821.26 / 21651.31 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Route Diagnostics

- `internal_route distribution = {standard_rag: 42, local_graphrag: 8}`
- `route_selection_reason distribution = {standard_question: 42, relation_question: 8}`
- `graph_used = 8/50`
- `requery_used = 9/50`
- `community_used = 0/50`
- `drift_used = 0/50`
- `p95 latency ratio vs standard = 1.26x`

### Delta Summary

- `enhanced_helps cases = 1`
  - `5ae4a3265542995ad6573de5`
- `enhanced_hurts cases = 0`
- `enhanced_ties cases = 49`

The previous false-positive requery hurt case
`5a79311755429970f5fffe67` is now closed. Enhanced top5 no longer inserts
`My Bride is a Mermaid`, and `requery_confidence_summary` reports no promoted
requery candidates for that query.

Decision:

- HotpotQA main retrieval surface remains improved after cleanup
- this is the correct stable baseline before any further cross-dataset work

## 2Wiki Limit=10 Small Smoke

Current verified smoke was executed on June 21, 2026 as the first cautious
cross-dataset check after HotpotQA cleanup.

Compared reports:

- `twowiki_standard_retrieval_limit10_smoke.json`
- `twowiki_enhanced_retrieval_limit10_smoke.json`

### standard_retrieval

- `Recall@2 = 0.70`
- `Recall@5 = 0.85`
- `Recall@10 = 0.85`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.85`
- `FullChainHit@5 = 0.70`
- `avg/p50/p95 latency = 12091.48 / 11234.70 / 16137.56 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.70`
- `Recall@5 = 0.80`
- `Recall@10 = 0.85`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.80`
- `FullChainHit@5 = 0.60`
- `avg/p50/p95 latency = 16051.30 / 11908.35 / 29846.32 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Route Diagnostics

- `internal_route distribution = {local_graphrag: 6, standard_rag: 4}`
- `route_selection_reason distribution = {relation_question: 6, standard_question: 4}`
- `graph_used = 6/10`
- `requery_used = 4/10`
- `community_used = 0/10`
- `drift_used = 0/10`
- `p95 latency ratio vs standard = 1.85x`

### Delta Summary

- `enhanced_helps cases = 0`
- `enhanced_hurts cases = 1`
  - `2ec440560bb011ebab90acde48001122`
- `enhanced_ties cases = 9`
- `standard_gap_cases = 3`
- `missed_opportunity_cases = 3`

Current blocker shape:

- query: `Who is the maternal grandfather of Antiochus X Eusebes?`
- standard top5 keeps both `Antiochus X Eusebes` and `Cleopatra IV of Egypt`
- enhanced local graph route promotes noisy genealogy neighbors and pushes
  `Cleopatra IV of Egypt` to rank 6

Decision:

- do not expand `2Wiki` beyond this smoke yet
- the next required work is graph ranking / path precision for genealogy-style
  bridge questions, not more requery tuning

## 2Wiki Limit=10 Targeted Rerun V2

Current verified targeted rerun was executed on June 21, 2026 after:

- genealogy bridge guardrail
- 2Wiki relation / comparison activation expansion
- enhanced activation metadata hardening

Compared reports:

- `twowiki_standard_retrieval_limit10_targeted_v2.json`
- `twowiki_enhanced_retrieval_limit10_targeted_v2.json`

### standard_retrieval

- `Recall@2 = 0.70`
- `Recall@5 = 0.85`
- `Recall@10 = 0.85`
- `Precision@5 = 0.36`
- `Precision@10 = 0.18`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.85`
- `ChainRecall@10 = 0.85`
- `FullChainHit@5 = 0.70`
- `FullChainHit@10 = 0.70`
- `avg/p50/p95 latency = 14866.14 / 14033.90 / 18782.37 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.70`
- `Recall@5 = 0.80`
- `Recall@10 = 0.90`
- `Precision@5 = 0.34`
- `Precision@10 = 0.19`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.80`
- `ChainRecall@10 = 0.90`
- `FullChainHit@5 = 0.60`
- `FullChainHit@10 = 0.80`
- `avg/p50/p95 latency = 16494.69 / 12822.09 / 27024.74 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Route Diagnostics

- `internal_route distribution = {local_graphrag: 9, standard_rag: 1}`
- `route_selection_reason distribution = {relation_question: 9, standard_question: 1}`
- `graph_used = 9/10`
- `requery_used = 4/10`
- `community_used = 0/10`
- `drift_used = 0/10`
- `standard_floor_used = 10/10`
- `genealogy_promotion_blocked count = 6`

### Delta Summary

- `enhanced_helps cases = 0`
- `enhanced_hurts cases = 1`
  - `2ec440560bb011ebab90acde48001122`
- `standard_gap_cases = 3`
- `missed_opportunity_cases = 3`

The important change is structural, not headline score:

- all three earlier missed-opportunity questions now activate
- none remains a pure under-activation miss
- remaining failures are now precision failures inside the activated route

Current blocker still is:

- `2ec440560bb011ebab90acde48001122`
- `Who is the maternal grandfather of Antiochus X Eusebes?`
- enhanced metadata now shows:
  - `graph_activation_reason = genealogy_bridge_pattern`
  - `candidate_blocked_reason = low_precision_genealogy`
  - `floor_preserved_reason = standard_floor_chain_protection`

But the current guardrail still does not fully protect top5:

- `North Marion High School (West Virginia)` still reaches rank 3
- `Cleopatra IV of Egypt` is still pushed to rank 6

### Decision

This rerun still fails the 2Wiki gate:

1. `enhanced Recall@5 >= standard Recall@5`: failed
2. `enhanced FullChainHit@5 >= standard FullChainHit@5`: failed
3. `failure_count = 0`: passed
4. `fallback_rate <= 30%`: passed
5. `p95 latency <= standard p95 * 2.5`: passed
6. `enhanced_hurts cases <= 1`: passed

Verdict:

- activation work improved observability and top10 recovery
- enhanced retrieval is still **not** baseline-preserving on `2Wiki limit=10`
- `2Wiki limit=20` remains blocked

## HotpotQA Limit=50 Regression Check After 2Wiki Tuning

Current verified regression check was executed on June 21, 2026 with:

- `hotpotqa_standard_retrieval_limit50_2wiki_regression_v2.json`
- `hotpotqa_enhanced_retrieval_limit50_2wiki_regression_v2.json`

### standard_retrieval

- `Recall@2 = 0.86`
- `Recall@5 = 0.98`
- `Recall@10 = 0.98`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.98`
- `FullChainHit@5 = 0.96`
- derived `FullChainHit@3 = 0.88`
- `avg/p50/p95 latency = 12418.59 / 11968.05 / 15253.67 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.98`
- `Recall@10 = 0.99`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.98`
- `FullChainHit@5 = 0.96`
- derived `FullChainHit@3 = 0.88`
- `avg/p50/p95 latency = 16108.13 / 13625.91 / 28336.51 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Regression Verdict

Current HotpotQA rerun stays inside the minimum non-regression envelope:

- `enhanced Recall@5 >= standard Recall@5`
- `enhanced FullChainHit@3 >= standard FullChainHit@3`
- `fallback_count = 0`
- `failure_count = 0`
- `p95 latency ratio = 1.86x < 2.2`

But it is no longer a stronger enhanced win:

- `Recall@2` drops from `0.86` to `0.85`
- current rerun shows `enhanced_hurts cases = 1`
- current rerun `enhanced_helps cases = 0`

So the current 2Wiki tuning is acceptable as a local targeted branch result,
but it does not justify broader rollout or larger 2Wiki expansion.

## 2026-06-22: W7 Genealogy Path Precision Ranking Closure

Verified reports:

- `twowiki_standard_retrieval_limit10_targeted_v4.json`
- `twowiki_enhanced_retrieval_limit10_targeted_v4.json`
- `hotpotqa_standard_retrieval_limit50_2wiki_regression_v3.json`
- `hotpotqa_enhanced_retrieval_limit50_2wiki_regression_v3.json`

### 2Wiki limit=10

#### standard_retrieval

- `Recall@5 = 0.85`
- `Recall@10 = 0.85`
- `FullChainHit@5 = 0.70`
- `FullChainHit@10 = 0.70`
- `MRR@10 = 1.00`
- `p95 latency = 16796.76 ms`
- `fallback_count = 0`
- `failure_count = 0`

#### enhanced_retrieval

- `Recall@5 = 0.85`
- `Recall@10 = 0.90`
- `FullChainHit@5 = 0.70`
- `FullChainHit@10 = 0.80`
- `MRR@10 = 1.00`
- `p95 latency = 24912.50 ms`
- `fallback_count = 0`
- `failure_count = 0`

#### 2Wiki closure verdict

- `enhanced Recall@5 >= standard Recall@5`: passed
- `enhanced FullChainHit@5 >= standard FullChainHit@5`: passed
- `enhanced_hurts cases = 0`
- `fallback_count = 0`
- `failure_count = 0`
- `p95 latency ratio = 1.48x < 2.5`

This is the first rerun in the current 2Wiki branch where enhanced retrieval
is baseline-preserving again on the targeted `limit=10` set without widening to
`limit=20`.

### HotpotQA limit=50 regression

#### standard_retrieval

- `Recall@2 = 0.86`
- `Recall@5 = 0.97`
- `Recall@10 = 0.97`
- `FullChainHit@5 = 0.94`
- `FullChainHit@10 = 0.94`
- `MRR@10 = 1.00`
- `p95 latency = 18578.41 ms`
- `fallback_count = 0`
- `failure_count = 0`

#### enhanced_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.98`
- `Recall@10 = 0.98`
- `FullChainHit@5 = 0.96`
- `FullChainHit@10 = 0.96`
- `MRR@10 = 1.00`
- `p95 latency = 23250.61 ms`
- `fallback_count = 0`
- `failure_count = 0`

#### HotpotQA regression verdict

- `enhanced Recall@5 >= standard Recall@5`: passed
- `enhanced FullChainHit@5 >= standard FullChainHit@5`: passed
- `fallback_count = 0`: passed
- `failure_count = 0`: passed
- `p95 latency ratio = 1.25x`: passed

So the W7 tightening does not just preserve HotpotQA; it slightly improves the
main retrieval metrics on this 50-question regression slice.

## 2026-06-23: W8 2Wiki Limit=20 Cautious Expansion

Fresh verification reports:

- `twowiki_standard_retrieval_limit20_verify_20260623.json`
- `twowiki_enhanced_retrieval_limit20_verify_20260623.json`

The earlier `cautious_v1` pair remains useful as historical evidence, but the
fresh `verify_20260623` pair is the current-state reading.

### standard_retrieval limit=20

- `Recall@2 = 0.65`
- `Recall@5 = 0.725`
- `Recall@10 = 0.725`
- `MRR@10 = 1.00`
- `ChainRecall@2 = 0.65`
- `ChainRecall@3 = 0.70`
- `ChainRecall@5 = 0.725`
- `ChainRecall@10 = 0.725`
- `FullChainHit@2 = 0.30`
- `FullChainHit@3 = 0.35`
- `FullChainHit@5 = 0.35`
- `FullChainHit@10 = 0.35`
- `p95 latency = 17096.99 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval limit=20

- `Recall@2 = 0.65`
- `Recall@5 = 0.75`
- `Recall@10 = 0.80`
- `MRR@10 = 1.00`
- `ChainRecall@2 = 0.65`
- `ChainRecall@3 = 0.70`
- `ChainRecall@5 = 0.75`
- `ChainRecall@10 = 0.80`
- `FullChainHit@2 = 0.30`
- `FullChainHit@3 = 0.35`
- `FullChainHit@5 = 0.40`
- `FullChainHit@10 = 0.50`
- `p95 latency = 26806.36 ms`
- `fallback_count = 0`
- `failure_count = 0`

### W8 diagnostics

- `internal_route distribution = {local_graphrag: 13, standard_rag: 7}`
- `route_selection_reason distribution = {relation_question: 13, standard_question: 7}`
- `graph_used = 13/20`
- `requery_used = 6/20`
- `community_used = 0/20`
- `drift_used = 0/20`
- `standard_floor_used = 20/20`
- `graph_challenger_pool_size avg = 2.05`
- `graph_promotion_allowed count = 2`
- `graph_promotion_blocked_reason distribution = {low_precision_genealogy: 2}`
- `final_top5_floor_preserved count = 2`
- `enhanced_helps cases = 3`
- `enhanced_hurts cases = 0`
- `missed_opportunity_cases = 0`
- `standard_gap_cases = 13` using current top5 full-chain misses as the
  operational definition on this slice
- `latency ratio = 1.57x`

### Gate result

`enhanced_retrieval` is baseline-preserving on 2Wiki `limit=20`.

Recorded conclusion:

- `enhanced_retrieval is baseline-preserving on 2Wiki limit=20.`
- `enhanced has stronger top10 recovery.`

Gate check:

1. `enhanced Recall@5 >= standard Recall@5`: passed
2. `enhanced FullChainHit@5 >= standard FullChainHit@5`: passed
3. `enhanced_hurts cases <= 2`: passed with `0`
4. `fallback_count = 0`: passed
5. `failure_count = 0`: passed
6. `p95 latency <= standard p95 * 2.5`: passed

Current reading:

- enhanced has stronger `top10` recovery than standard on this slice
- the top5 baseline-preserving gate now also passes
- this supports a cautious small-to-medium expansion claim
- `2Wiki limit=50` is now allowed as the next step
- this still does not justify any full-dataset superiority claim

### Fresh HotpotQA Regression Rail

Verified reports:

- `hotpotqa_standard_retrieval_limit50_verify_20260623.json`
- `hotpotqa_enhanced_retrieval_limit50_verify_20260623.json`

Current result:

- `standard Recall@5 = 0.97`
- `enhanced Recall@5 = 0.98`
- `standard FullChainHit@5 = 0.94`
- `enhanced FullChainHit@5 = 0.96`
- `fallback_count = 0`
- `failure_count = 0`
- `p95 latency ratio = 1.48x`
- `enhanced_hurts cases = 0`

The fresh W8 verification therefore does not break the HotpotQA regression
rail.
