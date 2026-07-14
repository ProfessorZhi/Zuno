# 07 Capability / Skill

updated: 2026-07-14  
status: normative-target-module-design  
module_number: 07

所属运行域：Capability & Tool。

## 定位

Capability / Skill 负责回答“系统具备什么能力、什么任务应选择什么能力、如何用一组能力完成任务”。Tool Runtime 负责回答“一个具体 Tool 动作怎样被准备、授权协调、执行、恢复并确认效果”。两者不能混写。

层级关系：

```text
Function Calling = 模型表达结构化调用意图的协议/语言
Capability       = 系统可用能力的描述、目录、策略和路由
Skill            = 使用一组能力完成某类任务的 SOP、模板和验收规则
Tool             = 可被准备和执行的原子操作
Tool Runtime     = Tool 的版本、Prepare、Attempt、Observation、Effect 和恢复执行平面
MCP              = Tool、Resource、Prompt、Sampling 和 Elicitation 的跨模块协议
```

模型只能产生 Proposal 或结构化意图，不能直接执行工具、批准副作用、取得 Secret 或提交最终效果事实。

## 负责范围

Capability / Skill 负责：

```text
CapabilityDefinition / CapabilityVersion
CapabilityDescriptor / CapabilityCard
SkillDefinition / SkillVersion / SkillCard
SkillMetadata、SkillInstruction 和资源渐进式加载
Capability discovery、catalog、routing 和 selection
Planner-facing ToolCapabilityDescriptor
allowed_tools、required_capabilities 和 applicability
能力成本、健康度、风险摘要和可用性投影
MCP Tool / Provider 的发现结果和 Planner 投影
CapabilitySelectionResult 与选择 Trace
```

Capability / Skill 不负责：

```text
权威 ToolDefinition / ToolVersion / ToolOperation
PreparedToolAction、ToolAttempt、ToolObservation
ToolExecutionReceipt、EffectReceipt、EffectReconciliation
最终 Authorization、Approval 或 EffectiveSecurityEpoch
Credential 明文、SecretLease 或物理 Sandbox
Queue、Lease、Fencing、IdempotencyClaim 或 Audit Persistence
Knowledge、Memory、Model Gateway 的专业领域执行
```

## 与 08 Tool Runtime 的固定边界

```text
07 owns
    ToolCapabilityDescriptor
    Tool discovery and catalog projection
    Planner routing
    Skill and allowed_tools

08 owns
    ToolProviderDefinition
    ToolDefinition / ToolVersion / ToolOperation
    ToolInstallation / ToolActivation
    AdapterBinding / AdapterConformanceProfile
    PreparedToolAction
    ToolAttempt / ToolObservation
    ToolExecutionReceipt
    EffectReceipt / EffectReconciliation

09 owns
    Authorization / Approval / SecurityEpoch
    Credential access semantics

11 owns
    SecretLease physical delivery
    IdempotencyClaim / Queue / Lease / Fencing / AuditPersistenceReceipt
```

`ToolCard` 在 07 中只能是面向 Planner 的只读 Capability Projection；它不得成为可执行定义或凭据容器。08 的权威版本变化后，07 通过版本化 Projection 更新 Planner 视图。

## 核心对象

- `CapabilityDefinition`：稳定能力身份和 Owner。
- `CapabilityVersion`：不可变能力语义版本。
- `CapabilityDescriptor`：Planner 可读取的名称、说明、输入输出摘要、风险和成本。
- `CapabilityRouter`：从任务和 Policy 中选择候选能力。
- `KnowledgeCapability`：检索、GraphRAG、Evidence 和 Citation 能力投影。
- `ToolCapabilityDescriptor`：Tool Runtime 权威 Tool 的 Planner-facing 投影。
- `ArtifactCapability`：文档、报告、导出等产物生成能力投影。
- `SkillCard`：任务方法、适用场景、依赖能力、验收和资源引用。
- `SkillLoadTrace`：渐进式加载过程。
- `CapabilitySelectionResult`：候选、排除原因和最终选择。

