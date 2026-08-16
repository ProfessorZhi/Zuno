# 09 Observability & Evaluation（可观测性与评测）

<!-- status: design-skeleton; implementation: not-authorized; quality: not-established -->

## Part A — Human Narrative

### 为什么“看得到 Trace”还不等于系统可信

一个复杂 Agent 任务可以产生非常漂亮的 Trace，但如果系统无法回答“这条结论为什么被正式准入”“谁批准了外部动作”“现实世界是否真的执行成功”，Trace 再完整也不能成为业务真相。

可观测性与评测模块负责帮助团队理解系统怎样运行、哪里变差、复杂度是否值得保留；它不拥有领域事实、安全决定或外部效果。

### 一次运行应该怎样被观察

所有责任域通过统一、可脱敏的遥测契约输出 run / step / model / retrieval / tool / admission 等关联信息。OpenTelemetry 可以作为与具体供应商无关的基础遥测契约，LangSmith 可以作为 Agent / LLM Trace 与 Eval 的一种 Provider；系统级指标则可以进入常规监控栈。

Provider 可以替换，但 trace / metric / eval identity、correlation 和 redaction 语义不能散落在各模块自己定义。

### 评测真正要回答什么

评测不是只问“LLM Judge 给了几分”。Zuno 需要知道：证据是否充分、引用是否正确、有没有无依据主张、冲突/争议抽取是否准确、法条适用是否正确、人工 Reviewer 是否接受、任务是否完成，以及质量提升换来了多少时延、Token、模型调用和工具调用。

同样重要的是消融：GraphRAG 是否只对某类问题有收益，长期记忆是否真的改善结果，多智能体是否优于单控制器加并行步骤，原生运行时是否比“通用宿主 + 法律后端”有稳定增益。没有测量收益的复杂度应当删除或外置。

### 为什么耐久审计不能放在这里

Observability 可以接收 Audit Event 或引用 AuditPersistenceReceipt，但“高风险动作前必须先落盘”的要求由 Security 决定，实际持久化边界证明它是否成功。Telemetry 丢失应该降低诊断能力，而不能让已经发生的正式领域提交或外部效果失去事实依据。

### 当前、目标与缺口

当前仓库保留正式 Eval 执行路径，但固定 benchmark 因外部实际数据不可用而处于 `MEASUREMENT_BLOCKED`，不能宣称质量优势或生产就绪。Current Runtime / Wave-1 已有部分观测 Contract 和 Adapter 基础；全链路生产 trace、法律评测数据集、release gate、真实 A/B/C benchmark 仍是缺口。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：Telemetry contract / projection、Trace、Metric、Evaluation Dataset、Evaluation Result、measurement experiment、release evaluation evidence。

**Does not own**：Canonical Domain fact、Authorization / Approval truth、Tool Effect truth、mandatory audit durability、production readiness declaration without evidence。

### B2 Telemetry Boundary

推荐 provider-neutral OTel-compatible envelope / span semantics；LangSmith 可作为 Agent/LLM trace/eval provider。敏感内容默认脱敏，Secret 不进入 telemetry。

### B3 Evaluation Families

至少覆盖：Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、conflict/dispute quality、fact–article mapping、applicability accuracy、Reviewer Acceptance、Task Completion，以及 latency / token / cost / model calls / retrieval rounds / tool calls。

### B4 Measurement Gates

需要持续保留对照的能力：Native Runtime vs Generic Host + Legal Backend；Long-term Memory ablation；Specialist/Multi-Agent vs parallel steps/subgraphs；GraphRAG query-class evaluation。测量结果可以删除复杂度，不以架构既有存在为保留理由。

### B5 Failure / Recovery

Telemetry sink 不可用时普通诊断可降级；MANDATORY audit 不能因为 telemetry 降级而被视为成功。Eval run 必须记录 dataset、sample count、metric、commit SHA、provider/config 和 blocked reason；缺关键输入时状态保持 blocked。

### B6 Current / Target / Gap

Current 见 [`current-eval-baseline.md`](../evidence/current-eval-baseline.md)：`MEASUREMENT_BLOCKED`。Target 是 provider-neutral telemetry + 可复现 legal eval/release gate。Gap：正式数据集、真实样本、外部 credentials、全链路 trace、生产 SLO/DR 观测和公开可复现 benchmark。

### B7 Code / Database / Migration Constraints

不因为使用某个 SaaS Trace Provider 就把它变成架构依赖。指标存储、Trace backend 和 dashboard 都可替换；先稳定 telemetry/eval contract、redaction 和 evidence 语义，再决定物理平台。
