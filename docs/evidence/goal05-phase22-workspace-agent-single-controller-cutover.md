# PHASE22 Workspace Agent Single Controller Cutover

phase_id: PHASE22
work_package: PHASE22-WORKSPACE-AGENT-SINGLE-CONTROLLER-CUTOVER
worker: deepseek-workspace-cutover
agent_name: DeepSeek-Workspace-Cutover
execution_client: Claude Code
provider: DeepSeek
base_sha: 83c1bbd0689d1b2b3b4ffd7f3983de813da11ebb
status: workspace_agent_cutover_implementation_available
production_ready: false

## Summary

`WorkSpaceSimpleAgent` 和 `WeChatAgent` 从独立 langchain ReAct Product Runtime /
直接工具调用路径切换到 Zuno 正式 Single Controller Runtime
(`UnifiedAgentRuntimeService` + Fixed AgentRunGraph + StepExecutionGraph)。
两个 agent 现在是薄 Product Adapter：把产品请求转换为 `WorkspaceRunRequest`，
由 canonical runtime 完成 Plan / Security / Approval / Budget / Trace /
Retry / Recovery / Idempotency / RunOutcome 闭环。

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
```

## After Call Chain

```text
workspace.py / wechat.py (API service, unchanged product API / SSE contract)
  -> WorkSpaceSimpleAgent / WeChatAgent (Product Adapter, astream/ainvoke)
       -> _resolve_governed_tool (确定性工具解析, 仅选择不执行)
       -> WorkspaceAgentRuntime (composition root, per session)
            -> UnifiedAgentRuntimeService (canonical)
                 -> Fixed AgentRunGraph (build_agent_graph)
                      -> Planning (direct_answer 单步 / tool 两步 / complex 三步)
                      -> StepExecutionGraph -> ReActStepRunner (仅单 Step 内)
                      -> Capability Resolution (session tool manifests)
                      -> Security Gate (planning admission + control plane)
                      -> Approval Gate (interrupt / resume / WAITING_APPROVAL)
                      -> Budget Gate (planning admission + RuntimeLimits)
                      -> ToolInvocationGateway / ToolControlPlaneRuntime
                      -> Observation -> Acceptance (tool 结果回注 answer step)
                      -> Final Gate -> RunOutcomeRecord
