# Multi-Agent Runtime：Agent 怎样协作而不复制业务代码？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Multi-Agent 的协作层级、共享状态和服务边界是什么？
owner: Agent Runtime Service

## Part A — Architecture Narrative

多个 Agent profile 只有在它们带来清晰的角色隔离、并行收益或不同权限/资源策略时才有意义。
复杂案件分析可以先由一个 Coordinator 生成 Plan，再让 Evidence、Dispute 和 Legal Research
profile 作为短生命周期 worker 并行执行；它们共享同一 Domain、Capability、Knowledge、Security
和 Eval Contract，因此不会因为角色不同就复制法律业务代码。

默认选择是 L0 Single Agent、L1 Role Pipeline 或 L2 Ephemeral Worker。L3 Specialized Profile
需要可解释的角色、权限、知识范围或模型策略；L4 Persistent Team 只有在独立长期状态、SLA、
资源池或发布生命周期被证明时才值得保留。L5 Autonomous Society 不属于当前目标。

如果一个强 Agent + parallel tools 已经达到相同的证据充分性、人工接受率、延迟和成本，多 Agent
拓扑应删除。主要失败是 delegation 放大权限、共享 Context 污染或一个 worker 的恢复状态与主
Controller 不一致；因此协作必须通过受版本约束的 Proposal、Snapshot 和 Receipt，而不是自由写共享事实。
Multi-Agent 不负责拥有 Canonical Fact、Permission、Secret 或最终 WorkProduct；这些责任留在
对应 Owner。

## Part B — Detailed Architecture Specification

### Delegation and shared-state contract

Coordinator 只向 profile/worker 发送受 `RunId`、`PlanVersion`、`DomainVersion`、scope、budget 和
permission downscope 约束的任务；worker 返回 Proposal、Observation、Reference 或 Receipt，不得
直接写共享 Domain State。Join 以 branch identity 和 input version 去重，重复结果幂等；失败分为
worker retry、replan、cancel、blocked 或 manual review。Delegation 不能扩大权限、Memory scope 或
Tool grant；恢复时 Runtime 先对账 branch receipt，再恢复或创建新的 PlanVersion。

## Levels

```text
L0 Single Agent
L1 Role Pipeline
L2 Ephemeral Worker / parallel tool
L3 Specialized Domain Agent profile
L4 Persistent Agent Team
```

优先验证 L0-L2；L3 由 role、skill、Knowledge Scope、Capability Binding、Permission、Memory/Model/Delegation Policy 区分。L4 只有独立长期状态、SLA、权限、资源池或发布生命周期证据才进入 Target。

## Shared Kernel

Coordinator、Evidence Agent、Dispute Agent、Legal Research Agent、Similar Case Agent、Judgment Assistance Agent、Contract Review Agent 和 Reviewer Agent 共享 Domain Kernel、Legal Capability Contracts、Knowledge Infrastructure、Security、Eval 和同一 Proposal/Review boundary。多个 Agent 不等于多套法律业务代码。

## Service rule

默认所有 profiles 运行在 `agent-runtime-service` 中，使用 ephemeral worker。一个 Agent 不自动成为一个微服务；拆分必须证明 independent deployment、security boundary、SLA 或 resource isolation 的收益。

`Single Controller + specialized role/profile + parallel steps` 是 Part-A 默认模型，不是自治
Agent Society。只有当某个 Agent 同时需要独立 Context、Permission、Model、Tool、Knowledge、
Resource Pool、Lifecycle 或 Evaluation，才保留独立 Agent Identity；否则降级为 Step、Skill 或
Capability Provider。

## Eval

比较 Single Agent、Role Pipeline、Ephemeral Worker、Specialized Profile、Persistent Team，固定模型/语料/工具/Token/时间预算，测 Legal quality、Evidence、Reviewer Acceptance、latency、cost、model/tool calls、failure/replan。若 L2 已足够，删除 L4 复杂度。

## Current / Target / Gap

- Current：仓库当前存在 Agent/runtime 代码和 worker 基础设施，但没有证明持久 Multi-Agent Team 的生产运行证据。
- Target：同一 `agent-runtime-service` 内的可组合 profiles、受控 delegation、共享 Domain/Capability Contract 和独立 checkpoint。
- Gap：需要 A/B/C 与 L0-L4 Benchmark、长任务恢复、权限不放大和资源隔离证据。
