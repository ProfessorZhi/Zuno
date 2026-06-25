# Tests Folder Organization Audit

Program: GraphRAG Eval Preparation Program

Phase: B - Tests Folder Organization Audit

Scope: audit only. No test files were moved in this phase.

Baseline commit before this audit: `3b8bc41 Audit current model and retrieval config surface`.

Status: History. This audit describes the test tree at the time it was written.
The former `tests/compat/` holding area has since been retired; current
migration compatibility coverage lives in root `tests/`.

## Evidence Sources

Audited paths:

- `tests/`
- `tests/compat/`
- `tests/compat/README.md`
- `pytest.ini` / `pyproject.toml` when present

Observed counts at audit time:

- total Python test/helper files under `tests/`: 135
- Python files under `tests/compat/`: 92
- root-level Python test files: 43
- root-level `test_phase*.py`: 23
- root-level `test_hardening*.py`: 2
- root-level product wiring/product skeleton tests: 2
- root-level eval/domain/GraphRAG related tests by filename: 10

## Current Directory Shape

```text
tests/
  compat/
    README.md
    conftest.py
    test_a2a/
    test_*.py
  test_docs_entrypoints.py
  test_domain_pack_api_skeleton.py
  test_frontend_*.py
  test_hardening*.py
  test_phase*.py
  test_product_wiring_v1_api_contract.py
  test_*.py
```

There is no root-level `tests/README.md` yet.

`tests/compat/README.md` already explains that compat tests keep repo-level
runtime regression checks outside the runtime package.

## Current Test Families

| Family | Current location | Examples | Current role | Move now? |
|---|---|---|---|---|
| Docs / public entrypoint tests | root | `test_docs_entrypoints.py`, `test_history_overview_and_branding.py`, `test_publish_boundary.py` | Protect current docs front path and publish boundary | No |
| Repo structure / runtime guard tests | root | `test_repo_structure_consistency.py`, `test_zuno_runtime_chain_guard.py`, `test_zuno_public_entrypoints.py` | Guard `src/backend/zuno` runtime truth and retired service roots | No |
| Phase tests | root | `test_phase0_runtime_recovery.py` through `test_phase6_agent_graphrag_pluginization.py` | Historical phase completion proof | No |
| Hardening tests | root | `test_hardening01_community_runtime_contract.py`, `test_hardening01_config_impact_contract.py` | Regression proof for specific hardening rounds | No |
| Product wiring tests | root | `test_phase1_knowledge_product_skeleton.py`, `test_product_wiring_v1_api_contract.py` | Product flow/API contract proof | No |
| Frontend static/snapshot tests | root | `test_frontend_model_page.py`, `test_frontend_workspace_features.py`, `test_ui_review_html_exports.py` | Static checks for routes, UI copy, exported snapshots | No |
| Eval tests | root and compat | `test_phase5_deep_graphrag_eval_surface.py`, compat `test_rag_eval_*`, `test_stackless_*` | Eval profile, metrics, stackless runner checks | No |
| Compatibility runtime tests | `tests/compat/` | `test_retrieval_planner.py`, `test_rag_eval_metrics.py`, `test_workspace_*` | Runtime regression checks and legacy-adjacent compatibility guards | No |
| Fixtures/helpers | scattered under compat/root helpers | `tests/compat/test_a2a/*` | Test-only helper modules | No |

## Phase Tests

Root-level phase tests are not just ordinary unit tests. They are architecture
closure evidence for prior completed phases. Moving them now would blur the
history-to-current-truth relationship unless references in docs and verification
scripts are updated together.

Recommendation: keep phase tests in place until a dedicated test migration
phase updates docs, pytest selection, and any README references together.

## Compat Tests

`tests/compat/` is already a meaningful boundary. It contains:

- runtime import compatibility checks
- retrieval planner/orchestrator checks
- RAG eval metrics and launcher checks
- stackless local eval checks
- workspace/session/runtime checks
- manual compatibility probes controlled by `ZUNO_RUN_MANUAL_COMPAT`

Recommendation: keep `tests/compat/` intact for now. It can later become the
source for a cleaner split, but moving files out of it before marker coverage
would create churn without improving eval readiness.

## Hardening Tests

Hardening tests are root-level because they are tied to recent closure gates.
They should stay root-level until there is a `tests/hardening/README.md` and a
pytest marker plan.

Recommendation: do not move in Phase B.

## Product Wiring Tests

Product tests currently sit at root because Product Wiring V1 is new and closely
connected to docs and frontend route checks.

Recommendation: keep root-level for now. If the product test family grows, move
it later to `tests/product/`.

## Eval Tests

Eval tests are currently split:

- public eval surface test at root
- detailed RAG/eval metrics and stackless runner tests under compat

This split is imperfect but safe: root tests protect the public compare surface;
compat tests protect lower-level implementation behavior.

Recommendation: for Phase C/D, add new multi-hop tests near the new eval tool
surface first, then decide whether to create `tests/eval/`.

## Tests That Should Stay In Place

Keep these in place during GraphRAG Eval Preparation:

- all `tests/test_phase*.py`
- all `tests/test_hardening*.py`
- `tests/test_repo_structure_consistency.py`
- `tests/test_zuno_runtime_chain_guard.py`
- `tests/test_zuno_public_entrypoints.py`
- `tests/test_docs_entrypoints.py`
- all existing `tests/compat/**`

Reason: these files double as architecture proof. Moving them would require a
separate migration with documentation and command updates.

## Tests That Could Be Grouped Later

Future grouping candidates:

- `tests/product/`
  - `test_phase1_knowledge_product_skeleton.py`
  - `test_product_wiring_v1_api_contract.py`
  - future knowledge product flow tests
- `tests/eval/`
  - `test_phase5_deep_graphrag_eval_surface.py`
  - future multihop adapter/runner tests
- `tests/hardening/`
  - `test_hardening01_*`
  - future hardening rounds
- `tests/phase/`
  - all `test_phase*.py`
- `tests/docs/`
  - docs/public-entrypoint tests

Do not do this move without a dedicated migration phase.

## Pytest Markers

Recommended markers for a later phase:

```ini
markers =
    phase: architecture phase closure tests
    hardening: hardening regression tests
    product: product workflow and API wiring tests
    eval: evaluation harness tests
    compat: compatibility/runtime regression tests
    frontend_static: static frontend source or snapshot checks
    slow: slow or integration-heavy tests
    manual: manual probes gated by environment variables
```

Do not add markers in Phase B because no test files are being edited.

## Recommended `tests/README.md`

Yes, add one later. It should explain:

- why root tests still exist
- what `compat/` means
- which commands are safe for quick verification
- which tests require services or environment flags
- where new eval tests should go

Do not add it in Phase B unless the team wants a docs-only prep step. The pasted
Phase B asks for an audit, not execution of the target structure.

## Suggested Future Target Shape

Target shape after a dedicated migration phase:

```text
tests/
  README.md
  phase/
  hardening/
  product/
  compat/
  eval/
  fixtures/
```

Migration rules:

1. Add markers before moving files.
2. Move one family at a time.
3. Preserve old command aliases in docs for at least one transition commit.
4. Run the exact legacy command and the new grouped command before merging.
5. Do not move tests that are referenced by architecture docs until those links
   are updated in the same commit.

## Phase B Closure Notes

No test files were moved. The safest next step is Phase C: add multi-hop dataset
downloaders, adapters, small fixtures, and adapter tests without reorganizing the
existing test tree.
