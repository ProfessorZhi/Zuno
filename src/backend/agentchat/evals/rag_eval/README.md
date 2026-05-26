# Zuno RAG Evaluation

This folder contains the local RAG / GraphRAG evaluation harness used to compare retrieval settings.

## What Is Committed

- `python_notes_eval.jsonl`: small query -> gold evidence dataset.
- `metrics.py`: offline metric calculator.
- `prepare_python_notes_corpus.py`: copies a local note folder into an ignored evaluation corpus.
- `ingest_prepared_corpus.py`: imports a prepared corpus into a Zuno knowledge base.
- `run_eval.py`: runs retrieval profiles and writes metrics/reports.

Generated corpora and eval runs are ignored by git:

- `corpus/`
- `runs/`

## Metrics

- Retrieval Recall: whether required evidence is found in top-k contexts.
- Context Precision: whether retrieved contexts are relevant and clean.
- Faithfulness: read from judge results, measuring whether answers are grounded in retrieved evidence.
- Answer Correctness: read from judge results, measuring answer quality against a reference answer.
- Citation Accuracy: whether citations actually match gold evidence.

## Typical Local Flow

```powershell
python src/backend/agentchat/evals/rag_eval/prepare_python_notes_corpus.py `
  --source "F:\Onboard anything\02_Notes_笔记\2llm_note\Python" `
  --output-dir src/backend/agentchat/evals/rag_eval/corpus/python_notes `
  --limit-files 40

python src/backend/agentchat/evals/rag_eval/ingest_prepared_corpus.py `
  --manifest src/backend/agentchat/evals/rag_eval/corpus/python_notes/manifest.json `
  --knowledge-name ZunoPythonEval `
  --output src/backend/agentchat/evals/rag_eval/runs/ingest-result.json

python src/backend/agentchat/evals/rag_eval/run_eval.py `
  --dataset src/backend/agentchat/evals/rag_eval/python_notes_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag,rag_rerank,rag_graph `
  --output-dir src/backend/agentchat/evals/rag_eval/runs/<run_id> `
  --trace-langsmith
```

LangSmith is used for trace replay and profile comparison. The numeric metrics are computed locally from `retrieval_results.jsonl`, `answers.jsonl`, `judge_results.jsonl`, and `metrics.json`.
