# Agent Platform：怎样计划、执行和组合能力？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Agent 如何把任务、计划、能力、权限和结果连接起来？
owner: Agent Runtime Service
replaces: `docs/project/modules/06-agent-core-planning-control.md`、`07-capability-skill.md`（Superseded）

## Part A — Architecture Narrative

Agent Runtime 的价值不在于把每个任务都变成自治 Agent，而在于把一个复杂法律任务拆成可观察、
可暂停、可恢复的执行过程。用户提交案件分析后，Coordinator 读取任务、权限、Domain Snapshot
和 EvidenceRequirement，选择一个 Plan；独立的 Evidence、Research 或 Dispute profile 可以并行
工作，Join 阶段再检查证据是否足够，最后由 Domain Owner 决定哪些 Proposal 可以提交。

Runtime State 记录 Run、Plan、Step、Branch、Interrupt 和 checkpoint，Domain State 记录 Matter、
Fact、Evidence、Finding 等业务世界。二者分离使 Runtime Provider 可以从 LangGraph 换成普通状态机、
Pi 或 Host Runtime，而不改变法律语义。Memory 只是可复用上下文，Capability 是可替换能力，
Tool 是执行通道；它们都不能直接批准 Domain mutation。

主要失败是 Plan 运行期间新证据到来、权限被撤销或一个外部 Tool 返回未知结果。此时 Retry 不等于
Replan，旧 Plan 不能静默继续；系统必须创建新的 PlanVersion、重新授权、对账 Receipt 或请求
人工复核。若 WorkBuddy + Zuno Legal Backend 已经能完成同样的 Domain Condition、Evidence Gate
和恢复语义，Native Runtime 应缩减而不是凭概念保留。

## Part B — Detailed Architecture Specification

### Runtime contract

`RunSubmit` 接收 Task、PolicySnapshot、DomainVersion、EvidenceRequirement 和预算；Coordinator 产生
不可变 `PlanVersion`，每个 Step 记录输入快照、Capability/Tool binding、权限 epoch、attempt 和
output receipt。Step 失败区分 transient、blocked、stale、unknown_effect 和 invalid；Retry 只适用
幂等瞬态故障，输入或业务条件变化必须 Replan。Join/Final Gate 未通过时，Run 只能等待、部分完成、
拒答或进入 Human Review，不能直接发布 Finding。

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

## Part-A execution model

默认执行模型是 `Single Controller + Plan`：简单任务使用确定性单步 Plan，复杂任务使用动态
Plan DAG；固定的 AgentRunGraph 负责生命周期，Plan DAG 负责业务步骤，StepExecutionGraph
负责执行、重试和汇合。可组合能力包括 Plan-and-Execute、ReAct、Reflection、Replan 和 Reflexion，
但 Retry 不等于 Replan，也不是每个 Step 都自动触发模型 Reflection。

每个 Step 都经过适用的 Action Evaluation、Step Acceptance/Reflection、Join Evaluation/Reflection、
Final Gate 和 Final Reflection。Reflection 是受策略、预算和 Eval 控制的能力，不是隐藏思维链的
持久化协议。

## Capability and Skill

Skill 是 HOW；Capability 是 WHAT；Tool 是 HOW executed；Knowledge 是可检索信息；Memory 是可复用上下文；Domain State 是业务世界当前状态。法律能力 Contract 不嵌入每个 Agent，Provider 通过统一 Proposal boundary 接入。

Zuno 只拥有 Memory 的 Scope、Write Gate、Recall Gate、Promotion Gate 和 Context Contract。
OpenViking 或其他 Memory/Context 实现是可替换 Provider，不是 Canonical Domain Store，也不是
所有部署都必须存在的 Runtime 组件；历史项目中用户参与过 OpenViking 接入这一事实仍由
`docs/project/facts/` 单独维护。

## Current / Target / Gap

- Current：仓库有 Agent runtime/graph/checkpoint 和 FastAPI run surfaces，但是单 backend image；没有独立 Agent Runtime Service evidence。
- Target：Python Agent Runtime Service + coordinator + profile/worker pools。
- Gap：multi-agent profile benchmark、service contract、独立 scaling/failure 和 runtime/domain reconciliation trace。
