# PHASE22 Workspace Agent Single Controller Cutover

phase_id: PHASE22
work_package: PHASE22-WORKSPACE-SINGLE-CONTROLLER-CUTOVER-ARCHITECTURE-REPAIR
worker: deepseek2
agent_name: DeepSeek-PR129-Product-Repair
execution_client: Claude Code
provider: DeepSeek
base_sha: 5dd6f2f8264ec8f662a7407e7a5b23f8cfc0e155
status: workspace_single_controller_structure_available
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

## Security / Approval / Budget Contract（Owner Fact）

- Security：Product Adapter 只携带 **opaque `security_decision_id`**（或
  untrusted envelope 中的 `decision_id`）；Agent Core / Composition 通过注入的
  `SecurityDecisionResolver.resolve(decision_id, context)` Port 从 Owner 取得
  正式事实（`SecurityDecisionRef`：decision_id / tenant / workspace /
  principal / action / resource / decision / epoch / hash / expires_at）。
  Product Profile **绝不信任 caller 提交的完整 ref 或自行计算的 hash**；
  Owner Resolver 未绑定 → `security_owner_resolver_unbound`；Owner 事实缺失 →
  `security_owner_fact_not_found`；tenant/workspace/principal/action/resource
  不匹配、stale epoch、hash 不匹配、decision denied、**expires_at 过期或
  非法**（`_check_expiry`，真实校验，非只定义字段）→ 全部 fail-closed。
- Budget：同样经 `BudgetDecisionResolver` Port（`BudgetDecisionRef`；
  budget_decision_id / tenant / workspace / run / allowed / limits / hash /
  owner）；owner 缺失或伪造 hash → fail-closed。Product Profile 每次计划运行
  都必须经过 **正式 Budget Admission**（简单无工具任务也要求；resolver
  未绑定 → `budget_owner_resolver_unbound` fail-closed）。
- Developer Test Profile：可注入 Fake Resolver（显式 test profile，不作为
  Product Evidence）。
- Approval：`ToolControlPlaneRuntime` approval gate → `approval_required` →
  runtime interrupt → `WAITING_APPROVAL`（test profile 内验证 resume 语义）。
  Product mode：approval_flow="none" → side-effect 直接
  `PRODUCT_APPROVAL_FLOW_NOT_BOUND`（零执行、无 WAITING_APPROVAL）。
- 无 fallback：任何 gate 拒绝直接传播为 FAILED/BLOCKED，不切换到旧 Runtime。

## Read-only 产品链（阻塞四）

- 简单无工具任务（product profile + budget resolver）：仍走 Deterministic
  Single-Step Plan（`answer_from_context`）+ Trace + Budget Admission +
  AnswerPolicy + Final Gate + RunOutcome；**不要求 tool.execute Security
  Decision**（`_verify_security_owner_ref` 仅在计划含工具执行时 required）。
- Read-only Tool：Security Owner Decision + Budget Owner Decision + Tool
  Control Plane（manifest 权威 policy），无需人工 Approval，有
  Audit/Trace（security_summary / budget_verdict 携带 decision_ref +
  trace_ref）。
- Side-effect Tool：approval_flow 未绑定 → `PRODUCT_APPROVAL_FLOW_NOT_BOUND`
  （零执行，不进入无人可 Resume 的 WAITING_APPROVAL）。
- Complex Task：Dynamic DAG Planner 未绑定 →
  `DYNAMIC_PLAN_RUNTIME_NOT_BOUND`（不恢复固定三步伪 DAG）。
- Server 默认组合（`WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition`）
  的 resolver 均为 None，且 Product Surface 尚无 tenant 上下文 →
  server 路径对计划请求 fail-closed（BLOCKED_CONFIGURATION /
  `budget_owner_resolver_unbound`）。Read-only 路径的可用性由 test profile
  以与生产相同契约形状（真实 Port + fake Owner 事实 + 真实 tenant/workspace
  身份）验证，故只声明 `workspace_single_controller_structure_available`，
  不声明 `workspace_readonly_single_controller_cutover_available`。

## Composition Root / Import-time（阻塞一）

- 双 `@classmethod` 已修复（单一 decorator）。
- 模块 import 不再执行全局 Composition Mutation（文件底部调用已删除）；
  初始化显式接入 Application Startup Composition Root
  （`zuno.main.init_config` → `configure_workspace_agent_product_composition`），
  幂等、可测试；import 不需要 PostgreSQL 连接。
- `reset_runtime_state_for_tests` 补上 `@classmethod`，且**不再创建** Product
  Composition（只清除）；import 本身也绝不创建 Composition。
- Import Smoke Test：`tests/agent/test_workspace_task_runtime_import_smoke.py`
  （6 项）验证模块可导入、方法 callable、初始化不抛 TypeError、重复初始化
  幂等、fresh-interpreter import 无副作用。

## Tenant / Workspace Ownership（阻塞二）

- `WorkspaceRuntimeComposition` **不拥有租户身份**（`tenant_id` 字段已删除，
  只注入基础设施依赖）；`RuntimeStartRequest` / `AgentRuntimeState` /
  `AgentRuntimeSnapshot` 的 `tenant:default` 默认值全部移除。
- Tenant / Workspace / Principal 来自真实 Product Request/Auth Context，
  贯穿 Product API → Product Adapter → `WorkspaceRunRequest` →
  `RuntimeStartRequest` → State/Snapshot → Tool Manifest →
  Security/Budget Owner Lookup → Tool Gateway 事实 → Event/Snapshot/Resume。
- 禁止 `workspace:{user_id}`；`_task_id_for` 使用真实 tenant + workspace +
  client_request_id（跨租户同 client_request_id 不冲突）。
