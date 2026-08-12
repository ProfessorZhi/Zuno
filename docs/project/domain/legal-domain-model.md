# Legal Domain Model：法律业务世界是什么？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪些对象是法律业务世界的 Canonical State，谁可以改变它？
owner: Platform / Domain Service
replaces: `docs/project/modules/01-product-surface.md`、`03-knowledge-agentic-graphrag.md` 中的重复领域描述（Superseded）

## Part A — Architecture Narrative

法律系统需要表示的不是“模型记住了什么”，而是案件世界中哪些内容在当前证据和审查规则下被
认为成立。Matter 给出工作范围，DocumentVersion 给出来源，Claim 和 Evidence 连接需要证明的
主张与材料，Finding 和 WorkProduct 表示可交付的分析结果。每个重要对象都需要稳定身份、版本、
来源、权限、依赖和审查语义，否则同一案件在不同 Run 中会被重复解释，用户也无法知道结论是否
仍然有效。

例如一次争议识别可以从文档中抽取 Event、Fact 或 ConflictProposal；这些结果可能很合理，但
它们没有因此成为业务真相。Knowledge、Legal Capability 或 Agent 只能提出 Proposal，Domain
Owner 结合 Evidence、权限、Schema 和 Review 决定是否提交 Canonical Version。新证据到来时，
依赖它的 Fact、Conflict 或 Finding 可能 stale，系统应重新评价或请求人工确认，而不是静默覆盖。

Domain Model 因此与 LLM、Prompt、Knowledge、Memory、Skill、Tool、Graph 和 LangGraph State
分离。最小替代方案是 JSON + PostgreSQL；只有当 identity/version/provenance/dependency/review
和审计门禁能解决真实跨文档任务问题时，才保留更正式的对象边界。对象数量必须由跨运行复用和
权限/审查需要证明，不能由名词数量推动。

## Part B — Detailed Architecture Specification

### Canonical admission contract

Provider 输入为带 `input_domain_version`、`capability_version`、provenance、Evidence lineage 和
权限范围的 Proposal；输出只能是 `Proposal`、`Candidate`、`Observation`、`Reference` 或 `Receipt`。
Domain Owner 依次执行 Schema、identity、provenance、dependency、permission、version/CAS、state
transition 和必要 Human Review，成功后提交新的 Canonical Version；失败进入 rejected、stale、
review_required 或 reconciliation，不静默重试或覆盖。

每个 Canonical Object 的持久化都必须能回答 identity、version、owner、mutation authority、source、
dependency、review、audit 和 staleness。若对象只在单次检索或单个 Provider 中存在，则保持 derived
view/proposal，不新增 Domain 表。
Canonical mutation 以稳定 identity 与幂等键收敛重复提交；发生版本冲突时返回 stale 或
review_required，而不是产生第二个业务版本。

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

## Part-A owner and mutation boundary

Domain Owner 的责任范围包括 Tenant、Workspace、Matter、DocumentVersion、Fact、Claim、Evidence、
Conflict、Dispute、LegalIssue、Finding、HumanDecision、WorkProduct、Review、DomainVersion 和
Provenance 的正式版本。这个 Owner 清单不等于每个名称都必须立即新增一张表：`Fact`、`Event`、
`Conflict`、`Dispute`、`LegalIssue`、`ApplicableLaw` 等仍须先满足 identity、version、dependency、
review 和 audit 的必要性条件，才从 typed proposal/derived view 升级为独立 Canonical Object。

只有 Domain Owner 能执行 Canonical mutation。任何 Provider 输出都必须经过 Schema、Provenance、
Evidence、Permission、Version、State transition 和必要 Human Review；业务语义不随 Runtime、
Memory Provider 或模型拓扑漂移。

## Scope boundary

Knowledge owns retrieval data and EvidenceCandidate；Agent owns plan/control；Memory owns reusable context；Tool owns external effects；Security owns decision/policy facts；Eval owns evaluation facts。它们可以引用 Domain State，但不能复制最终状态机。

## Current / Target / Gap

- Current：仓库已有通用 DocumentVersion、Claim/Evidence 和 Product/Agent tables；未证明完整 Legal Domain Kernel。
- Target：最小 Canonical Domain Model 与 Proposal → Validation → Version → Review 闭环。
- Gap：Matter/Fact/Finding identity、dependency invalidation、human review 和跨服务 write trace 未实现证明。
