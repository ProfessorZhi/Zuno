# Goal05 PHASE22 ChatGPT Review-Fix Round Report

status: chatgpt_review_fixes_complete
phase: PHASE22
parent_pr: 97
integration_branch: codex/phase22-final-closure
reviewed_head_sha: e484816d18bc657509ae0aa1fcf6b6a8e74489f7
report_generated_at: 2026-08-02T15:42:00Z

## Frozen Facts

- PHASE22 = in_progress
- Program = active
- Fixed Benchmark = BLOCKED / blocked_not_measured
- actual_case_count = 0
- reviewer_approved_count = 0
- benchmark_eligible_count = 0
- Production Readiness = not established
- Mandatory Coverage = 11/11 CURRENT
- Removal Candidates = 7/7 resolved_retired

## Start / End Timestamps

- Start: `2026-08-02T15:19:37Z` (Get-Date -Format o)
- End:   `2026-08-02T15:42:00Z` (Get-Date -Format o)

## Pre-Flight

- `git fetch origin --no-tags` — run.
- Local `main` = `origin/main` = `dfb9981995f4193488ca022ee5ec15eeff6a6349`.
- PR #97 head (at start) = `6a3400688507d2d2d393ec7066557af681a7cf43`.
- Worktree `HEAD` (at start) = `6a3400688507d2d2d393ec7066557af681a7cf43` (no drift).
- Worktree status (at start) — empty (clean).
- 15 commits on integration branch at start; 3 added this round.
- No rebase, reset, amend, force push, merge, or main edit.

## Final Head

- branch: `codex/phase22-final-closure`
- **head SHA: `e484816d18bc657509ae0aa1fcf6b6a8e74489f7`** (pushed)
- base: `main` @ `dfb9981995f4193488ca022ee5ec15eeff6a6349`
- 18 commits on integration branch
- PR #97: **Open / Draft / Title = `[Claude Code + MiniMax] PHASE22 final canonical closure`**

## ChatGPT Review Items Resolved

### 1. Commit Attribution CI

- Historical commits on the integration branch predate the new
  attribution contract (Agent / Agent-Mode / Human-Owner /
  Architecture-Reviewer / Work-Package).
- The contract forbids amend / rebase / reset / force-push and
  rewriting history.
- Historical commits are recorded as
  `BLOCKED_GOVERNANCE_CONTRACT` in
  `docs/evidence/goal05-phase22-commit-attribution-blocked.md`.
- New commits this round use the correct trailer set:
  `Agent: Claude-Code`, `Agent-Mode: Codex`, `Human-Owner: ProfessorZhi`,
  `Architecture-Reviewer: ChatGPT`, `Work-Package: PHASE22-PR97-REVIEW-FIX`,
  `Parent-PR: #97`, `Metrics-Run: NOT_AVAILABLE_INTERACTIVE_SESSION`.
- A clean state requires a future squash at merge time.

### 2. Test Shim Removal

- `tests/conftest.py` no longer installs `tools.evals.zuno` as
  `zuno.evals` in `sys.modules`.
- 89 references in 12 test files migrated to real owner path
  `tools.evals.zuno.*`. `tests/repo/test_phase22_eval_package_contract.py`
  is kept as the contract enforcer (it now correctly reports no
  production-code alias injections).
- Deltas vs `main` HEAD `dfb99819` recorded in
  `docs/evidence/goal05-phase22-import-fix-deltas.md`.

### 3. Dispatcher Contract

