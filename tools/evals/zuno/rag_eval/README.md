# Zuno RAG Evaluation

This folder contains the local RAG / GraphRAG evaluation harness used to compare retrieval settings.

## What Is Committed

- `python_notes_eval.jsonl`: small query -> gold evidence dataset.
- `metrics.py`: offline metric calculator.
- `prepare_python_notes_corpus.py`: copies a local note folder into an ignored evaluation corpus.
- `public_enterprise_datasets.py`: normalizes first-pass public enterprise-style datasets into the Zuno eval schema.
- `ingest_prepared_corpus.py`: imports a prepared corpus into a Zuno knowledge base.
- `run_eval.py`: runs retrieval profiles and writes metrics/reports.

Generated corpora and eval runs are ignored by git under `.local/evals/zuno/rag_eval/`:

- `corpus/`
- `runs/`

## Retrieval Metrics

The local retrieval comparison between `RAG` and `GraphRAG` should always track these five retrieval metrics:

- Retrieval Recall@K
- Hit Rate@K
- Context Precision@K
- MRR@K
- NDCG@K

Optional answer-layer metrics can be added on top:

- Faithfulness
- Answer Correctness
- Citation Accuracy
- Source Span Accuracy
- Unsupported Claim Rate

## Public Enterprise Dataset V1

The first public enterprise-style adapter surface is intentionally small:

- `techqa_rag_eval`: adapter-ready. Converts TechQA-RAG-Eval style `question / answer / is_impossible / contexts` rows into a local Markdown corpus plus Zuno eval JSONL.
- `cfqa`: adapter-ready for dataset rows. Keeps Chinese annual-report page grounding in `gold_evidence`, but marks the corpus as `external_documents_required` until the public annual-report PDFs are downloaded. It must not create fake PDF corpus files.
- `enterprise_rag_bench`: selected-adapter-ready. Converts EnterpriseRAG-Bench `questions` rows plus a local document parquet/directory into a local Markdown corpus and Zuno eval JSONL. Full 500K-document runs remain an external-scale target; the adapter only writes cases whose `expected_doc_ids` are present locally.
- `open_rag_benchmark`: registry-only in this pass. It needs a qrels/corpus adapter before it becomes runnable.

Prepare a small TechQA-style raw file:

```powershell
python tools/evals/zuno/rag_eval/public_enterprise_datasets.py `
  --dataset techqa_rag_eval `
  --raw .local/evals/raw/techqa_rag_eval_sample.jsonl `
  --output-dir .local/evals/zuno/rag_eval/corpus/public_enterprise_v1/techqa_rag_eval `
  --limit 50
```

Then run it through the existing stackless compare path:

```powershell
python tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py `
  --manifest .local/evals/zuno/rag_eval/corpus/public_enterprise_v1/techqa_rag_eval/manifest.json `
  --dataset .local/evals/zuno/rag_eval/corpus/public_enterprise_v1/techqa_rag_eval/techqa_rag_eval_eval.jsonl `
  --sample-limit 20 `
  --local-compare-rerank-threshold-override 0.0 `
  --output-root .local/evals/zuno/rag_eval/runs/public-enterprise-v1-techqa
```

For CFQA, run the normalizer first to produce a page-grounded dataset, then download the annual-report PDFs and prepare the corpus in a separate step. Until those PDFs are present, the generated `manifest.json` has `file_count = 0`, `external_documents_required = true`, and `blocked_reason = cfqa_annual_report_pdf_required`.

For EnterpriseRAG-Bench, first download the question parquet and at least a local document parquet subset, then normalize a bounded sample:

```powershell
python tools/evals/zuno/rag_eval/public_enterprise_datasets.py `
  --dataset enterprise_rag_bench `
  --raw .local/evals/raw/enterprise_rag_bench/hf/data/questions/test.parquet `
  --source-root .local/evals/raw/enterprise_rag_bench/hf/data/documents/test.parquet `
  --output-dir .local/evals/zuno/rag_eval/corpus/public_enterprise_v1/enterprise_rag_bench_core `
  --limit 20
```

The generated manifest records `selected_question_count`, `skipped_case_count`, `loaded_doc_count`, and any `missing_doc_ids`. If the document parquet is not available, the adapter reports `external_documents_required` and does not fake corpus files.

## Deep GraphRAG Eval Surface

This repo now exposes a small public eval surface for the current Deep GraphRAG V1 round.

Supported public profiles:

- `baseline_rag`
- `local_graphrag`
- `deep_graphrag`

Supported public compare set:

- `deep_graphrag_compare`

