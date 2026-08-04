# PHASE22 Feature Flag and Residual Runtime Cutover — Evidence

Work package: `PHASE22-FEATURE-FLAG-AND-RESIDUAL-RUNTIME-CUTOVER`
Worker: `deepseek-flag-runtime-cutover` (Execution-Client: Claude Code, Provider: DeepSeek)
Base: `origin/main` @ `83c1bbd0` — Branch: `claude/deepseek-phase22-feature-flag-runtime-cutover`
Status: `FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED` (verifier, fail-closed)

## Summary

Closed the PHASE22 residual rollout flags and the AgentControlRuntime /
product_baseline residual ownership. The four flags
(`product_api_v1_adapter`, `workspace_projection_stream_v1`,
`tool_runtime_readonly_gateway`, `postgres_domain_uow_shadow`) had **zero
production readers** (full-source inventory, see
`flag_reader_inventory.json`); each semantic area was verified canonical, so
all four were retired **fail-closed** (`RETIRE_FLAG_FAIL_CLOSED`) with the
versioned Public API contracts preserved. `AgentControlRuntime` was reclassified
INTERNAL_TEST_HARNESS: removed from the `zuno.agent` production facade, kept
importable for the eval harness, and gated against production entry points.

## Flag Retirement Summary

| Flag | expires | was | now | Form | Public API kept |
|---|---|---|---|---|---|
| `product_api_v1_adapter` | PHASE10 | DECLARED | RETIRED | RETIRE_FLAG_FAIL_CLOSED | v1 product/workspace routes |
| `workspace_projection_stream_v1` | PHASE10 | DECLARED | RETIRED | RETIRE_FLAG_FAIL_CLOSED | SSE v1 `/events/stream` |
| `tool_runtime_readonly_gateway` | PHASE15 | DECLARED | RETIRED | RETIRE_FLAG_FAIL_CLOSED | Gateway (mechanism, not API) |
| `postgres_domain_uow_shadow` | PHASE04 | DECLARED | RETIRED | RETIRE_FLAG_FAIL_CLOSED | PostgreSQL UoW (mechanism) |

Retirement form rationale (task section 七): no reader exists in production
source; the registry must preserve the migration history for audit
(`verify_phase02_compatibility_boundaries.py` requires ≥ 5 flag blocks);
deleting the flag does not delete any Public API contract — the v1 routes,
SSE v1 protocol, DTOs and adapter stay untouched. Runtime selection, dual
read/write, shadow and rollback capabilities were already gone; the registry
now records that as the terminal state.

## Reader Inventory (per flag)

Full inventory in `flag_reader_inventory.json`. Highlights:

- `product_api_v1_adapter`: readers = registry + `phase02_compatibility_runtime.py`
  (governance tool) + its test. Production runtime never branches on it.
- `workspace_projection_stream_v1`: same reader set. One SSE route
  (`GET /api/v1/workspace/task/{taskId}/events/stream`), one stream owner
  (`WorkspaceTaskRuntimeService.stream_task_events`).
- `tool_runtime_readonly_gateway`: same reader set. `ToolInvocationGateway`
  is the only execution entry in the canonical surface.
- `postgres_domain_uow_shadow`: same reader set. `ProductUnitOfWork` is the
  single PostgreSQL persistence path.

## Public API Preservation

- `POST /api/v1/product/runtime/request` family (`api/v1/product.py`) — kept.
- `api/v1/workspace.py` task lifecycle + SSE stream — kept.
- Public adapter (`api/services/product/*`) — kept; verified to persist only
  through `ProductUnitOfWork`/`ProductRepository` (no direct DAO import).
- Frontend-compatible DTOs (`api/dto/*`) — untouched.
- The `api-contract-compatibility-matrix.yaml` records these v1 endpoints as
  stable contracts; their `rollback`/`sunset` columns are historical planning
  records (removal_task P22-T03), not live switches.

## Removed Runtime Branches

- No dual-path branch existed in production for any of the four flags (no
  reader). Removed: the `DECLARED` default + open rollback_command semantics
  in the registry; the PHASE02 state-machine simulation of open transitions
  (now asserts fail-closed rejection).
- Removed `AgentControlRuntime` / `AgentRuntimeResult` / `RuntimeObservation`
  from the `zuno.agent` production facade (`__all__` + lazy export table).

## AgentControlRuntime Reachability

Classification: **INTERNAL_TEST_HARNESS**. Zero production callers
(main / completion / workspace task / workers / CLI / tool scripts). Callers:
`product_baseline.py` (eval scenario generator) and
`tests/agent/test_react_reflection_replan_runtime.py`. The
`AgentControlRuntime.RuntimeObservation` string in `agent/runtime/adapters.py`
is a source tag, not an import. Re-import gate: facade rejects attribute
access; `verify_phase22_feature_flag_runtime_cutover.py` fails if any
production entry point imports it.