- `.agent/scripts/dispatch_claude_worker.ps1` now:
  - Loads and validates
    `.agent/programs/worker-result.schema.json` (inline validator
    using `System.Web.Script.Serialization.JavaScriptSerializer`-style
    approach; PowerShell 5.1 compatible; ConvertTo-Json with high
    depth to avoid the string-wrapping bug).
  - Validates `worker_task_id` equals Task Card `WORKER_TASK_ID`.
  - Refuses to promote `BLOCKED_*` to COMPLETED, even when a commit
    is present.
  - Reads `SUMMARY_PATH` from **raw** stdout, then sanitises for the
    persisted `summary_path` field.
  - Defaults `quota_snapshot_available` to `NOT_QUERIED`; only flips
    to `CONFIG_REQUIRED` when a real summary reports that state.
  - Worker Result is a `COMPLETION_CANDIDATE` until the controller
    manually reviews Diff / Branch / Forbidden Paths / Tests. No
    automatic promotion to `COMPLETED`.
  - Distinct exit codes: `0` OK-COMPLETED, `2` PRECHECK_FAILED,
    `3` RUNNER_FAILED, `10` COMPLETION_CANDIDATE, `20`
    FAILED_WORKER_COMPLETION, `30` BLOCKED_*.
  - Worktree lock with `pid`, `created_at`, and stale-PID recovery;
    active locks are not preempted.
  - `launcher_resolved` and `summary_path` are redacted
    (`%USERPROFILE%` substitution) before persistence.
  - JSON serialisation uses `ConvertTo-Json -Depth 32` (PowerShell 5.1
    compatible) — no handcrafted JSON.

### 4. Evidence Truth

- `docs/evidence/goal05-phase22-minimax-live-run.md` downgraded to
  `provider_wrapper_smoke_observed`. The recorded run was a metrics
  wrapper smoke, not a full Worker E2E.
- Self-referencing `integration_head_sha` / `final head SHA` fields
  in evidence renamed to `reviewed_head_sha` (records which head was
  reviewed, not which head carries the evidence; the two may differ).
- `source_sha_at_generation` used in new evidence.
- `approximate, will refresh` self-reference removed.

### 5. Tests

- `tests/repo/test_dispatch_claude_worker.py` extended with new
  contract tests: schema validation, task_id mismatch, BLOCKED not
  promoted, summary path redaction, NOT_QUERIED default, CONFIG_REQUIRED
  via summary, COMPLETION_CANDIDATE not COMPLETED, stale lock recovery,
  active lock blocks dispatch.
