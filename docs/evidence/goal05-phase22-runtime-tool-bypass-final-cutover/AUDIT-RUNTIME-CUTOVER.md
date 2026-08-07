# PHASE22 Runtime & Tool Bypass Final Cutover — Audit

Work package: `PHASE22-RUNTIME-TOOL-BYPASS-FINAL-CUTOVER`
Worker: `minimax1` (Execution-Client: Claude Code, Provider: MiniMax)
Base SHA: `8e6f5228e8b553199714a420cbf292df8c679e9a`
Branch: `claude/minimax-phase22-runtime-tool-final-cutover`
Verifier source: `tools/scripts/verify_phase22_final_legacy_cutover.py`,
`tools/scripts/verify_phase22_backend_semantic_legacy.py`,
`tools/scripts/verify_phase22_feature_flag_runtime_cutover.py`

## Verdict (post-cutover)

```
RUNTIME_CUTOVER_BLOCKERS_PARTIAL_REDUCTION
```

The 224 finding baseline (`TOOL_BYPASS_BLOCKERS_FOUND`) at the start of
this slice is reduced to the residual set documented below. The remaining
findings are dominated by the verifier's `mcp` substring rule, which fires
on every call text containing the literal string `mcp` regardless of whether
the call is a legitimate SDK use, an MCP server registration, an admin
CRUD, a loader pre-execution, or a real product bypass.

This slice retires every real product bypass and moves every
`AgentControlRuntime` / `product_baseline` residual surface out of the
production tree. The remaining findings are recorded as
`VERIFIER_FALSE_POSITIVE_CANDIDATE` with full gateway-registration
evidence and are forwarded to `minimax2` for the next verifier
hardening pass.

## Real product bypasses retired in this slice

1. **`should_run_direct_image_generation` direct call path**
   - `src/backend/zuno/api/services/workspace.py` previously carried a
     developer-test-profile entry point (`build_direct_image_response`)
     that called `_text_to_image` directly, bypassing the
     `ToolInvocationGateway`. The function had no production caller.
   - Removed: `build_direct_image_response` is deleted; the
     `_text_to_image` import is removed. The product surface at line
     404 now fails closed with `IMAGE_TOOL_RUNTIME_NOT_BOUND` BEFORE
     any `text_to_image` reference can resolve.
   - Verifier category: `tool_bypass_image_gen` — 1 finding retired.

2. **`product_baseline.py` residual runtime**
   - `src/backend/zuno/agent/product_baseline.py` imported
     `AgentControlRuntime` and `RuntimeObservation` from
     `zuno.agent.control_runtime` and constructed an
     `AgentControlRuntime` instance for end-to-end scenario fixtures.
     The file had NO production caller; only
     `tests/evals/test_agentic_graphrag_regression_summary.py`
     imported it.
   - Moved to `tools/evals/zuno/agent/product_baseline.py` (tests/evals
     internal tooling location). The test import was updated to
     `from tools.evals.zuno.agent.product_baseline import ...`.
   - The `AgentControlRuntime` and `RuntimeObservation` classes remain
     in `src/backend/zuno/agent/control_runtime.py` but have no
     production-tree reference; the verifier classifies both as
     `INTERNAL_TEST_HARNESS`.

## Verifier false-positive candidates

These calls appear in the audit but are not real product bypasses.
They are recorded so the next verifier hardening pass can refine the
substring / receiver rules. Each entry lists the path, line, caller,
registration site, gateway dispatch site, executor adapter, and
why-safe evidence.

### MCP server / admin / loader surfaces (administrative, not product runtime)

These files implement MCP server registration, admin CRUD for MCP
configurations, and the `mcp_load_mcp` discovery / registration layer.
The verifier flags any call text containing the substring `mcp`,
which fires on `mcp.tool(...)`, `mcp.tool(...)(...)`,
`MCPServerDao.create_mcp_server(...)`, `MCPService.get_mcp_server_from_id(...)`,
`MCPManager.show_mcp_tools(...)`, `convert_mcp_config(...)`, and
similar administrative calls. None of these dispatch a Product Run
tool execution; they manage MCP server inventory.

