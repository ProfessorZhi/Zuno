# PHASE06 Capability Skill Tool MCP Layer

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE06_capability-skill-tool-mcp-layer
status: completed

## 目标

把 Capability Layer 正式落地为 Skill、Knowledge、Tool、MCP、External API、File / Code / Browser 和 Artifact capabilities 的注册、授权、路由和观测层。

## 范围

- CapabilityRegistry、CapabilityRouter、CapabilityPolicy。
- SkillCard：skill_id、skill_version、when_to_use、task_type、recommended_retrieval_profile、required_evidence、allowed_tools、memory_scopes、output_contract、safety_policy、eval_rubric、max_steps、reflection_policy。
- KnowledgeCapability、ToolCapability、MCPCapability、ArtifactCapability。
- contract_review、research_report、code_review 或 bug_diagnosis 中至少两个 SkillCard fixture。

## Capability Policy Contract

PHASE06 必须把权限模型从 Tool 专属扩展为所有 capability 共享的策略对象。Skill、Knowledge、Tool、MCP、External API、File / Code / Browser 和 Artifact capability 都必须能接入统一策略、风险和审计。

### CapabilityPolicy

```text
CapabilityPolicy
  capability_id
  capability_type: skill / knowledge / tool / mcp / external_api / file / code / browser / artifact
  workspace_scope
  required_roles
  approval_required
  side_effect_level
  network_policy
  credential_policy
  data_access_policy
  audit_policy
```

### CapabilityRiskProfile

```text
CapabilityRiskProfile
  read_only
  write_workspace
  external_write
  network_access
  credential_access
  code_execution
  browser_control
```

### CapabilityAuditEvent

```text
CapabilityAuditEvent
  capability_id
  task_id
  decision
  reason
  latency_ms
  error
  approval_id
```

### Capability 统一边界

- Skill 是 task method package，可约束 retrieval profile、allowed tools、memory scopes、output contract、eval rubric 和 reflection policy。
- KnowledgeCapability 也必须带 ACL、sensitivity、workspace_scope 和 data_access_policy，不只是 Tool 有权限。
- MCPCapability 可以暴露工具或数据源，但必须产生 permission denied / target-blocked / dependency probe 的可观测结果。
- ArtifactCapability 必须声明导出、下载、分享和 redaction policy。

## 目标架构拼接点

本 phase 拼到 Agent Core 的 Capability Layer。它把“Agent 能做什么”从工具函数列表升级为可编排能力目录：

- Skill 是任务方法包，描述何时使用、需要什么证据、推荐检索深度、允许哪些工具、输出什么 artifact、如何评测。
- Tool 是具体动作，必须受 Tool Gate、credential policy 和 sandbox profile 控制。
- MCP 是外部能力接入协议，可以暴露工具或数据源，但不能绕过 Capability Policy。
- KnowledgeCapability 把标准检索 / 深度检索作为 Agent 可调用能力。
- ArtifactCapability 统一报告、表格、导出等输出。

本 phase 的输出由 PHASE09 Skill selection 和 PHASE10 ReAct runner 消费。

## 并行开发可行性

本 phase 可由 Workstream D 独立推进，但 Tool security 部分必须与 Workstream E 对齐。

可并行：

- SkillCard fixtures 与 CapabilityRegistry 可以并行。
- ToolCapability 与 MCPCapability boundary 可以并行。
- ArtifactCapability 可以和 Product API workstream 约定输出摘要。

不可并行：

- 不得让 SkillCard 自带任意执行逻辑，执行必须经 Planning / Capability Router。
- 不得让 MCP tool bypass Tool Gate。
- 不得同时修改 SkillCard contract 和 planning selected skill contract。

## 详细执行卡

- 输入依赖：PHASE02 CapabilityCard / SkillCard / ToolCard contract、现有 capability 和 agent_system guardrails。
- 主要交付物：CapabilityRegistry、CapabilityRouter、CapabilityPolicy、CapabilityRiskProfile、CapabilityAuditEvent、SkillCard fixtures、KnowledgeCapability、ToolCapability、MCPCapability、ArtifactCapability。
- 可并行工作包：SkillCard fixture、ToolCard policy、MCP boundary、Artifact capability 可拆；CapabilityRouter 由单 owner 收口，防止 registry contract 分叉。
- Coordinator 锁点：Skill 的正式定义和产品边界：Skill 是任务方法包，不是 Tool、不是 Knowledge、不是产品级多 Agent runtime。
- 下游交接：PHASE09 用 Skill selection；PHASE10 用 capability execution plan；PHASE07 用 tool approval/safety policy；PHASE13 用 skill_selected / capability_used metrics。
- PR / commit 建议：`feat(capability): add skill capability registry` 与 `test(capability): cover skill routing and allowed tools`。

