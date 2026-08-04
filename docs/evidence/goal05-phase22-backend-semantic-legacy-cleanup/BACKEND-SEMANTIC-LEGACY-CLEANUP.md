# PHASE22 Backend Semantic Legacy Cleanup — Evidence (Dual Scope)

Work package: `PHASE22-BACKEND-LEGACY-SCOPED-TRUTH-FINAL`
Worker: `minimax-legacy-truth` (Execution-Client: Claude Code, Provider: MiniMax)
Base: `origin/main` @ `83c1bbd0` — Branch: `claude/deepseek-phase22-backend-semantic-legacy-cleanup`
Head (start): `b57c1566c711c8c66943f97d231fbc57779042a3`

## Two-Layer Truth

This slice separates the PR's own retirement of the GeneralAgent family
from the full Backend Product Runtime cutover. The previous verifier
collapsed both layers into a single "BACKEND_SEMANTIC_LEGACY_CLEAN" status
even while Workspace agents and `AgentControlRuntime` were still live.
That collapsed truth was masking known bypasses.

### Scoped Result (this PR's own retirement)

**Status:** `AGENT_FAMILY_LEGACY_SLICE_CLEAN`

The PR successfully retired the entire GeneralAgent family
(`GeneralAgent`, `AgentConfig`, `StreamAgentState`, `EmitEventAgentMiddleware`,
`ReactAgent`, `PlanExecuteAgent`, `CodeActAgent`, `Text2SQLAgent`) and the
three legacy export shims (`agent/runtime.py`, `agent/state.py`,
`agent/streaming.py`). No production entry point can import a retired
module, and the agent package `__all__` no longer re-exports any retired
symbol.

See `scoped_report.json` for the machine-readable record.

### Repository Result (full Backend Product Runtime cutover)

**Status:** `BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED`

The Single Controller is **not yet** the only top-level Product Runtime
in the repository. The following live surfaces continue to host a
top-level runtime class or a direct tool-call bypass:

| Surface | Category | Detail |
|---|---|---|
| `src/backend/zuno/agent/control_runtime.py:50` | top_level_runtime_class_definition | `AgentControlRuntime` class still present |
| `src/backend/zuno/platform/services/workspace/simple_agent.py:122` | top_level_runtime_class_definition | `WorkSpaceSimpleAgent` class still present |
| `src/backend/zuno/platform/services/workspace/simple_agent.py:1121` | workspace_bypass | `await handler(request)` direct tool call |
| `src/backend/zuno/platform/services/workspace/simple_agent.py:1198` | workspace_bypass | `await handler(request)` direct tool call |
| `src/backend/zuno/platform/services/workspace/wechat_agent.py:132` | workspace_bypass | `await handler(request)` direct tool call |
| `src/backend/zuno/platform/services/workspace/wechat_agent.py:135` | workspace_bypass | `await handler(request)` direct tool call |

These findings are pinned by the repository mode of
`verify_phase22_backend_semantic_legacy.py` so the cutover wave cannot
silently regress. The owner of these surfaces is the workspace cutover
wave (out of scope for this PR).

See `repository_report.json` for the machine-readable record.

## Why the previous truth was wrong

The previous verifier reported `BACKEND_SEMANTIC_LEGACY_CLEAN` whenever
no symbol from the retired family was found, regardless of whether other
top-level runtime classes still existed. It also relied on string
matching for `direct_answer` and `ZUNO_AGENT_RUNTIME`, which made the gate
susceptible to refactors that hide the keyword inside a constant or a
docstring.

The new verifier:

- Uses the Python `ast` module exclusively for production-code checks.
- Inspects every `ClassDef` for the top-level Product Runtime shapes
  (`SingleControllerRuntimeHarness`, `WorkSpaceSimpleAgent`, `WechatAgent`,
  `AgentControlRuntime`).
- Inspects every `Call` node for the direct `await handler(request)`
  pattern by AST shape, not by string.
- Reports `BACKEND_PRODUCT_RUNTIME_UNRESOLVED` when a dynamic
  construction (`globals()[...]`, `getattr(..., 'AgentName')`,
  `eval(...)`, `__import__(...)`) is found, because the verifier cannot
  prove which class is built.
- Defaults to `--scope repository` so the CI gate is fail-closed.

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
`--scope agent-family`. Default invocation is the repository scope and is
expected to return non-zero (exit 1) until the workspace cutover wave
finishes its slice.

## Test Coverage

`tests/repo/test_phase22_backend_semantic_legacy.py` — 14 tests covering:

1. `test_general_agent_family_files_are_gone` — physical file removal.
2. `test_agent_family_scope_returns_clean` — scoped mode emits CLEAN.
3. `test_repository_scope_returns_blocked` — repository mode emits BLOCKED.
4. `test_repository_scope_would_return_confirmed_without_workspace_agents` — mirror-based confirmation that removing the workspace agents drops the workspace findings (and only the `AgentControlRuntime` finding remains).
5. `test_unknown_dynamic_runtime_returns_unresolved` — fake `getattr(__import__(...))` flips status to UNRESOLVED.
6. `test_direct_handler_request_is_blocked` — workspace bypass category is detected and is confined to the workspace tree.
7. `test_tool_invocation_gateway_is_not_misclassified` — canonical gateway is not flagged.
8. `test_structured_response_agent_is_internal_step_capability` — retained internal step capability is not classified as a top-level runtime finding.
9. `test_react_step_runner_is_step_internal` — ReAct remains a step-internal mechanism.
10. `test_agent_control_runtime_with_production_caller_returns_blocked` — `AgentControlRuntime` definition is surfaced.
11. `test_agent_control_runtime_history_only_when_no_production_caller` — moving the production caller under `tests/agent/history_only/` drops the AgentControlRuntime finding.
12. `test_default_mode_does_not_return_scoped_clean` — default mode is repository, not scoped.
13. `test_scoped_json_shape_is_stable` — JSON output schema is stable.
14. `test_repository_json_shape_is_stable` — JSON output schema is stable.

## PR Body Truth

The PR #127 body has been updated to reflect the two-layer result:

- **Scoped Result:** `AGENT_FAMILY_LEGACY_SLICE_CLEAN`
- **Repository Result:** `BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED`

The PR body no longer claims:

- `BACKEND_SEMANTIC_LEGACY_CLEAN`
- "Single Controller is the only top-level product runtime"
- "All clean" for the workspace cutover

The PR body's `Agent-Mode` is `Standard`, matching the real commit
trailers; `Worker` identity is preserved via the `Agent-Name` / `Worker`
trailers.

## Test Run Results (this slice)

`pytest -q tests/repo/test_phase22_backend_semantic_legacy.py`
→ **14 passed in 144.05s**.

The wider repository pytest run is left as-is (10 pre-existing failures
proved against `origin/main` in the prior slice).

## Out of Scope (read-only)

- `workspace/simple_agent.py`, `workspace/wechat_agent.py`
- `phase08_cutover.py`
- `workspace_task_runtime.py` (Phase08 config block)
- `zuno.agent.control_runtime` and `zuno.agent.product_baseline`
- Backend code under `src/backend/zuno/`

These surfaces are pinned by the repository mode of the verifier and are
owned by parallel cutover waves.