The intent of this surface is narrow:

1. give one stable baseline for normal RAG
2. give one stable local-graph profile
3. give one stable deep-routed GraphRAG profile

It is **not** a full production evaluation framework.
It is the V1 public compare surface for the current architecture round.

Minimal example:

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profile-set deep_graphrag_compare `
  --output-dir .local/evals/zuno/rag_eval/runs/<run_id>
```

If you want to isolate one profile at a time:

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag,local_graphrag,deep_graphrag `
  --output-dir .local/evals/zuno/rag_eval/runs/<run_id>
```

## Typical Local Flow

```powershell
python tools/evals/zuno/rag_eval/prepare_python_notes_corpus.py `
  --source "F:\Onboard anything\02_Notes_笔记\2llm_note\Python" `
  --output-dir .local/evals/zuno/rag_eval/corpus/python_notes `
  --limit-files 40

python tools/evals/zuno/rag_eval/ingest_prepared_corpus.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --knowledge-name ZunoPythonEval `
  --text-embedding-model-id <local_embedding_llm_id> `
  --output .local/evals/zuno/rag_eval/runs/ingest-result.json

python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profile-set local_compare `
  --output-dir .local/evals/zuno/rag_eval/runs/<run_id> `
  --trace-langsmith
```

`--text-embedding-model-id` should point at a locally running embedding model that has already been registered in Zuno as an `Embedding` LLM entry. The recommended first-pass comparison is `--profile-set local_compare`, which runs:

- `baseline_rag`
- `rag_rerank`
- `rag_graph_chunk_backed`

If you specifically want to compare GraphRAG hop settings, run:

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profile-set graph_compare `
  --output-dir .local/evals/zuno/rag_eval/runs/<run_id>
```

LangSmith is used for trace replay and profile comparison. The numeric metrics are computed locally from `retrieval_results.jsonl`, `answers.jsonl`, `judge_results.jsonl`, and `metrics.json`.

## One-Command Local Embedding Eval

If you already have a locally running embedding model registered in Zuno as an `Embedding` LLM entry, you can use the end-to-end launcher:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --knowledge-name ZunoLocalEmbeddingEval `
  --text-embedding-model-id <local_embedding_llm_id> `
  --profile-set local_compare
```

This launcher will:

1. validate that the supplied model id is an `Embedding` model
2. ingest the prepared corpus with that embedding model bound into the knowledge config
3. run `RAG` / `GraphRAG` comparison profiles
4. write `summary.json` and `summary.md`

If you do not remember the model id, list candidate models first:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --list-embedding-models `
  --local-only
```

If your local embedding model is already registered in Zuno and its `base_url` points at `localhost`, `127.0.0.1`, or `host.docker.internal`, you can also let the launcher auto-pick it:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --auto-pick-local-embedding `
  --validate-only
```

If the model table is temporarily unavailable or you intentionally want to use the currently active `multi_models.embedding` config, you can fall back to the active config slot directly:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --use-active-config-embedding `
  --validate-only
```

If you have a local OpenAI-compatible embedding endpoint but have not registered it in Zuno yet, you can now pass it directly and let the launcher auto-register a temporary `Embedding` entry:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --local-embedding-model-name bge-m3 `
  --local-embedding-base-url http://127.0.0.1:11434/v1 `
  --validate-only
```

That path is intentionally strict:

- it only accepts `localhost` / `127.0.0.1` / `host.docker.internal` style endpoints as local
- it auto-registers a temporary `Embedding` LLM entry so the existing knowledge runtime can keep using `llm_id`
- it rejects remote endpoints, so the local-eval workflow cannot silently fall back to DashScope or other hosted embedding services

If you do not already have a local embedding service running, the repo now includes a tiny OpenAI-compatible dev server you can start locally:

```powershell
python tools/evals/zuno/rag_eval/local_embedding_server.py `
  --host 127.0.0.1 `
  --port 11434 `
  --model-name zuno-local-embedding-dev
```

Then preflight the local-eval chain against that server:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --local-embedding-model-name zuno-local-embedding-dev `
  --local-embedding-base-url http://127.0.0.1:11434/v1 `
  --validate-only
```

In `--validate-only` mode, Zuno now probes that local endpoint directly and does **not** require the database-backed LLM registry to be up first. The registry step is deferred until you run the full ingest + eval flow.

## Stackless Local Compare

If you want to compare `baseline_rag`, `rag_rerank`, and `rag_graph_chunk_backed` without relying on database-backed knowledge metadata, use the stackless launcher:

```powershell
python tools/evals/zuno/rag_eval/run_stackless_local_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --profile-set local_compare `
  --sample-limit 1 `
  --spawn-dev-embedding-server `
  --spawn-dev-rerank-server `
  --rerank-score-threshold-override 0.0 `
  --output-root .local/evals/zuno/rag_eval/runs/stackless-local-compare
```

