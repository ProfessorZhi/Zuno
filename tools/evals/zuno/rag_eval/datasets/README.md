# Public Benchmark Dataset Registry & Adapters

This package contains public benchmark dataset registration, local caching, and verification adapters for Zuno Goal05 / PHASE22.

## Modules

- `public_dataset_registry.yaml`: Registration of official public benchmark datasets (Microsoft GraphRAG Benchmarking, HotpotQA, MultiHop-RAG).
- `download_public_datasets.py`: Script to generate download plans and securely manage dataset caching in `.local/eval-datasets/`.
- `verify_public_dataset_cache.py`: Script to verify local dataset cache integrity against expected SHA256 checksums.

## Usage

```powershell
# Generate download plan
python -m tools.evals.zuno.rag_eval.datasets.download_public_datasets --dry-run

# Verify dataset cache
python -m tools.evals.zuno.rag_eval.datasets.verify_public_dataset_cache
```