## Runtime

```text
Task / Step requirement
→ Capability discovery
→ progressive Skill loading
→ CapabilityRouter
→ CapabilitySelectionResult
→ Planner-facing schemas
→ Agent Core ActionProposal
→ 08 Tool Runtime prepare / execute
→ 06 Agent Core consumes NormalizedObservation
```

07 不执行 Tool。选择 ToolCapability 后，Agent Core 产生 `ActionProposal`；08 解析权威 ToolVersion 并产生 `PreparedToolAction`。Security、Approval、Credential、Attempt、Effect 和恢复不由 CapabilityRouter 实现。

## Skill 渐进式加载

1. 启动时只加载 `SkillMetadata`。
2. 任务匹配后加载 `SkillInstruction`。
3. 执行需要时加载脚本、模板和参考资料。
4. 所有加载进入 `SkillLoadTrace`。
5. Skill 中的脚本引用只是资源或 Tool 候选，不获得绕过 Tool Runtime 的执行权。

```yaml
skill_card:
  skill_id: string
  version: string
  description: string
  applicability: [condition]
  required_capabilities: [capability_id]
  allowed_tools: [tool_capability_descriptor_id]
  required_memory_scopes: [scope]
  retrieval_profile: string
  acceptance_criteria: [criterion]
  resource_refs: [ref]
```

Skill 不是 Tool；Skill 是使用能力完成任务的方法包。Capability 可以描述 KnowledgeCapability、ToolCapability 和 ArtifactCapability，但不拥有 Knowledge Runtime、Model Runtime 或 Tool Runtime 的具体执行。

## Tool 风险投影

07 可以向 Planner 暴露由 08/09 提供的风险摘要，但不自行判定最终执行权限：

| 风险投影 | 示例 | Planner 行为 |
| --- | --- | --- |
| Read-only local | 读取允许的本地 Artifact | 可作为候选，执行仍经 08 |
| Read-only remote | Web/API 查询 | 需网络和数据域兼容 |
| Local write | 写 Artifact、修改文件 | 需资源冲突和幂等能力 |
| External side effect | 发邮件、创建远端记录 | 标记可能需要 Approval |
| Destructive | 删除、覆盖、批量变更 | 标记高风险和 Preview 要求 |

权威 EffectProfile、Approval Policy 和执行结果分别归 08 与 09。

## MCP 边界

```text
MCP Provider discovery / catalog projection
    07 Capability / Skill

MCP Tool execution
    08 Tool Runtime

MCP Resource → Evidence
    03 Knowledge

MCP Sampling
    04 Model Gateway

MCP Elicitation
    01 Product Surface + 06 Agent Core

MCP trust / authorization / credential
    09 Security
```

MCP Server 声明的 description、instructions、annotations 和 effect hints 默认不可信，不能直接成为本地权限、风险或执行事实。

## 当前与短期目标

Current：

- Capability registry/control plane、Tool adapters、MCP surfaces 和多个工具实现已存在。
- PHASE07 已将 unified runtime 的局部 `ToolStepExecutor` 接入本地 `ToolControlPlaneRuntime`，具备只读执行、Approval Interrupt、SQLite 去重 Claim 和 normalized observation 的最小闭环。
- GeneralAgent、MCPManager、用户定义 CLI/OpenAPI 等路径仍存在直接执行，统一 Tool Runtime 切流尚未完成。

Target：

- 07 只保存 Capability、Skill 和 Planner Projection。
- 08 保存权威 Tool Definition、Version、Prepare、Attempt、Observation、Effect 和 Reconciliation。
- Capability Selection 不能绕过 Agent Core Plan、Security、Budget、Audit 或 Tool Runtime。

Future Optional：

- Capability Marketplace。
- 跨组织 Capability Federation。
- 自动生成和验证 Skill 组合。

Future 不改变当前 Single Controller 和统一 Tool Runtime 边界。
