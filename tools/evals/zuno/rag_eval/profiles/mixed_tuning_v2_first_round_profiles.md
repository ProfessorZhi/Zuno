# mixed_tuning_v2 First Round Profiles

## Goal

Use `F:\resume project\03_rag_eval_dataset\prepared\mixed_tuning_v2` to compare three first-round retrieval modes without assuming GraphRAG is globally better:

1. `baseline_rag`: pure RAG.
2. `rag_rerank`: RAG + rerank.
3. `rag_graph`: RAG + GraphRAG.

The first run should report the same five metrics for every profile:

- `Recall@K`
- `Context Precision@K`
- `MRR@K`
- `NDCG@K`
- `Citation Accuracy`

Use `K=5` for the first pass because the current `metrics.py` defaults to `k=5` and `EVAL_PLAN.md` already anchors the first round on `@5`.

## Dataset

- Corpus root: `F:\resume project\03_rag_eval_dataset\prepared\mixed_tuning_v2`
- Golden questions: `tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_eval_draft.jsonl`
- Question count: 48
- Must slice results by `question_type`, especially `graph_relation`.

## Profiles

| Profile | Purpose | Retrieval mode | Chunk strategy | Top K | Rerank | Graph settings |
| --- | --- | --- | --- | ---: | --- | --- |
| `baseline_rag` | Pure RAG baseline | `rag` | `general` | 5 | off | none |
| `rag_rerank` | Strong lexical/vector baseline | `rag` | `general` | 5 | on, `rerank_top_k=3` | none |
| `rag_graph` | GraphRAG candidate | `rag_graph` | `parent_child` preferred | 5 | on, `rerank_top_k=3` | `graph_hop_limit=2`, `max_paths_per_entity=5` |

## Suggested Concrete Settings

```json
{
  "k": 5,
  "profiles": {
    "baseline_rag": {
      "retrieval_mode": "rag",
      "retrieval_options": {
        "top_k": 5,
        "rerank_enabled": false,
        "rerank_top_k": 5,
        "score_threshold": null,
        "needs_query_rewrite": false
      }
    },
    "rag_rerank": {
      "retrieval_mode": "rag",
      "retrieval_options": {
        "top_k": 5,
        "rerank_enabled": true,
        "rerank_top_k": 3,
        "score_threshold": 0.7,
        "needs_query_rewrite": true
      }
    },
    "rag_graph": {
      "retrieval_mode": "rag_graph",
      "retrieval_options": {
        "top_k": 5,
        "rerank_enabled": true,
        "rerank_top_k": 3,
        "score_threshold": 0.7,
        "graph_hop_limit": 2,
        "max_paths_per_entity": 5,
        "needs_query_rewrite": true
      }
    }
  }
}
```

## First-Pass Decision Rule

Do not select by overall score only.

1. If `rag_graph` improves `graph_relation` but hurts `fact` or `summary`, keep it as a targeted advanced mode.
2. If `rag_graph` improves overall and does not degrade non-graph types, promote it into the large-sample candidate.
3. If `rag_rerank` beats `rag_graph` overall and on `graph_relation`, skip 3-hop until the knowledge graph extraction quality is inspected.

## Run Suggestions

Import the prepared corpus first:

```powershell
python tools/evals/zuno/rag_eval/ingest_prepared_corpus.py `
  --manifest "F:\resume project\03_rag_eval_dataset\prepared\mixed_tuning_v2\sample_manifest.csv" `
  --knowledge-name ZunoMixedTuningV2 `
  --output .local/evals/zuno/rag_eval/runs/mixed_tuning_v2_ingest_result.json
```

Then run the three-profile comparison:

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_eval_draft.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag,rag_rerank,rag_graph `
  --output-dir .local/evals/zuno/rag_eval/runs/<timestamp> `
  --trace-langsmith
```

Before relying on the ingest command above, verify whether `ingest_prepared_corpus.py` expects a JSON manifest or can read this CSV manifest. If it only accepts the older JSON shape, add a tiny converter instead of editing the source dataset.
