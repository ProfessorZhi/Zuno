# PHASE22 Backend Semantic Legacy Cleanup — Evidence (Dual Scope)

Work package: `PHASE22-PR127-OWNERSHIP-REACHABILITY-FAIL-CLOSED-FINAL`
Worker: `minimax2` (Execution-Client: Claude Code, Provider: MiniMax)
Base: `origin/main` @ `83c1bbd0` — Branch: `claude/deepseek-phase22-backend-semantic-legacy-cleanup`
Head (start): `c150aa1f27988f78d2f51b3433dfc5418c03d841`
Head (this slice): the new commit on top of `c150aa1f`.

## What this slice changes

This slice closes the **fail-open** classification decision in the
verifier. The previous `classify_class()` decision tree
auto-classified any class with a production caller and no detected
legacy evidence as `PRODUCT_ADAPTER` (allowed). That is fail-open:
a class that the verifier does not recognise silently passes as a
Product Adapter even when its ownership and reachability cannot be
proven.

This slice:

  1. Introduces the `UNRESOLVED` verdict for the fail-closed case:
     production caller + no legacy evidence + no canonical delegation
     → `UNRESOLVED` (repository scope exits non-zero).
  2. Extends `_production_callers_for()` to detect:
     - direct `ClassName(...)` calls
     - module-qualified `module.ClassName(...)` calls
     - module-alias-qualified `alias.ClassName(...)` calls
     - `from x import ClassName as Alias` followed by `Alias(...)`
     - module-level `LocalName = ClassName` followed by `LocalName(...)`
  3. Extends `_evidence_for_class()` to detect the thin-adapter
     delegation pattern (`self.<attr>.<method>(...)` where the
     attribute is NOT a model / tool locator and the method is a
     known runtime entry point) — this is the canonical_delegate
     evidence that the thin adapter must produce.
  4. Adds `UNRESOLVED` status handling to the repository scope:
     any class classified as `UNRESOLVED` (or any dynamic-loader
     construction site) forces `BACKEND_PRODUCT_RUNTIME_UNRESOLVED`.
  5. Adds new fixtures and tests covering all alias / qualified /
     factory / UNRESOLVED cases.

The decision tree is now:

| Step | Classified as |
|---|---|
| `INTERNAL_STEP_CAPABILITY_CLASSES` membership | `INTERNAL_STEP_CAPABILITY` (allowed) |
| Class name is `SingleControllerRuntimeHarness` | `PRODUCT_CANONICAL` (allowed) |
| No production caller | `INTERNAL_TEST_HARNESS` (allowed) |
| Production caller + any legacy evidence | `PRODUCT_LEGACY_RUNTIME` (BLOCKED) |
| Production caller + `canonical_delegate` evidence + no legacy | `PRODUCT_ADAPTER` (allowed) |
| Production caller + no `canonical_delegate` + no legacy | `UNRESOLVED` (BLOCKED via non-zero exit) |
| Dynamic construction (`globals`, `getattr`, `eval`, `__import__`, `import_module`, `locals`, `vars`) with an `Agent`/`Runtime`/`Controller`/`Service`/`Harness`/`Factory` token | repository scope → `BACKEND_PRODUCT_RUNTIME_UNRESOLVED` (non-zero exit) |

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
| `WorkSpaceSimpleAgent` | `src/backend/zuno/platform/services/workspace/simple_agent.py:122` | `PRODUCT_LEGACY_RUNTIME` | Production caller + `create_agent` + `handler(request)` + `self.model.ainvoke` + `tool.ainvoke` + `final_answer` |
| `WeChatAgent` | `src/backend/zuno/platform/services/workspace/wechat_agent.py:45` | `PRODUCT_LEGACY_RUNTIME` | Production caller + `create_agent` + `handler(request)` + `self.model.ainvoke` + `final_answer` |

The repository mode also reports four `direct_handler_bypass` findings
inside the workspace tree (the workspace agents call `await handler(request)`
directly, bypassing `ToolInvocationGateway`).

