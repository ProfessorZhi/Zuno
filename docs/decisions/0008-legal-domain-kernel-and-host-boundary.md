# ADR-0008：法律 Domain Kernel 与 Host 边界

- 状态：`accepted-target`
- 日期：2026-08-12
- 依据：`RED-KERNEL-V3`，基线 `0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f`
- 关联：历史架构审查过程保留在 Git history；本 ADR 是当前长期边界。
- 适用：Legal Domain State、Host Integration、Capability Provider、Agent Runtime、Knowledge、Memory、Security、Eval、Infrastructure
- 后续细化：ADR-0013 冻结九模块 Responsibility Taxonomy；ADR-0014 细化 Invocation / Publication、Citation、Lifecycle、Admission、Invalidation 和 Recovery 的权威 Owner。

## 阅读说明：本 ADR 与后续 ADR 的关系

本 ADR 决定的是“为什么保留最小法律领域后端、哪些对象进入第一阶段 Canonical Kernel、Generic Host 与 Native Runtime 怎样取舍”。它早于 Round 02 的九模块责任分类。

因此，本文中早期出现的“Legal Backend 负责 permission / audit”等宽泛表述，必须按 ADR-0013 / ADR-0014 的后续明确 Ownership 解释：

- 02 Legal Domain & Work Product 拥有 Canonical Domain State、Formal Admission、AdmissionReceipt、正式 WorkProduct 历史引用和 Domain invalidation truth；
- 03 Knowledge & Evidence 拥有 KnowledgeGeneration、task-level ReadinessDecision、EvidenceCandidate 和 CitationLineage；
- 08 Security & Governance 是 Authorization、Approval、Model Egress、Tool Permission、Secret / Credential 和 Effective Lifecycle Policy 的政策 Owner；
- 各 Store / Tool / Domain / Knowledge 边界执行安全政策并保存自己的 enforcement fact；
- 04 Agent Runtime & Control 只有在任务进入 Zuno Native Runtime 时拥有 Plan / Step / Checkpoint 等控制事实；Native Runtime 继续由测量门控。

这段说明是 **clarification（澄清）而不是新决策**。如果本文较早的宽泛措辞与 ADR-0013 / ADR-0014 的显式 Owner 冲突，以后者为准。

## Context

候选产品命题是“法律案件智能 + Agent 平台”。复杂度引入者必须证明：法律业务状态、证据依赖、人工决定和审计边界不能由 WorkBuddy / Dify / Pi / LangGraph / RAGFlow 等通用能力组合加普通 MCP / API 完全替代。

RED-KERNEL-V3 的关键结论不是“Zuno 已经优于通用 Host”，而是：

1. 完整独立 Host 和自研 Native Runtime 没有通过默认必要性证明；
2. 一个 Host-agnostic Legal Backend（与宿主解耦的法律后端）仍可能对跨文档、跨运行、人工修订、证据依赖失效和审计有价值；
3. 当时仓库没有法律 Domain Kernel 的完整 Current 证据，以下长期边界主要是 Target / Hypothesis；
4. GraphRAG、Persistent Multi-Agent、Long-term Memory、Event Sourcing、十一微服务和自研 Tool Runtime 都没有默认保留理由。

## Decision

### 1. 最小 Legal Domain Kernel

Legal Domain Model（法律领域模型）是对法律业务世界的正式、可审计表示，不是 LLM Model、Prompt、Knowledge Base、Memory、Skill、Tool、GraphRAG 或 LangGraph State。

第一阶段冻结的最小 Canonical Kernel 为：

| 类别 | Canonical 对象 | 边界 |
| --- | --- | --- |
| 根与来源 | `Matter`、`DocumentVersion` | `Case` 默认只是 Profile / 别名；只有独立身份、权限或生命周期证据才能成为新根 |
| 主张与证据 | `Claim`、`Evidence` | 正式对象必须有来源、版本、稳定位置、权限和可追溯关系 |
| 结论与人工权威 | `Finding`、`HumanDecision`、`WorkProduct` | Model / Provider 不能直接提交 |

`Party`、`Fact`、`Event`、`Conflict`、`Dispute`、`LegalIssue`、`StatuteVersion`、`LegalElement`、`ApplicableLaw`、`SimilarCase` 保留为领域语义候选，但默认是 typed Proposal、Projection、Derived View 或 Capability Provider 输出，不自动增加 Canonical 表和状态机。

一个新概念只有在能明确 Identity、Version、Provenance、State、Ownership、Mutation Authority、Staleness、Dependency、Review 和 Audit 时，才有资格进入正式 Canonical Kernel。

### 2. Domain State、Knowledge、Memory 与 Runtime 分离

