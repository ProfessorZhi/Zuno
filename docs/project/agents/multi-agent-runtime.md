# Multi-Agent Runtime：Agent 怎样协作而不复制业务代码？

status: normative-target
canonical_question: Multi-Agent 的协作层级、共享状态和服务边界是什么？
owner: Agent Runtime Service

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

## Eval

比较 Single Agent、Role Pipeline、Ephemeral Worker、Specialized Profile、Persistent Team，固定模型/语料/工具/Token/时间预算，测 Legal quality、Evidence、Reviewer Acceptance、latency、cost、model/tool calls、failure/replan。若 L2 已足够，删除 L4 复杂度。

## Current / Target / Gap

- Current：仓库当前存在 Agent/runtime 代码和 worker 基础设施，但没有证明持久 Multi-Agent Team 的生产运行证据。
- Target：同一 `agent-runtime-service` 内的可组合 profiles、受控 delegation、共享 Domain/Capability Contract 和独立 checkpoint。
- Gap：需要 A/B/C 与 L0-L4 Benchmark、长任务恢复、权限不放大和资源隔离证据。
