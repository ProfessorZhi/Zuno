# EnterpriseRAG Paired Benchmark

- status: `blocked`
- measurement_status: `blocked_not_measured`
- runtime_mode: `contract-smoke`
- is_test_double: `true`
- reproduce_command: `poetry run python -m tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark --questions-file tools/evals/zuno/rag_eval/python_notes_eval.jsonl --runtime-mode contract-smoke --sample-size 80 --output-root docs/evidence/goal05-phase22-blocked-benchmark`
- selected_case_count: `8`
- measured_case_count: `0`
- chunk_size_override: `None`
- overlap_override: `None`
- citation_chunking_strategy: `citation_sized_with_parent_context`
- citation_chunk_char_limit: `240`
- parent_context_char_limit: `1200`

| Profile | Measured | Recall@5 | MRR@5 | Answer Correctness | Citation Accuracy | Source Doc Citation | Evidence Text Available | Latency p95 ms | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| standard_rag | false | - | - | - | - | - | - | - | - |
| local_graphrag | false | - | - | - | - | - | - | - | - |
| deep_graphrag | false | - | - | - | - | - | - | - | - |
| agentic_graphrag | false | - | - | - | - | - | - | - | - |

## Agentic Metrics

- graph_usage_gain: `-`
- replan_success_rate: `-`
- cost_quality_ratio: `-`

## Hard Negative Coverage

- status: `incomplete`
- configured_count: `0`
- missing_categories: `same_document_neighbor_wrong_chunk, same_topic_different_document, table_vs_body, header_footer_noise, ocr_noise, multi_document_conflict, graph_summary_requires_source_citation`

| Category | Count | Examples |
|---|---:|---|
| same_document_neighbor_wrong_chunk | 0 |  |
| same_topic_different_document | 0 |  |
| table_vs_body | 0 |  |
| header_footer_noise | 0 |  |
| ocr_noise | 0 |  |
| multi_document_conflict | 0 |  |
| graph_summary_requires_source_citation | 0 |  |

## Release Gate

- status: `blocked_not_measured`
- measured: `false`
- failed_checks: `none`

| Check | Observed | Target | Passed |
|---|---:|---:|---:|

## Blocked

- blocked_reason: `measurement_blocked: dataset case count is insufficient or contains unapproved cases`
- The fixed paired benchmark is not measured until every required profile writes the same fixed case set.

## Agentic GraphRAG

- measured: `false`
- blocked_reason: `dataset_measurement_blocked`

## Failure Tag Limitations

Advanced tags require per-sample graph context, rerank rank trace, no-answer labels, and per-case cost/latency fields. Missing fields are tagged as unavailable_due_to_missing_trace_fields rather than inferred.
