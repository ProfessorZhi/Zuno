# PHASE22 Workspace Agent Single Controller Cutover

phase_id: PHASE22
work_package: PHASE22-WORKSPACE-SINGLE-CONTROLLER-CUTOVER-ARCHITECTURE-REPAIR
worker: deepseek-workspace-cutover-repair
agent_name: DeepSeek-Workspace-Cutover-Repair
execution_client: Claude Code
provider: DeepSeek
base_sha: 7ebf1b5694a6cdf53493732768924186f4407256
status: workspace_readonly_single_controller_cutover_available
production_ready: false

## Summary

`WorkSpaceSimpleAgent` 和 `WeChatAgent` 从独立 langchain ReAct Product Runtime /
直接工具调用路径切换到 Zuno 正式 Single Controller Runtime
(`UnifiedAgentRuntimeService` + Fixed AgentRunGraph + StepExecutionGraph)，
并且本轮完成 Coordinator Review 要求的架构修复：

1. Product 默认不再创建临时 SQLite：`WorkspaceAgentRuntime` 只是 Composition
   Adapter，durable store / checkpointer / Tool-Security-Infrastructure UoW /
   security epoch / approval flow 全部从 Server Composition Root 注入
   （`WorkspaceRuntimeComposition` + `WorkspaceTaskRuntimeService
   .configure_workspace_agent_product_composition`）。SQLite 只保留在显式
   `DEVELOPER_TEST_PROFILE`。Product 绑定缺失 → `BLOCKED_CONFIGURATION`。
2. Tool Policy 来自 Tool Owner 声明的 Manifest（`DeclaredToolPolicy` /
   `ToolCardManifest`，含 tenant/workspace scope、manifest_version、policy_hash、
   policy_resolution）；按工具名猜副作用的 `_classify_tool_effect` /
   `_tool_execution_mode` / `_tool_has_network` 全部删除。未知/缺失 Manifest →
   `UNRESOLVED_TOOL_POLICY` → BLOCKED，绝不默认 READ。
3. Side-effect Gateway fail-closed：`ToolControlPlaneRuntime` 对
   WRITE_LOCAL/WRITE_EXTERNAL/DESTRUCTIVE 强制要求 ToolInvocationGateway
   三个 UoW Factory；缺失 → `SIDE_EFFECT_GATEWAY_NOT_BOUND` → BLOCKED，
   Executor 调用次数为 0。不存在“缺 Gateway → 直接 Executor”。
4. Security/Budget 使用 Owner Decision Ref（`SecurityDecisionRef` /
   `BudgetDecisionRef`，decision hash + epoch + tenant/workspace/principal
   scope），Agent Core 启动时确定性验证；raw caller dict 不再是 Owner
   Decision。缺失 ref / stale epoch / 跨 tenant / 伪造 hash / denied 全部
   fail-closed。
5. 每个任务都有正式 Plan：简单任务 = 显式 Deterministic Single-Step Plan
   （`answer_from_context`，PlanState plan_version=1，activation 属于 Agent
   Core）；工具任务 = Tool Step + Answer Step（tool_id/arguments 绑定在
   PlanVersion）；复杂任务 = 绑定 Dynamic DAG Planner，未绑定 →
   `DYNAMIC_PLAN_RUNTIME_NOT_BOUND` → BLOCKED（不再用固定三步伪装 DAG）。
6. 请求身份 = tenant + workspace + principal + submission_id +
   client_request_id；文本 Hash 只是 content_fingerprint。同
   client_request_id → Replay（相同事实、不重复副作用）；不同
   client_request_id（即使文本相同）→ 新 Run。
7. Tenant/Workspace 隔离：所有 Domain Fact 和 Runtime Ref 带正式
   tenant_id/workspace_id；跨 tenant 读 Run / 恢复 Checkpoint / Resume /
   Events 全部 fail-closed（共享 store 上验证）。
8. 失败语义：PRE_DISPATCH_FAILURE → NO_EFFECT；post-dispatch 异常 →
   `UNKNOWN_EFFECT` → `RECONCILIATION_REQUIRED`（不自动 Retry）；正式
   Effect Receipt 持久化后 → `CONFIRMED_EFFECT` → EFFECT_COMMITTED。
   Telemetry 写入失败不抹掉真实业务失败（保持 UNKNOWN，不写成 NO_EFFECT）。
9. Approval Product Flow 采用 Path B：Product Approval Command 未接入 →
   Side-effect Tool 全部 fail-closed（`PRODUCT_APPROVAL_FLOW_NOT_BOUND`）；
   不声明完整 Workspace Tool Cutover。runtime 级 interrupt/resume 语义在
   developer test profile 内可验证。

