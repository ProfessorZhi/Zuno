# Goal05 PHASE22 Final Legacy/Cutover Audit (V2)

status: LEGACY_RUNTIME_BLOCKERS_FOUND
date: 2026-08-04
branch: claude/minimax-phase22-legacy-cutover-audit-v2
base_branch: main
base_sha: 83c1bbd0689d1b2b3b4ffd7f3983de813da11ebb
head_sha: <resolved at runtime via git rev-parse HEAD>
work_package: PHASE22-LEGACY-CUTOVER-AUDIT-V2
verifier_exit_code: 1
priority: RUNTIME_BLOCKER (highest)

## Scope

This evidence record accompanies the rebuilt PHASE22 final legacy/cutover
audit gate. The V2 verifier supersedes PR #119 by addressing every
finding flagged by the Coordinator review:

1. **AST-based Python analysis.** The verifier walks every Python
   production file with the ``ast`` module. It classifies imports,
   detects ``sys.meta_path`` / ``sys.modules`` mutations, scans
   ``try/except`` legacy fallbacks and inspects the
   ``Phase08CutoverController`` for the live ``rollback`` / ``shadow`` /
   ``canary`` branches, ``legacy_runner`` field, ``_run_legacy`` and
   exception-driven ``_fallback_to_legacy`` paths.
2. **Multi-language scan.** The verifier scans TypeScript, JavaScript,
   Shell, PowerShell, YAML, TOML, JSON and workflow files for legacy
   runtime selectors, fallback runtime, rollback mode, dual read/write,
   old route/store/API references, compatibility aliases, environment
   variable runtime selectors, build-script references to retired
   entrypoints, and workflow executions of legacy commands. The scan
   covers ``src/backend``, ``apps/web``, ``apps/desktop``, ``tools``,
   ``infra``, ``.github/workflows``, plus top-level config files
   (``pyproject.toml``, ``package.json``).
3. **Feature-flag expiry enforcement.** Each flag's
   ``expires_at_phase`` is compared against the current ``PHASE22``.
   Expired flags must satisfy ``default=RETIRED`` AND a retirement
   command, otherwise the gate reports ``DUAL_PATH_BLOCKERS_FOUND``.
4. **Public-adapter ownership violation.** The verifier scans every
   public adapter root (``api/v1``, ``api/product``, ``api/errcode``,
   ``apps/web/src/apis``, ``apps/web/src/api``) for direct DAO /
   Repository writes. Any public adapter that imports
   ``zuno.platform.database`` and calls ``session.add`` /
   ``session.delete`` / ``session.commit`` / ``session.execute``
   deterministically reports
   ``PUBLIC_ADAPTER_OWNERSHIP_VIOLATION``.
5. **Removal-candidate allowlist discipline.** The verifier loads
   ``.agent/programs/work-products/phase22-removal-candidates.yaml``
   with ``yaml.safe_load`` and only admits entries whose
   ``current_status`` equals ``active_candidate``. Anything else fails
   closed.
6. **Git head SHA via ``git rev-parse HEAD``.** The verifier shells
   out to ``git rev-parse HEAD`` instead of guessing from
   ``.git/HEAD`` text.
7. **Unresolved escalation tracking.** The verifier scans
   ``docs/evidence`` for ESCALATE_TO_DEEPSEEK markers paired with
   open status indicators and records them as ``AUDIT_UNRESOLVED``
   findings. On the current head there is an unresolved escalation
   in ``docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/allowlist_classification.md``.

This audit slice does NOT modify the runtime, the database, the
security boundary, the budget machinery or the agent state machine.
It only adds the verifier, tests, contract fixtures and evidence
artefacts.

## Counts (current origin/main)

| Category | Count |
| -------- | ----- |
| Runtime blockers | 7 |
| Dual-path blockers | 145 |
| Alias/bypass blockers | 14 |
| Public-adapter violations | 0 |
| Unresolved items | 1 |

The seven runtime blockers come from the live Phase08 controller:

