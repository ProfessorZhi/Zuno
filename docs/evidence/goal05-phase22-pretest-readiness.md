# Goal05 / PHASE22 Pre-Test Readiness Report

- **Current State**: `PRE_TEST_READY`
- **Branch**: `codex/goal05-phase15-sandbox-repair`
- **Base SHA**: `269bb0b935ab68a02b206c3c77802390e25c1fe0`
- **PHASE22 Status**: `in_progress`
- **Production Readiness**: `implementation available, pre-test ready, measurement blocked, quality not yet proven, production ready not established`

---

## Pre-Test Engineering Prep Summary

1. **Eval Package Contract**:
   - Cleaned all repetitive `sys.path.insert`, `curr.name != "Zuno"`, and dynamic alias injections from `tools/evals/zuno/rag_eval/*.py`.
   - Formed explicit package hierarchy: `tools/__init__.py`, `tools/evals/__init__.py`, `tools/evals/zuno/__init__.py`, `tools/evals/zuno/rag_eval/__init__.py`.
   - CLI Entry module run command: `python -m tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark --help` verified.
   - Removed global `.pth` dependency (`E:\develop\Python312\Lib\site-packages\__zuno_backend_src_backend__.pth` backed up to `F:\internship-work\__zuno_backend_src_backend__.pth.backup` and removed).

2. **LangSmith Observability Adapter**:
   - Implemented `ObservabilityTracePort`, `NoopTraceAdapter`, and `LangSmithTraceAdapter` in `src/backend/zuno/platform/observability/trace_adapter.py`.
   - Enabled fail-open exception handling (`fail_open: true`), sensitive key redaction (`redact_sensitive_data`), field character limits, and configurable sampling.
   - Default state: `langsmith.enabled: false`.

3. **Public Dataset Registry & Cache**:
   - Created dataset registry at `tools/evals/zuno/rag_eval/datasets/public_dataset_registry.yaml` for Microsoft GraphRAG Benchmarking, HotpotQA, and MultiHop-RAG.
   - Added download script `download_public_datasets.py` and cache verifier `verify_public_dataset_cache.py`.

4. **80-Case Candidate Review Pack**:
   - Created review pack at `docs/evidence/goal05-phase22-public-benchmark-review-pack/`.
   - Includes: `README.md`, `candidate_cases.jsonl`, `review_sheet.csv`, `source_manifest.json`, `coverage_report.json`, `duplicate_report.json`, `license_report.md`, `approval_summary.json`.
   - Metrics:
     - `raw_candidate_count = 80`
     - `reviewer_approved_count = 0`
     - `benchmark_eligible_count = 0`
     - `approval_required = true`

5. **Four Profile Runner Wiring**:
   - Configured and wired runners for `standard_rag`, `local_graphrag`, `deep_graphrag`, `agentic_graphrag`.
   - Standard retrieval gold evidence floor preservation ensured.

6. **Pre-Verification Contract Coverage**:
   - Created structural boundary test `tests/repo/test_phase22_eval_package_contract.py` and registered in `tools/scripts/verify_phase22_cleanup_boundary.py`.