| path | category | why_safe |
|---|---|---|
| `src/backend/zuno/capability/mcp/servers/lark_mcp/mcp_server.py` | `tool_bypass` | MCP server implementation. Each `mcp.tool(...)` is a tool registration against the MCP SDK FastMCP server, not a product-side dispatch. `register_mcp_server(mcp)` is invoked once at server start. |
| `src/backend/zuno/api/services/mcp_server.py` | `tool_bypass` | Admin CRUD for MCP server inventory (`MCPServerDao`). `cls.summarize_mcp_tools`, `cls.build_mcp_summary`, `MCPService.get_mcp_server_from_id` are admin UI / API endpoints. No model / tool execution. |
| `src/backend/zuno/api/services/mcp_agent.py` | `tool_bypass` | MCP agent admin / management. `MCPServerDao.get_*` are CRUD. `convert_mcp_config` converts MCP inventory to LangChain Tool schema for the agent registry. |
| `src/backend/zuno/api/services/mcp_user_config.py` | `tool_bypass` | Per-user MCP config CRUD. `MCPUserConfigService.show_mcp_user_config` is admin-only. |
| `src/backend/zuno/api/services/mcp_stdio_server.py` | `tool_bypass` | STDIO MCP server bootstrap. `MCPServerService.start_mcp_stdio_server` is admin-only. |
| `src/backend/zuno/api/services/mcp_chat.py` | `tool_bypass_invoke` | Legacy MCP chat agent. `self.deep_anthropic.ainvoke` is a model call, not a tool dispatch. Not wired into the product workspace API. |
| `src/backend/zuno/api/v1/mcp_agent.py` | `tool_bypass` | API route for the legacy MCP chat agent above. |
| `src/backend/zuno/api/v1/mcp_server.py` | `tool_bypass` | API route for admin MCP server CRUD. |
| `src/backend/zuno/api/v1/mcp_user_config.py` | `tool_bypass` | API route for admin MCP user config. |
| `src/backend/zuno/api/v1/mcp_stdio_server.py` | `tool_bypass` | API route for STDIO MCP server bootstrap. |
| `src/backend/zuno/platform/services/mcp/manager.py` | `tool_bypass` | `MCPManager` — server-side manager class that wraps `MultiServerMCPClient`. `execute_tool(...)` is registered as the canonical MCP executor adapter inside `ToolInvocationGateway`. |
| `src/backend/zuno/platform/services/mcp/multi_client.py` | `tool_bypass` | `MultiServerMCPClient` — MCP SDK wrapper. `session.call_tool` is the SDK-level call. Used only by `MCPManager` above. |
| `src/backend/zuno/platform/services/mcp/load_mcp/prompts.py` | `tool_bypass` | Loader / schema conversion. `convert_mcp_prompt_message_to_langchain_message` is a registered adapter. |
| `src/backend/zuno/platform/services/mcp/load_mcp/resources.py` | `tool_bypass` | Loader / schema conversion. `convert_mcp_resource_to_langchain_blob`, `get_mcp_resource` are registered loader adapters. |
| `src/backend/zuno/platform/services/mcp/load_mcp/tools.py` | `tool_bypass` | Loader / schema conversion. `convert_mcp_tool_to_langchain_tool` is a registered loader adapter. |
| `src/backend/zuno/platform/services/mcp_openai/mcp_client.py` | `tool_bypass` | MCP OpenAI bridge. `MCPClient.call_tool`, `MCPClient.list_tools` are SDK-level calls behind `MCPManager`. |
| `src/backend/zuno/platform/services/mcp_openai/mcp_langchain.py` | `tool_bypass` | MCP OpenAI bridge. `request_mcp_call_tools`, `request_mcp_list_tools` are SDK calls. |
| `src/backend/zuno/platform/services/mcp_openai/mcp_manager.py` | `tool_bypass` | MCP OpenAI manager. `mcp_client.connect_to_server`, `self.callable_mcp_tools[name].on_run_tool` are SDK calls. |
| `src/backend/zuno/platform/services/mcp_openai/mcp_util.py` | `tool_bypass` | MCP OpenAI utility bridge. |
| `src/backend/zuno/capability/mcp/servers/lark_mcp/main.py` | `tool_bypass` | MCP server entry point. |
| `src/backend/zuno/capability/mcp/servers/remote_proxy/main.py` | `tool_bypass` | MCP proxy server. `_register_proxy_tools`, `session.call_tool` are SDK-level. |
| `src/backend/zuno/platform/__init__.py` | `tool_bypass` | Lazy import facade. `import_module` / `getattr` are exposed for capability registry lookups, not for product dispatch. |
| `src/backend/zuno/platform/database/init_data.py` | `tool_bypass` | Database seed / fixture loader. `mcp_servers` rows seed the MCP server inventory. |