不声明 `PHASE22_COMPLETED` / `PRODUCTION_READY` /
`LEGACY_CUTOVER_AUDIT_CLEAN` / `FULL_REPOSITORY_SINGLE_RUNTIME_CONFIRMED`。

## Before Call Chain

```text
workspace.py / wechat.py (API service)
  -> WorkSpaceSimpleAgent / WeChatAgent
       -> langchain create_agent (独立 ReAct Product Runtime)      [REMOVED]
       -> setup_middlewares (awrap_model_call / awrap_tool_call)   [REMOVED]
       -> astream: direct tool.ainvoke paths:
            _run_direct_routed_tool   (named tool / tool creation / knowledge route)
            _run_direct_image_generation (text2image direct)
            _guess_direct_mcp_call -> tool.ainvoke                 [REMOVED]
       -> ainvoke: self.model.ainvoke 直接生成最终答案             [REMOVED]
       -> _classify_tool_effect / _tool_execution_mode /
          _tool_has_network (按工具名猜 Policy)                    [REMOVED]
       -> 每 session 临时 SQLite:
          temp/zuno_workspace_agent_<user>_<session>.db            [REMOVED]
```

## After Call Chain

```text
workspace.py / wechat.py (API service, unchanged product API / SSE contract)
  -> WorkSpaceSimpleAgent / WeChatAgent (Product Adapter, astream/ainvoke)
       -> _resolve_governed_tool (确定性工具解析, 仅选择不执行)
       -> WorkspaceAgentRuntime (composition ADAPTER, per session)
            store / UoW factories / epoch / approval flow / issuers
            全部来自 WorkspaceRuntimeComposition (server composition root)
       -> UnifiedAgentRuntimeService (canonical Agent Core facade)
            -> Fixed AgentRunGraph (build_agent_graph)
                 -> explicit plan (single-step / tool two-step / DAG or blocked)
                 -> StepExecutionGraph -> ReActStepRunner (仅单 Step 内)
                 -> Security Gate (owner decision ref verification)
                 -> Approval Gate (interrupt / resume, test profile)
                 -> Budget Gate (owner decision ref verification)
                 -> ToolInvocationGateway (side effects, fail-closed)
                 -> Observation / Acceptance -> Final Gate -> RunOutcome
```

## Removed Direct Tool Paths

- `create_agent`（langchain prebuilt ReAct runtime）— 全部删除。
- `setup_middlewares` / `WorkspaceReactMiddleware` — 删除。
- `_run_direct_routed_tool` — 删除（直接 `tool.ainvoke` 路径）。
- `_run_direct_image_generation` — 删除（生图现在是 governed tool step）。
- `react_agent.ainvoke` / `self.model.ainvoke` 最终答案 — 删除。
- `_classify_tool_effect` / `_tool_execution_mode` / `_tool_has_network`
  （workspace + wechat）— 删除；Policy 改为 Tool Owner 在注册时声明。
- 每 session 临时 SQLite store — 删除；Product 使用注入的 server store。

保留（产品表面, 允许范围）：`astream`/`ainvoke` 签名、SSE 事件格式
(status/final/tool_call/tool_result)、session 写入、标题生成、
`_detect_route_hint`/`_guess_direct_mcp_call`/`_parse_direct_named_tool_invocation`
等解析辅助（现在只做解析, 执行走 runtime）。

## Plan Contract

- 简单请求 → `plan_kind="simple"`：显式 Deterministic Single-Step Plan
  （`answer_from_context`），PlanState `plan_version=1`、
  `activation_status="activated"`、`activated_by="agent_core"`；仍经过
  Trace / Budget / AnswerPolicy / Final Gate / RunOutcome。
- 工具请求 → `plan_kind="tool"`：`tool_call` step（绑定 `tool_id` +
  `tool_arguments`）+ `answer_with_evidence` step；PlanVersion 激活后不可变。
- 复杂请求 → `plan_kind="complex"`：绑定 Dynamic DAG Planner；未绑定 →
  `DYNAMIC_PLAN_RUNTIME_NOT_BOUND` → BLOCKED_CONFIGURATION（不再固定三步）。
- `direct_answer` 不再绕过：简单任务也有显式 plan；无 plan 的请求产生
  blocked plan。

## Security / Approval / Budget Contract

- Security：`SecurityDecisionRef`（decision_id / tenant / workspace /
  principal / action / resource / decision / epoch / hash）由 Owner 签发，
  Product Adapter 只携带；Agent Core 启动时验证（`owner_refs.py`）。
  缺失 ref（product mode 工具任务）、tenant/workspace/principal 不匹配、
  stale epoch、hash 不匹配、decision denied → 全部 fail-closed。
  硬编码 `security-epoch:workspace-v1` 已删除。
