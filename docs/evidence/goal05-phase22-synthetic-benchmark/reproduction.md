# Reproduction Guide — PHASE22 Synthetic Enterprise Benchmark

This document explains how to reproduce every artifact in
`docs/evidence/goal05-phase22-synthetic-benchmark/` deterministically from
the generation scripts.

## Required tools

- Python >= 3.10 (validated against CPython 3.12)
- No third-party packages required for generation; only the standard library
- The validator, hash functions, and JSON loaders use `hashlib`, `json`,
  `pathlib`, `re`, and `difflib`.

## Step 0 — clean working tree

```bash
git status
# Expect: nothing to commit, working tree clean
```

## Step 1 — build the world model and corpus

```bash
python docs/evidence/goal05-phase22-synthetic-benchmark/build_world_model.py \
    --out-root docs/evidence/goal05-phase22-synthetic-benchmark
```

Expected output (exact):

```
world_model_sha256=<64 hex chars>
corpus_manifest_sha256=<64 hex chars>
graph_manifest_sha256=<64 hex chars>
document_count=62
relation_count=92
```

## Step 2 — build the 80-case benchmark

```bash
python docs/evidence/goal05-phase22-synthetic-benchmark/build_cases.py \
    --out-root docs/evidence/goal05-phase22-synthetic-benchmark
```

Expected output:

```
stratification: {'single_doc_fact': 20, 'multi_hop': 20, 'graph_path': 6,
                  'graph_relation': 6, 'graph_community': 3,
                  'temporal_version': 6, 'temporal_conflict': 4,
                  'no_answer': 5, 'permission_restricted': 4,
                  'permission_deny': 1, 'fault_partial_index': 5}
case_set_sha256=<64 hex chars>
```

## Step 3 — run the deterministic machine validator

```bash
python docs/evidence/goal05-phase22-synthetic-benchmark/validate_cases.py \
    --out-root docs/evidence/goal05-phase22-synthetic-benchmark
```

Expected output:

```
verdict=PASSED passed=80 failed=0 duplicates=0 leaks=0
```

## Step 4 — wire Zuno runtime and run the four canonical profiles

```bash
python docs/evidence/goal05-phase22-synthetic-benchmark/ingest_and_run.py \
    --out-root docs/evidence/goal05-phase22-synthetic-benchmark
```

Expected output:

- `runtime_ingestion.json` (KnowledgeVersion + Snapshot evidence)
- `profile_results/standard_rag.json`
- `profile_results/local_graphrag.json`
- `profile_results/deep_graphrag.json`
- `profile_results/agentic_graphrag.json`
- `core_five_metrics.json`
- `release_decision.json`

When the local ES / Milvus / Neo4j services are not running, the script
will mark each profile `BLOCKED`/`blocked_not_measured` and the release
decision will reflect that — without inventing any MEASURED value.

## Step 5 — rebuild sha256 ledger

The validator script writes `validation_report.json` and the runtime script
writes `runtime_ingestion.json`, `core_five_metrics.json`, and
`release_decision.json`. SHA-256 hashes for each artifact are recorded
inside `case_set_manifest.json` (case set hash), `derived/corpus_hashes.json`
(corpus hashes), and the run scripts themselves.

## Reproducibility invariants

- World model and corpus are byte-identical across reruns.
- Case set is byte-identical across reruns.
- Validator verdict is reproducible (PASSED, passed=80, failed=0).
- Runtime profile results are bound to the actual ingest state — when
  Elasticsearch/Milvus/Neo4j are unreachable, profiles are correctly
  BLOCKED; the script never fabricates MEASURED.

## Seed

`phase22-synthetic-2026-08-03-auroralis-v1`

The same seed reproduces the same hashes. Changing the seed regenerates
a fully different fictional enterprise (entities, relations, corpus,
cases) but preserves the stratification contract (20/20/15/10/5/5/5).