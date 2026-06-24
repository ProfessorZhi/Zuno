# Public Demo Runbook

## Purpose

This runbook explains how to reproduce the strongest public-facing proof that currently exists in Zuno:

1. local embedding preflight works
2. local `RAG` vs `GraphRAG` evaluation works
3. contract-review domain modeling becomes materially useful when the corpus gets larger and noisier

This is the shortest reproducible path for a public demo audience.

For the formal public acceptance gate of this material, see:

- [public-demo-acceptance.md](public-demo-acceptance.md)

For the lowest-cost live runtime smoke check, run:

```powershell
python tools/scripts/verify_public_demo_runtime.py
```

For the lowest-cost strict-grounding smoke check, run:

```powershell
python tools/scripts/verify_public_demo_strict_grounding.py
```

## Demo Goal

The demo should prove three things:

1. Zuno can run local retrieval evaluation without depending on a remote embedding service
2. Zuno can compare `baseline_rag`, `rag_rerank`, and `rag_graph_chunk_backed` under fixed metrics
3. for contract review, structured domain modeling plus GraphRAG is more valuable when the dataset is larger and more confusing

## What To Run

### Step 1: Preflight a local embedding endpoint

If you already have a local OpenAI-compatible embedding endpoint:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --local-embedding-model-name zuno-local-embedding-dev `
  --local-embedding-base-url http://127.0.0.1:11434/v1 `
  --validate-only
```

If you do not already have one, start the built-in dev server first:

```powershell
python tools/evals/zuno/rag_eval/local_embedding_server.py `
  --host 127.0.0.1 `
  --port 11434 `
  --model-name zuno-local-embedding-dev
```

### Step 2: Run the generic graph-relation compare matrix

```powershell
python tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py `
  --manifest .local/evals/zuno/rag_eval/corpus/mixed_tuning_v2/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --sample-limit 10 `
  --output-root .local/evals/zuno/rag_eval/runs/public-demo-graph-relation
```

Expected proof pattern:

- `rag_graph_chunk_backed` should outperform `baseline_rag` on graph-relation questions
- the acceptance table should remain green

Reference evidence already in repo:

- [public-demo-evidence.md](public-demo-evidence.md)

### Step 3: Run the contract-review domain demo

```powershell
python tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py `
  --manifest .local/evals/zuno/rag_eval/corpus/contract_review_scale_corpus/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/contract_review_graph_relation_small.jsonl `
  --domain-pack-id contract_review `
  --output-root .local/evals/zuno/rag_eval/runs/public-demo-contract-review
```

Expected proof pattern:

- `rag_graph_chunk_backed` should clearly beat `baseline_rag`
- citation accuracy should remain strong
- answer faithfulness should remain high

Reference evidence already in repo:

- [public-demo-evidence.md](public-demo-evidence.md)

### Step 4: Run the low-cost end-to-end smoke verifier

```powershell
python tools/scripts/verify_public_demo_runtime.py
```

Expected proof pattern:

- the verifier should pass in `dev_offline`
- it should produce at least one markdown report artifact in a temp directory
- the report should still contain answer text, citation output, and graph-path support

### Step 5: Run the strict-grounded conservative-failure verifier

```powershell
python tools/scripts/verify_public_demo_strict_grounding.py
```

Expected proof pattern:

- a supported evidence case should keep a grounded answer
- an unsupported evidence case should downgrade to `NO_RELEVANT_EVIDENCE_FOUND`
- the demo therefore proves not only "can answer", but also "does not pretend to be grounded when evidence is weak"

## Metrics To Show Publicly

For retrieval quality, the public demo should always show these five core metrics:

- Recall@5
- Hit Rate@5
- Context Precision@5
- MRR@5
- NDCG@5

Optional answer-layer metrics that are already available:

- Faithfulness
- Citation Accuracy

## What Result Matters Most

For a public audience, the most convincing result is not "GraphRAG exists".
It is this:

- on the generic graph-relation set, GraphRAG beats baseline on relation-heavy retrieval
- on the scaled contract-review set, GraphRAG plus domain modeling beats baseline by a wide margin

That is the shortest proof of the architecture thesis.

## Public Demo Notes

- Do not publish `.local/`, local config files, or generated eval corpora/runs.
- Use committed datasets and committed docs as the public explanation layer.
- Treat generated run directories as reproducible local evidence, not public repo assets.