- **Domain State**：业务世界正式承认的 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision 和 WorkProduct 版本。
- **Knowledge Projection**：围绕 DocumentVersion 生成的可重建解析、OCR、index、graph、KnowledgeGeneration、ReadinessDecision、EvidenceCandidate 和 CitationLineage；其当前 Owner 由 ADR-0013 / 模块 03 明确。
- **Memory / Context**：可复用上下文和经验，可压缩、过期、删除或按策略召回，不是权威事实源。
- **Runtime Control State**：Plan、Step、Checkpoint、Interrupt、Reducer 和恢复位置；只回答执行到哪里。
- **Tool Effect State**：现实动作的 PreparedAction、Attempt、EffectReceipt 和 Reconciliation；不等于 Domain State。

LangGraph、Pi、WorkBuddy 或其他 Runtime 不能把 Checkpoint 当作法律事实。Runtime 可以消费 / 产生版本化 Domain Contract，但 Domain Store 仍由 Canonical Owner 管理。

### 3. New Evidence 与版本化 PostgreSQL

默认使用 PostgreSQL 保存 Canonical Domain State、不可变 / 受控版本、依赖、HumanDecision、WorkProduct 历史引用和必要 Receipt；不默认引入 Event Sourcing。

新的正式 DocumentVersion / Evidence 被接纳后：

1. 根据正式依赖关系找到可能受影响的 Claim / Finding / WorkProduct；
2. 将受影响的正式结果标为 review-required / stale 类语义；
3. Event、Conflict、Dispute、ApplicableLaw 等派生结果按影响范围执行 bounded re-evaluation（有界重新评估）；
4. 必要时创建新的 Agent Run / Proposal；
5. 由 02 Canonical Owner 和所需 HumanDecision 提交新版本。

不在同一事务中盲目全量重算。恢复使用 DomainVersion、AdmissionReceipt、当前版本、Runtime Checkpoint 和必要 Effect / Security facts 对账；跨 Store 2PC 不是默认方案。

### 4. 默认 Host 边界

默认最小产品形态允许是：

```text
WorkBuddy / Dify / Pi / 法院已有系统 / 其他 Generic Host
  + Legal Skills / Knowledge Scope
  + MCP / API Legal Capability Provider
  + 最小 Zuno Legal Domain Backend（仅在跨运行业务状态确有必要时）
```

Host 可以负责交互、会话、普通工作流、简单问答、一般模型编排和普通工具接入。Zuno Legal Backend 保护需要长期稳定的法律业务 Contract：Canonical Domain State、正式 Evidence / Review、版本、历史引用、Formal Admission 和 staleness。

权限与生命周期政策不因为“后端负责业务状态”就归 02；其 Policy Owner 由 ADR-0014 明确为 08 Security & Governance。02 / 03 / 06 等边界只执行当前政策并保存自己的执行事实。

这个边界不宣称 Generic Host 缺少能力；它只是把需要长期验证的法律业务契约从 Host 的具体实现中隔离出来。

### 5. Runtime Provider 而非 Runtime 主权

Plain Python、Async Workflow、State Machine、LangGraph、Pi 或 Host 自带 Runtime 都是可替换候选。LangGraph 只有在 durable execution、Checkpoint、Interrupt / Resume、parallel / reducer、Replan 或 HITL 需求被 Benchmark 证明时才需要成为 Zuno 自有 Native Runtime 的关键 Provider。

如果任务进入当前 Target 的 Zuno Native Agent Runtime，则遵守后续固定原则：Single Controller（单控制器）；简单任务也有 Deterministic Single-Step Plan；复杂任务使用 Dynamic DAG Plan；不得通过 direct answer 绕过 Plan / Trace / Budget / AnswerPolicy / RunOutcome。

但 **Native Runtime 本身继续是 Conditional / Measurement-gated**。它若不能在 A/B/C 测量中证明比 Generic Host + Zuno Legal Backend 带来可归因收益，就应保持外置或删除，而不是因 LangGraph 已存在就成为产品前提。

### 6. Capability Provider

法律能力采用稳定 Capability Contract，例如：

`EVENT_EXTRACTION`、`EVENT_ALIGNMENT`、`CONFLICT_DETECTION`、`FACT_ARTICLE_MAPPING`、`SIMILAR_CASE_RETRIEVAL`、`LEGAL_APPLICABILITY`、`EVIDENCE_REASONING`。

Provider 可以由本地算法、LLM、fine-tuned model、OSS、API 或 MCP 实现，输出只能是 Proposal、Candidate、Observation、Reference 或非领域提交类 Receipt。02 Canonical Owner 负责正式 Domain Admission；03 负责 Knowledge / Citation candidate 语义；08 负责 Security policy。

### 7. Conditional 能力

