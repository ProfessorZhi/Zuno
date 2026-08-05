# PHASE22 Backend Semantic Legacy Cleanup — Evidence (Dual Scope)

Work package: `PHASE22-BACKEND-RUNTIME-OWNERSHIP-REACHABILITY-GATE`
Worker: `minimax-legacy-ownership-gate` (Execution-Client: Claude Code, Provider: MiniMax)
Base: `origin/main` @ `83c1bbd0` — Branch: `claude/deepseek-phase22-backend-semantic-legacy-cleanup`
Head (start): `a878f6baff2fc53594507703b45010257c85b5ae`
Head (this slice): the new commit on top of `a878f6ba`.

## What this slice changes

The previous verifier classified every candidate runtime class (`WorkSpaceSimpleAgent`,
`WeChatAgent`, `AgentControlRuntime`) by **class name alone**. As soon as
the `ClassDef` existed anywhere in `src/backend/zuno/`, the verifier
emitted a top-level runtime finding. That made it impossible for the
verifier to ever reach `BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED` once
the Workspace cutover wave turns the legacy classes into thin Product
Adapters that delegate to `UnifiedAgentRuntimeService`.

This slice replaces the name-based heuristic with an **ownership +
reachability** classifier. Every candidate class is classified by:

  1. Whether the class appears in `INTERNAL_STEP_CAPABILITY_CLASSES`
     (e.g. `ReActStepRunner`, `StructuredResponseAgent`) → always
     `INTERNAL_STEP_CAPABILITY`.
  2. Whether any **Production Entry Point** constructs the class.
     Production callers are detected by AST: a `ClassName(...)`
     construction in any production module (excluding `tests/`,
     `docs/`, `.agent/`, `__init__.py` facade re-exports, and the
     `product_baseline.py` baseline generator).
  3. The class's own method bodies, walked for behaviour evidence:
     - `independent_graph` — `create_agent`, `create_react_agent`,
       `StateGraph`, `ToolNode`.
     - `direct_model_call` — `self.model.ainvoke`, `model.invoke`, etc.
     - `direct_tool_call` — `self.tool.ainvoke`, `tool.invoke`, etc.
     - `direct_handler_await` — `response = await handler(request)`
       inside an `AgentMiddleware` shape.
     - `product_lifecycle_attr` — references to `trace_events`,
       `final_answer`, `capability_plan`, `RunOutcome`, etc.
     - `canonical_delegate` — references to
       `UnifiedAgentRuntimeService`,
       `SingleControllerRuntimeHarness`,
       `SingleControllerDurableRuntime`,
       `WorkspaceAgentRuntime`, `WorkspaceTaskRuntimeService`.

The decision tree is:

| Step | Classified as |
|---|---|
| `INTERNAL_STEP_CAPABILITY_CLASSES` membership | `INTERNAL_STEP_CAPABILITY` (allowed) |
| Class name is `SingleControllerRuntimeHarness` | `PRODUCT_CANONICAL` (allowed) |
| No production caller | `INTERNAL_TEST_HARNESS` (allowed) |
| Production caller + any legacy evidence | `PRODUCT_LEGACY_RUNTIME` (BLOCKED) |
| Production caller + only canonical delegation evidence | `PRODUCT_ADAPTER` (allowed) |
| Production caller + no execution / graph / lifecycle evidence | `PRODUCT_ADAPTER` (allowed) |
| Dynamic construction (`globals`, `getattr`, `eval`, `__import__`) with an `Agent`/`Runtime`/`Controller`/`Service` token | repository scope → `BACKEND_PRODUCT_RUNTIME_UNRESOLVED` (non-zero exit) |

## Two-Layer Truth (current state of this branch)

### Scoped Result (this PR's own retirement)

**Status:** `AGENT_FAMILY_LEGACY_SLICE_CLEAN`

The PR successfully retired the entire GeneralAgent family
(`GeneralAgent`, `AgentConfig`, `StreamAgentState`,
`EmitEventAgentMiddleware`, `ReactAgent`, `PlanExecuteAgent`,
`CodeActAgent`, `Text2SQLAgent`) and the three legacy export shims
(`agent/runtime.py`, `agent/state.py`, `agent/streaming.py`). No
production entry point can import a retired module, and the agent
package `__all__` no longer re-exports any retired symbol.

See `scoped_report.json` for the machine-readable record.

### Repository Result (full Backend Product Runtime cutover)

**Status:** `BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED`

The classifier surfaces the following per-class ownership verdicts:

| Class | Module | Classification | Reason |
|---|---|---|---|
| `SingleControllerRuntimeHarness` | `src/backend/zuno/agent/harness.py:184` | `PRODUCT_CANONICAL` | Canonical runtime |
| `AgentControlRuntime` | `src/backend/zuno/agent/control_runtime.py:50` | `INTERNAL_TEST_HARNESS` | No production caller (only facade export + tests + baseline) |
| `WorkSpaceSimpleAgent` | `src/backend/zuno/platform/services/workspace/simple_agent.py:122` | `PRODUCT_LEGACY_RUNTIME` | Production caller (`api/services/workspace.py:160`) + `create_agent` + `handler(request)` + `self.model.ainvoke` + `tool.ainvoke` + `final_answer` |
| `WeChatAgent` | `src/backend/zuno/platform/services/workspace/wechat_agent.py:45` | `PRODUCT_LEGACY_RUNTIME` | Production caller (`api/services/wechat.py:59`) + `create_agent` + `handler(request)` + `self.model.ainvoke` + `final_answer` |

