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

Both directories are gitignored.

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
