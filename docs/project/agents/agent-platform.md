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
 → Domain Snapshot / EvidenceRequirement / stale dependencies
 → capability and Knowledge actions
 → Proposal / Observation / Receipt
 → acceptance / replan / HITL
 → Domain Owner commit
 → RunOutcome / WorkProduct reference
```

## Domain-aware Runtime Contract

Native Domain-aware Runtime 的候选差异不是“能调用法律 API”，而是 Runtime 在计划和完成
判断时能消费版本化的 Domain Contract，例如：

- 当前缺少哪个 `Fact`、`Evidence` 或 `EvidenceRequirement`；
- 哪个 `Claim`、`Dispute` 或 `Finding` 因新证据而 `STALE`；
- 哪个 `EvidenceRef` 支持当前主张，哪些关系仍需验证；
- 哪个 Domain Condition 满足后才允许完成当前 Step 或提交 Review。

Agent 仍然只能返回 Proposal、Candidate、Observation 或 Receipt；Domain Owner 才能
提交正式版本。业务语义与 Runtime 深度集成，但实现保持松耦合：WorkBuddy/Dify/Pi、
普通 Workflow 或 LangGraph 都可以作为 Host/Runtime Provider，前提是遵守同一 Contract。

这是 `ACCEPTED_TARGET + H2`，不是 Current 质量证据。若 WorkBuddy + Zuno Legal Backend
已经实现同样的 Domain Conditions、staleness、Evidence Gate 和恢复对账，则 Native
Runtime 不获得额外保留理由。

所有外部动作需要 Security/Approval/Idempotency/Effect Receipt。Model 只能提出计划、查询、Proposal 或 Action；不能批准 Domain commit、拿 secret 或发布不可逆副作用。

## Runtime provider

LangGraph、Plain Python workflow、State Machine、Pi 或 Host Runtime 都是 provider。LangGraph 只在 Agent Runtime Service 内负责 orchestration/durable workflow；Checkpoint 是 control state，不是 Domain State。

## Capability and Skill

Skill 是 HOW；Capability 是 WHAT；Tool 是 HOW executed；Knowledge 是可检索信息；Memory 是可复用上下文；Domain State 是业务世界当前状态。法律能力 Contract 不嵌入每个 Agent，Provider 通过统一 Proposal boundary 接入。

## Current / Target / Gap

- Current：仓库有 Agent runtime/graph/checkpoint 和 FastAPI run surfaces，但是单 backend image；没有独立 Agent Runtime Service evidence。
- Target：Python Agent Runtime Service + coordinator + profile/worker pools。
- Gap：multi-agent profile benchmark、service contract、独立 scaling/failure 和 runtime/domain reconciliation trace。