```

## Removed Direct Tool Paths

- `create_agent`（langchain prebuilt ReAct runtime）— 全部删除。
- `setup_middlewares` / `WorkspaceReactMiddleware` — 删除。
- `_run_direct_routed_tool` — 删除（直接 `tool.ainvoke` 路径）。
- `_run_direct_image_generation` — 删除（生图现在是 governed tool step）。
- `react_agent.ainvoke` / `self.model.ainvoke` 最终答案 — 删除。
- WeChatAgent 的 `create_agent` + `self.model.ainvoke` — 删除。

保留（产品表面, 允许范围）：`astream`/`ainvoke` 签名、SSE 事件格式
(status/final/tool_call/tool_result)、session 写入、标题生成、
`_detect_route_hint`/`_guess_direct_mcp_call`/`_parse_direct_named_tool_invocation`
等解析辅助（现在只做解析, 执行走 runtime）。

## Plan Contract

- 简单请求 → `plan_kind="simple"`：canonical selector 生成确定性单步
  `answer_from_context` plan（Deterministic Single-Step Plan）。
- 工具请求 → `plan_kind="tool"`：适配器绑定真实 `tool_id` + `tool_arguments`
  的 `tool_call` step + `answer_with_evidence` step（step 携带工具,
  执行仍过全部门）。
- 复杂请求 → `plan_kind="complex"`：3 步确定性 plan
  (`model_transform` → `prepare_replan_if_evidence_low` → `answer_from_context`)。
- `direct_answer` 不再绕过：绕过路径（直接 model/tool handler）已删除。
- Dynamic DAG（`DynamicPlanRuntimeController`）是独立派发系统, 未接入 unified
  graph 产品路径 — Remaining Gap, 与 P08 程序注记一致（"动态 DAG 仍明确
  Target, 未伪装完成"）。

## Security / Approval / Budget Contract

- Security：planning admission（`PlanningRequest.security_summary` → blocked
  plan, 不创建 step）+ stale security epoch fail-closed（`WorkspaceRunRequest.
  security_epoch_ref` 与 runtime 当前 epoch 不符 → `stale_security_epoch`
  blocked plan）+ 控制平面 `ToolSecurityGate`。
- Approval：`ToolControlPlaneRuntime` approval gate → `approval_required` →
  runtime interrupt → `WAITING_APPROVAL`（store status `approval_waiting`）→
  `resume(approved/rejected)`（拒绝 → failed, 不执行）。未批准前 executor
  零调用。
- Budget：planning admission（`budget_verdict.allowed=False` → blocked plan,
  副作用前阻断）+ `RuntimeLimits`（max_steps/tokens/cost 注入 state,
  `hard_limit_route` 强制执行）。
- 无 fallback：任何 gate 拒绝直接传播为 FAILED/BLOCKED, 不切换到旧 Runtime。

## Retry / Replan / Recovery / Idempotency

- Retry：工具 transient failure → `failed` observation（控制平面把 executor
  异常转成 failed result, 不 crash graph）→ `FAILED/BLOCKED`；`retry_run`
  按原 plan 重跑（副作用未提交时）。
- Replan：`prepare_replan_if_evidence_low` step + `ReplanEngine`（证据不足时
  replan, 新 PlanVersion; 已激活 plan 不可变 — canonical 契约）。
- Recovery：SQLiteAgentRunStore 持久化 checkpoint/interrupt/events；worker
  重启后新 composition root 同 store 可恢复 snapshot 并 resume。
- Idempotency：`start_with_replay`（同 task_id 已 terminal → 返回同一
  snapshot, 不重复执行/不重复事件）；`claim_tool_execution`（resume 幂等,
  副作用只执行一次）；EFFECT_COMMITTED 后重复请求不重复副作用。
- Unknown effect：非 terminal 非 interrupt 状态 → `RECONCILIATION_REQUIRED`
  （不盲目重试, Operator/Coordinator 确认）。

## Failure Semantics（classify_final_state）

- `EFFECT_COMMITTED` — 副作用工具 completed（approval_required 集合内）。
- `COMPLETED` — finalized。
- `FAILED/BLOCKED` — tool failed/blocked、security/budget 阻断、blocked plan、
  failed/blocked/abstained 终态。
- `RECONCILIATION_REQUIRED` — 无已识别终态（副作用状态未知）。

## Tests

- `tests/agent/test_workspace_single_controller_cutover.py`（新, 26 项）：
  25 个要求场景全覆盖（normal/security/approval/budget/failure/recovery/
  idempotency/static gates）+ wechat 同 controller。
- `tests/agent/test_workspace_simple_agent.py`：9 个钉住已删除 ReAct 内部的
  测试转换为 adapter 契约（resolution / bindings / astream 事件映射 /
  humanization 辅助）。
- `tests/api/test_layered_api_boundaries.py`、`test_workspace_usage_agent_name.py`、
  `test_capability_layer_surfaces.py`、`test_workspace_project_query_runtime.py`、
  `tests/repo/test_phase5_workspace_real_runtime_flow.py`、
  `test_phase11c_workspace_project_query_cutover.py`、
  `test_repo_hygiene.py`、`tests/retrieval/test_workspace_retrieval_trace.py` —
  全部通过（95 passed batch）。

## Commands / Exit Codes

- `git diff --check` — 0。
- `verify_repo_structure.py` — 0。
- `verify_agent_core_target_protocols.py` — 0。
- `verify_phase22_cleanup_boundary.py` — 0。
- `verify_tool_execution_bypass.py` — 0。
- `.agent/scripts/verify_agent_system.py` — 0。
- `verify_current_program.py` — pre-existing 环境失败（`No module named
  'zuno'`, 脚本未配置 sys.path; 干净 base 同样失败）。
- workspace 相关 pytest 批：95 passed + 34 passed（runtime 批）+ 36 passed
  （repo 批）+ 26 passed（cutover 套件）。
- `tests/agent/runtime/test_runtime_tool_control_plane.py` 3 项 +
  `test_runtime_tool_idempotency.py` 1 项（共 3 个用例）：
  NOT_RUN_ENVIRONMENT_BLOCKED — `psycopg ConnectionTimeout`（本环境无
  PostgreSQL localhost:5432; `build_default_tool_control_plane_runtime` 的
  Postgres UoW 工厂路径, pre-existing 环境依赖, 干净 base 同样失败）。

## GitHub Actions

未运行（Draft PR 创建后由 CI 执行）。本地 attribution gate:
`verify_agent_commit_attribution.py --base <BASE> --head HEAD` 在 commit 后运行。

## Remaining Gaps

- Dynamic DAG plan 未接入 unified graph 产品路径（`DynamicPlanRuntimeController`
  为独立派发系统, 复杂请求当前走确定性多步 plan）。
- 产品侧 approval UI / resume endpoint 未接入（runtime 的
  `resume(approved/rejected)` 已就绪; API surface 的 approve_task 属于
  workspace_task_runtime 产品面, 未在本工作包范围）。
- 模型 step 的 prompt 为 goal+step 文本（tool observation 已回注 answer
  step）; 结构化 message history 未传（system prompt + history 由适配器
  拼入 goal）。
- `workspace.py` 的 `should_run_direct_image_generation` API 层捷径仍存在
  （产品 API 面, 不在本工作包 agent 文件范围; 文本生图请求在 agent 内已走
  governed tool step）。
- Postgres 依赖测试（gateway 持久化路径）本环境 NOT_RUN_ENVIRONMENT_BLOCKED。
- WeChatAgent 的 `mcp_requires_user_config` 未保留（原实现总是注入 MCP 用户
  配置; 现 `_execute_binding_tool` 对 MCP 工具恒注入 — 行为一致）。
