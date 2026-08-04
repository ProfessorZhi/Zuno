# PHASE22 Backend Semantic Legacy Cleanup — Evidence

Work package: `PHASE22-BACKEND-SEMANTIC-LEGACY-CLEANUP`
Worker: `deepseek-legacy-backend` (Execution-Client: Claude Code, Provider: DeepSeek)
Base: `origin/main` @ `83c1bbd0` — Branch: `claude/deepseek-phase22-backend-semantic-legacy-cleanup`
Status: `BACKEND_SEMANTIC_LEGACY_CLEAN`

## Summary

Removed the semantic legacy agent runtimes that were still hiding under
canonical names inside `src/backend/zuno/agent/` **outside** of the
Phase08CutoverController. After this cleanup the Single Controller Product
Runtime is the only top-level product runtime:

| Layer | Canonical implementation |
|---|---|
| Single Controller | `SingleControllerRuntimeHarness` (`zuno.agent.harness`) |
| Fixed AgentRunGraph | `build_agent_graph` (`zuno.agent.runtime.graph`) |
| Dynamic Plan DAG | `RuntimePlanner` / `PlanExecutor` (`zuno.agent.runtime.planning`) |
| Fixed StepExecutionGraph | `build_phase08_step_graph` (`zuno.agent.runtime.phase08`) |
| Service facade | `UnifiedAgentRuntimeService` (`zuno.agent.runtime.service`) |

Every product run passes through Plan (CREATE_OR_UPDATE_PLAN), Trace
(trace_id / observe / evidence_gate), Budget (RuntimeLimits + budget verdicts),
and RunOutcome (FINALIZE / FinalizationStatus).

## Deleted Runtime

| File | Class / symbols | Classification |
|---|---|---|
| `src/backend/zuno/agent/core/agents/general_agent.py` | `GeneralAgent`, `AgentConfig`, `StreamAgentState`, `EmitEventAgentMiddleware` | PRODUCT_LEGACY_RUNTIME |
| `src/backend/zuno/agent/core/agents/react_agent.py` | `ReactAgent` | PRODUCT_LEGACY_RUNTIME |
| `src/backend/zuno/agent/core/agents/plan_execute_agent.py` | `PlanExecuteAgent` | PRODUCT_LEGACY_RUNTIME |
| `src/backend/zuno/agent/core/agents/codeact_agent.py` | `CodeActAgent` | TEST_OR_HISTORY_ONLY |
| `src/backend/zuno/agent/core/agents/text2sql_agent.py` | `Text2SQLAgent` | TEST_OR_HISTORY_ONLY |
| `src/backend/zuno/agent/runtime.py` | shadowed dead re-export shim (`GeneralAgent`/`AgentConfig`) | TEST_OR_HISTORY_ONLY |
| `src/backend/zuno/agent/state.py` | export shim (`StreamAgentState`) | TEST_OR_HISTORY_ONLY |
| `src/backend/zuno/agent/streaming.py` | export shim (`EmitEventAgentMiddleware`/`StreamAgentState`) | TEST_OR_HISTORY_ONLY |

Exports removed from `zuno.agent`, `zuno.agent.core` and
`zuno.agent.core.agents` (the lazy export surfaces now expose only
`StructuredResponseAgent`).

## Retained Internal Mechanism

| Mechanism | Retained implementation | Role |
|---|---|---|
| ReAct | `ReActStepRunner` (`runtime/execution/react_runner.py`), `ReActStepExecutor` | single-step Action/Observation inside the fixed StepExecutionGraph |
| Planner | Dynamic Plan DAG (`runtime/planning/*`: `RuntimePlanner`, `PlanExecutor`, `dynamic_dag`) | plan creation / replan inside the run |
| Structured Response | `StructuredResponseAgent` (`core/agents/structured_response_agent.py`) | deterministic schema-validated capability used by `agent_skill.py` / `mcp_server.py`; no top-level task lifecycle |
| Code Execution | `zuno.platform.services.sandbox` | controlled capability |
| Single Controller family | `harness.py`, `durable_runtime.py`, `planning.py`, `runtime_batch.py` | canonical runtime foundation |

## Production Callers Migrated

None required: the retirement audit proved **zero production callers** for every
deleted symbol. Completion, Workspace Task, Queue Worker, CLI, main and tool
scripts were already on the canonical runtime. No `api/services` old-agent call
existed to migrate.

## Hidden Dual Path Findings

All checks clean (`findings: []` in `verifier_report.json`):

- `ZUNO_AGENT_RUNTIME` env selector: absent from production.
- `_create_chat_agent`: absent from production.
- `legacy_general_agent` rollback: absent from completion; `ZUNO_COMPLETION_CUTOVER_MODE=rollback` rejected fail-closed.
- `try/except ModuleNotFoundError` runtime fallback: none in agent entry points.
- `direct_answer`: canonical planner strategy only (planning.py / runtime.planning / contracts).
- SQLite/InMemory stores: canonical run stores (`SQLiteAgentRunStore`, `InMemoryDurableRuntimeStore`), not fallbacks.
- Old completion helper / stream generator: none (completion route/service are canonical; `zuno.agent.streaming` deleted).

## Phase08 Dependencies

`DEPENDENCY_ON_DEEPSEEK_LEGACY_RUNTIME` — recorded, no conflicting edits:

- `workspace_task_runtime.py` Phase08 cutover configuration block: read, NOT modified.
- `zuno.agent.runtime.phase08_cutover` / `zuno.agent.runtime.phase08`: read-only.

## Unresolved Symbols