* `Phase08CutoverController.mode=='rollback'`
* `Phase08CutoverController.mode=='shadow'`
* `Phase08CutoverController.mode=='canary'`
* `Phase08CutoverController._run_legacy`
* `Phase08CutoverController.legacy_runner`
* `Phase08CutoverController._fallback_to_legacy`
* `workspace_task_runtime.py::_run_phase08_cutover_for_task` synthesises a `legacy_runner` factory

The unresolved item is the open DeepSeek escalation recorded in
`docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/allowlist_classification.md`.
The dual-path blockers come from expired feature flags in
`.agent/programs/work-products/feature-flag-registry.yaml` and
expired allowlist entries in
`.agent/programs/work-products/temporary-allowlist.yaml`.
The alias/bypass blockers come from try/except legacy fallbacks and
`importlib.import_module` usage in production source.

The current head SHA recorded in the verifier JSON output is
`baf9c72f8042460ae477cc4be7da1b3be8c441d3`.

## Status

`LEGACY_RUNTIME_BLOCKERS_FOUND` — exit code 1.

This is the highest-priority status in the audit. Per the task
contract:

> 当前 main 在 DeepSeek 修复前，预期不能返回 CLEAN。
> 合理结果应为：DUAL_PATH_BLOCKERS_FOUND 或 AUDIT_UNRESOLVED。
> 不得为了 exit 0 降低规则。

The V2 verifier returns the highest-priority status it actually finds.
Because the Phase08CutoverController still exposes the
`_fallback_to_legacy` runtime (the lone architectural escalation to
DeepSeek), the priority logic raises the status to
`LEGACY_RUNTIME_BLOCKERS_FOUND` rather than the weaker
`DUAL_PATH_BLOCKERS_FOUND`.

## Files Added

- `tools/scripts/verify_phase22_final_legacy_cutover.py`
- `tests/repo/test_phase22_final_legacy_cutover.py`
- `tests/fixtures/phase22_legacy_cutover/01_clean_canonical_tree.py`
- `tests/fixtures/phase22_legacy_cutover/02_fallback_to_legacy.py`
- `tests/fixtures/phase22_legacy_cutover/03_legacy_runner_injection.py`
- `tests/fixtures/phase22_legacy_cutover/04_rollback_mode.py`
- `tests/fixtures/phase22_legacy_cutover/05_shadow_legacy_primary.py`
- `tests/fixtures/phase22_legacy_cutover/06_canary_legacy_shadow.py`
- `tests/fixtures/phase22_legacy_cutover/07_exception_autofallback_legacy.py`
- `tests/fixtures/phase22_legacy_cutover/08_product_api_generalagent_reachable.py`
- `tests/fixtures/phase22_legacy_cutover/09_legacy_runtime_history_only.py`
- `tests/fixtures/phase22_legacy_cutover/10_python_legacy_import.py`
- `tests/fixtures/phase22_legacy_cutover/11_dynamic_legacy_import.py`
- `tests/fixtures/phase22_legacy_cutover/12_sys_meta_path.py`
- `tests/fixtures/phase22_legacy_cutover/13_sys_modules_alias.py`
- `tests/fixtures/phase22_legacy_cutover/14_try_except_legacy_import.py`
- `tests/fixtures/phase22_legacy_cutover/15_typescript_legacy_api.ts`
- `tests/fixtures/phase22_legacy_cutover/16_shell_legacy_env.sh`
- `tests/fixtures/phase22_legacy_cutover/17_workflow_legacy_command.yml`
- `tests/fixtures/phase22_legacy_cutover/18_dual_read_marker.py`
- `tests/fixtures/phase22_legacy_cutover/19_dual_write_marker.py`
- `tests/fixtures/phase22_legacy_cutover/20_expired_unretired_flag.yaml`
- `tests/fixtures/phase22_legacy_cutover/21_retired_no_runtime_reader.yaml`
- `tests/fixtures/phase22_legacy_cutover/22_public_adapter_dao_write.py`
- `tests/fixtures/phase22_legacy_cutover/23_public_adapter_application_service.py`
- `tests/fixtures/phase22_legacy_cutover/24_dynamic_unresolved_call.py`
- `tests/fixtures/phase22_legacy_cutover/25_history_document_legal.py`
- `tests/fixtures/phase22_legacy_cutover/26_evidence_fake_clean.md`
- `tests/fixtures/phase22_legacy_cutover/27_legacy_guards_rebuilt.py`
- `tests/fixtures/phase22_legacy_cutover/28_legacy_alias_registry_rebuilt.py`
- `docs/evidence/goal05-phase22-legacy-cutover-final-audit-v2/inventory.json`
- `docs/evidence/goal05-phase22-legacy-cutover-final-audit-v2/reachability_report.json`
- `docs/evidence/goal05-phase22-legacy-cutover-final-audit-v2/verifier_report.json`