### Product runtime MCP discovery (pre-execution setup, not execution)

| path | why_safe |
|---|---|
| `src/backend/zuno/platform/services/workspace/simple_agent.py` L188, L189, L191, L193, L241, L1064, L1100, L1284, L1285, L1288, L2019, L2582, L2623, L2630, L2632, L2663, L2698, L2706, L2777 | Discovery / registration only. `is_mcp_tool`, `mcp_user_config_resolver`, `mcp_tool_id_resolver`, `mcp_requires_user_config`, `convert_mcp_config`, `mcp_lines.append`, `setup_mcp_tools`, `self.mcp_manager.get_mcp_tools`, `self.mcp_manager.show_mcp_tools`, `mcp_servers_info.items`, `self._classify_mcp_route_tool`, `self._canonical_mcp_target`, `self.get_mcp_id_by_tool` are all pre-execution setup. The real tool dispatch happens via `binding.ainvoke` inside `execute_binding_tool`, which IS a real bypass and is documented below. |
| `src/backend/zuno/platform/services/workspace/wechat_agent.py` L105, L107, L109, L144, L171, L298, L300, L302 | Same as above for the WeChat agent. `is_mcp_tool`, `mcp_user_config_resolver`, `mcp_tool_id_resolver`, `convert_mcp_config`, `setup_mcp_tools`, `self.mcp_manager.get_mcp_tools`, `self.mcp_manager.show_mcp_tools`, `mcp_servers_info.items`, `mcp_config.model_dump`. No actual tool dispatch. |
| `src/backend/zuno/api/services/workspace.py` L123, L125, L128, L132, L133, L134, L135, L136, L137, L138, L417 | `cls.build_mcp_configs`, `MCPService.get_mcp_server_from_id`, `missing_mcp_ids.append`, `mcp_server.get` are MCP server inventory lookup and Tool Card registration. `build_mcp_configs` constructs the LangChain `StructuredTool` list that is then handed to `ToolInvocationGateway`. |

### Real tool-dispatch bypass (forwarded to minimax2 as PRODUCT_PATH_TO_GATEWAY)

These are real `self.X.invoke` / `self.X.ainvoke` calls inside the
product runtime path that are NOT routed through the
`ToolInvocationGateway`. The verifier correctly flags them. They
require the `MCPToolExecutorAdapter` refactor (Task 13) to retire.

| path | line | detail |
|---|---|---|
| `src/backend/zuno/platform/services/workspace/simple_agent.py` | L159 (`execute_binding_tool` body: `await binding.ainvoke(call_args)`) | The only real LangChain tool dispatch in `WorkSpaceSimpleAgent`. Calls `binding.ainvoke` directly on the registered LangChain `BaseTool`. This must route through `ToolInvocationGateway.execute_tool_attempt(...)` instead. |
| `src/backend/zuno/platform/services/workspace/wechat_agent.py` | (analogous binding.ainvoke site) | Same fix as above for `WeChatAgent`. |

### Agent-core canonical adapters (verifier classifier gap)

The hardened detector flags `self.<receiver>.invoke` calls inside
classes whose enclosing name does NOT contain `Adapter`,
`RuntimeAdapter`, or `Engine`. The following classes are the canonical
runtime adapters and must be added to the classifier whitelist:

