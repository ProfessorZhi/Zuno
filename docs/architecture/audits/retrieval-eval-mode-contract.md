# Retrieval Eval Mode Contract

This audit defines how retrieval evaluation should be grouped after the current
GraphRAG route-activation and retrieval-quality work.

The key correction is simple:

- product comparisons should use `standard_retrieval` vs `enhanced_retrieval`
- internal route studies should use ablation or diagnostic labels

## Product Comparison Modes

Future product-facing retrieval evaluation should compare:

1. `standard_retrieval`
2. `enhanced_retrieval`

Definitions:

- `standard_retrieval`
  - product baseline
  - vector + BM25 + fusion + rerank + citations
- `enhanced_retrieval`
  - product enhanced mode
  - `standard_retrieval` floor
  - query rewrite / requery
  - Local GraphRAG
  - community/global retrieval
  - DRIFT-like deep route
  - baseline-preserving fusion
  - final rerank

## Internal Ablation And Diagnostic Modes

These labels are allowed in eval reports, but they are not product modes:

1. `vector_only_ablation`
2. `bm25_ablation`
3. `local_graphrag_ablation`
4. `deep_route_ablation`
5. `force_graph_diagnostic`

Meaning:

- `vector_only_ablation`
  - isolates vector retrieval quality
- `bm25_ablation`
  - isolates keyword retrieval contribution
- `local_graphrag_ablation`
  - explains graph-path contribution on relation-heavy or bridge questions
- `deep_route_ablation`
  - explains deep route contribution when global/community/deep behavior is
    enabled
- `force_graph_diagnostic`
  - forces graph entry for debugging coverage, fallback, and path quality; not a
    product score

## Naming Rules For Eval Reports

Eval reports should follow these rules:

- product scorecards use `standard_retrieval` and `enhanced_retrieval`
- internal experiments use explicit ablation names
- `local_graphrag` is not a product label
- `deep_graphrag` is not a product label
- `force_graph` is diagnostic only

Historical compatibility note:

- current runner still uses `baseline_rag`, `local_graphrag`, and
  `deep_graphrag`
- until the runner is renamed, every product-facing report should translate
  those labels explicitly and call out the mismatch

Current runtime-alignment status:

- `standard_retrieval` is now a supported real-runtime eval alias
- `enhanced_retrieval` is now a supported real-runtime eval alias
- `baseline_rag` remains compatible but deprecated
- `local_graphrag` and `deep_graphrag` remain internal ablation labels

Current product-comparison status:

- HotpotQA `limit=10` product comparison has now been executed with
  `standard_retrieval` vs `enhanced_retrieval`
- current verdict is baseline-preserving tie, not clear enhanced win
- next allowed sample expansion is HotpotQA `limit=20`
- HotpotQA `limit=20` has now also been executed
- current verdict is still baseline-preserving, but not superior
- immediate next move should favor HotpotQA hard-subset tuning rather than
  direct `2Wiki` expansion

## What Each Internal Label Is Allowed To Claim

### `local_graphrag_ablation`

May claim:

- local graph path contribution
- graph seed quality effect
- graph fallback behavior
- path-ranking effect

Must not claim:

- full enhanced product win
- final global/community capability
- final product mode performance

### `deep_route_ablation`

May claim:

- route-selection contribution
- deeper route activation behavior
- community/global/deep route readiness signals

Must not claim:

- final product enhanced mode score by itself

### `force_graph_diagnostic`

May claim:

- graph readiness
- graph path availability
- seed extraction or alias problems
- graph-only failure reasons

Must not claim:

- final user-facing retrieval quality
- product-grade latency or product-grade win rate

## Next HotpotQA Limit=10 Comparison Rule

The next preferred `limit=10` retrieval comparison should be:

1. `standard_retrieval`
2. `enhanced_retrieval`
3. `local_graphrag_ablation` optional
4. `vector_only_ablation` optional
5. `deep_route_ablation` optional

Do not lead the next report with:

- `baseline_rag` vs `local_graphrag` vs `deep_graphrag`

That comparison is still useful for engineering diagnosis, but it is no longer
the right front-door product story.

## Required Metrics

Next-round retrieval comparison should report:

- `Recall@2`
- `Recall@5`
- `Recall@10`
- `Precision@5`
- `Precision@10`
- `MRR@10`
- `FullChainHit@2`
- `FullChainHit@3`
- `FullChainHit@5`
- hard-subset metrics
- latency
- fallback
- route distribution
- `retriever_used` distribution

Optional but helpful:

- graph-active question ratio
- community-active question ratio
- route degradation reasons
- source-mix distribution after fusion

## Reporting Boundary

This contract is intentionally retrieval-only.

It does not authorize:

- using `gold_support` as runtime input
- using final answer EM/F1 as the primary score for this retrieval phase
- shipping diagnostic route names as product UX labels

## Immediate Conclusion

Current repository should keep engineering diagnostics, but future front-path
evaluation must separate:

- product retrieval comparison
- internal module attribution
- graph-route diagnostics