This mode:

1. starts an in-process local embedding dev server when requested
2. builds a synthetic knowledge runtime in memory
3. indexes chunks into local Chroma storage
4. injects a local graph retriever instead of depending on Neo4j-backed graph runtime
5. can run `rag_rerank` against a real local rerank dev server instead of fallback ordering
6. lets you override the rerank score threshold when local dev-model score scales differ from production rerank models

Use `--profiles baseline_rag` or `--profiles rag_graph_chunk_backed` when you want to isolate one profile at a time.

If you want one command that produces both `local_compare` and `graph_compare` summary artifacts, use:

```powershell
python tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --sample-limit 3 `
  --local-compare-rerank-threshold-override 0.0 `
  --output-root .local/evals/zuno/rag_eval/runs/stackless-compare-matrix
```

This matrix runner writes:

- `local_compare/report.json`
- `graph_compare/report.json`
- `summary.json`
- `summary.md`

## Contract Review GraphRAG Project Eval

The repo now includes a dedicated contract-review corpus and graph-relation dataset:

- `.local/evals/zuno/rag_eval/corpus/contract_review/manifest.json`
- `tools/evals/zuno/rag_eval/datasets/contract_review_graph_relation_small.jsonl`

Use the same stackless matrix runner, but bind the `contract_review` GraphRAG
Project so GraphRAG uses the structured contract extractor instead of the
generic extractor:

```powershell
python tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py `
  --manifest .local/evals/zuno/rag_eval/corpus/contract_review/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/contract_review_graph_relation_small.jsonl `
  --sample-limit 12 `
  --graphrag-project-id contract_review `
  --chunk-size-override 256 `
  --overlap-override 48 `
  --local-compare-rerank-threshold-override 0.0 `
  --output-root .local/evals/zuno/rag_eval/runs/stackless-contract-review
```

This setup is the fastest way to answer the real architecture question for the contract domain:

1. does structured domain extraction improve relation-heavy retrieval over baseline RAG
2. which contract clause / party / obligation / regulation links are actually helping
3. whether the current corpus is too small and homogeneous to show the next GraphRAG gains

For contract review specifically, smaller clause-level chunks are usually more truthful than generic 1k-character chunks. If the corpus is still collapsing into one chunk per contract, GraphRAG will be under-represented because baseline vector retrieval can win by grabbing the entire document in one shot.

If you want to test whether GraphRAG starts to matter more as the contract corpus gets larger and more confusing, generate a scaled local corpus with synthetic distractor variants:

```powershell
python tools/evals/zuno/rag_eval/generate_contract_review_scale_corpus.py `
  --output-dir .local/evals/zuno/rag_eval/corpus/contract_review_scale `
  --copies-per-file 4
```

Then run the same contract-review matrix against the generated manifest. This is the fastest local way to test the "does domain modeling need larger data volume?" hypothesis without waiting for a real production corpus.

Before launching the full ingest + eval flow, you can run a pure preflight check:

```powershell
python tools/evals/zuno/rag_eval/run_local_embedding_eval.py `
  --manifest .local/evals/zuno/rag_eval/corpus/python_notes/manifest.json `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --text-embedding-model-id <local_embedding_llm_id> `
  --validate-only
```

That preflight will:

1. confirm the model id exists
2. confirm it is typed as `Embedding`
3. send a real embedding probe request before the expensive eval stages begin
4. report all visible embedding candidates, so you can see what the launcher would pick
5. optionally fall back to the active embedding slot config when the DB-side model registry is not the right source of truth
6. optionally auto-register a direct local embedding endpoint for the current run

If the database-backed LLM registry or knowledge-ingest path is unavailable, the full launcher no longer has to fail hard when you are using a direct local embedding endpoint. It will now fall back to the stackless local-eval path and still write `summary.json` / `summary.md`, while reporting `execution_mode = stackless_fallback` in the CLI output.

For stricter answer quality metrics, run:

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag `
  --answer-mode llm `
  --judge-mode llm `
  --trace-langsmith
```

`--answer-mode llm` asks the configured conversation model to answer from retrieved evidence. `--judge-mode llm` asks the configured conversation model to score Faithfulness and Answer Correctness as JSON. If LangSmith is not configured, traces are skipped but local metrics still run.