No `UNRESOLVED` findings are emitted on the live branch because both
`WorkSpaceSimpleAgent` and `WeChatAgent` carry legacy markers
(`create_agent`, `self.model.ainvoke`, `await handler(request)`) and
therefore classify as `PRODUCT_LEGACY_RUNTIME` before the
fail-closed path runs.

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

A thin Product Adapter must produce `canonical_delegate` evidence
inside its methods. The verifier recognises two shapes:

1. **Symbol references**: `UnifiedAgentRuntimeService`,
   `SingleControllerRuntimeHarness`, `SingleControllerDurableRuntime`,
   `WorkspaceAgentRuntime`, `WorkspaceTaskRuntimeService`.
2. **Method delegation**: `self.<attr>.<method>(...)` where the
   attribute is NOT a model / tool locator and the method is a known
   runtime entry point (`start`, `stream`, `astream`, `astream_events`,
   `run`, `run_step`, `execute`, `drive`).

The mirror-based test
`test_thin_workspace_adapter_in_production_tree_is_not_blocked` replaces
the live `simple_agent.py` with the thin adapter fixture and asserts:

- `WorkSpaceSimpleAgent.classification == "PRODUCT_ADAPTER"`.
- The repository mode emits no finding on `simple_agent.py`.

This pins the verifier contract: once the Workspace cutover wave
replaces `simple_agent.py` with the thin adapter shape, the verifier
will flip to `BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED` without
further verifier changes.

The opposite mirror test `test_invalid_adapter_in_production_tree_is_blocked`
shows that an adapter that **keeps** a `create_agent(...)` call inside
its methods still classifies as `PRODUCT_LEGACY_RUNTIME`.

The mirror test `test_thin_canonical_adapter_classifies_as_product_adapter`
asserts that the `candidate_constructor` fixture (which uses the
method-delegation pattern) classifies as `PRODUCT_ADAPTER`.

The mirror test `test_assignment_alias_to_non_delegate_is_unresolved`
asserts that a class reached through a static assignment alias
(`Runtime = WorkSpaceSimpleAgent`) but with no `canonical_delegate`
evidence classifies as `UNRESOLVED`.

## Fixture catalogue

`tests/fixtures/phase22_backend_semantic_legacy/`:

### Runtime definitions

- `thin_workspace_adapter.py` — `PRODUCT_ADAPTER` shape; delegates to
  `UnifiedAgentRuntimeService` via method delegation.
- `candidate_constructor.py` — `PRODUCT_ADAPTER` shape; uses the
  `self._unified.start(...)` / `self._unified.stream(...)` method
  delegation pattern.
- `candidate_constructor_unknown.py` — `UNRESOLVED` shape; reached by
  a production caller but has no `canonical_delegate` evidence and no
  legacy evidence.
- `no_canonical_delegate_unknown.py` — same as above.
- `invalid_adapter_with_create_agent.py` — `PRODUCT_LEGACY_RUNTIME`;
  keeps `create_agent`.
- `agent_control_runtime_no_prod_caller.py` — `INTERNAL_TEST_HARNESS`;
  tests-only caller.
- `agent_control_runtime_with_prod_caller.py` — used together with
  `production_callers/caller_of_agent_control.py` to prove a production
  caller flips it to `PRODUCT_LEGACY_RUNTIME`.
- `react_step_runner.py` — `INTERNAL_STEP_CAPABILITY`.
- `structured_response_agent.py` — `INTERNAL_STEP_CAPABILITY`.
- `direct_model_final_answer.py` — `PRODUCT_LEGACY_RUNTIME`;
  `self.model.ainvoke`.
- `direct_tool_ainvoke.py` — `PRODUCT_LEGACY_RUNTIME`; `self.tool.ainvoke`.
- `direct_handler_await.py` — `PRODUCT_LEGACY_RUNTIME`;
  `await handler(request)`.
