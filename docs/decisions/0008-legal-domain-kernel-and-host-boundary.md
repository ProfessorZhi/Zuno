# ADR-0008：法律 Domain Kernel 与 Host 边界

- 状态：`accepted-target`
- 日期：2026-08-12
- 依据：`RED-KERNEL-V3`，基线 `0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f`
- 关联：历史架构审查过程保留在 Git history；本 ADR 是当前长期边界。
- 适用：Legal Domain State、Host Integration、Capability Provider、Agent Runtime、Knowledge、Memory、Security、Eval、Infrastructure

## Context

候选产品命题是“法律案件智能 + Agent 平台”。复杂度引入者必须证明：法律业务状态、证据依赖、人工决定和审计边界不能由 WorkBuddy / Dify / Pi / LangGraph / RAGFlow 的组合加普通 MCP/API 承载。

RED-KERNEL-V3 对最新 `main`、Target 文档、代码目录、官方竞品资料和法律 AI primary sources 做了竞争性反证。结论不是 Zuno 已经优于任何 Host，而是：

1. 完整独立 Host 和自研 Native Runtime 没有通过必要性证明；
2. 一个 Host-agnostic Legal Backend 仍可能对跨文档、跨运行、人工修订、证据依赖失效和审计有价值；
3. 当前仓库没有法律 Domain Kernel 的完整 Current 证据，以下全部是 Target 或 Hypothesis；
4. GraphRAG、Persistent Multi-Agent、Long-term Memory、Event Sourcing、十一微服务和自研 Tool Runtime 都没有默认保留理由。

## Decision

### 1. 最小 Legal Domain Kernel

Legal Domain Model 是对法律业务世界的正式、可审计表示，不是 LLM Model、Prompt、Knowledge Base、Memory、Skill、Tool、GraphRAG 或 LangGraph State。

第一阶段只冻结最小 Canonical 候选：

| 类别 | Canonical 候选 | 边界 |
|---|---|---|
| 根与来源 | `Matter`、`DocumentVersion` | `Case` 默认是 Profile/别名；只有独立身份、权限或生命周期证据才能成为新根 |
| 主张与证据 | `Claim`、`Evidence` | 有来源、版本、引用位置、权限和可追溯关系 |
| 结论与人工权威 | `Finding`、`HumanDecision`、`WorkProduct` | 结论不能由模型或 Provider 直接提交 |

`Party`、`Fact`、`Event`、`Conflict`、`Dispute`、`LegalIssue`、`StatuteVersion`、`LegalElement`、`ApplicableLaw`、`SimilarCase` 保留为领域语义候选，但默认作为 typed Proposal、Projection、Derived View 或 Capability Provider 输出，不自动增加 Canonical 表和状态机。

Canonical 对象只有在能够明确 Identity、Version、Provenance、State、Ownership、Mutation Authority、Staleness、Dependency、Review、Audit 时才可进入正式状态。

### 2. Domain State 与 Memory / Runtime 分离

- Domain State：业务世界的当前可审计事实、主张、证据、结论和人工决定。
- Memory：可复用的上下文/经验；可压缩、过期、删除或按策略召回，不是权威事实源。
- Runtime State：Plan、Step、checkpoint、interrupt、reducer 和恢复位置。
- Tool：能力执行适配器，不拥有业务事实。

LangGraph、Pi、WorkBuddy 或其他 Runtime 不能把 checkpoint 当作法律事实。Runtime 可以消费/产生版本化 Domain Contract，但 Domain Store 仍由 Canonical Owner 管理。

### 3. New Evidence 与版本化 PostgreSQL

默认使用 PostgreSQL 保存当前业务事实、不可变版本、依赖引用、审核记录和必要 Outbox；不默认引入 Event Sourcing。

新 EvidenceVersion 提交后：

1. 根据依赖引用找到受影响 Claim/derived object；
2. 将受影响 Fact/Finding 标为 `STALE` 或 `REVIEW_REQUIRED`；
3. 对 Conflict、Dispute、ApplicableLaw 等派生结果按策略执行 bounded re-evaluation；
4. 必要时创建新的 Agent Run/Proposal；
5. 由 Canonical Owner 与所需 Human Review 提交新版本。

同一事务不盲目全量重算；恢复时以 Domain Store、Runtime checkpoint、Receipt、幂等记录和当前版本对账。

### 4. 默认 Host 边界

默认最小形态是：

```text
WorkBuddy / Dify / Pi / 其他 Host
  + Legal Skills / Knowledge Scope
  + MCP / API Legal Capability Provider
  + 最小 Legal Domain Backend（仅在跨运行状态有必要时）
```

Host 可以负责交互、任务入口、模型编排和一般工具；Legal Backend 负责最小 Canonical Domain State、Evidence/Review Contract、Provider Proposal 接收、版本、权限和审计。这个边界不宣称 WorkBuddy 缺少能力；它只把需要验证的法律业务契约从 Host 中隔离出来。

### 5. Runtime Provider 而非 Runtime 主权

Plain Python、Async Workflow、State Machine、LangGraph、Pi 或 Host 自带 Runtime 都是可替换候选。LangGraph 只有在 durable execution、checkpoint、interrupt/resume、parallel/reducer、replan 或 HITL 需求被 Benchmark 证明时才采用；其 graph control state 与 Legal Domain State 必须分离。

