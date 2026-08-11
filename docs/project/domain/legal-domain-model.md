# Legal Domain Model：法律业务世界是什么？

status: normative-target
canonical_question: 哪些对象是法律业务世界的 Canonical State，谁可以改变它？
owner: Platform / Domain Service
replaces: `docs/project/modules/01-product-surface.md`、`03-knowledge-agentic-graphrag.md` 中的重复领域描述（Superseded）

## Definition

Domain Model 不是 LLM Model、Prompt、Knowledge Base、Memory、Skill、Tool、GraphRAG 或 LangGraph State。它是系统对 Matter 中可审计业务状态的正式表示，包含 identity、version、provenance、state、ownership、mutation authority、staleness、dependency、review 和 audit。

## Minimum Canonical Objects

| Object | Meaning | Owner / write rule |
|---|---|---|
| `Matter` | 一项法律工作及租户/权限边界 | Domain Service 创建和版本化 |
| `DocumentVersion` | 一个可追溯的来源文档版本 | Domain/Ingestion contract；内容 provenance 不可伪造 |
| `Claim` | 需要证据支持的主张 | Agent/Capability proposal；Domain owner 接受 |
| `Evidence` | 已接受、可引用、带来源和权限的证据 | Domain owner commit；Knowledge 只产生 candidate |
| `Finding` | 基于版本化 Claim/Evidence 的工作结论 | Domain owner + policy/Human Review |
| `HumanDecision` | 人工接受、拒绝、修订或发布决定 | Reviewer authority |
| `WorkProduct` | 面向用户/系统的版本化交付物 | Domain/Product publication gate |

`Case` 默认是 Matter 的法律 Profile/别名；`Party`、`Fact`、`Event`、`Conflict`、`Dispute`、`LegalIssue`、`StatuteVersion`、`LegalElement`、`ApplicableLaw`、`SimilarCase` 先作为 typed proposal、derived view 或 capability output。只有跨运行身份、版本、权限、依赖和审查需求被证明，才升级为 Canonical object。

## Provider rule

Agent、Legal Intelligence、Knowledge、LLM、OSS、API 和 MCP Provider 只能返回 `Proposal`、`Candidate`、`Observation`、`Reference` 或 `Receipt`，不能直接写 `FactVersion`、`ConflictVersion` 或 `FindingVersion`。

## Scope boundary

Knowledge owns retrieval data and EvidenceCandidate；Agent owns plan/control；Memory owns reusable context；Tool owns external effects；Security owns decision/policy facts；Eval owns evaluation facts。它们可以引用 Domain State，但不能复制最终状态机。

## Current / Target / Gap

- Current：仓库已有通用 DocumentVersion、Claim/Evidence 和 Product/Agent tables；未证明完整 Legal Domain Kernel。
- Target：最小 Canonical Domain Model 与 Proposal → Validation → Version → Review 闭环。
- Gap：Matter/Fact/Finding identity、dependency invalidation、human review 和跨服务 write trace 未实现证明。
