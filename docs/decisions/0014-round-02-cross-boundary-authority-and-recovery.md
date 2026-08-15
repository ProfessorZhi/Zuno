# ADR-0014：Round 02 Cross-boundary Authority and Recovery

- 状态：`accepted-target`
- 日期：2026-08-15
- 决策来源：Round 02 Main Judgment，记录见 [`docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md`](../history/red-blue/manual-round-02-overall-architecture-freeze-review.md)
- 适用：调用准入、答案发布、历史引用、生命周期、正式 Admission、失效交付和关键恢复
- 不包含：数据库表、Migration、ORM class、物理服务拆分或实现任务

## Context

Round 02 暴露了几类跨边界事实容易混淆的问题：请求是否允许执行不等于答案是否允许发布；Knowledge 找到引用不等于正式 WorkProduct 拥有历史引用权威；Memory 删除不等于所有副本物理消失；Domain Commit 不等于 Runtime Checkpoint 已更新；WorkProduct 失效不等于外部 Consumer 已收到通知；Telemetry Trace 也不等于关键审计事实。

这些语义必须在总体架构层拥有长期稳定的 Owner 和恢复锚点，否则不同模块或 Provider 会各自发明互相冲突的状态机。

## Decision

### Invocation and Publication

`InvocationDecision` 由 Application & Integration 负责组合。它消费 Security Authorization、Knowledge Readiness、Capability Eligibility、Model/Provider Eligibility 和适用时的 Runtime Control Decision，但不重算这些事实。

`AnswerPublicationDecision` 的最终 Owner 取决于发布边界：Zuno 自己发布时由 Application & Integration 拥有；外部 Generic Host 发布时，Host 拥有最终 UI/发布决定。Zuno 提供 typed result、eligibility evidence、citation 和 policy references，不声称控制外部 Host 的最终显示行为。

### Historical Citation Binding

Knowledge & Evidence 拥有 CitationLineage，回答检索系统当时如何找到和排序候选。Legal Domain & Work Product 拥有正式 WorkProductVersion 的 Historical Citation Binding，回答当时究竟引用了哪份不可变 DocumentVersion 的哪一处。

正式 Admission 必须能够绑定 DocumentVersion、immutable source reference/hash、stable source location/span、source representation identity/hash、必要 evidence/excerpt hash 和可选 CitationLineage reference。Chunk ID、Vector ID、Graph Node ID 或当前 Index identity 不能单独成为长期 Citation Authority。

### Effective Lifecycle Policy

Security & Governance 是 Retention、Deletion、Legal Hold 和 Compliance Exception 的唯一 Policy Decision Owner；各 Store 是 Enforcement Owner。Retention 不等于 Recall Eligibility。删除后的 Memory 或其他上下文未来不得继续召回；尚存副本是否依法保留由有效生命周期政策决定。

### Admission Causation and Recovery

当 Step 的完成条件要求 Formal Domain Admission 时，没有 durable `AdmissionReceipt`，Runtime 不能宣布 Step 完成。Receipt 至少关联 run identity、plan version、step run identity、proposal/admission identity、idempotency identity、expected prior domain version 和 resulting domain version。

Domain mutation 与证明该 mutation 的 AdmissionReceipt 必须处于同一个 Domain transactional durability boundary。PostgreSQL 与 LangGraph Checkpointer 的 2PC 不是默认方案。

- Domain Commit 和 Receipt 成功、Checkpoint 失败：通过匹配 Receipt 修复 Runtime Control State。
- Checkpoint 显示 completed、Receipt 缺失：不能推断 Formal Admission 成功。
- Domain 存在更高版本、但 causation 不匹配：不能把其他 Run/Step 的版本冒充当前结果。

### Invalidation, Delivery and Acknowledgement

对已发布 WorkProduct 必须区分三类事实：

1. **Domain Invalidation Truth**：例如 WorkProduct V3 = STALE，由 Legal Domain & Work Product 拥有；
2. **Invalidation Delivery Fact**：例如 PENDING、SENT、FAILED、RETRYING，由 Application & Integration 拥有；
3. **Consumer Acknowledgement Observation**：例如 ACKNOWLEDGED、NO_ACK、UNKNOWN，由 Application & Integration 观察和保存。

Consumer 是否在线不影响 Domain Invalidation Truth；Consumer Acknowledgement Observation 也不能声称拥有远端系统内部真实认知状态。Integration Target 支持 Push Invalidation 和 Pull Current-validity Query。

### Critical Reconstruction

高风险外部动作必须通过 durable facts 回答：做了什么、为什么允许、谁批准、现实世界最终发生了什么。关键事实链由 PreparedAction/ToolAttempt、Security Authorization Decision、Approval Decision（如需）、Audit Persistence Receipt、EffectReceipt、必要时 ReconciliationReceipt 和适用时 AdmissionReceipt 组成，并通过 action identity、action hash、run/step causation 和 idempotency identity 关联。

LangSmith、OpenTelemetry、普通日志和可视化 Trace 只是 Projection、Diagnostic View、Correlation 或 Evaluation Input。Telemetry 丢失不能破坏 Critical Reconstruction；Durable Audit 丢失时，也不能用完整 Trace 假装同等级替代品。Secret Material 不得因为重建需要而写入 Prompt、Trace、普通 Audit Payload 或普通数据库列。

## Consequences

正面：Simple QA、复杂分析、外部 Effect 和发布失效都拥有清晰的决策边界；恢复时可以依赖 durable facts，而不是猜测 Checkpoint 或 Telemetry 的含义。

负面：跨边界操作需要保存更多 Receipt、引用和策略版本；Provider 不能只返回一个字符串或 HTTP 状态就被视为完成。具体字段和实现仍需模块设计与证据验证，不由本 ADR 自动授权。

## Current / Target / Gap

- Current：当前仓库可能已包含部分 Runtime、Receipt、Audit、Citation 或 Delivery 表面，但不能证明完整不变量已经实现。
- Target：本 ADR 的 Authority、Citation、Lifecycle、Admission、Invalidation 和 Reconstruction 语义。
- Gap：AdmissionReceipt 实现、跨 Store 恢复、外部 Consumer 交付、生命周期执行和故障注入证据尚未完成。
