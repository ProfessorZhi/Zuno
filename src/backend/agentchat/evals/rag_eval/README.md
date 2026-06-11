# Zuno RAG Evaluation

This folder contains the local RAG / GraphRAG evaluation harness used to close `Phase 6`.

## What Is Committed

- `metrics.py`: offline metric calculator.
- `ingest_prepared_corpus.py`: imports a prepared corpus into a Zuno knowledge base.
- `run_eval.py`: shared retrieval-profile runner.
- `run_local_embedding_eval.py`: one-command local embedding eval launcher.
- `run_stackless_local_eval.py`: stackless local eval path that does not require database-backed knowledge metadata.
- `run_stackless_compare_matrix.py`: one-command `local_compare + graph_compare` matrix runner.
- `summarize_eval_profiles.py`: profile summary / markdown report helper.
- `local_embedding_server.py`: tiny OpenAI-compatible local embedding dev server.
- `local_rerank_server.py`: tiny local rerank dev server.
- `generate_contract_review_scale_corpus.py`: synthetic distractor-corpus generator for harder contract-review evaluation.

Generated corpora and eval runs remain ignored by git:

- `corpus/`
- `runs/`

## Profile Contract

`run_eval.py` now exposes the Phase 6 profile contract explicitly:

- `local_compare`
  - `baseline_rag`
  - `rag_rerank`
  - `rag_graph_chunk_backed`
- `graph_compare`
  - `baseline_rag`
  - `rag_graph_chunk_backed`
  - `rag_graph_chunk_backed_3hop`

Older names such as `rag_graph` and `rag_graph_3hop` are kept only as compatibility aliases.

## Minimum Verification

The current minimum `Phase 6` proof surface is:

```powershell
pytest -q src/backend/agentchat/test/test_contract_eval_runner.py `
  src/backend/agentchat/test/test_rag_eval_local_scheme.py `
  src/backend/agentchat/test/test_stackless_compare_matrix.py `
  src/backend/agentchat/test/test_rag_eval_local_launcher.py
```

That set proves the current local profile contract, launcher behavior, compare-matrix surface, and stackless fallback chain.

## Typical Local Flow

If you already have a prepared corpus and a database-backed knowledge flow available:

```powershell
python src/backend/agentchat/evals/rag_eval/run_eval.py `
  --dataset src/backend/agentchat/evals/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag,rag_rerank,rag_graph_chunk_backed `
  --output-dir src/backend/agentchat/evals/rag_eval/runs/<run_id> `
  --trace-langsmith
```

## One-Command Local Embedding Eval

If you want the end-to-end local embedding path:

```powershell
python src/backend/agentchat/evals/rag_eval/run_local_embedding_eval.py `
  --manifest src/backend/agentchat/evals/rag_eval/corpus/python_notes/manifest.json `
  --dataset src/backend/agentchat/evals/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --knowledge-name ZunoLocalEmbeddingEval `
  --text-embedding-model-id <local_embedding_llm_id> `
  --profile-set local_compare
```

If your local embedding endpoint exists but the DB-backed registration / ingest path is temporarily unavailable, this launcher can now fall back to the stackless local-eval path when you pass a direct local embedding target.

## Stackless Local Compare

If you want a local proof path that does not depend on database-backed knowledge metadata:

```powershell
python src/backend/agentchat/evals/rag_eval/run_stackless_local_eval.py `
  --manifest src/backend/agentchat/evals/rag_eval/corpus/python_notes/manifest.json `
  --dataset src/backend/agentchat/evals/rag_eval/python_notes_eval.jsonl `
  --profile-set local_compare `
  --sample-limit 1 `
  --spawn-dev-embedding-server `
  --spawn-dev-rerank-server `
  --rerank-score-threshold-override 0.0 `
  --output-root src/backend/agentchat/evals/rag_eval/runs/stackless-local-compare
```

This mode:

1. can start local dev-model servers
2. builds a synthetic knowledge runtime in memory
3. indexes chunks into local vector storage
4. injects a local graph retriever instead of depending on Neo4j-backed graph runtime
5. lets you compare `baseline_rag`, `rag_rerank`, and `rag_graph_chunk_backed` from one local proof path

## Compare Matrix

If you want one command that produces both `local_compare` and `graph_compare` summary artifacts:

```powershell
python src/backend/agentchat/evals/rag_eval/run_stackless_compare_matrix.py `
  --manifest src/backend/agentchat/evals/rag_eval/corpus/python_notes/manifest.json `
  --dataset src/backend/agentchat/evals/rag_eval/python_notes_eval.jsonl `
  --sample-limit 3 `
  --local-compare-rerank-threshold-override 0.0 `
  --output-root src/backend/agentchat/evals/rag_eval/runs/stackless-compare-matrix
```

This matrix runner writes:

- `local_compare/report.json`
- `graph_compare/report.json`
- `summary.json`
- `summary.md`

It also exposes coverage information so tiny sample slices cannot masquerade as strong GraphRAG conclusions.

## Contract Review Domain Eval

For the contract-review domain, use the same stackless matrix runner with `--domain-pack-id contract_review`.

If you want to test the "GraphRAG only becomes clearly valuable once the local corpus is larger and noisier" hypothesis, generate a scaled local corpus first:

```powershell
python src/backend/agentchat/evals/rag_eval/generate_contract_review_scale_corpus.py `
  --output-dir src/backend/agentchat/evals/rag_eval/corpus/contract_review_scale `
  --copies-per-file 4
```

Then run the same compare matrix against the generated manifest.