Native Domain-aware Runtime 是 `DEFERRED / HYPOTHESIS`，不是当前默认必选组件。它若最终保留，必须以版本化 Domain Contract 作为输入/输出，而不是把业务状态搬进某个框架的 checkpoint。

### 6. Capability Provider

法律能力采用稳定 Contract：

`EVENT_EXTRACTION`、`EVENT_ALIGNMENT`、`CONFLICT_DETECTION`、`FACT_ARTICLE_MAPPING`、`SIMILAR_CASE_RETRIEVAL`、`LEGAL_APPLICABILITY`、`EVIDENCE_REASONING`。

Provider 可由本地算法、LLM、fine-tuned model、OSS、API 或 MCP 实现，输出只能是 `Proposal`、`Candidate`、`Observation`、`Reference` 或 `Receipt`。Canonical Owner 负责 Schema、Provenance、Evidence、Permission、Version、State Transition 和 Human Review。

### 7. Conditional 能力

- Graph：Conditional Provider，不是默认路径。
- Multi-Agent：先 L0 Single Agent、L1 Role Pipeline、L2 Ephemeral Worker、L3 Specialized Agent；L4 Persistent Team 和 L5 Autonomous Society 删除为默认目标。
- Memory：Working/Session 优先；Long-term 只有在消融证明收益后启用。
- Tool Runtime：优先 MCP/API/CLI/现有 Sandbox 加薄 Adapter；Zuno 只冻结安全、幂等、Receipt、审计和对账 Contract。
- Deployment：模块化单体 + 独立 worker 优先；用户数不是微服务证据。

### 8. 安全可验证性

不采用“闭源不安全”或“开源天然安全”的判断。Zuno 的安全差异仅作为 Target/Hypothesis：能否提供 Source-level Audit、Build Reproducibility、SBOM、Signed Artifact、Network Egress Audit、Secret/Model/Tool/Domain/Human Decision Trace、Sandbox Boundary Test 和部署主权证据。WorkBuddy 的安全能力保持公开资料所能支持的事实与 UNKNOWN，不做负面推断。

## Rejected Alternatives

1. **从第一天自建完整 Legal-native Host + Native Runtime**：没有通过 WorkBuddy Host + Backend 的 Kill Test。
2. **WorkBuddy-only 且不保存 Domain State**：对一次性低状态任务可成立；对跨运行、人工修订、stale 传播和审计则保留为要验证的失败边界，而不是全局默认。
3. **全部法律对象一律 Canonical**：对象膨胀，缺少必要性证据。
4. **Event Sourcing 作为法律状态基础**：当前版本、依赖和审计可先用 PostgreSQL 实现。
5. **Always-on GraphRAG**：没有 query-class 级质量/成本证据。
6. **Persistent Multi-Agent Team**：没有相对 Single Agent/parallel tools 的可测收益。
7. **十一逻辑模块直接拆成微服务**：没有 workload、failure、scaling、security 或 team ownership 证据。

## Benchmark Requirement

必须执行同模型、同原始语料、同外部工具、可比 Prompt/Skills、同 Token/时间预算的：

- A：WorkBuddy Generic Legal Agent；
- B：WorkBuddy + Zuno Legal Capabilities；
- C：Zuno Native Runtime + first-class Domain State。

质量指标至少包括 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict/Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion；效率指标至少包括 Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Domain State Reuse Rate。禁止只报告 LLM Judge。

## Security Verification Requirement

在任何安全优势进入 Current 前，至少完成 no-egress/offline、network allowlist、secret leakage、cross-tenant、prompt injection + tool、sandbox escape、revoked permission、stale credential、duplicate side effect、SBOM、signed image/artifact 等测试，并保存可复现证据。

## Consequences

正面：降低首版概念数、Host 锁定、图/记忆/微服务和 Runtime 的运营负担；法律状态、证据和人工决定仍有稳定的迁移出口。

负面：需要设计一个足够窄但真实的 Domain Contract；MCP/API 集成增加边界测试；若未来 C>B，需承受 Runtime 迁移成本；若 B 已足够，则应删除 C，而不是为维护简历亮点保留它。

## Reversal Criteria

撤销“Native Runtime deferred”只有在以下条件同时满足时：

1. A/B/C 在至少两类复杂跨文档法律任务和独立数据切片上重复测量；
2. C 相对 B 在质量或效率上达到预先注册的实际阈值，且不是由更多 Token、更多工具或不同模型造成；
3. 收益能归因于 first-class Domain State、Evidence Requirement、staleness/dependency 或 HITL 对账，而不是普通 Backend Workflow 也能实现的逻辑；
4. C 的安全、恢复、运维和替换成本可被接受。

若 C 与 B 近似，删除 Native Runtime 目标；若 B 与 A 近似，删除不产生测量收益的 Domain Backend 复杂度。

## Current / Target / Hypothesis Boundary

- Current：仓库已有通用 Agent、Knowledge、Document/Evidence 和目标模块文档；生产就绪状态仍为 `NOT_ESTABLISHED`。
- Target：本 ADR 的最小 Domain Contract、Host 边界、Provider 边界和 Benchmark/Security Gate。
- Hypothesis：Legal Backend 的质量/效率收益、Native Runtime 的额外收益、Graph/Memory/Multi-Agent 的收益、安全可验证性优势。
- Future：在 Reversal Criteria 通过后再增加 Native Runtime 或更多 Canonical Legal Objects。
