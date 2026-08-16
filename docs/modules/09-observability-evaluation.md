# 09 Observability & Evaluation（可观测性与评测）

<!-- status: design-baseline-v1; implementation: not-authorized; quality: not-established -->

## Part A — Human Narrative

### 为什么“看得到 Trace”还不等于系统可信

一个复杂 Agent 任务可以产生非常漂亮的 Trace，但如果系统无法回答“这条结论为什么被正式准入”“谁批准了外部动作”“现实世界是否真的执行成功”，Trace 再完整也不能成为业务真相。

可观测性与评测负责两个不同但相关的问题：第一，**系统这次到底怎样运行**；第二，**这些复杂机制到底值不值得保留**。前者靠统一遥测和关联，后者靠可复现实验、评测数据集和对照组。

### 一次运行应该怎样被观察

所有责任域通过统一、可脱敏的 telemetry contract（遥测契约）输出 run、plan、step、model、retrieval、capability、tool、security、admission 和 publication 等关联信息。OpenTelemetry 可以作为与具体供应商无关的基础契约，LangSmith 可以作为 Agent / LLM Trace 与 Eval 的一种 Provider；系统级 CPU、内存、队列、数据库等指标仍进入常规平台监控。

Provider 可以替换，但 correlation、redaction、身份引用和采样语义不能散落在各模块自己定义。否则换一个 Trace 后端就会失去跨模块对账能力。

### Current 到底已经有什么

当前仓库已经存在 `ObservabilityTracePort`、Noop / InMemory / LangSmith adapters、OTel / LangSmith-compatible span schema、redacted export、eval dataset schema、release baseline contract 和 audit span bridge 等基础。这能证明“统一观测 Contract 和 Provider adapter 基础存在”，但不能证明 AgentRunGraph、StepExecutionGraph、Retrieval、Tool Gateway 和 Final Gate 已经完成全链路生产接线。

因此当前更准确的状态是 **contract foundation available**，不是“完整 Observability Platform 已完成”。同样，固定 benchmark 当前仍受实际数据、runtime / credentials 等外部条件阻塞，质量优势不能因为评测框架存在就被宣称成立。

### Trace 和 durable audit 为什么必须分开

Telemetry 的目标是诊断、关联、性能分析和评测。它可以采样、降级、异步发送，甚至在 Provider 故障时暂时丢失一部分非关键数据。

Durable Audit（耐久审计）回答的是另一类问题：高风险动作前是否已经保存了必须的授权、审批和审计事实，事后能否重建关键业务因果。这类事实不能因为 LangSmith / OTel sink 挂了就被视为“以后补 Trace 即可”。

所以正常 telemetry 可以 fail-open / degrade，而被安全策略声明为 mandatory 的审计持久化必须按策略 fail-closed。09 可以关联 `AuditPersistenceReceipt`，但不拥有“强制审计已成功”的事实。

### 评测真正要回答什么

评测不是只问“LLM Judge 给了几分”。Zuno 需要知道证据是否充分、引用是否正确、有没有无依据主张、冲突 / 争议抽取是否准确、法条适用是否正确、人工 Reviewer 是否接受、任务是否完成，以及质量提升换来了多少时延、Token、模型调用、检索轮次和工具调用。

同样重要的是消融和对照：GraphRAG 是否只对某类问题有收益，长期记忆是否真的改善结果，专业多智能体是否优于单控制器加并行步骤，原生运行时是否比“通用宿主 + 法律后端”有稳定增益。没有测量收益的复杂度应当删除、外置或降级为可选 Provider。

### 发布门为什么不能只看平均分

法律场景里，一个平均分提高并不能自动说明系统可以发布。评测需要保留 failure taxonomy（失败分类）：例如证据不足、引用错误、法条适用错误、越权检索、重复副作用、stale 结果未失效、人工拒绝等。

Release Gate（发布评测门）应基于明确数据集版本、样本数、指标、阈值、commit SHA、模型 / Provider 配置和 blocked reason。缺少关键数据时应保持 blocked，而不是用 synthetic demo 或空样本填出“质量通过”。

### 如何观察一次跨模块恢复

如果 Domain commit 成功但 Runtime checkpoint 失败，Trace 可以帮助工程师看到事件顺序，但真正恢复依赖 AdmissionReceipt；如果 Tool POST 超时，Trace 可以看到请求发出，但现实结果需要 Effect / Reconciliation receipt；如果权限中途撤销，Trace 可以记录 Security Epoch 变化，但授权真相仍由 08 的 Decision 决定。

因此 Observability 的价值是把这些权威事实串起来，帮助人快速理解“发生了什么”，而不是自己成为所有事实的 Owner。

### Provider 怎么选才不会锁死架构

推荐边界是：OpenTelemetry / OTLP 作为 provider-neutral canonical telemetry contract；LangSmith 作为 Agent / LLM Trace 与 Eval 的默认 / 优先 Provider；系统指标保持 Grafana-compatible；如果部署主权、成本或安全要求需要，也可以评估 Langfuse 等 OSS / on-prem Provider。

这些都是物理 Provider 选择，不改变上层 correlation、redaction、evidence 和 evaluation semantics。法院侧部署不能因为使用某个 SaaS Trace Provider 才能正常运行核心业务。

### 当前、目标与缺口

