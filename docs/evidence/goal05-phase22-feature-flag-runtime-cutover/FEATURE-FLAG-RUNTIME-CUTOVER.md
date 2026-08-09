# PHASE22 Feature Flag Registry Slice and Repository Runtime Truth — Evidence

Work package: `PHASE22-FEATURE-FLAG-SCOPED-AND-REPOSITORY-TRUTH`
Worker: `Codex`
Base: `codex/phase22-closure-audit` @ `27615813`

## Two-Layer Truth

This PR no longer claims repository-wide cutover. It reports two distinct
results:

1. **Registry Slice** (this PR's own slice):
   `ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED` (verifier `--scope registry`,
   exit 0).
2. **Repository Runtime Truth** (whole production tree):
   `FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED` (verifier `--scope repository`,
   exit 1) while real bypasses exist on the branch. BLOCKED is the correct,
   expected result until the other runtime PRs are integrated — it is not a
   failed implementation.

The registry slice proves only the slice: four RETIRED records, rejected
rollback transitions, no production Flag Reader, no dynamic Selector,
Public v1 / SSE v1 contracts preserved, and PHASE02 executable-boundary
integration (yaml.safe_load parse). It does not prove the repository cutover.

## Registry Slice — What is Proven

| Claim | Evidence |
|---|---|
| 4 records RETIRED | `yaml.safe_load` parse of `feature-flag-registry.yaml`; `default: "RETIRED"` for `product_api_v1_adapter`, `workspace_projection_stream_v1`, `tool_runtime_readonly_gateway`, `postgres_domain_uow_shadow` |
| fail-closed rollback_command | each record's `rollback_command` documents `retired and fail-closed`; no executable rollback command exists |
| rollback transition rejected | lifecycle `RETIRED: []`; every non-RETIRED transition raises `ValueError` (state machine, fail-closed) |
| no Flag Reader | AST reference audit over `src/backend/zuno/**` (identifiers, string constants, attribute wrappers, import aliases, registry-file reads, env/config lookups); zero references on this branch |
| no dynamic Selector | AST audit for `ZUNO_PRODUCT_ADAPTER` / `ZUNO_PROJECTION_STREAM` / `ZUNO_TOOL_GATEWAY` / `ZUNO_UOW` lookups; zero on this branch; concatenated keys resolve to UNRESOLVED (fail-closed) |
| Public v1 API kept | `api/v1/product.py`, `api/v1/workspace.py`, `api/router.py` exist; SSE route `events/stream` with `text/event-stream` present |
| slice integrates | full lifecycle, mandatory fields, `retire_task: P22-T03`, ≥ 5 flag records — PHASE02 executable-compatibility boundary holds |

Reader inventory detail per flag is in `flag_reader_inventory.json`.

## Repository Truth — What is NOT Proven on this Branch

The repository scope scans the ENTIRE production tree and reports every real
bypass with an annotation (`owner_work_package` / `candidate_pr` /
`external_dependency`). An active bypass can be annotated — never
allowlisted away. An allowlisted bypass keeps the repository result BLOCKED.

Findings on this branch (`verifier_report.json`, 12 findings):

- **Direct tool dispatch** (`direct_tool_bypass`):
  - `capability/mcp/servers/remote_proxy/main.py` — allowlisted direct MCP
    proxy execution.
  - `platform/__init__.py` — allowlisted dynamic import facade.
  - `mcp/load_mcp/tools.py` — direct `tool.ainvoke(...)` plus direct MCP
    loader call.
  - `mcp/manager.py` — direct `execute_tool(...)`.
  - `mcp/multi_client.py` and `mcp_openai/{mcp_client,mcp_langchain,mcp_util}.py`
    — direct MCP client/transport surfaces.
  - `platform/services/user_defined_tool_runtime.py` — direct user-defined
    tool adapter execution.
- **Residual product runtime**: none. `AgentControlRuntime` and
  `product_baseline.py` are recorded as `internal_test_harness` only.
- **Phase08 dual runtime**: none in the current repository result.

`ToolInvocationGateway` is the canonical execution entry in
`zuno/capability/tool_runtime`; the repository result is BLOCKED because the
surfaces above remain active or allowlisted direct execution surfaces.

## AgentControlRuntime Reachability (repository-wide, AST based)

Classification is based on a repository-wide import / call / dynamic-load
audit, not a fixed entry-point list:

- references confined to tests/evals ......... `INTERNAL_TEST_HARNESS`
- production-tree reference .................. `RESIDUAL_PRODUCT_RUNTIME_FOUND`
- dynamic load that cannot be proven ......... `UNRESOLVED` (fail-closed)

On this branch `product_baseline.py` and `control_runtime.py` have no
production-tree callers. Their tests/evals-only reachability is recorded as
`INTERNAL_TEST_HARNESS` and is non-blocking. The facade no longer exports
`AgentControlRuntime` / `AgentRuntimeResult` / `RuntimeObservation` and the
re-import gate is enforced by the verifier.

## Static vs Live Evidence Boundary

String-contract checks prove only `STATIC_CONTRACT_AVAILABLE`. The verifier
never emits `ATOMICITY_LIVE_VERIFIED`, `STREAM_RESUME_LIVE_VERIFIED`,
`IDEMPOTENCY_LIVE_VERIFIED` or `SECURITY_EPOCH_LIVE_VERIFIED`, and lists its
`not_proven_boundary` explicitly:

- PostgreSQL UoW atomicity (current state + outbox in one transaction):
  static contract only — no live PostgreSQL fault receipt was executed in
  this environment. Unit-level fault semantics are behavior-tested with
  fakes (`test_uow_commit_exception_rolls_back`).
- SSE resume/reconnect: static contract only — no live SSE reconnect
  receipt.
- Idempotency (`client_request_id`, `ON CONFLICT DO NOTHING`,
  `idempotency_key=call_id`): static contract only.
- Security epoch recheck: static contract only.

No PostgreSQL, SSE-reconnect or side-effect runtime receipt is fabricated.

## Tests

`tests/repo/test_phase22_feature_flag_runtime_cutover.py` — 44 tests:
real-tree pins (registry slice CONFIRMED, repository BLOCKED with the full
bypass inventory, static evidence never claims live verification) plus
fixture trees (`tests/fixtures/phase22_feature_flag_runtime_cutover/`)
pinning every detector boundary: alias/wrapper readers, dynamic config
selectors, concatenated selector keys (UNRESOLVED), allowlisted active
bypass never CLEAN, direct tool bypass, harness production caller,
test-only harness no false positive, dynamic runtime load UNRESOLVED,
registry scoped success independent of repository blockers, JSON stability,
repository fail-closed on a broken registry.

## Verifier

`tools/scripts/verify_phase22_feature_flag_runtime_cutover.py` — default
scope is `repository` (fail-closed). Statuses:

- registry: `ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED` /
  `REGISTRY_SLICE_BLOCKED` / `REGISTRY_SLICE_UNRESOLVED` / `TOOL_ERROR`
- repository: `FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED` /
  `FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED` / `FEATURE_FLAG_RUNTIME_CUTOVER_UNRESOLVED` /
  `TOOL_ERROR`

## Candidate Dependencies

- PR #124 — not assumed accepted.
- PR #127 (semantic legacy cleanup) — not assumed accepted; its legacy
  modules remain on origin/main and are reported here as annotated
  findings, not fixed. Not cherry-picked into this branch.
- Workspace cutover wave — backend semantic verifier confirms simple/wechat
  agents are canonical product adapters, not direct-dispatch findings.
- PHASE08 cutover — no current repository `phase08_dual_runtime` finding;
  the remaining runtime/legacy cleanup is tracked by the final audit.

## Phase08 Dependencies

No `phase08_dual_runtime` finding is emitted by the current repository
verifier. This does not prove full final verification or production
readiness; it only records the current static finding set.

## Remaining Gaps

1. `tests/repo/test_backend_facade_layers.py` has 3 pre-existing failures on
   origin/main (stale facade list vs `__all__` — `AgentRuntimeBatchError` etc.
   missing; legacy `zuno.core` lightweight import paths) — reproduced
   identically on a baseline worktree; not caused by and not fixed in this
   work package.
2. Direct MCP/client and user-defined tool execution surfaces remain —
   repository BLOCKED until they are migrated or retired.
3. Real-PostgreSQL integration runs (UoW fault suite) were not executed in
   this environment (no local Postgres); static-contract evidence only, per
   the evidence boundary above.