The repository mode also reports four `direct_handler_bypass` findings
inside the workspace tree (the workspace agents call `await handler(request)`
directly, bypassing `ToolInvocationGateway`).

`AgentControlRuntime`'s class definition still carries
`product_lifecycle_attr` evidence (`trace_events`, `final_answer`,
`PlannerOutput`, etc.), but the verifier does **not** classify a
class-definition-only as blocking any more. As soon as a Production
Entry Point starts importing or constructing `AgentControlRuntime`, the
classification flips to `PRODUCT_LEGACY_RUNTIME` and the repository
status flips to BLOCKED. This is proven by the
`test_agent_control_runtime_production_caller_fixture_is_blocked` test.

`AgentControlRuntime`'s callers today:

- `src/backend/zuno/agent/product_baseline.py` (baseline generator, not
  a Production Entry Point — the verifier excludes it).
- `src/backend/zuno/agent/__init__.py` (facade re-export / TYPE_CHECKING
  import, not a construction).
- `src/backend/zuno/agent/runtime/adapters.py:28` (string literal in a
  `source=` keyword, not a code reference).
- `tests/agent/test_agent_layer_surfaces.py`,
  `tests/agent/test_react_reflection_replan_runtime.py`,
  `tests/repo/test_phase22_backend_semantic_legacy.py` (tests).

See `repository_report.json` for the machine-readable record.

## What thin Product Adapters look like under the new verifier

`tests/fixtures/phase22_backend_semantic_legacy/runtime_definitions/thin_workspace_adapter.py`
defines a `WorkSpaceSimpleAgent` whose `ainvoke` / `astream` methods
delegate to `UnifiedAgentRuntimeService`. It does **not** call
`create_agent`, `model.ainvoke`, `tool.ainvoke`, or
`await handler(request)`. The verifier classifies it as
`PRODUCT_ADAPTER` (allowed) when reached by a production caller.

The mirror-based test
`test_thin_workspace_adapter_in_production_tree_is_not_blocked` replaces
the live `simple_agent.py` with the thin adapter fixture and asserts:

- `WorkSpaceSimpleAgent.classification == "PRODUCT_ADAPTER"`.
- The repository mode emits no finding on `simple_agent.py`.

This pins the verifier contract: once the Workspace cutover wave
replaces `simple_agent.py` with the thin adapter shape, the verifier
will flip to `BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED` without
further verifier changes.

The opposite mirror test
`test_invalid_adapter_in_production_tree_is_blocked` shows that an
adapter that **keeps** a `create_agent(...)` call inside its methods
still classifies as `PRODUCT_LEGACY_RUNTIME`.

## Fixture catalogue

`tests/fixtures/phase22_backend_semantic_legacy/`:

- `runtime_definitions/thin_workspace_adapter.py` — `PRODUCT_ADAPTER`
  shape; delegates to `UnifiedAgentRuntimeService`.
- `runtime_definitions/invalid_adapter_with_create_agent.py` —
  `PRODUCT_LEGACY_RUNTIME`; keeps `create_agent`.
- `runtime_definitions/agent_control_runtime_no_prod_caller.py` —
  `INTERNAL_TEST_HARNESS`; tests-only caller.
- `runtime_definitions/agent_control_runtime_with_prod_caller.py` —
  used together with `production_callers/caller_of_agent_control.py`
  to prove a production caller flips it to `PRODUCT_LEGACY_RUNTIME`.
- `runtime_definitions/react_step_runner.py` — `INTERNAL_STEP_CAPABILITY`.
- `runtime_definitions/structured_response_agent.py` —
  `INTERNAL_STEP_CAPABILITY`.
- `runtime_definitions/direct_model_final_answer.py` —
  `PRODUCT_LEGACY_RUNTIME`; `self.model.ainvoke`.
- `runtime_definitions/direct_tool_ainvoke.py` —
  `PRODUCT_LEGACY_RUNTIME`; `self.tool.ainvoke`.
- `runtime_definitions/direct_handler_await.py` —
  `PRODUCT_LEGACY_RUNTIME`; `await handler(request)`.
- `runtime_definitions/dynamic_runtime_load.py` — drives
  `BACKEND_PRODUCT_RUNTIME_UNRESOLVED`.
- `production_callers/caller_of_agent_control.py` — synthetic
  Production Entry Point that constructs `AgentControlRuntime`.
- `test_callers/test_agent_control_harness.py` — synthetic test caller
  that proves the `tests/` prefix is excluded from production
  reachability.

## Verifier Usage

```
# This PR's slice
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope agent-family

# Full repository runtime cutover (default, fail-closed)
python tools/scripts/verify_phase22_backend_semantic_legacy.py
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope repository

# Machine-readable output
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope agent-family --json
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope repository --json

# Evidence persistence
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope agent-family --report
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope repository --report
```