- `dynamic_runtime_load.py` — drives `BACKEND_PRODUCT_RUNTIME_UNRESOLVED`
  via `getattr` / `__import__`.
- `factory_constructor.py` — drives `UNRESOLVED` via a factory function
  whose return type cannot be resolved statically.
- `getattr_runtime.py` — drives `UNRESOLVED` via `getattr` /
  `__import__` token matching.

### Production callers

- `caller_of_agent_control.py` — synthetic Production Entry Point that
  constructs `AgentControlRuntime`.
- `caller_with_import_alias.py` — `from x import WorkSpaceSimpleAgent as Agent`
  followed by `Agent(...)`.
- `caller_with_qualified_constructor.py` — `module.WorkSpaceSimpleAgent(...)`.
- `caller_with_module_alias.py` — `import module as runtime_module`
  followed by `runtime_module.WorkSpaceSimpleAgent(...)`.
- `caller_with_assignment_alias.py` — `Runtime = WorkSpaceSimpleAgent`
  followed by `Runtime(...)`.
- `caller_with_assignment_alias_unknown.py` — same shape but using the
  no-delegate candidate (drives `UNRESOLVED`).
- `caller_with_import_alias_unknown.py` — same shape but using the
  no-delegate candidate (drives `UNRESOLVED`).

### Test callers

- `test_agent_control_harness.py` — synthetic test caller that proves
  the `tests/` prefix is excluded from production reachability.

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

`tests/repo/test_phase22_backend_semantic_legacy.py` — 42 tests:

### Slice tests (agent-family retirement)

1. `test_general_agent_family_files_are_gone` — physical file removal.
2. `test_agent_family_scope_returns_clean` — scoped mode emits CLEAN.
3. `test_default_mode_does_not_return_scoped_clean` — default mode is
   repository, not scoped.
4. `test_scoped_json_shape_is_stable` — JSON output schema is stable.
5. `test_scoped_and_repository_status_are_independent` — scoped and
   repository status do not overwrite each other.
6. `test_retired_import_restoration_is_detected` — re-introducing a
   retired import in `main.py` flips scoped status to BLOCKED.

### Repository baseline tests

7. `test_repository_scope_returns_blocked` — repository mode emits
   BLOCKED with both `legacy_runtime_owner` and `direct_handler_bypass`
   categories, and the workspace agents classified as
   `PRODUCT_LEGACY_RUNTIME`, `AgentControlRuntime` classified as
   `INTERNAL_TEST_HARNESS`.
8. `test_repository_json_shape_is_stable` — JSON output schema is
   stable and includes `classifications` and `unresolved` keys.
9. `test_tool_invocation_gateway_is_not_misclassified` — canonical
   gateway path is not flagged.
10. `test_direct_handler_request_in_workspace_is_blocked` —
    `direct_handler_bypass` category is detected and confined to the
    workspace tree.
11. `test_repository_scope_without_workspace_agents_keeps_blocked` —
    removing the workspace files flips `AgentControlRuntime`
    classification back to `INTERNAL_TEST_HARNESS`.
12. `test_thin_workspace_adapter_in_production_tree_is_not_blocked` —
    replacing `simple_agent.py` with the thin adapter fixture drops
    the WorkSpaceSimpleAgent finding.
13. `test_invalid_adapter_in_production_tree_is_blocked` —
    replacing `simple_agent.py` with the invalid adapter fixture
    keeps the BLOCKED status.
14. `test_agent_control_runtime_production_caller_fixture_is_blocked`
    — replacing the live repo with the production-caller fixture flips
    `AgentControlRuntime` classification to `PRODUCT_LEGACY_RUNTIME`.

### Behaviour fixtures (verifier API)

15. `test_thin_workspace_adapter_is_product_adapter` — thin adapter
    classifies as `PRODUCT_ADAPTER`.
16. `test_invalid_adapter_with_create_agent_is_legacy_runtime` —
    invalid adapter classifies as `PRODUCT_LEGACY_RUNTIME`.
