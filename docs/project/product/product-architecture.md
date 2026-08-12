# Product Architecture：用户如何完成法律工作？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 用户、Host、Matter、Review 和 WorkProduct 的产品边界是什么？
owner: Product / Domain Surface
replaces: `docs/project/modules/01-product-surface.md`（Superseded）

## Part A — Architecture Narrative

法院用户面对的不是一个抽象的 Agent Run，而是一项需要持续处理材料、核对证据并交付成果的
法律工作。用户进入 Matter，上传或引用 DocumentVersion，提出案件问题，等待系统整理证据和
候选分析，最后在 Review 中确认哪些内容可以进入 WorkProduct。这个场景要求产品入口能清楚地
展示工作状态、证据依据和人工决定，而不能把一段模型文本当作业务完成。

Zuno UI、WorkBuddy、Dify、企业 Portal 或 MCP Client 都可以承担 Host 角色。Host 负责意图、
交互和交付展示；Domain 负责案件事实；Agent Runtime 负责长任务；Knowledge 负责检索；Review
负责业务复核。这样的边界让外部 Host 可以被替换，也避免某个 UI 或 Agent 框架获得全部 Canonical
写权限。最小方案是 Host + Legal Backend；只有当 Domain 条件能够影响计划完成、stale 传播和
恢复，并在公平测试中产生额外收益时，才需要 Native Runtime 深度集成。

典型失败是用户看到 HTTP 200 或 checkpoint 完成，却没有得到已提交 Finding，或者 Host 把过期
材料生成的答案直接发布。产品层必须展示 versioned projection、Review 状态和明确的 blocked/
review_required，而不是隐藏这些边界。若普通 API + WorkBuddy 已经能提供同等门禁和可追溯交付，
Zuno 不应为保持独立 UI 或 Runtime 而增加复杂度。

## Part B — Detailed Architecture Specification

### Contract coverage

| Contract | Input | Output | Gate / owner |
|---|---|---|---|
| Matter command | Principal、Tenant、Matter intent、idempotency key | versioned command receipt | Platform Domain authorization |
| Review query | Review ID、DomainVersion、scope | versioned projection with evidence refs | Product reads; Domain owns state |
| WorkProduct delivery | accepted Finding、HumanDecision、delivery target | WorkProduct receipt or review_required | publication policy and audit |

HTTP 200 只表示应用接口完成自己的边界。若 Domain version、permission epoch 或 evidence gate
发生变化，交付必须返回 stale、blocked 或 review_required；重复命令按 idempotency key 收敛。
短暂的投递故障可以在相同 command version 下 bounded retry；未知交付结果必须恢复查询并对账，
不能用第二次发布代替 reconciliation。

## Scope

Product Surface 可以是 Zuno Web/Desktop、WorkBuddy、企业 Portal 或 MCP/API Client。它负责意图、入口、Matter/Review 展示、用户命令、Human Review 和 WorkProduct delivery；不拥有 Agent checkpoint、Knowledge index、Memory projection、Tool secret 或模型内部状态。

## Target flow

```text
User / External Host
  → edge-api authentication and request correlation
  → platform-domain Matter / Review command
  → Knowledge or Agent Run submission
  → Evidence / Proposal / HumanDecision
  → Finding / WorkProduct projection
  → optional approved Tool Effect
```

`Review` 是业务工作，不等于 `AgentRun`；一个 Review 可以引用多次 Run、多个 EvidenceVersion 和人工决定。Product 只能展示 Owner 提供的 versioned projection，不能因 HTTP 200 或 checkpoint 完成而宣布业务成功。

## Canonical / non-canonical

Platform Domain Service owns `Tenant`、`User`、`Workspace`、`Matter`、`DocumentVersion`、accepted Domain facts、`Review`、`HumanDecision` 和 `WorkProduct`。Agent、Knowledge、Tool、Security 和 Eval 通过 Contract 引用，不复制 Product 状态机。

## Part-A acceptance boundary

本专题的 `ACCEPTED_TARGET` 只冻结 Product/Host 与 Domain、Runtime、Review 的边界：WorkBuddy、
Dify、Pi 或 Zuno UI 都可以作为外部 Host；Host 不能因为拥有交互入口就获得 Canonical Domain
State 的全部写入权。真实产品交付、客户质量和生产部署仍由 facts、eval 和 readiness 证据决定。

## Current / Target / Gap

- Current：仓库有 FastAPI Product API 和 Web/Desktop client；目标业务状态、历史用户和真实交付保持以 facts/status/evidence 为准。
- Target：外部 Host 可调用 Product/Domain API；Product 与 Service/Domain/Runtime 分离。
- Gap：没有独立 edge-api/platform-domain service 的部署和 E2E 证据。
