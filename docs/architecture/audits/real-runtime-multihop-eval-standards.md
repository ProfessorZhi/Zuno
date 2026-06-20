# Real Runtime Multihop Eval Standards

This audit defines the first committed standard for Zuno multi-hop retrieval
evaluation. It is intentionally narrower than a full answer-quality benchmark.

## Scope

Round 1 is **retrieval-only real runtime evaluation**.

That means:

- use real normalized benchmark questions
- use a real Zuno runtime retrieval path
- measure retrieval quality, latency, fallback, and failure behavior
- do not use Answer EM / Answer F1 as primary acceptance metrics in round 1

Round 1 does **not** claim final answer-generation quality for GraphRAG.

## Execution Modes

The repository now has three clearly separated execution modes:

1. `mocked`
   - source: `run_multihop_eval.py`
   - purpose: report-shape and CLI smoke only
   - not a real retrieval benchmark

2. `stackless`
   - source: `ingestion/stackless_index.py`
   - purpose: deterministic ingestion smoke over prepared corpus rows
   - not a real runtime benchmark

3. `real_runtime`
   - source: `run_real_runtime_eval.py`
   - purpose: actual runtime retrieval-only evaluation
   - only this mode may be used for real multihop retrieval claims

Any report, summary, or doc must preserve this distinction.

## Primary Metrics

Round 1 real runtime multihop eval uses the following primary metrics.

### Gold Document Recall

- `Recall@2`
- `Recall@5`
- `Recall@10`

Definition:

- `gold_doc_ids` = unique gold supporting document ids for one question
- `retrieved_doc_ids[:K]` = top-K retrieved unique document ids
- `Recall@K = hits_at_k / gold_count`

If `gold_count == 0`, the sample is invalid for recall averaging and must be
excluded from macro averages.

### Precision

- `Precision@5`
- `Precision@10`

Definition:

- `Precision@K = hits_at_k / K`

Important rule:

- denominator stays fixed at `K`
- do not divide by `min(retrieved_count, K)`
- `retrieved_count` must still be recorded separately

### Ranking Quality

- `MRR@10`

Definition:

- use the first relevant rank within top 10
- if no relevant document appears in top 10, score is `0.0`

### Multi-hop Chain Coverage

- `ChainRecall@5`
- `ChainRecall@10`
- `FullChainHit@5`
- `FullChainHit@10`

Round 1 chain rule:

- `ChainRecall@K = hits_at_k / gold_count`
- `FullChainHit@K = 1.0` only when all gold document ids appear inside top K
- otherwise `FullChainHit@K = 0.0`

This first rule treats the document set as the minimal observable multi-hop
chain surface. It does not claim full path-level GraphRAG reasoning quality.

## Runtime Health Metrics

Real runtime reports must also include:

- `avg_latency_ms`
- `p50_latency_ms`
- `p95_latency_ms`
- `failure_count`
- `failure_rate`
- `fallback_count`
- `fallback_rate`
- `empty_result_count`

Optional when the runtime can distinguish it cleanly:

- `timeout_count`
- `timeout_rate`

Definitions:

- `failure`: request could not complete a usable retrieval response
- `fallback`: runtime downgraded from the requested route to another route
- `empty_result`: runtime returned zero retrieved documents

## Aggregation Rules

Aggregate metrics must follow these rules:

- use macro average across valid questions
- invalid-gold samples are excluded from recall / precision / MRR / chain
  averages
- failure samples still count toward runtime health totals
- failure samples contribute zero to retrieval metrics when a valid gold set
  exists but no usable retrieval result is returned

## Required Per-question Fields

Each real runtime per-question row must capture at least:

- `question_id`
- `gold_count`
- `retrieved_count`
- `hits_at_2`
- `hits_at_5`
- `hits_at_10`
- `recall_at_2`
- `recall_at_5`
- `recall_at_10`
- `precision_at_5`
- `precision_at_10`
- `mrr_at_10`
- `chain_recall_at_5`
- `chain_recall_at_10`
- `full_chain_hit_at_5`
- `full_chain_hit_at_10`
- `latency_ms`
- `fallback`
- `failure`
- `invalid_gold`

## Required Aggregate Fields

Each real runtime aggregate block must capture at least:

- `question_count`
- `valid_question_count`
- `Recall@2`
- `Recall@5`
- `Recall@10`
- `Precision@5`
- `Precision@10`
- `MRR@10`
- `ChainRecall@5`
- `ChainRecall@10`
- `FullChainHit@5`
- `FullChainHit@10`
- `avg_latency_ms`
- `p50_latency_ms`
- `p95_latency_ms`
- `failure_count`
- `failure_rate`
- `fallback_count`
- `fallback_rate`
- `empty_result_count`

## Explicit Non-goals For Round 1

Round 1 does not require:

- answer EM / answer F1 as closure metrics
- full Microsoft GraphRAG parity
- community hierarchy quality metrics
- path-faithfulness grading
- automatic judge-model scoring

## Acceptance Boundary

For a result to be called a real runtime multihop evaluation:

- dataset questions must come from normalized benchmark files
- retrieval must run through a real Zuno runtime path
- the report must say `execution_mode = "real_runtime"`
- fallback and failure behavior must be recorded explicitly
- if graph or community capability is unavailable, the report must say so and
  must not claim real GraphRAG success
