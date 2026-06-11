# Public Demo Evidence

## Purpose

This page captures the public-facing evidence that is safe to keep in the repository.
It replaces direct links to ignored local eval-run folders.

## Generic Graph-Relation Benchmark

Dataset scope:

- graph-relation questions
- local compare matrix
- 10 samples

Key result:

| Profile | Recall@5 | MRR@5 | Citation Accuracy |
|---|---:|---:|---:|
| `baseline_rag` | `0.1167` | `0.2000` | `0.1000` |
| `rag_graph_chunk_backed` | `0.3167` | `0.4000` | `0.1667` |

Interpretation:

- GraphRAG already beats baseline on relation-heavy retrieval questions.
- This is the public proof that graph-aware retrieval is not just architectural decoration.

## Contract-Review Scaled Domain Benchmark

Dataset scope:

- contract-review graph-relation questions
- scaled contract corpus
- local compare matrix
- 12 samples

Key result:

| Profile | Recall@5 | MRR@5 | NDCG@5 | Citation Accuracy |
|---|---:|---:|---:|---:|
| `baseline_rag` | `0.3333` | `0.1486` | `0.1931` | `0.3333` |
| `rag_graph_chunk_backed` | `1.0000` | `0.9583` | `0.9692` | `1.0000` |

Interpretation:

- When the contract corpus becomes larger and noisier, domain modeling plus GraphRAG becomes materially more valuable than baseline RAG.
- This is the strongest public proof currently available for the contract-review architecture direction.

## What This Proves

Together, these results support three claims:

1. local embedding-based evaluation is already strong enough to compare retrieval strategies
2. GraphRAG is useful for relation-heavy retrieval, not just for generic text similarity
3. domain modeling matters more as data volume and distractor density increase

## Reproduction

For the reproducible local commands, see:

- [public-demo-runbook.md](./public-demo-runbook.md)
