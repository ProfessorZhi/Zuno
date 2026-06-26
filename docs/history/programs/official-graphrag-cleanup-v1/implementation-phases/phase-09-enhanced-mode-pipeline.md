# Phase 09: Enhanced Mode Pipeline

## Goal

Implement Enhanced Mode as a complete query pipeline, not a single graph
retriever.

## Why This Phase Exists

Current retrieval already has planner, orchestrator, fusion, graph, community,
drift-like, and requery pieces. The target needs an explicit pipeline and proof.

## Required Reading

- Phase 08 evidence package
- `.agent/architecture/near-term/12-enhanced-mode-pipeline.md`
- `docs/history/audits/real-runtime-multihop-eval-results.md`

## Scope

Auto router, query rewrite, multi-retriever recall, fusion/RRF, rerank,
evidence check, conditional requery, citation answer, fallback trace, and tests.

## Non-goals

- new frontend UI
- default multi-agent behavior
- independent GraphRAG service

## Candidate Files

- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/retrieval/retrievers.py`
- `src/backend/zuno/services/rag/handler.py`
- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `tests/test_enhanced_retrieval_composition.py`
- `tests/test_enhanced_requery_activation.py`
- `tests/test_enhanced_requery_precision_gate.py`
- `tests/test_enhanced_standard_floor_invariance.py`

## Execution Order

1. Added tests for Basic, Local, Global, and DRIFT pipeline composition.
2. Proved Basic uses BM25, dense vector, fusion/rerank, evidence check, and
   citations when available.
3. Proved Enhanced trace includes requested method, resolved method,
   retrievers, fallback reason, evidence bundle, and citation coverage.
4. Preserved graph/requery standard-floor guards.
5. Updated docs and eval notes.

## Implemented Pipeline Trace

`RetrievalOrchestrator` now exposes:

- `pipeline_trace`
- `evidence_bundle`
- `citation_coverage`
- `retrievers_used`

`pipeline_trace.steps` records these stable steps:

1. `query_method_router`
2. `query_rewrite`
3. `multi_retriever_recall`
4. `fusion`
5. `rerank`
6. `evidence_check`
7. `conditional_requery`
8. `citation_answer`

The trace is assembled from the existing runtime components rather than a new
service boundary. That keeps Phase 09 scoped to proof and contract hardening,
not a runtime rewrite.

## Query Method Coverage

- Explicit `query_method=basic` keeps Enhanced mode on the strong standard
  pipeline and prevents graph/community route activation.
- `auto` relation questions resolve to `local` and include vector, BM25, and
  graph recall when available.
- `auto` global evidence questions resolve to `drift` when graph and community
  assets are ready.
- Unavailable graph/community assets remain visible through fallback trace from
  Phase 08.

## Evidence And Citation Contract

`evidence_bundle` records document count, source types, chunk ids, citation
chunks, cited document count, and citation coverage. This makes citation proof
available to tests and eval diagnostics without requiring frontend changes.

## Acceptance Criteria

- Basic is a strong non-graph baseline.
- Local uses graph paths and chunk backlinks.
- Global uses community reports and map-reduce semantics.
- DRIFT uses community primer plus follow-up retrieval.
- Fallback and requery are traceable.
- Tests/evals show no baseline regression.

Status: satisfied for the backend pipeline trace contract and existing
baseline-preserving gates. No new broad real-runtime eval was run in this
phase; the current eval note remains the existing W8 evidence plus this trace
contract hardening.

## Verification Commands

```powershell
pytest -q tests/test_enhanced_retrieval_composition.py
pytest -q tests/test_enhanced_requery_activation.py
pytest -q tests/test_enhanced_requery_precision_gate.py
pytest -q tests/test_enhanced_standard_floor_invariance.py
python tools\scripts\verify_docs_entrypoints.py
git diff --check
```

## GitHub Sync Requirements

Before editing:

```powershell
git branch --show-current
git status --short
git log -1 --oneline
```

Before commit:

```powershell
git status --short
git diff --stat
git diff --check
```

After validation passes:

```powershell
git add src/backend/zuno tests docs .agent tools
git commit -m "feat: complete enhanced mode pipeline"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Enhanced Mode hurts standard retrieval floor.
- Trace cannot prove evidence and citation coverage.
- DRIFT requires future worker architecture.

## Evidence Package Required

- pipeline step proof
- Basic floor proof
- trace field examples
- test/eval output
- commit hash and push result

## Risks

- Treating Enhanced Mode as graph-only.
- Adding broad behavior without a focused baseline-preserving gate.

## Follow-up Phase

Phase 10: Frontend API Contract Migration.