Workflows that only own the agent-family slice should use
`--scope agent-family`. Default invocation is the repository scope and
is expected to return non-zero (exit 1) until the Workspace cutover
wave finishes its slice.

## Test Coverage

`tests/repo/test_phase22_backend_semantic_legacy.py` — 25 tests:

1. `test_general_agent_family_files_are_gone` — physical file removal.
2. `test_agent_family_scope_returns_clean` — scoped mode emits CLEAN.
3. `test_repository_scope_returns_blocked` — repository mode emits
   BLOCKED with both `legacy_runtime_owner` and `direct_handler_bypass`
   categories, and the workspace agents classified as
   `PRODUCT_LEGACY_RUNTIME`, `AgentControlRuntime` classified as
   `INTERNAL_TEST_HARNESS`.
4. `test_default_mode_does_not_return_scoped_clean` — default mode is
   repository, not scoped.
5. `test_scoped_json_shape_is_stable` — JSON output schema is stable.
6. `test_repository_json_shape_is_stable` — JSON output schema is
   stable and includes `classifications` and `unresolved` keys.
7. `test_scoped_and_repository_status_are_independent` — scoped and
   repository status do not overwrite each other.
8. `test_retired_import_restoration_is_detected` — re-introducing a
   retired import in `main.py` flips scoped status to BLOCKED.
9. `test_thin_workspace_adapter_is_product_adapter` — thin adapter
   classifies as `PRODUCT_ADAPTER`.
10. `test_invalid_adapter_with_create_agent_is_legacy_runtime` —
    invalid adapter classifies as `PRODUCT_LEGACY_RUNTIME`.
11. `test_independent_create_agent_graph_is_blocked` —
    `create_agent(...)` triggers `PRODUCT_LEGACY_RUNTIME`.
12. `test_direct_model_final_answer_is_blocked` —
    `self.model.ainvoke` triggers `PRODUCT_LEGACY_RUNTIME`.
13. `test_direct_tool_ainvoke_is_blocked` — `self.tool.ainvoke`
    triggers `PRODUCT_LEGACY_RUNTIME`.
14. `test_await_handler_request_is_blocked` —
    `response = await handler(request)` triggers
    `PRODUCT_LEGACY_RUNTIME`.
15. `test_agent_control_runtime_with_only_test_callers_is_internal_test_harness`
    — `AgentControlRuntime` with only `tests/` callers classifies as
    `INTERNAL_TEST_HARNESS`.
16. `test_agent_control_runtime_with_production_caller_is_blocked` —
    synthetic production caller flips classification to
    `PRODUCT_LEGACY_RUNTIME`.
17. `test_react_step_runner_is_internal_step_capability` —
    `ReActStepRunner` is step-internal.
18. `test_structured_response_agent_is_internal_step_capability` —
    `StructuredResponseAgent` is step-internal.
19. `test_dynamic_runtime_load_is_unresolved` — `getattr` /
    `__import__` in production code forces
    `BACKEND_PRODUCT_RUNTIME_UNRESOLVED`.
20. `test_tool_invocation_gateway_is_not_misclassified` — canonical
    gateway path is not flagged.
21. `test_direct_handler_request_in_workspace_is_blocked` —
    `direct_handler_bypass` category is detected and confined to the
    workspace tree.
22. `test_repository_scope_without_workspace_agents_keeps_blocked` —
    removing the workspace files flips `AgentControlRuntime`
    classification back to `INTERNAL_TEST_HARNESS`.
23. `test_thin_workspace_adapter_in_production_tree_is_not_blocked` —
    replacing `simple_agent.py` with the thin adapter fixture drops
    the WorkSpaceSimpleAgent finding.
24. `test_invalid_adapter_in_production_tree_is_blocked` —
    replacing `simple_agent.py` with the invalid adapter fixture
    keeps the BLOCKED status.
25. `test_agent_control_runtime_production_caller_fixture_is_blocked`
    — replacing the live repo with the production-caller fixture flips
    `AgentControlRuntime` classification to `PRODUCT_LEGACY_RUNTIME`.

## Test Run Results (this slice)

`pytest -q tests/repo/test_phase22_backend_semantic_legacy.py`
→ **25 passed in 129.54s**.

## Out of Scope (read-only)

- `workspace/simple_agent.py`, `workspace/wechat_agent.py`
- `phase08_cutover.py`
- `workspace_task_runtime.py` (Phase08 config block)
- `zuno.agent.control_runtime` and `zuno.agent.product_baseline`
- Backend code under `src/backend/zuno/`

These surfaces are pinned by the repository mode of the verifier and
are owned by parallel cutover waves.

## What this slice did NOT consume

- PR #129 (workspace-agent-cutover) — not merged, not cherry-picked.
  The thin-adapter behaviour is proven only by mirror tests against
  fixtures; the live Workspace cutover is owned by the parallel worker.
- PR #124/#128 — not consumed.
- The production code paths under `src/backend/zuno/`. No production
  source file was modified by this slice.