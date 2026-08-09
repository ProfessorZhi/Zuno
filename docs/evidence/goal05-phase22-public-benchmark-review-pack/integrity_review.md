# Benchmark Candidate Pack Integrity Review

**Generated**: 2026-08-09T18:27:33.337007+00:00
**Validator**: v1.0.0
**Schema**: v1.0.0
**Overall Status**: **REVIEW_REQUIRED**

## Summary

| Metric | Value |
|---|---|
| Total Cases | 80 |
| VERIFIED | 80 |
| INCOMPLETE | 0 |
| UNVERIFIABLE | 0 |
| INVALID | 0 |
| Evidence Complete | 80 |
| Exact Duplicates | 0 |
| Near Duplicates | 0 |
| License Verified | 80 |
| License Pending | 0 |
| Source ID Verified | 80 |
| Reviewer Approved | 0 |
| Benchmark Eligible | 0 |

## Dataset Slices

| Slice | Count |
|---|---|
| snapshot_global_summary_textbook_corpus | 24 |
| snapshot_graph_reasoning_slice | 24 |
| snapshot_multihop_fact_slice | 32 |

## Findings by Rule

| Rule | Violation Count |
|---|---|
| rule_14 | 80 |
| rule_5 | 48 |
| rule_6 | 24 |

## Duplicate Analysis

- Near-duplicate threshold (Jaccard): 0.8
- Exact duplicate pairs: 0
- Near duplicate pairs: 0

## Notes

- HotpotQA records use the upstream `_id`/`id` when available; MultiHop-RAG and GraphRAG-Bench retain deterministic adapter IDs plus an upstream line ref where the source does not publish a record ID.
- MultiHop-RAG selection requires a nonempty upstream `evidence_list`; the fixed slice therefore contains only evidence-complete records.
- GraphRAG-Bench selection requires an exact case-folded question match in the cached official textbook corpus; evidence refs carry the source file and line span.
- The candidate pack has 80 evidence-complete cases and 0 incomplete cases.
- Provenance remains a compact string for backward schema compatibility; the selection rule and GraphRAG corpus hashes are recorded in `source_manifest.json`.
- `reviewer_approved_count` = 0; `benchmark_eligible_count` = 0 (blocked on human review).