当前仓库保留正式 Eval 执行路径和观测 Contract / Adapter 基础，但固定 benchmark 处于 `MEASUREMENT_BLOCKED`，不能宣称质量优势或生产就绪。Target 是全链路 provider-neutral telemetry、可复现法律评测、release evidence 和复杂度淘汰机制；Gap 包括正式数据集、真实样本、生产 trace wiring、A/B/C benchmark、SLO / DR 观测和长期质量回归。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

Telemetry != Durable Audit；Observability != Business Truth；Provider 可替换但 correlation / redaction / identity contract 稳定；Eval 缺关键输入时保持 blocked；复杂度必须接受对照测量，架构存在本身不是保留理由。

### B2 Responsibility / Ownership

**Owns**：Telemetry contract / projection、Trace、Metric、Evaluation Dataset、Evaluation Result、measurement experiment、release evaluation evidence、quality / cost trend、provider-neutral observability conventions。

**Does not own**：Canonical Domain fact、Authorization / Approval truth、Tool Effect truth、mandatory audit durability、production readiness declaration without evidence、各业务模块的成功状态。

### B3 Upstream / Downstream

上游接收所有责任域的脱敏 telemetry / fact refs，包括 run / step、model、retrieval、capability、tool、security、domain admission、publication / delivery。下游向工程、Release Gate、architecture measurement 和运行监控提供 trace / metric / eval / experiment evidence。

### B4 Authoritative Facts / Core Objects

核心对象族包括 Trace / Span / Correlation refs、Metric series / event、Eval Dataset / DatasetVersion、Eval Run / Evaluation Result、Experiment / Baseline、Release Evaluation Evidence、blocked reason、sampling / redaction configuration。`AuditPersistenceReceipt` 只作为外部权威引用。

### B5 Cross-boundary Contracts

统一 telemetry envelope 至少需要 trace / correlation identity、module / operation、run / plan / step / action refs、domain / knowledge / security refs、provider refs、timing、status / error class、sampling / redaction metadata。敏感正文按 policy opt-in，Secret never export。

### B6 Normal Flow

module emits typed telemetry → redact / normalize → export through ObservabilityTracePort / OTLP-compatible adapter → provider stores / visualizes → eval pipeline binds dataset + commit + provider/config → compute deterministic / model / human metrics → compare baseline / experiment → produce release / measurement evidence or blocked result。

### B7 State / Lifecycle

Trace / span 属于诊断投影，可 sampled / partial；Eval Dataset 需要版本化；Eval Run 需要 queued / running / completed / failed / blocked 等语义；Release Evidence 绑定具体 commit / configuration。具体 enum 后续冻结，但 blocked 不得和 pass 合并。

### B8 Failure Taxonomy

主要失败包括 telemetry sink unavailable、export retry exhausted、redaction failure、correlation break、trace partial / sampled、eval dataset missing、zero sample、credential / provider unavailable、judge unavailable、metric computation failure、baseline incomparable、release threshold not met。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

普通 telemetry export 可以有限重试和降级，不能反向阻塞低风险业务；mandatory audit 失败不由 09 自行降级。Eval Run 通过 stable run identity 避免重复计数；同 dataset + config + commit 的可重复实验应能区分 retry 和新的 experiment。Observability 不拥有 Runtime Replan / Tool Reconcile。

### B10 Security / Approval / Audit

默认 redaction；Secret never export；受保护 prompt / response / evidence 只有在 policy 明确允许时才进入 trace payload。Security 决定 mandatory audit requirement，09 只关联其 receipt。法院生产部署不得硬依赖外部 SaaS telemetry 才能保持业务正确性。

### B11 Persistence / Transaction Boundaries

Telemetry backend、metric store、eval result store 可物理替换，不参与 Domain / Effect 原子事务。关键评测证据要能绑定 immutable dataset / commit / config 和样本数。普通 Trace 丢失允许降级；Release Evidence 和正式 Eval Result 的保存要求由治理策略决定。

### B12 Observability / Evaluation

评测族至少覆盖 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、conflict / dispute quality、fact–article mapping、applicability accuracy、Reviewer Acceptance、Task Completion，以及 latency / token / cost / model calls / retrieval rounds / tool calls。

持续保留四类关键测量门：Native Runtime vs Generic Host + Legal Backend；Long-term Memory ablation；Specialist / Multi-Agent vs parallel steps / subgraphs；GraphRAG query-class evaluation。

### B13 Current / Target / Gap / Evidence

Current 见 [`current-eval-baseline.md`](../evidence/current-eval-baseline.md) 和 `src/backend/zuno/platform/observability/README.md`：Contract / Adapter foundation available，正式 benchmark 为 `MEASUREMENT_BLOCKED`。Target 是 provider-neutral telemetry + full-chain tracing + reproducible legal eval / release gate。Gap 包括真实数据集、凭证、全链路 wiring、production SLO / DR、公开可复现实验和长期回归基线。

### B14 Code / Database / Migration Constraints

不因为使用 LangSmith、Grafana、Langfuse 或其他 Provider 就把它们变成不可替换架构依赖。先稳定 telemetry / eval contract、correlation、redaction、dataset / result identity，再决定物理平台。不得把业务代码写成“Trace 成功才算业务成功”，也不得用 telemetry 表替代 Domain / Security / Effect receipt。