`product_baseline.py` classification: **INTERNAL_TEST_HARNESS** — only
`tests/evals/*` reference it; it is listed in `phase22-removal-candidates.yaml`
as a future removal candidate (not removed here: it feeds eval evidence and is
outside this package's mandatory removal list).

## Failure and Recovery Semantics (task section 八)

- 配置缺失: no runtime config exists for retired flags; unknown flag states
  are rejected by the lifecycle (fail-closed). Completion cutover mode
  resolves to `new_default` and rejects `rollback` fail-closed.
- Security denial: `ToolInvocationGateway` records `security_blocked_reason`
  and refuses dispatch (applies to READ_ONLY tools too — exemption is only
  from human approval, never from Security/Audit/Budget/Trace).
- Budget denial: budget verdicts flow through the Single Controller
  (EXECUTE_STEP node carries RuntimeLimits); denial blocks dispatch.
- Retry after committed side effect: idempotency bound by `client_request_id`
  (product commands) and `idempotency_key=call_id` (prepared tool actions);
  duplicates are no-ops (`ON CONFLICT DO NOTHING`).
- Unknown state after commit: reconciliation-bound — outbox replay
  (`InfrastructureRepository.enqueue_outbox`) is the recovery path;
  `ProductPersistenceConflict` signals conflicts; no blind retry.
- Stream restart: single event owner replays deterministically; reconnect
  goes through the same SSE route (reauthorization + gap resync semantics are
  documented in the contract matrix).
- UoW commit atomicity: current state + outbox commit in one transaction on
  one connection (`ProductUnitOfWork.__exit__` commits only on clean exit,
  rolls back otherwise).
- Public adapter does not own domain facts: adapter calls application
  services; PostgreSQL owner tables are the fact owner.
- Tool Gateway is the only execution entry (canonical surface); known
  out-of-scope direct-dispatch files are pinned and fail-closed on growth.

## Tests

Added: `tests/repo/test_phase22_feature_flag_runtime_cutover.py` — 24 tests
covering the task matrix:

1. Retired flags have no production reader
2. Registered RETIRED fail-closed (registry)
3. Rollback transition rejected (state machine)
4. Unknown/open flag states fail closed
5. Public v1 API contract preserved
6. SSE v1 stream single owner
7. Public adapter does not import DAO directly
8. READ_ONLY tool policy goes through Gateway (no approval, audit kept)
9. Unknown side-effect level fails closed
10. No shadow write in persistence layer
11. Current state + outbox atomic commit
12. Duplicate command idempotent
13. Production entry points cannot construct AgentControlRuntime
14. Facade rejects dynamic access to residual runtime
15. Package exports do not expose residual runtime
16. product_baseline is test-harness only
17. Single Controller keeps Plan/Trace/Budget/RunOutcome
18. ReAct remains step-internal
19. UoW commit exception rolls back
20. Unknown commit outcome is reconciliation-bound
21. Stream reconnect replays deterministically
22. Tool Gateway errors propagate fail-closed
23. Stale security epoch is bound fail-closed
24. Duplicate requests do not duplicate side effects

Updated: `tests/agent/test_agent_layer_surfaces.py` (facade no longer exposes
AgentControlRuntime; negative gate added), `tools/scripts/phase02_compatibility_runtime.py`
(transition simulation now asserts fail-closed retirement for all five flags).

## Verifier

`tools/scripts/verify_phase22_feature_flag_runtime_cutover.py` (fail-closed)
→ `FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED`. Statuses:
`FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED`, `ACTIVE_RUNTIME_READER_FOUND`,
`DUAL_PATH_FOUND`, `PUBLIC_ADAPTER_OWNERSHIP_VIOLATION`,
`RESIDUAL_PRODUCT_RUNTIME_FOUND`, `UNRESOLVED`, `TOOL_ERROR`. Unknown dynamic
readers resolve to UNRESOLVED with non-zero exit. The verifier pins the known
out-of-scope direct-dispatch surface (workspace agents; legacy agent modules
owned by PR #127) so the surface cannot grow.

## Candidate Dependencies

- PR #124 — not assumed accepted.
- PR #127 (semantic legacy cleanup) — not assumed accepted; its legacy
  modules remain on origin/main and are pinned, not fixed, here. The final
  CLEAN state is only judged by the MiniMax Final Audit on an integrated tree.

## Phase08 Dependencies

`DEPENDENCY_ON_DEEPSEEK_LEGACY_RUNTIME` — Phase08CutoverController and the
workspace_task_runtime Phase08 config block were read but NOT modified; the
shadow-mode machinery there belongs to the parallel DeepSeek-Legacy-Runtime
session.

## Remaining Gaps

1. `tests/repo/test_backend_facade_layers.py` has 3 pre-existing failures on
   origin/main (stale facade list vs `__all__` — `AgentRuntimeBatchError` etc.
   missing; legacy `zuno.core` lightweight import paths) — reproduced
   identically on a baseline worktree at `83c1bbd0`; not caused by and not
   fixed in this work package.
2. Workspace simple/wechat agents still execute tools directly (workspace
   cutover wave, other worker).
3. Legacy GeneralAgent-family modules still exist on origin/main (PR #127).
4. Real-PostgreSQL integration runs (UoW fault suite) were not executed in
   this environment (no local Postgres); the UoW code was not modified, only
   audited — unit-level fault tests cover the transaction semantics.