## 禁止范围

- Skill 不写成 Tool。
- Skill 不写成 Knowledge。
- Skill 不写成产品级多 Agent runtime。
- MCP 不绕过 Tool Gate 或 Credential policy。

## 验收闸门

- Capability registry tests 通过。
- SkillCard fixture tests 通过。
- skill 限制 allowed_tools 测试通过。
- skill 限制 capability / tool 权限测试通过。
- cross-workspace KnowledgeCapability 被 Retrieval / Capability policy block。
- MCP capability 未配置或无权限时产生 target-blocked / permission denied evidence。
- pinned skill 覆盖自动选择的 contract 清晰。
- Tool / MCP capability boundary 有 permission 和 trace 字段。

## 验证命令

```powershell
git diff --check
pytest -q tests/capability -p no:cacheprovider
pytest -q tests/agent_system -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/capability/**`
- `src/backend/zuno/capability/mcp/**`
- `src/backend/zuno/capability/tools/**`
- `tests/capability/**`
- `tests/agent_system/**`

## 需要修改的文件

- `src/backend/zuno/capability/**`
- `src/backend/zuno/capability/mcp/**`
- `src/backend/zuno/capability/tools/**`
- `tests/capability/**`
- `tests/agent_system/**`

## 执行拆解

1. 写 CapabilityRegistry focused test。
2. 写 SkillCard fixture tests。
3. 写 allowed_tools / output_contract tests。
4. 写 Tool / MCP boundary tests。
5. 实现最小 registry / router / policy。
6. 交给 Planning phase 消费 capability summary。

## 多 agent 分工

- Workstream D owner。
- Workstream E 审查 Tool Gate / permission。
- Workstream F 只消费 selected skill / capability plan。

## 需要返回的证据

- SkillCard fixture 列表。
- Capability registry 示例。
- Skill 与 Tool / Knowledge / MCP 边界说明。
- tests 输出。

## Closure Evidence

- 本地实现：新增 `src/backend/zuno/capability/layer.py`，以 PHASE02 `CapabilityCard`、`CapabilityPolicy`、`CapabilityRiskProfile`、`CapabilityAuditEvent`、`SkillCard` 和 `ToolCard` 为唯一共享 contract surface，提供 `CapabilityLayerRegistry`、`CapabilityRouter`、`CapabilityRouteRequest`、`CapabilityDecision` 和默认 registry builder。
- Skill fixture：默认包含 `contract_review` 和 `research_report`，二者均声明 recommended retrieval profile、required evidence、allowed tools、memory scopes、output contract、safety policy、eval rubric、max_steps 和 reflection policy。Skill 仍是任务方法包，不是 Tool、不是 Knowledge、不是产品级多 Agent runtime。
- Capability registry：覆盖 Knowledge、Tool、MCP、External API、File、Code、Browser 和 Artifact capability；所有 capability 均带统一 `CapabilityPolicy`、`CapabilityRiskProfile`、workspace scope、role policy、side-effect、network / credential / data access / audit policy。
- Policy / router：`CapabilityRouter.route` 支持自动 skill selection、pinned skill override、skill allowed_tools 限制、cross-workspace knowledge block、MCP permission denied 和 not-configured target-blocked evidence；Tool / MCP boundary 通过 PHASE02 `ToolCard` 暴露 permission 和 trace fields。
- Focused tests：`pytest -q tests/capability/test_capability_skill_layer.py -p no:cacheprovider` -> 7 passed；RED 首次运行 7 failures，根因为 `zuno.capability.layer` 不存在。
- Compatibility tests：`pytest -q tests/capability/test_capability_skill_layer.py tests/agent/test_capability_layer_surfaces.py tests/agent/test_capability_system.py tests/agent/test_capability_registry.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider` -> 27 passed。
- 边界：本 phase 不声明 PHASE07 Security / Governance gates 已完成，不声明 PHASE09 Planner 已消费 capability registry，不声明 MCP 真实外部服务已配置；`mcp.lark.send_message` 当前以 target-blocked dependency probe 表达。

## 停止条件

- SkillCard 需要改成 multi-agent runtime 才能表达。
- Tool capability 会绕过 approval 或 credential-ref-only policy。
- Capability route 与现有 ToolCard contract 冲突且无法兼容。
