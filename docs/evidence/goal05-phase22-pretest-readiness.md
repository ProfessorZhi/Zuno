# Goal05 / PHASE22 Machine-Executable Preparation & Dry Run Report

- **Current State**: `MACHINE_EXECUTABLE_PREPARATION_COMPLETE` (Measurement Blocked)
- **Branch**: `codex/goal05-phase15-sandbox-repair`
- **Base SHA**: `269bb0b935ab68a02b206c3c77802390e25c1fe0`
- **PHASE22 Status**: `in_progress`
- **Production Readiness**: `implementation available, machine prep complete, measurement blocked, quality not yet proven, production ready not established`

---

## Machine-Executable Preparation & Engineering Summary

1. **Eval Package Contract**:
   - Cleaned all repetitive `sys.path.insert`, `curr.name != "Zuno"`, and dynamic alias injections from `tools/evals/zuno/rag_eval/*.py`.
   - Formed explicit package hierarchy and pyproject packages configuration: `tools`, `src/backend`.
   - CLI Entry module run command: `python -m tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark --help` verified.
   - Verified clean import without global `.pth` files or `PYTHONPATH` injections.

2. **LangSmith Observability Adapter & Tracing**:
   - Implemented `ObservabilityTracePort`, `NoopTraceAdapter`, and `LangSmithTraceAdapter` in `src/backend/zuno/platform/observability/trace_adapter.py`.
   - Wired 18 canonical node types (`AgentRun`, `PlanCreation`, `PlanValidation`, `StepExecution`, `RetrievalRound`, `QueryRewrite`, `BM25`, `Vector`, `Graph`, `Fusion`, `Rerank`, `EvidenceAcceptance`, `ToolInvocation`, `StepAcceptance`, `Replan`, `FinalSynthesis`, `CitationValidation`, `FinalGate`, `RunOutcome`).
   - Enabled fail-open exception handling (`fail_open: true`), sensitive key redaction (`redact_sensitive_data`), field character limits, and configurable sampling.
   - Added unit test suite in `tests/platform/test_langsmith_trace_adapter.py`.

3. **Public Dataset Registry & Real Data Ingestion**:
   - Verified official dataset registry at `tools/evals/zuno/rag_eval/datasets/public_dataset_registry.yaml` with official URLs, licenses (CC-BY-SA 4.0, Apache-2.0, MIT), versions, and checksums.
   - Downloaded real upstream datasets into `.local/eval-datasets/`:
     - HotpotQA (`hotpot_dev_distractor_v1.json`)
     - MultiHop-RAG (`queries.json`, `corpus.json`)
     - Microsoft GraphRAG Benchmarking (`questions.jsonl`)
   - Verification via `verify_public_dataset_cache.py` passed with 0 missing datasets.

4. **Real 80-Case Candidate Review Pack**:
   - Created candidate pack at `docs/evidence/goal05-phase22-public-benchmark-review-pack/` containing 80 real public dataset cases:
     - 32 HotpotQA cases (CC-BY-SA-4.0)
     - 24 MultiHop-RAG cases (Apache-2.0)
     - 24 Microsoft GraphRAG Benchmarking cases (MIT)
   - Zero placeholder questions ("Sample question...") remain.
   - Status tracking:
     - `raw_candidate_count = 80`
     - `reviewer_approved_count = 0`
     - `benchmark_eligible_count = 0`
     - `reviewer_status = pending` for all 80 cases.

5. **Four Profile Runner Wiring & Standard Retrieval Floor**:
   - Implemented profile runners in `tools/evals/zuno/rag_eval/profile_runners.py`: `StandardRAGProfileRunner`, `LocalGraphRAGProfileRunner`, `DeepGraphRAGProfileRunner`, `AgenticGraphRAGProfileRunner`.
   - Wired Standard Retrieval Floor (`agentic_candidates = standard_candidates + graph_candidates + deep_candidates`) with preservation tracking.
   - Added unit test suite in `tests/evals/test_profile_runners.py`.

6. **No-Paid-Model Dry Run**:
   - Implemented and executed `run_dry_run_benchmark.py` on real candidate subset.
   - Output recorded in `docs/evidence/goal05-phase22-dry-run-output/`.
   - Status confirmed: `BLOCKED` (`blocked_not_measured`).

7. **Automated Testing & Repository Gates**:
   - Layer 1 pytest (35 tests) PASSED.
   - Layer 2 pytest (37 tests) PASSED.
   - Layer 3 Repository Gate Verifiers PASSED.

---

## Remaining Blocker for Formal Benchmark

Formal measurement is blocked strictly on:
1. Human Reviewer Approval of 80 real candidate cases (`reviewer_approved_count=0`).
2. Paid Model Credentials & Budget Authorization.