17. `test_independent_create_agent_graph_is_blocked` —
    `create_agent(...)` triggers `PRODUCT_LEGACY_RUNTIME`.
18. `test_direct_model_final_answer_is_blocked` —
    `self.model.ainvoke` triggers `PRODUCT_LEGACY_RUNTIME`.
19. `test_direct_tool_ainvoke_is_blocked` — `self.tool.ainvoke`
    triggers `PRODUCT_LEGACY_RUNTIME`.
20. `test_await_handler_request_is_blocked` —
    `response = await handler(request)` triggers
    `PRODUCT_LEGACY_RUNTIME`.
21. `test_agent_control_runtime_with_only_test_callers_is_internal_test_harness`
    — `AgentControlRuntime` with only `tests/` callers classifies as
    `INTERNAL_TEST_HARNESS`.
22. `test_agent_control_runtime_with_production_caller_is_blocked` —
    synthetic production caller flips classification to
    `PRODUCT_LEGACY_RUNTIME`.
23. `test_react_step_runner_is_internal_step_capability` —
    `ReActStepRunner` is step-internal.
24. `test_structured_response_agent_is_internal_step_capability` —
    `StructuredResponseAgent` is step-internal.
25. `test_dynamic_runtime_load_is_unresolved` — `getattr` /
    `__import__` in production code forces
    `BACKEND_PRODUCT_RUNTIME_UNRESOLVED`.

### Fail-closed semantic (this slice)

26. `test_thin_canonical_adapter_classifies_as_product_adapter` — thin
    canonical adapter with method-delegation pattern classifies as
    `PRODUCT_ADAPTER`.
27. `test_production_class_without_canonical_delegate_is_unresolved` —
    production caller + no canonical_delegate + no legacy →
    `UNRESOLVED` (fail-closed).
28. `test_import_alias_constructor_is_recognised` —
    `from x import WorkSpaceSimpleAgent as Agent` then `Agent(...)` is
    classified as `PRODUCT_ADAPTER`.
29. `test_module_qualified_constructor_is_recognised` —
    `module.WorkSpaceSimpleAgent(...)` is classified as
    `PRODUCT_ADAPTER`.
30. `test_module_alias_constructor_is_recognised` —
    `alias.WorkSpaceSimpleAgent(...)` is classified as
    `PRODUCT_ADAPTER`.
31. `test_assignment_alias_resolves_to_candidate` — module-level
    `Runtime = WorkSpaceSimpleAgent` resolves to the candidate.
32. `test_assignment_alias_to_non_delegate_is_unresolved` — same alias
    shape but the candidate has no `canonical_delegate` →
    `UNRESOLVED`.
33. `test_factory_constructor_is_unresolved` — factory function
    `make_agent()` that returns a `WorkSpaceSimpleAgent` is
    `UNRESOLVED`.
34. `test_getattr_dynamic_runtime_is_unresolved` — `getattr` /
    `__import__` that targets a runtime class is `UNRESOLVED`.
35. `test_direct_model_call_classification` — re-pinned DIRECT_MODEL.
36. `test_direct_tool_call_classification` — re-pinned DIRECT_TOOL.
37. `test_independent_graph_classification` — re-pinned
    INDEPENDENT_GRAPH.
38. `test_only_test_callers_yields_internal_test_harness` — re-pinned
    test-only.
39. `test_production_caller_agent_control_runtime_is_legacy` —
    re-pinned production caller.
40. `test_repository_unresolved_exits_one` — repository UNRESOLVED
    exits 1.
41. `test_repository_blocked_exits_one` — repository BLOCKED exits 1.
42. `test_repository_confirmed_exits_zero` — repository CONFIRMED
    exits 0.

## Test Run Results (this slice)

`pytest -q tests/repo/test_phase22_backend_semantic_legacy.py`
→ **42 passed in 681.07s**.

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