| Symbol | Module | Finding | Disposition |
|---|---|---|---|
| `WorkSpaceSimpleAgent` | `platform/services/workspace/simple_agent.py` | Production React agent outside the Single Controller; executes tools via direct `handler(request)` without `ToolInvocationGateway` (unapproved side-effect bypass) | NOT MODIFIED — out of work-package scope; work product lists workspace services as an active canonical surface; owned by the workspace cutover wave. Pinned by test `test_tool_side_effect_gateway_is_enforced` (bypass phrase confined to exactly the two workspace agent files) |
| `WechatAgent` | `platform/services/workspace/wechat_agent.py` | same direct tool execution pattern | NOT MODIFIED — same disposition |
| `AgentControlRuntime` | `zuno.agent.control_runtime` | superseded controller; used only by `product_baseline.py`, facade export and tests | retained (outside allowed scope); future retirement candidate |

## Tests

Added: `tests/repo/test_phase22_backend_semantic_legacy.py` (22 tests) covering:

1. Product API no GeneralAgent import
2. Queue Worker no GeneralAgent
3. CLI no GeneralAgent
4. GeneralAgent production export gone
5. Dynamic import cannot restore
6. Env selector cannot restore (incl. rollback fail-closed)
7. Single Controller is the only top-level runtime
8. Every run has Plan
9. Every run has Trace
10. Every run has Budget
11. Every run has RunOutcome
12. ReAct remains a step-internal mechanism
13. Security/Approval cannot be bypassed
14. Tool side-effect gateway enforced (agent-core surface) + workspace bypass pinned
15. No Developer/CI adapter default in production
16. Tests do not depend on the retired runtime success path
17. Package import smoke
18. Restart/Resume via canonical runtime

Converted/deleted legacy tests:

- Deleted: `tests/agent/test_generalagent_context_memory_runtime.py`, `tests/agent/test_general_agent_project_query_runtime.py`
- Converted to retirement gates: `tests/repo/test_phase11b_single_generalagent_cutover.py`, `tests/repo/test_phase5_general_agent_real_runtime_flow.py`, `tests/repo/test_phase5_domain_runtime_paths.py` (partial), `tests/repo/test_phase6_agent_graphrag_pluginization.py` (partial)
- Updated surfaces: `tests/agent/test_agent_layer_surfaces.py`, `tests/agent/test_hooks_evidence_trace_artifacts.py` (local fixture), `tests/agent/runtime/test_runtime_model_roles.py` (canonical model-step roles), `tests/repo/test_backend_facade_layers.py` (synced facade lists; also fixed pre-existing drift against `zuno.services.*` legacy aliases), `tests/api/test_layered_api_boundaries.py`

Verifier scripts updated (retired-file assertions): `verify_phase22_cleanup_boundary.py`, `verify_model_gateway_boundaries.py`, `verify_tool_execution_bypass.py`.

## Test Run Results (2026-08-04, this session)

Full scope run: `pytest -q tests/agent tests/api/test_completion_unified_runtime.py
tests/api/test_workspace_task_runtime.py tests/repo/test_phase22_backend_semantic_legacy.py`
→ **10 failed, 390 passed, 4 warnings in 1929.53s (32:09)**.

All 10 failures are **pre-existing on `origin/main`** (proven by re-running the
identical tests in a clean worktree at `origin/main`, same interpreter):

- 8 × `psycopg.errors.ConnectionTimeout` — no local Postgres at
  `localhost:5432` in this environment (tool control plane ×2, tool
  idempotency, capability-system secret-ledger, database memory store,
  workspace task runtime ×3). The workspace-task failures sit in the
  Phase08 cutover domain owned by the parallel DeepSeek-Legacy-Runtime
  session and are unrelated to this cleanup.
- 2 × pre-existing drift/behavior failures that reproduce identically at
  `origin/main`: `test_completion_factory_knowledge_step_uses_durable_port_not_missing_dependency`
  (durable knowledge port returns `blocked` instead of `skipped`) and
  `test_platform_layer_modules_expose_target_boundaries` (stale
  `__all__` expectations in `zuno.platform.*` — 10 extra exports such as
  `ObservabilityTracePort`). Neither file nor its subject module is
  touched by this work package; fixing the platform-surface drift is
  outside the allowed modification scope.

The new enforcement suite passes: `tests/repo/test_phase22_backend_semantic_legacy.py`
→ **22 passed in 12.39s** (covers all 18 required invariants).

## Tests Not Run

- Full repo suite (`tests/` beyond the scope above, incl. `tests/integration/**`,
  `tests/e2e/**`, `tests/capability/**`, `tests/knowledge/**`, `tests/memory/**`) not run.

## Verifier

`tools/scripts/verify_phase22_backend_semantic_legacy.py` → `BACKEND_SEMANTIC_LEGACY_CLEAN`
(see `verifier_report.json`). Statuses: `BACKEND_SEMANTIC_LEGACY_CLEAN`, `PRODUCT_LEGACY_RUNTIME_FOUND`,
`CANONICAL_RUNTIME_BYPASS_FOUND`, `PRODUCTION_ADAPTER_FALLBACK_FOUND`, `UNRESOLVED`, `TOOL_ERROR`.

## Remaining Gaps

1. Workspace simple/wechat agents still run outside the Single Controller and
   execute tools directly (side-effect gating missing at the agent layer).
   Owned by the workspace cutover wave; pinned, not fixed, here.
2. `AgentControlRuntime` + `product_baseline.py` remain as history-only code
   (outside allowed scope).
3. Pre-existing failures reproduced identically at `origin/main` (see Test Run
   Results): 8 Postgres-connection timeouts (environment lacks local Postgres)
   and 2 stale drift tests (`test_runtime_dependency_factory.py` knowledge-step
   expectation, `test_platform_layer_surfaces.py` platform `__all__`). Not
   caused by, and not fixed in, this work package.
4. Full repo test suite (all of `tests/`) not performed in this work package.
