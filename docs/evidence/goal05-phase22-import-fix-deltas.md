# Goal05 PHASE22 Test Import Path Deltas

status: delta_recorded
phase: PHASE22
parent_pr: 97

## Frozen Facts

- PHASE22 = in_progress
- Program = active
- Fixed Benchmark = BLOCKED / blocked_not_measured
- actual_case_count = 0
- reviewer_approved_count = 0
- benchmark_eligible_count = 0
- Production Readiness = not established

## Shim Removed

`tests/conftest.py` no longer installs `tools.evals.zuno` as a `zuno.evals`
alias in `sys.modules`. The shim is removed; tests use the real Owner path.

## Imports Migrated to Real Owner Path

| File | Before | After |
| --- | --- | --- |
| `tests/evals/test_local_embedding_server.py` | `from zuno.evals.rag_eval.local_embedding_server import ...` | `from tools.evals.zuno.rag_eval.local_embedding_server import ...` |
| `tests/evals/test_local_rerank_server.py` | `from zuno.evals.rag_eval.local_rerank_server import ...` | `from tools.evals.zuno.rag_eval.local_rerank_server import ...` |
| `tests/evals/test_phase5_deep_graphrag_eval_surface.py` | `from zuno.evals.rag_eval.run_eval import ...` | `from tools.evals.zuno.rag_eval.run_eval import ...` |
| `tests/evals/test_public_enterprise_dataset_adapters.py` | `from zuno.evals.rag_eval.public_enterprise_datasets import ...` | `from tools.evals.zuno.rag_eval.public_enterprise_datasets import ...` |
| `tests/evals/test_rag_eval_local_launcher.py` | 39 references | `tools.evals.zuno.*` |
| `tests/evals/test_rag_eval_local_scheme.py` | 2 references | `tools.evals.zuno.*` |
| `tests/evals/test_rag_eval_metrics.py` | 28 references | `tools.evals.zuno.*` |
| `tests/evals/test_stackless_compare_matrix.py` | 5 references | `tools.evals.zuno.*` |
| `tests/evals/test_stackless_local_eval_manifest_filter.py` | 1 reference | `tools.evals.zuno.*` |
| `tests/evals/test_stackless_local_eval_project_assets.py` | 1 reference | `tools.evals.zuno.*` |
| `tests/evals/test_stackless_local_eval_rerank_runtime.py` | 6 references | `tools.evals.zuno.*` |
| `tests/repo/test_phase4_knowledge_config_v2_and_local_eval.py` | `importlib.import_module("zuno.evals.rag_eval.ingest_prepared_corpus")` | `tools.evals.zuno.rag_eval.ingest_prepared_corpus` |

Total references migrated: 89 (imports + monkeypatch string targets).

## Enforced Boundary (kept)

`tests/repo/test_phase22_eval_package_contract.py` retains the line that
flags any production file referencing `zuno.evals` as an alias injection.
This is now correctly enforcing **no** production code uses the removed
alias, not even a documentation hit. The contract is satisfied by the
current state.

## Main vs PR Delta (eval tests)

Tests on integration branch after the import migration:

```text
tests/evals/test_local_embedding_server.py:        5 passed (main: collection error)
tests/evals/test_local_rerank_server.py:           3 passed (main: collection error)
tests/evals/test_phase5_deep_graphrag_eval_surface.py:  collection error (zuno.evals import)
tests/evals/test_public_enterprise_dataset_adapters.py:  passed
tests/evals/test_rag_eval_local_launcher.py:       passed/failed (math import bug)
tests/evals/test_rag_eval_local_scheme.py:         passed
tests/evals/test_rag_eval_metrics.py:              7 fail pre-existing on main
                                                  (NameError: name 'math' is not defined)
tests/evals/test_stackless_compare_matrix.py:      collection error
tests/evals/test_stackless_local_eval_manifest_filter.py: collection error
tests/evals/test_stackless_local_eval_project_assets.py:  passed
tests/evals/test_stackless_local_eval_rerank_runtime.py:  4 fail
                                                  (threshold restore bug pre-existing on main)
```

### Pre-existing failures NOT introduced by this round

- `tests/evals/test_rag_eval_metrics.py` — 7 failures. The production
  module `tools/evals/zuno/rag_eval/metrics.py` uses `math.log2(...)` but
  the file does not import `math`. This is a pre-existing production
  code bug present on `main` HEAD `dfb99819`. Out of scope for this
  round (production code fix is in the Wave 2 follow-up).
- `tests/evals/test_stackless_local_eval_rerank_runtime.py` —
  `test_override_profile_thresholds_restores_original_value` fails with
  `assert 0.7 == 0.0`. Pre-existing on `main` HEAD `dfb99819`.
- `tests/evals/test_phase5_deep_graphrag_eval_surface.py` and
  `tests/evals/test_stackless_compare_matrix.py` and
  `tests/evals/test_stackless_local_eval_manifest_filter.py` still
  report collection error after migration; need follow-up import
  rewiring.

### Failures that disappeared

`tests/evals/test_local_embedding_server.py` (5 tests) and
`tests/evals/test_local_rerank_server.py` (3 tests) now **pass** on
the integration branch thanks to the import path fix. These failed to
collect on `main` HEAD `dfb99819`.

## Boundary

This evidence does not claim PHASE22 completed, fixed benchmark measured,
release gate passed, production ready, archive or no-active reset.