## Verification

```bash
python tools/scripts/verify_phase22_final_legacy_cutover.py
python tools/scripts/verify_phase22_final_legacy_cutover.py --json
python tools/scripts/verify_phase22_final_legacy_cutover.py \
  --evidence-dir docs/evidence/goal05-phase22-legacy-cutover-final-audit-v2
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python -m pytest -q \
  tests/repo/test_phase22_final_legacy_cutover.py \
  tests/repo/test_phase22_cleanup_boundary.py \
  tests/api/test_layered_api_boundaries.py \
  tests/api/test_completion_unified_runtime.py \
  -p no:cacheprovider
git diff --check
```

Expected results on the current origin/main head:

* `verify_phase22_final_legacy_cutover.py` exits 1 with status
  `LEGACY_RUNTIME_BLOCKERS_FOUND`.
* `verify_phase22_cleanup_boundary.py` exits 0 with no errors.
* `verify_repo_structure.py` exits 0 with no errors.
* `.agent/scripts/verify_agent_system.py` exits 0 with no errors.
* The pytest invocation above runs 78 tests, all pass.

## Remaining Gaps

* Phase08 `_fallback_to_legacy` runtime escalation to DeepSeek is
  unresolved; this prevents the verifier from returning
  `LEGACY_CUTOVER_AUDIT_CLEAN` on the current head.
* Expired feature flags (`product_api_v1_adapter`,
  `workspace_projection_stream_v1`, `tool_runtime_readonly_gateway`,
  `postgres_domain_uow_shadow`) remain in
  `.agent/programs/work-products/feature-flag-registry.yaml` with
  `default != RETIRED`. They are scheduled to retire in P22-T03 but
  have not been retired yet.
* The temporary allowlist `.agent/programs/work-products/temporary-allowlist.yaml`
  contains entries whose `deadline_phase` predates PHASE22. They are
  not yet removed; the audit gate surfaces every expired entry as a
  dual-path blocker.
* Production source still uses `try/except ImportError` legacy
  fallbacks and `importlib.import_module` in production source
  (`tools/scripts/verify_*.py`, `tools/evals/zuno/rag_eval/run_eval.py`,
  `src/backend/zuno/platform/database/metadata.py`,
  `src/backend/zuno/agent/runtime/nodes/core.py`,
  `src/backend/zuno/knowledge/ingestion/gateway.py`,
  `src/backend/zuno/platform/services/rag/rerank.py`,
  `src/backend/zuno/platform/model_gateway.py`). These are flagged
  as alias/bypass blockers; the work to migrate them to canonical
  imports is owned by `minimax-runtime-cleanup`.
* The fixed benchmark, formal four-profile runtime, production
  readiness decision, full final verification and program archive are
  still pending per `PHASE22_fixed-benchmark-production-readiness-and-closure.md`.

## Notes

The V2 audit gate does NOT claim PHASE22 is complete. It documents
the repository state on the exact final head and refuses to call the
audit CLEAN until the Phase08 production fallback is retired or
proven unreachable, the expired feature flags and allowlist entries
are removed, and the unresolved DeepSeek escalation is resolved.