# Real Runtime Multihop Eval Results

This audit records the current evidence for retrieval-only real runtime
multihop evaluation.

## Current Status

Completed first retrieval-only real runtime smoke on June 20, 2026.

Important profile note:

- the first HotpotQA `limit=5` smoke used the older `qwen-plus` retrieval-only
  profile
- after `GraphRAG Route Activation Debug V1`, the default committed multihop
  retrieval profile is aligned to `deepseek-v4-flash`
- later reruns should therefore show the DeepSeek-aligned profile unless an
  explicit backup profile is chosen

Executed dataset and limit:

- dataset: `hotpotqa`
- limit: `5`
- top_k: `10`
- model profile:
  - conversation model: `qwen-plus`
  - text embedding model: `text-embedding-v4`
  - rerank model: `gte-rerank-v2`

## Real Runtime Results

### baseline_rag

- execution mode: `real_runtime`
- requested runtime mode: `rag`
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
- `avg_latency_ms = 11294.88`
- `p50_latency_ms = 11816.87`
- `p95_latency_ms = 13371.06`
- `failure_count = 0`
- `fallback_count = 0`
- verdict: real runtime baseline retrieval succeeded

### local_graphrag

- execution mode: `real_runtime`
- requested runtime mode: `local_graphrag`
- `Recall@2 = 0.60`
- `Recall@5 = 1.00`
- `Recall@10 = 1.00`
- `Precision@5 = 0.40`
- `Precision@10 = 0.20`
- `MRR@10 = 0.8667`
- `ChainRecall@5 = 1.00`
- `ChainRecall@10 = 1.00`
- `FullChainHit@5 = 1.00`
- `FullChainHit@10 = 1.00`
- `avg_latency_ms = 22279.38`
- `p50_latency_ms = 22183.11`
- `p95_latency_ms = 24315.79`
- `failure_count = 0`
- `fallback_count = 5`
- fallback reason: all five samples degraded with `graph_result_empty`
- verdict: not a clean local GraphRAG win; current runtime path fell back for every sample

### deep_graphrag

- execution mode: `real_runtime`
- requested runtime mode: `rag_graph_deep`
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
- `avg_latency_ms = 13772.39`
- `p50_latency_ms = 13117.17`
- `p95_latency_ms = 16221.32`
- `failure_count = 0`
- `fallback_count = 0`
- verdict: this run stayed on real runtime, but the internal route remained `standard_rag`

## Interpretation

Current evidence proves:

- retrieval-only real runtime eval is now executable
- baseline RAG can run against normalized HotpotQA + built corpus without mocked
  or stackless substitution
- local GraphRAG currently degrades under this sample because graph retrieval did
  not return usable graph evidence
- deep GraphRAG did not fail, but these five HotpotQA questions did not trigger
  a graph/community route, so this is not yet proof of deep GraphRAG quality

Current evidence does **not** prove:

- Community GraphRAG quality
- DRIFT-like quality
- stable local GraphRAG gains on benchmark multihop questions
- cross-dataset results for 2Wiki or MuSiQue

## Blockers And Gaps

- `twowiki` normalized sample50 file was not present in the current workspace at
  run time, so 2Wiki real runtime execution was not started in this round.
- `local_graphrag` needs follow-up debugging on why graph retrieval returns
  empty graph results for all five sampled HotpotQA questions.
- `deep_graphrag` needs a second-round audit with questions that actually
  trigger relation/global routing, otherwise it mostly behaves like baseline
  standard retrieval.

## Required Reading

The scoring contract is defined in:

- [Real Runtime Multihop Eval Standards](./real-runtime-multihop-eval-standards.md)

## Reporting Rules

When a run succeeds, this audit must record:

- dataset
- limit
- mode
- `Recall@2/5/10`
- `Precision@5/10`
- `MRR@10`
- `ChainRecall@5/10`
- `FullChainHit@5/10`
- `avg/p50/p95 latency`
- `failure_count`
- `fallback_count`
- whether the run used real GraphRAG or degraded

When a run is blocked, this audit must record:

- blocker
- failure point
- completed parts
- next fix