- Budget：`BudgetDecisionRef`（budget_decision_id / tenant / workspace /
  run / allowed / limits / hash / owner）；owner 缺失或伪造 hash → fail-closed。
- Approval：`ToolControlPlaneRuntime` approval gate → `approval_required` →
  runtime interrupt → `WAITING_APPROVAL`（test profile 内验证 resume 语义）。
  Product mode：approval_flow="none" → side-effect 直接
  `PRODUCT_APPROVAL_FLOW_NOT_BOUND`，绝不进入无 Resume 路径的等待。
- 无 fallback：任何 gate 拒绝直接传播为 FAILED/BLOCKED，不切换到旧 Runtime。

## Failure Semantics（classify_final_state）

- `EFFECT_COMMITTED` — 正式 Effect Receipt（CONFIRMED_EFFECT）已持久化。
- `RECONCILIATION_REQUIRED` — side effect 已 dispatch 但 outcome 未知
  （UNKNOWN_EFFECT）；禁止自动 Retry，必须 Reconciliation。
- `COMPLETED` — finalized。
- `FAILED/BLOCKED` — tool failed/blocked、security/budget 阻断、unresolved
  policy、SIDE_EFFECT_GATEWAY_NOT_BOUND、PRODUCT_APPROVAL_FLOW_NOT_BOUND、
  DYNAMIC_PLAN_RUNTIME_NOT_BOUND、blocked plan。

## Tests

- `tests/agent/test_workspace_single_controller_cutover.py`（42 项）：
  normal / security / approval / budget / persistence / identity / tenant
  isolation / failure / static gates。
- `tests/agent/test_workspace_phase22_repair.py`（15 项）：B1 组合绑定、
  B3 缺 Gateway 零执行、B8 pre/post-dispatch 语义、telemetry 失败、
  UNKNOWN_EFFECT 不重试、B6 身份、B7 共享 store 隔离、B9 审批流 fail-closed。
- `tests/agent/test_workspace_simple_agent.py`（26 项）：adapter 契约。
- `tests/agent/_phase22_gateway_fakes.py`：ToolInvocationGateway 三个 UoW
  的 in-memory test double（仅测试；product 路径要求正式 PostgreSQL UoW）。
- 相关批次：workspace 批 98 passed；capability 批 45 passed（2 skipped）；
  phase08/runtime graph 34 passed；API/repo 批 66 passed；runtime 批 65
  passed。

## Commands / Exit Codes

- `git diff --check` — 0。
- `verify_repo_structure.py` — 0。
- `verify_agent_core_target_protocols.py` — 0。
- `verify_phase22_cleanup_boundary.py` — 0。
- `verify_tool_execution_bypass.py` — 0。
- `.agent/scripts/verify_agent_system.py` — 0。

## NOT_RUN_ENVIRONMENT_BLOCKED（本环境无 PostgreSQL localhost:5432）

以下测试在干净 base（7ebf1b56）同样失败，属 pre-existing 环境依赖
（psycopg ConnectionTimeout），不是本工作包回归：

- `tests/agent/runtime/test_runtime_tool_control_plane.py`（2 项）
- `tests/agent/runtime/test_runtime_tool_idempotency.py`（1 项）
- `tests/api/test_workspace_task_runtime.py`（3 项 Postgres 工具路径）
- `tests/agent/runtime/test_runtime_dependency_factory.py`
  `test_completion_factory_knowledge_step_uses_durable_port_not_missing_dependency`
  （base 同样失败, AssertionError pre-existing）
- `tests/agent/test_capability_system.py`、`test_hooks_evidence_trace_artifacts.py`、
  `test_memory_durable_runtime.py`、`test_platform_layer_surfaces.py`
  （base 同样失败, pre-existing）

SQLite test 不作为 Product Persistence Evidence；Recovery 只声明
“test profile 内恢复验证”，不声明 Recovery Live Verified。

## GitHub Actions

推送到分支后由 CI 执行（Draft PR）。本地 attribution gate:
`verify_agent_commit_attribution.py --base <BASE> --head HEAD` 在 commit 后运行。

## Remaining Gaps

- Product Approval Command / Resume API 未接入（Path B：side-effect 全部
  fail-closed）；Server Security/Budget Owner issuer 未接入（tool 任务在
  product mode 因缺 Security Decision Ref 而 fail-closed）。
- Dynamic DAG planner 未绑定（复杂任务 fail-closed）。
- Postgres 依赖测试本环境 NOT_RUN_ENVIRONMENT_BLOCKED。
- WorkSpacePlugins / MCP 等外部工具注册表无 Tool Owner Policy 声明 →
  UNRESOLVED_TOOL_POLICY → 执行时 blocked（不猜测）。