- Product Surface 无法提供 tenant_id/workspace_id → **fail-closed
  BLOCKED_CONFIGURATION**（`WorkspaceAgentRuntime.__init__` 与
  `WorkSpaceSimpleAgent`/`WeChatAgent._build_canonical_runtime` 双重校验），
  不回退 tenant:default、不根据 user_id 猜 workspace_id。
- Tool Gateway 事实（`ToolControlPlaneRuntime._record_tool_runtime_facts`）
  使用 request.tenant_id / workspace_id，不再用 user_id 或
  tenant:default/workspace:default。

## Failure Semantics（classify_final_state）

- `EFFECT_COMMITTED` — 正式 Effect Receipt（CONFIRMED_EFFECT）已持久化。
- `RECONCILIATION_REQUIRED` — side effect 已 dispatch 但 outcome 未知
  （UNKNOWN_EFFECT）；禁止自动 Retry，必须 Reconciliation。
- `COMPLETED` — finalized。
- `FAILED/BLOCKED` — tool failed/blocked、security/budget 阻断、unresolved
  policy、SIDE_EFFECT_GATEWAY_NOT_BOUND、PRODUCT_APPROVAL_FLOW_NOT_BOUND、
  DYNAMIC_PLAN_RUNTIME_NOT_BOUND、blocked plan。

## Tests

- `tests/agent/test_workspace_single_controller_cutover.py`（52 项）：
  normal / security / approval / budget / persistence / identity / tenant
  isolation / failure / static gates；新增 Owner Fact 组：
  product simple QA 只需 Budget Admission 不需 tool Security Decision、
  product read-only tool 经 Owner Resolver + Control Plane 完成、product
  不信任 caller-provided refs、expires_at 过期拒绝（直接 ref 与 resolver
  事实两条路径）、owner fact 缺失拒绝、缺 tenant/workspace →
  BLOCKED_CONFIGURATION、Tool Manifest tenant/workspace 不匹配 → blocked。
- `tests/agent/test_workspace_phase22_repair.py`（15 项）：B1 组合绑定
  （显式初始化、import 无副作用）、B3 缺 Gateway 零执行、B8
  pre/post-dispatch 语义、telemetry 失败、UNKNOWN_EFFECT 不重试、B6 身份、
  B7 共享 store 隔离、B9 审批流 fail-closed（Owner Resolver 路径）。
- `tests/agent/test_workspace_simple_agent.py`（27 项）：adapter 契约 +
  跨租户同 client_request_id 不冲突。
- `tests/agent/test_workspace_task_runtime_import_smoke.py`（6 项）：
  Import Smoke Test（双 @classmethod / import-time 初始化 / 幂等 / 无 PG）。
- `tests/agent/_phase22_gateway_fakes.py`：ToolInvocationGateway 三个 UoW
  的 in-memory test double（仅测试；product 路径要求正式 PostgreSQL UoW）。
- 相关批次：workspace+smoke 批 100 passed；capability 批 34 passed（2
  skipped）；workspace API 批 29 passed；agent 批 426 passed（5 项
  pre-existing 失败，base 同样失败）；repo 批 516 passed（29 项
  pre-existing 文档/发布边界失败，base 同样失败）。

## CI（阻塞四）

`.github/workflows/phase22-contract-verification.yml`：

- `repository-gates`：新增 `poetry run python -c "import
  zuno.api.services.workspace_task_runtime"`（compileall 不执行 import，
  该检查直接捕获 Import-time 初始化失败）。
- `phase22-focused-tests`：新增 4 个文件 —
  `tests/agent/test_workspace_task_runtime_import_smoke.py`、
  `tests/agent/test_workspace_phase22_repair.py`、
  `tests/agent/test_workspace_single_controller_cutover.py`、
  `tests/agent/test_workspace_simple_agent.py`。
  CI 能捕获：双 @classmethod；import-time 初始化失败；tenant:default
  回退（identity 缺失 → BLOCKED_CONFIGURATION）；product 信任 caller
  refs；expires_at 未检查；simple read-only 被错误阻塞（product + resolver
  可运行）；side-effect 被错误执行（PRODUCT_APPROVAL_FLOW_NOT_BOUND）。

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

- Server 默认组合（`configure_workspace_agent_product_composition`）的
  Security/Budget Owner Resolver 仍为 None，且 Product Surface（
  `WorkSpaceSimpleTask` / WeChat 入口）尚无 tenant 上下文 →
  server 计划请求 fail-closed（BLOCKED_CONFIGURATION /
  `budget_owner_resolver_unbound` / `security_owner_resolver_unbound`）。
  接真实 tenant 上下文 + Owner Resolver（可复用
  `SecurityUnitOfWork`/`validate_pre_effect_authorization`）后才能声明
  `workspace_readonly_single_controller_cutover_available`。
- Product Approval Command / Resume API 未接入（Path B：side-effect 全部
  fail-closed）。
- Dynamic DAG planner 未绑定（复杂任务 fail-closed）。
- Postgres 依赖测试本环境 NOT_RUN_ENVIRONMENT_BLOCKED。
- WorkSpacePlugins / MCP 等外部工具注册表无 Tool Owner Policy 声明 →
  UNRESOLVED_TOOL_POLICY → 执行时 blocked（不猜测）。

不声明 `PHASE22_COMPLETED` / `PRODUCTION_READY` /
`FULL_REPOSITORY_SINGLE_RUNTIME_CONFIRMED` /
`WORKSPACE_FULL_TOOL_CUTOVER_CONFIRMED` /
`workspace_readonly_single_controller_cutover_available`。