- **GraphRAG**：Query Class / Evidence-gated，不是默认检索主干。
- **Multi-Agent / Specialist**：优先 Single Controller + parallel steps / subgraphs；Persistent Autonomous Team 不作为默认 Target。
- **Memory**：Working / Session 优先；Long-term 只有消融证明收益后启用，并可由 OpenViking 或 Host 等 Provider 提供。
- **Tool Runtime**：优先 MCP / API / CLI / existing sandbox + thin adapter；Zuno 只保护 Authorization / Approval binding、Idempotency、EffectReceipt、Audit 和 Reconciliation 语义。
- **Deployment**：模块化 Python Backend + Worker 优先；用户数不是微服务证据。

### 8. 安全可验证性

不采用“闭源不安全”或“开源天然安全”的判断。任何 Zuno 安全优势进入 Current 前，需要 Source-level Audit、Build Reproducibility、SBOM、Signed Artifact、Network Egress Audit、Secret / Model / Tool / Domain / Human Decision Trace、Sandbox Boundary Test 和部署主权等可复现证据。

Current Policy Ownership 以后续 ADR-0014 为准：Authorization、Approval、Egress、Secret 和 Effective Lifecycle Policy 归 08；各执行边界保存自己的 enforcement fact；Telemetry 不能替代 Durable Audit。

## Rejected Alternatives

1. **从第一天自建完整 Legal-native Host + Native Runtime**：没有通过 Generic Host + Backend 的必要性测试。
2. **Generic Host-only 且完全不保存 Domain State**：一次性低状态任务可能成立；跨运行、人工修订、staleness 和正式历史引用仍需要验证 Legal Backend 的价值。
3. **全部法律对象一律 Canonical**：对象膨胀，缺少必要性证据。
4. **Event Sourcing 作为默认法律状态基础**：当前版本、依赖、Receipt 和审计可先用 PostgreSQL 实现。
5. **Always-on GraphRAG**：没有 query-class 级质量 / 成本证据。
6. **Persistent Multi-Agent Team**：没有相对 Single Controller + parallel steps / tools 的可测收益。
7. **逻辑模块直接拆成微服务**：没有 workload、failure、scaling、security、availability、lifecycle 或 operational ownership 证据。

## Benchmark Requirement

必须执行同模型、同原始语料、同外部工具、可比 Prompt / Skills、同 Token / 时间预算的：

- A：Generic Host + Legal Skills；
- B：Generic Host + Zuno Legal Backend；
- C：Zuno Native Runtime + first-class Domain State。

质量指标至少包括 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict / Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion；效率和复杂度指标至少包括 Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Domain State Reuse Rate 和 recovery / safety behavior。禁止只报告 LLM Judge。

## Security Verification Requirement

在任何安全优势进入 Current 前，至少完成 no-egress / offline、network allowlist、secret leakage、cross-tenant、prompt injection + tool、sandbox escape、revoked permission、stale credential、duplicate side effect、SBOM、signed image / artifact 等测试，并保存可复现证据。

## Consequences

正面：降低首版 Host 锁定、图 / 记忆 / 微服务和 Runtime 的运营负担；法律状态、证据和人工决定仍拥有稳定的迁移出口。

负面：需要设计足够窄但真实的 Domain Contract；MCP / API 集成增加边界测试；如果未来 C > B，需要承担 Native Runtime 的工程成本；如果 B 已足够，则应删除 C，而不是为技术展示保留复杂度。

## Reversal Criteria

撤销“Native Runtime measurement-gated”只有在以下条件同时满足时：

1. A/B/C 在至少两类复杂跨文档法律任务和独立数据切片上重复测量；
2. C 相对 B 在质量、效率、恢复或安全上达到预先注册的实际阈值，且不是由更多 Token、更多工具或不同模型造成；
3. 收益能够归因于 first-class Domain State、Evidence requirement、staleness / dependency、durable execution 或 HITL recovery，而不是普通 Backend Workflow 也能实现的逻辑；
4. C 的安全、恢复、运维和替换成本可接受。

若 C 与 B 近似，删除或外置 Native Runtime 目标；若 B 与 A 近似，继续简化不产生测量收益的 Legal Backend 复杂度。

## Current / Target / Hypothesis Boundary

- **Current**：仓库已有通用 Agent、Knowledge、有限 Domain mutation / citation provenance、Runtime / Tool / Observability 等工程基础；具体证据以 `docs/evidence/` 为准，Production Readiness 仍为 `NOT_ESTABLISHED`。
- **Target**：本 ADR 的最小 Domain Kernel、Host boundary、Provider boundary 和 Benchmark / Security Gate，以及 ADR-0013 / ADR-0014 对其后的责任细化。
- **Hypothesis**：Legal Backend 的质量 / 效率收益、Native Runtime 的额外收益、Graph / Memory / Multi-Agent 收益、安全可验证性优势。
- **Future**：只有新的身份 / 生命周期证据或 Reversal Criteria 通过后，才扩大 Canonical Kernel、Native Runtime 或独立服务范围。