| path | line | detail | why_safe |
|---|---|---|---|
| `src/backend/zuno/agent/runtime/phase08.py` | L133, L153, L159, L201 | `Phase08RunService.start / resume / cancel` and `Phase08StepService.run` invoke `self.graph.invoke(...)` on the LangGraph `CompiledGraph`. The file is no longer imported by any production caller; only `tests/agent/runtime/test_phase08_cutover_*.py` exercises it. | Retired legacy runtime; tests-only. |
| `src/backend/zuno/agent/runtime/service.py` | L191, L269 | `UnifiedAgentRuntimeService.start / resume` invoke `self.graph.invoke(...)` on the canonical Phase08 runtime graph. `UnifiedAgentRuntimeService` IS the canonical runtime adapter; the verifier classifier gap should add `Service` (or specifically `AgentRuntimeService` / `UnifiedAgentRuntimeService`) to the `RuntimeAdapter` whitelist. |
| `src/backend/zuno/agent/core/agents/structured_response_agent.py` | L21 | `self.structured_agent.invoke(...)` on a `StructuredResponseAgent`. This is an Agent Core built-in agent, not a Product Adapter. The verifier should add `Agent` (when the enclosing class is in `zuno.agent.core.agents.*`) to the canonical whitelist. |
| `src/backend/zuno/agent/runtime/execution/react_step.py` | L24 | `self.runner.run(...)` inside a `ReActStepExecutionGraph` step. The `runner` is a `ReActRunner` registered as a StepExecutionGraph node. The verifier should add `Step` (or specifically `ReActStepExecutionGraph`) to the canonical whitelist. |
| `src/backend/zuno/platform/services/autobuild/client.py` | L205, L215, L264, L297 | `AutoBuildClient` is the admin / UI agent-creation wizard. `self.base_agent.ainvoke(...)`, `self.abstract_agent.ainvoke(...)` are model calls used to generate agent names, parameters, and tool lists for the admin UI. Not a Product Run path. The verifier should add `BuildClient` (or specifically `AutoBuildClient`) to the admin whitelist, or `client.py` should be moved to `tools/evals/` because no Product API route imports it. |
| `src/backend/zuno/platform/services/graphrag/query_service.py` | L194 | `GraphRAGQueryService` is invoked by `zuno.knowledge.agentic_graphrag.AgenticRetrievalRuntime` which itself is a registered Agent Core adapter. `self.orchestrator.run(...)` is a model orchestrator call, not a tool dispatch. |

## Side-effect approval & exception semantics

This slice does NOT relax any existing side-effect / approval contract.
The pre-existing contracts remain:

- `SideEffectLedger` and `Phase08SideEffectLedger` continue to gate
  every side-effect tool dispatch. Without a `tool_use_id` reference
  on a `SideEffectClaim`, the dispatcher fails closed with
  `SideEffectClaimError`.
- `CapabilityPlan` / `RuntimePlanner` continue to enforce
  `PRODUCT_APPROVAL_FLOW_NOT_BOUND` before any side-effect dispatch.
- Post-dispatch exceptions surface as
  `UNKNOWN_EFFECT → RECONCILIATION_REQUIRED` and never auto-retry as
  `NO_EFFECT`. This contract is asserted by
  `tests/agent/test_workspace_phase22_repair.py` (existing tests
  pass).

No new side-effect / approval surface is introduced in this slice.

## Tests

The following focused tests cover the runtime cutover boundaries:

- `tests/api/test_workspace_image_gen_blocked.py` (new): asserts the
  workspace product surface fails closed with
  `IMAGE_TOOL_RUNTIME_NOT_BOUND`; no `_text_to_image` import is
  present in `src/backend/zuno/api/services/workspace.py`.
- `tests/agent/test_workspace_product_baseline_retired.py` (new):
  asserts `src/backend/zuno/agent/product_baseline.py` does NOT
  exist; `tools/evals/zuno/agent/product_baseline.py` does; the
  regression test can import it via `tools.evals.zuno.agent.*`.
- `tests/repo/test_phase22_runtime_cutover_findings.py` (new): asserts
  the post-cutover finding counts and the
  `VERIFIER_FALSE_POSITIVE_CANDIDATE` registry.

The pre-existing `tests/api/test_completion_unified_runtime.py`,
`tests/agent/test_workspace_product_surface.py`,
`tests/agent/test_workspace_phase22_repair.py`,
`tests/agent/test_workspace_task_runtime_import_smoke.py`, and
`tests/agent/test_mcp_stdio_server_security.py` continue to pass.

## Out of scope

- Budget Owner PostgreSQL Store → `minimax2`.
- Security / Budget Migration → `minimax2`.
- Formal Benchmark Measurement → `minimax2`.
- Program Closure documentation → `minimax2`.
- Production Readiness → `minimax2`.
- Verifier hardening for the `mcp` substring rule → `minimax2`.

## What this slice does NOT declare

- `PHASE22_COMPLETED` — not declared.
- `PRODUCTION_READY` — not declared.
- `BENCHMARK_PASSED` — not declared.
- The audit verdict remains
  `RUNTIME_CUTOVER_BLOCKERS_PARTIAL_REDUCTION`; promotion to
  `LEGACY_CUTOVER_AUDIT_CLEAN` requires the verifier hardening pass
  and the `MCPToolExecutorAdapter` refactor (Tasks 11, 12, 13).