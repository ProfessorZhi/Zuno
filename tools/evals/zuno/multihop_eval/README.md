# Zuno Multi-hop Eval Preparation

This folder prepares HotpotQA, 2WikiMultiHopQA, and MuSiQue for Zuno retrieval
evaluation.

Phase C scope:

- dataset download helpers
- dataset adapters
- normalized JSONL schema
- small committed sample fixtures
- offline adapter smoke tests

Phase C does **not** run full GraphRAG evaluation and does not commit raw or
full normalized datasets.

Phase D adds a mocked smoke runner for report-shape validation. It is useful for
CLI flow and artifact checks, not for claiming real GraphRAG quality.

Phase E adds the first real runtime multihop retrieval standard. The committed
standard lives in:

```text
docs/architecture/audits/real-runtime-multihop-eval-standards.md
```

Its core rule is simple:

- round 1 is retrieval-only real runtime eval
- Answer EM / F1 are not primary closure metrics yet
- mocked, stackless, and real_runtime results must never be mixed

## Explicit Eval Profiles

Current status:

- this folder now includes `eval_profiles.example.json`
- the file is a committed example, not a secret-bearing local config
- it uses model names, not DB ids
- current mocked runner does not fully consume `--profile-file` / `--profile-name` yet

Why this exists:

- real multihop eval should not depend on ambiguous default slot resolution
- especially do not rely on implicit `conversation_model` when local DB state may
  contain duplicate active defaults
- text-only multihop eval should explicitly name conversation, text embedding,
  and rerank models

Recommended rule for future real eval:

1. pass an explicit eval profile file
2. select one named profile for the run
3. resolve model names into current registry rows at runtime
4. fail early if a required named model cannot be resolved cleanly

Current example file:

```text
tools/evals/zuno/multihop_eval/eval_profiles.example.json
```

The first example profile is the recommended baseline for upcoming real
HotpotQA / 2Wiki / MuSiQue text-only retrieval work:

- conversation model: `qwen-plus`
- text embedding model: `text-embedding-v4`
- VL embedding model: `null`
- rerank model: `gte-rerank-v2`

For lower-cost answer generation experiments, the example also includes:

- conversation model: `deepseek-v4-flash`

This example file must never include:

- API keys
- database primary keys
- local database dumps

## Normalized Schema

```json
{
  "dataset": "hotpotqa | 2wikimultihopqa | musique",
  "id": "...",
  "question": "...",
  "answer": "...",
  "documents": [
    {
      "doc_id": "...",
      "title": "...",
      "sentences": ["..."],
      "text": "..."
    }
  ],
  "gold_support": [
    {
      "title": "...",
      "sent_id": 0,
      "text": "..."
    }
  ],
  "gold_entities": [],
  "gold_evidence_path": [],
  "metadata": {}
}
```

## Download Commands

```powershell
python tools/evals/zuno/multihop_eval/download_datasets.py --dataset hotpotqa --split dev --sample 50
python tools/evals/zuno/multihop_eval/download_datasets.py --dataset twowiki --split dev --sample 50
python tools/evals/zuno/multihop_eval/download_datasets.py --dataset musique --split dev --sample 50
```

Raw files are written under:

```text
data/evals/multihop/raw/
```

Normalized files are written under:

```text
data/evals/multihop/normalized/
```

Benchmark corpus files are written under:

```text
data/evals/multihop/corpus/
```

Temporary ingestion manifests can be written under:

```text
data/evals/multihop/ingested/
```

All four directories are gitignored.

## Sources

- HotpotQA: official HotpotQA download links for `hotpot_dev_distractor_v1.json`
  and `hotpot_dev_fullwiki_v1.json`:
  `http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json`
  and `http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_fullwiki_v1.json`.
- 2WikiMultiHopQA: official `Alab-NII/2wikimultihop` README link for
  `data_ids_april7.zip`:
  `https://www.dropbox.com/s/ms2m13252h6xubs/data_ids_april7.zip`.
- MuSiQue: official `stonybrooknlp/musique` `download_data.sh` Google Drive id
  for `musique_v1.0.zip`: `1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h`.

If a network download fails, the downloader exits with a clear error. It does
not fabricate data or mark a failed download as successful.

## Offline Smoke Fixtures

Committed sample fixtures live in:

```text
tools/evals/zuno/multihop_eval/sample_data/
```

These are tiny normalized JSONL files for adapter tests and stackless smoke
work. They are not benchmark results.

## Benchmark Corpus Ingestion

Phase I adds benchmark corpus preparation for future real runtime evaluation.

Current ingestion tools:

- `ingestion/build_corpus.py`
- `ingestion/stackless_index.py`
- `ingestion/ingest_to_knowledge.py` placeholder

`build_corpus.py` converts normalized multihop records into per-document corpus
rows with:

- `question_id`
- `doc_id`
- `is_gold`
- `gold_sent_ids`

`stackless_index.py` validates that the resulting corpus can be consumed by a
deterministic local retrieval flow. Its report must always be treated as:

- execution mode: `stackless`
- purpose: ingestion smoke only
- not a real GraphRAG runtime result

## Real Runtime Retrieval Metrics

Round 1 real runtime multihop eval uses retrieval-only metrics:

- `Recall@2/5/10`
- `Precision@5/10`
- `MRR@10`
- `ChainRecall@5/10`
- `FullChainHit@5/10`
- latency / failure / fallback metrics

These metrics are shared across future real runtime runners so that:

- HotpotQA / 2Wiki / MuSiQue use the same aggregation rules
- failure and fallback are visible instead of hidden
- graph-unavailable downgrade cases are recorded explicitly

Answer-generation metrics remain out of the primary closure gate for this first
real runtime round.

## Smoke Runner

Phase D exposes:

```powershell
python tools/evals/zuno/multihop_eval/run_multihop_eval.py --dataset hotpotqa --mode baseline_rag
python tools/evals/zuno/multihop_eval/run_multihop_eval.py --dataset hotpotqa --mode local_graphrag
python tools/evals/zuno/multihop_eval/run_multihop_eval.py --dataset hotpotqa --mode deep_graphrag
```

Current runner status:

- execution mode: `mocked`
- purpose: sample-data smoke and report-shape validation
- not a real GraphRAG benchmark

It writes per-mode reports plus:

```text
reports/evals/multihop/compare_matrix.json
```

The report explicitly labels itself as `mocked`, so it cannot be mistaken for a
real GraphRAG result.

Future real runtime output must instead:

- use `execution_mode = "real_runtime"`
- record runtime fallback / failure
- avoid Answer EM / F1 as the main headline metrics for round 1

## Future Runner Wiring

The intended next integration path is:

1. add `--profile-file`
2. add `--profile-name`
3. resolve named models before launching real multihop retrieval/eval
4. keep current mocked runner behavior unchanged until real multihop runtime is
   intentionally enabled

Until that wiring lands, treat `eval_profiles.example.json` as the source of
truth for how future real multihop runs should bind models explicitly.
