# Agent Platform：怎样计划、执行和组合能力？

status: normative-target
canonical_question: Agent 如何把任务、计划、能力、权限和结果连接起来？
owner: Agent Runtime Service
replaces: `docs/project/modules/06-agent-core-planning-control.md`、`07-capability-skill.md`（Superseded）

## Boundary

FastAPI 是 Application/API Interface；Agent Runtime 是长运行控制平面。Runtime owns `AgentRun`、`Plan`、`Step`、budget、delegation、checkpoint、interrupt、replan 和 control outcome；不拥有 Matter、Fact、Evidence、Finding、Permission 或 Tool Effect。

## Flow

```text
Run Submit
 → Task / Goal / Policy Snapshot
 → Coordinator creates Plan
 → capability and Knowledge actions
 → Proposal / Observation / Receipt
 → acceptance / replan / HITL
 → Domain Owner commit
 → RunOutcome / WorkProduct reference
```

所有外部动作需要 Security/Approval/Idempotency/Effect Receipt。Model 只能提出计划、查询、Proposal 或 Action；不能批准 Domain commit、拿 secret 或发布不可逆副作用。

## Runtime provider

LangGraph、Plain Python workflow、State Machine、Pi 或 Host Runtime 都是 provider。LangGraph 只在 Agent Runtime Service 内负责 orchestration/durable workflow；Checkpoint 是 control state，不是 Domain State。

## Capability and Skill

Skill 是 HOW；Capability 是 WHAT；Tool 是 HOW executed；Knowledge 是可检索信息；Memory 是可复用上下文；Domain State 是业务世界当前状态。法律能力 Contract 不嵌入每个 Agent，Provider 通过统一 Proposal boundary 接入。

## Current / Target / Gap

- Current：仓库有 Agent runtime/graph/checkpoint 和 FastAPI run surfaces，但是单 backend image；没有独立 Agent Runtime Service evidence。
- Target：Python Agent Runtime Service + coordinator + profile/worker pools。
- Gap：multi-agent profile benchmark、service contract、独立 scaling/failure 和 runtime/domain reconciliation trace。