- All 30 dispatcher tests pass (was 20 before this round).
- 7 pre-existing `tests/evals/test_rag_eval_metrics.py` failures
  (NameError: math not defined) are **pre-existing on `main` HEAD
  `dfb99819`**. Production code fix is out of scope (changing
  production source on main is forbidden by this round's contract).

## Mandatory Verifier Run

| Verifier | Result |
| --- | --- |
| `git diff --check` | passed |
| `python .agent/scripts/verify_agent_system.py` | passed |
| `python .agent/scripts/verify_doc_boundaries.py` | passed |
| `python tools/scripts/verify_repo_structure.py` | passed |
| `python tools/scripts/verify_current_program.py` | passed |
| `python tools/scripts/verify_phase22_completion_blockers.py` | passed |
| `python tools/scripts/verify_phase22_cleanup_boundary.py` | passed |
| `python tools/scripts/verify_agent_commit_attribution.py --base origin/main --allow-human-only` | **FAILED** (historical commits, see BLOCKED_GOVERNANCE_CONTRACT) |
| `pytest -q tests/repo/test_dispatch_claude_worker.py -p no:cacheprovider` | **30 passed** |
| `pytest -q tests/evals -p no:cacheprovider` (collectible subset) | **539 passed, 30 subtests passed; 7 pre-existing failures on `main` HEAD `dfb99819`** |
| `cd apps/web && npm run lint` | **PASSED (exit 0)** |
| `cd apps/web && npm run build` | **PASSED (exit 0)** |

## GitHub Actions Run (PR #97 head `e484816d`)

| Workflow | Status |
| --- | --- |
| `Generate Verification Evidence & Summary` | success |
| `PHASE22 Focused Test Suite` | success |
| `Repository Gates & Static Checks` | **failure** (matches the local attribution verifier — historical commits) |
| `validate` | success |

The `Repository Gates & Static Checks` failure is the same
`BLOCKED_GOVERNANCE_CONTRACT` reported locally. New commits this
round pass the verifier; only historical commits (which cannot be
amended per the round's contract) fail.

## Files Modified (this round)

- `.agent/scripts/dispatch_claude_worker.ps1` (rewrite for new contract)
- `tests/conftest.py` (removed zuno.evals shim)
- `tests/repo/test_dispatch_claude_worker.py` (added 10 new contract tests, updated 7 existing tests for new exit codes)
- `tests/evals/test_local_embedding_server.py` (import fix)
- `tests/evals/test_local_rerank_server.py` (import fix)
- `tests/evals/test_phase5_deep_graphrag_eval_surface.py` (import fix)
- `tests/evals/test_public_enterprise_dataset_adapters.py` (import fix)
- `tests/evals/test_rag_eval_local_launcher.py` (import fix)
- `tests/evals/test_rag_eval_local_scheme.py` (import fix)
- `tests/evals/test_rag_eval_metrics.py` (import fix)
- `tests/evals/test_stackless_compare_matrix.py` (import fix)
- `tests/evals/test_stackless_local_eval_manifest_filter.py` (import fix)
- `tests/evals/test_stackless_local_eval_project_assets.py` (import fix)
- `tests/evals/test_stackless_local_eval_rerank_runtime.py` (import fix)
- `tests/repo/test_phase4_knowledge_config_v2_and_local_eval.py` (import fix)
- `docs/evidence/goal05-phase22-commit-attribution-blocked.md` (new)
- `docs/evidence/goal05-phase22-import-fix-deltas.md` (new)
- `docs/evidence/goal05-phase22-minimax-live-run.md` (downgraded to provider_wrapper_smoke_observed)
- `docs/evidence/goal05-phase22-final-controller-report.md` (reviewed_head_sha)
- `docs/evidence/goal05-phase22-final-verification-run.md` (reviewed_head_sha)
- `docs/evidence/goal05-phase22-stop-hook-resolution.md` (reviewed_head_sha)
- `docs/evidence/goal05-phase22-wave1-controller-plan.md` (reviewed_head_sha)
- `docs/evidence/goal05-phase22-chatgpt-review-fix-report.md` (this file)

## Items Not Run (mandatory disclosure)

- Browser E2E
- Desktop Build/Smoke
- Alembic Upgrade/Downgrade against PostgreSQL
- Real PostgreSQL / RabbitMQ / Object Store / LangGraph Checkpointer
  runs
- Fault Injection, Security, Load/Soak/DR, Backup/Restore drill
- Four-profile Fixed Benchmark
- `tests/evals/test_agentic_graphrag_product_baseline.py` and
  `tests/evals/test_agentic_graphrag_regression_summary.py` (parser
  bug: `file_phase12_docx` not blocking — pre-existing on main).
- `tests/repo/test_agent_system.py` (7 pre-existing failures on
  main).
- `tests/evals/test_rag_eval_metrics.py` (7 pre-existing failures
  on main: NameError `math`).

## PHASE22 Remaining Blockers (unchanged)

1. `actual_case_count=0`, `reviewer_approved_count=0`,
   `benchmark_eligible_count=0`.
2. Fixed Benchmark `blocked_not_measured`.
3. Agentic GraphRAG parser regression: `file_phase12_docx` not
   blocking.
4. Production Readiness `not established`.
5. Program archive not done.
6. `BLOCKED_GOVERNANCE_CONTRACT` for historical commit attribution
   trailers.
7. Pre-existing 7 production test failures on `main`.

## ChatGPT Exact-Head Re-Review Request

Please review exact head `e484816d18bc657509ae0aa1fcf6b6a8e74489f7`
against `main` for:

- Architecture consistency vs `docs/architecture/architecture.md`
  and the eleven module target documents.
- Code quality of `.agent/scripts/dispatch_claude_worker.ps1`,
  `.agent/programs/worker-result.schema.json` and
  `tests/repo/test_dispatch_claude_worker.py`.
- State machine, failure semantics, recovery, idempotency,
  concurrency and security of the dispatcher.
- Test sufficiency for schema validation, task_id match, BLOCKED
  not promoted, summary redaction, NOT_QUERIED default,
  COMPLETION_CANDIDATE gate, lock TTL, path redaction.
- Evidence truthfulness vs PHASE22 frozen facts.

PR #97 remains Draft. No merge is requested. No `MERGE_APPROVED` is
written.

End: `Get-Date -Format o` → `2026-08-02T15:42:00Z`