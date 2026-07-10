# Capability and Skill Layer

所属运行域：Capability & Tool。

## 定位

Capability & Tool 负责把 Agent 的意图转成可治理的能力调用。Skill 定义任务方法，Tool 执行具体动作；二者不能混写。

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
-> CapabilityRouter
-> Policy / Approval
-> CredentialRef
-> ExecutionAdapter
-> ResultNormalizer
-> ToolTrace
-> Observation
```

副作用工具必须有 approval、timeout、幂等 key 和 trace。Agent 只能消费 normalized observation，不直接依赖工具内部返回结构。

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
