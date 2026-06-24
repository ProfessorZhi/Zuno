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
- `docs/architecture/audits/real-runtime-multihop-eval-results.md`

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

1. Add tests for Basic, Local, Global, and DRIFT pipeline composition.
2. Prove Basic uses BM25, dense vector, fusion/rerank, evidence check, requery,
   and citations when available.
3. Prove Enhanced trace includes requested method, resolved method, retrievers,
   fallback reason, evidence bundle, and citation coverage.
4. Guard against graph/requery hurting Basic floor.
5. Update docs and eval notes.

## Acceptance Criteria

- Basic is a strong non-graph baseline.
- Local uses graph paths and chunk backlinks.
- Global uses community reports and map-reduce semantics.
- DRIFT uses community primer plus follow-up retrieval.
- Fallback and requery are traceable.
- Tests/evals show no baseline regression.

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
