# ADR 0007：Reuse-first 与可替换能力 Provider 边界

status: accepted-target
decision_date: 2026-08-12
scope: Zuno 全局架构、Canonical Taxonomy、Build-vs-Buy 评审和后续 Provider 适配
taxonomy_note: 旧 11 模块仅作为 History；目录和服务边界以 ADR 0011 为准。

## Context

RB-ARCH-001 的 100 问 Baseline 暴露出一个根因：Zuno 的 Target Architecture 已经定义了大量 Agent、RAG、Memory、Tool、Security 和 Infrastructure 语义，但项目事实和 Current Evidence 尚不足以证明这些能力都已由 Zuno 自研、部署或生产验证。

如果继续用“通用开源方案不够企业级”解释自研，会把品牌印象误当成架构证据；如果直接 Fork 一个完整 Agent/RAG 产品，又可能继承上游 Domain Model、Runtime、Persistence、Security、Failure 和升级路径，形成难以退出的长期 Private Fork。

## Decision

Zuno 正式采用：

> **Reuse First, Build Requires Evidence**

能力采用顺序为：

```text
Complete Product
→ Fork
→ Reuse Subsystem
→ Framework
→ Component
→ Protocol / SDK
→ Build Delta
```

每个候选必须先经过五道 Gate：

```text
G1 Capability Fit
G2 Contract Fit
G3 Modification Surface
G4 Operational / License Fit
G5 Evidence
```

Gate 结果只能是 `PASS`、`FAIL` 或 `UNKNOWN`。`UNKNOWN` 不得被叙事改写为通过，也不得自动触发 `BUILD` 或最终 `ADOPT`。

Zuno 的正式宏观架构为：

```text
Zuno Domain / Control Plane
  Matter / LegalTask / Review
  DocumentVersion / Claim / Evidence / Provenance
  Finding / Proposal / HumanDecision / WorkProduct
  Plan / PlanVersion / RunOutcome
  Security Decision / Approval / Tool Effect / Audit
  Recovery Contract / Eval Contract / Release Gate
          │
          │ Canonical Contracts
          ▼
Replaceable Capability Providers
  DocumentPipelineBackend
  RetrievalBackend / GraphRetrievalBackend
  MemoryBackend
  AgentRuntime
  ConnectorBackend
  ModelProvider / Parser / Reranker / EmbeddingProvider
```

Provider 可以负责存储、索引、解析、检索、图遍历、上下文组织、图执行或外部连接，但不得直接提交 Zuno 的 Canonical Business Fact。Provider 的输出必须先被规范化为 `Proposal`、`Observation`、`Candidate`、`Snapshot`、`Reference` 或 `Receipt`，再由对应 Zuno Canonical Owner 做版本、权限、质量、状态和审计确认。

## 为什么不把完整产品 Fork 作为默认策略

完整产品 Fork 不是被禁止，而是必须证明修改面可控。若为了满足 Zuno Contract 需要穿透以下五个核心面：

```text
S1 Domain Model
S2 Runtime / State
S3 Persistence
S4 Security
S5 Failure / Effect
```

并且还要长期维护上游升级、部署和回滚，则这通常已经不是轻量二开，而是长期 Private Fork。优先寻找官方 Extension Point、API、SDK、MCP、Provider 或 Adapter 边界；只有这些边界无法满足且 G5 证据证明自建必要时，才进入 Build Delta。

## Canonical Contract 与 Owner

- 02 仍拥有 `SourceObject`、`DocumentVersion`、`ParseSnapshot`、`SourceSpan`、Reviewability 和权限绑定；`DocumentPipelineBackend` 只提供解析、OCR、布局、表格和通用切分候选。
- 03 仍拥有 `EvidenceRequirement`、`RetrievalRound`、`Evidence`、`Citation` 和 `EvidenceEvaluation`；`RetrievalBackend` 与 `GraphRetrievalBackend` 只提供候选与观察。
- 05 仍拥有 `MemoryCandidate`、`MemoryWriteDecision`、`MemoryVersion`、Scope、Authority、Temporal Validity、Conflict、Provenance 和 `ContextPack`；`MemoryBackend` 只提供存储、索引、层级上下文和基础召回。
- 06 仍拥有 `TaskContract`、`PlanVersion`、`AgentRun`、`RunOutcome`、Proposal 和业务完成；`AgentRuntime` 只提供图执行、Checkpoint、Interrupt 和 Resume 机制。
- 10 仍拥有 Zuno `Eval Contract`、Benchmark、Release Gate 和质量证据；任何候选产品自带 Benchmark 都不能替代 Zuno 质量证明。

## Security、License、Migration 与 Exit

Provider 适配必须经过 09 Security 的 Tenant、Workspace、Data Classification、Secret、Network、Supply Chain、Permission 和 Revocation 检查；Provider 的自动 Memory、Connector Permission、Tool Effect 或外部授权不能绕过 Zuno Security Gate。

G4 必须记录许可证、版本、部署模型、数据出口、升级责任、依赖供应链、隔离和退出路径。候选即使功能匹配，也不能因为许可证或运营边界未核验而进入最终 Adopt。

任何未来 Adapter / Provider 计划都必须先定义：输入输出 Contract、版本兼容、失败与重试、幂等/对账、数据回迁或退出、Shadow/Benchmark 方式和删除路径。本 ADR 不授权实现这些计划。

## Alternatives

1. **全部 Native Build**：被拒绝为默认策略。它需要对每项自研承担更高的 G1–G5 证明责任，且容易重复成熟能力。
2. **Fork 一个完整平台**：保留为候选，但不作为默认。只有 Modification Surface 没有穿透 S1–S5 且升级/许可证可控时才可考虑。
3. **直接把候选产品当作 Zuno 事实源**：拒绝。Provider 输出不能替代 Zuno Canonical Owner、Evidence、Security、Effect、Recovery 或 Eval Contract。
4. **能力级 Adapter / Provider**：选为默认评估路径，因为它保留 Zuno 领域事实和治理语义，同时允许复用成熟子系统。

## Verification

本 ADR 的文档一致性由架构文档集、语义对齐、内部链接、红蓝会话和 Repository Verifier 检查；具体候选的 G1–G5 必须由 `project-red-blue/09-open-source-review.md` 记录官方资料、源码、测试、License、Spike 和 Benchmark 证据后，才可升级决策状态。

本 ADR 是 `accepted-target`，不是 Current、实现证明或 Production Readiness 证明。
