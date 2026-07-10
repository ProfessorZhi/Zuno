# Capability and Skill Layer

所属运行域：Capability & Tool。

## 定位

Capability & Tool 负责把 Agent 的意图转成可治理的能力调用。Skill 定义任务方法，Tool 执行具体动作；二者不能混写。

层级关系：

```text
Function Calling = 模型表达结构化调用意图的协议/语言
Capability       = 系统可用能力的描述、目录、策略和路由
Skill            = 使用一组能力完成某类任务的 SOP、模板和验收规则
Tool / MCP       = 原子外部动作、数据访问和资源能力
Tool Runtime     = 宿主代码的审批、凭据、执行、timeout、normalize 和 trace
```

模型只负责决策和结构化意图，宿主代码负责真实执行。

## 核心对象

- SkillCard：任务方法说明、适用场景、输入输出约束。
- CapabilityCard：能力类型、策略、owner、trace 要求。
- CapabilityRouter：从 CapabilityPlan 选择可用能力。
- KnowledgeCapability：检索、GraphRAG、citation 相关能力。
- ToolCapability：外部动作、MCP、本地工具。
- ArtifactCapability：文档、报告、导出等产物生成。
- ToolCard：具体工具 manifest。
- ToolRequest：一次工具调用意图。
- Approval：副作用审批。
- CredentialRef：凭据引用，禁止把 secret 写入 trace。
- ExecutionAdapter：工具执行适配器。
- ResultNormalizer：把工具结果归一成 Agent observation。
- ToolTrace：审批、执行、timeout、错误和结果摘要。

## Runtime

```text
CapabilityPlan
-> Skill discovery
-> progressive Skill loading
-> CapabilityRouter
-> structured ToolCallIntent
-> Policy / Approval
-> CredentialRef
-> ToolCard / MCP tool
-> ExecutionAdapter
-> ResultNormalizer
-> ToolTrace
-> Observation
```

副作用工具必须有 approval、timeout、幂等 key 和 trace。Agent 只能消费 normalized observation，不直接依赖工具内部返回结构。

## Skill 渐进式加载

1. 启动时只加载 `SkillMetadata`。
2. 任务匹配后加载 `SkillInstruction`。
3. 执行需要时加载脚本、模板和参考资料。
4. 所有加载进入 `SkillLoadTrace`。

```yaml
skill_card:
  skill_id: string
  description: string
  applicability: [condition]
  required_capabilities: [capability_id]
  allowed_tools: [tool_id]
  required_memory_scopes: [scope]
  retrieval_profile: string
  acceptance_criteria: [criterion]
  resource_refs: [ref]
```

Skill 不是 Tool；Skill 是使用能力完成任务的方法包。Capability 可以描述 KnowledgeCapability、ToolCapability 和 ArtifactCapability，但不拥有 Knowledge Runtime 或 Tool Runtime 的具体执行。

## Tool 风险与审批

| 风险 | 示例 | 默认策略 |
| --- | --- | --- |
| Read-only local | 读取文件、查询知识库 | policy allow + trace |
| Read-only remote | Web/API 查询 | domain/network policy + trace |
| Local write | 写 artifact、修改文件 | workspace scope + idempotency |
| External side effect | 发邮件、创建远端记录 | explicit approval |
| Destructive | 删除、覆盖、批量变更 | explicit approval + preview + audit |

Tool contract 必须包含 JSON schema、input/output、side-effect class、timeout、retry、idempotency key、credential reference、redaction、approval policy 和 trace requirements。

## 当前与短期目标

Current：

- capability registry/control plane、tool adapters、MCP surfaces 和多个工具实现已存在。

Short-term：

- P1 选择 2-3 个真实工具完成 approval / timeout / trace 闭环。
- 工具失败必须进入 Agent observation，使 Agent 可 replan 或 abstain。
- credential 只以 reference 进入 runtime 和 trace。

Future Optional：

- marketplace。
- 复杂远程企业工具治理。
- Firecracker 级隔离。
