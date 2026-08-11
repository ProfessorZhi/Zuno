# Product Architecture：用户如何完成法律工作？

status: normative-target
canonical_question: 用户、Host、Matter、Review 和 WorkProduct 的产品边界是什么？
owner: Product / Domain Surface
replaces: `docs/project/modules/01-product-surface.md`（Superseded）

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

## Current / Target / Gap

- Current：仓库有 FastAPI Product API 和 Web/Desktop client；目标业务状态、历史用户和真实交付保持以 facts/status/evidence 为准。
- Target：外部 Host 可调用 Product/Domain API；Product 与 Service/Domain/Runtime 分离。
- Gap：没有独立 edge-api/platform-domain service 的部署和 E2E 证据。
