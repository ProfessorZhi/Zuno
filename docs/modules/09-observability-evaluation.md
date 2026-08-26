# 09 Observability & Evaluation（可观测性与评测）

<!-- status: design-baseline-v1; implementation: not-authorized; quality: not-established; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块其实在回答两个不同问题：发生了什么，以及这样做值不值得

系统出故障时，工程师需要沿一次请求找到相关 Run、检索、模型、Capability、Tool、Domain 和 Delivery；架构演进时，团队又需要判断 GraphRAG、Reflection、Native Runtime 或强模型是否真的提高质量。

Observability 负责解释系统发生了什么，Evaluation 负责判断结果好不好、复杂度是否值得保留。两者共享版本、关联和数据治理，但不能因为都“看数据”就混成一个 Dashboard。

### 最简单的“Trace 里有完整链路，所以 Trace 就是真相”为什么危险

Trace 非常适合关联调用，但它可能被采样、Exporter 失败、网络中断或 redaction 删除内容。如果恢复和业务判断依赖 Trace，观测系统故障会反过来破坏业务正确性。

因此保持：

```text
Telemetry != Durable Audit != Business Truth
```

02、06、08 等 Owner 保存自己的耐久事实，09 引用它们解释时间线。漂亮 span 不能替代 AdmissionReceipt、EffectReceipt 或安全审计证明。

### 事故调查为什么应该先问 Owner Fact

用户报告“系统重复提交了两次”，第一步不是统计 Trace 里有几个 HTTP span，而是查询 06 的逻辑动作、Attempt、EffectReceipt 和 Reconciliation，确认现实世界到底发生了几个效果。

随后再用 Runtime Plan、Security decision、Delivery 和 Trace 对齐时间线。Observability 的价值是帮助解释“为什么发生”，不是自己裁决“业务事实是什么”。

### Correlation 为什么重要，但不能成为万能业务 ID

九个责任域各自拥有事实，如果没有稳定 correlation，就很难回答某次模型调用属于哪个 Step、产生哪个 Capability output、最后是否正式进入 Domain。

系统可以传播 request / run / step / action / admission 等 opaque refs 做定位，但 correlation id 不能自动成为幂等 key、授权 token 或业务主键。关联帮助查询，不产生权威。

### OpenTelemetry Baggage 为什么要保持最小化

Baggage 会跨进程广泛传播，如果把 tenant 名称、案件名称、用户 PII、材料正文或授权内容直接塞进去，诊断便利会扩大敏感数据暴露面。

默认只传播最小 opaque identity，在可信边界回查 Owner fact。尤其 `Secret NEVER EXPORT`。必要业务文本只有在策略允许、完成 redaction 且确实有诊断价值时才进入受控 Telemetry。

### Sampling 为什么只能影响观测细节

高吞吐系统不可能永久保存每一个成功 span，Sampling 是合理成本控制。可以提高 error / high-risk task 采样率，降低普通成功请求采样。

但 Sampling 不能决定 Domain、Effect、Authorization 或 Mandatory Audit 是否存在。关闭 tracing 不能让系统失去恢复能力，也不能让安全证明消失。

### Eval Dataset 为什么必须版本化

今天一百个 case，明天修改二十个标签，如果两次分数直接比较，就无法判断变化来自模型还是数据集。Dataset 本身也是实验输入。

DatasetVersion 需要稳定 case identity、材料 refs、任务类别、标签 / expected evidence、annotation provenance 和数据政策。数据集变化产生新版本，保证实验结果可解释。

### 训练暴露为什么必须和测试集分开

Prompt tuning、few-shot、模型训练或人工调参如果已经看过某些 case，这些样本就不能在不说明的情况下继续充当独立 test。

Eval 需要记录 split 和 exposure provenance。真实法院材料受数据政策限制时，也不能偷偷换成合成数据后仍然声称“真实法院质量已验证”；测量范围必须明确。

### LLM Judge 为什么只能处理适合模型判断的问题

引用是否存在、JSON 是否合法、action hash 是否一致、重复 Effect 是否发生，都应该优先使用 deterministic checker。开放式法律论证、适用性和表达质量才更适合 LLM Judge。

Judge 自身也有模型、Prompt 和漂移问题，因此 JudgeVersion 需要进入 Eval config，并用人工金标准校准。Judge 不可靠时结果应标记 blocked / unreliable，而不是为了持续产分数而假装可信。

### PASS、FAIL 和 BLOCKED 为什么必须严格区分

PASS 表示在冻结 Dataset、配置、样本数和阈值下真正达标；FAIL 表示评测有效执行但结果不达标；BLOCKED 表示根本没有资格判断，例如没有样本、凭证缺失、Judge 不可用或 baseline 不可比。

当前正式 benchmark 在证据不足时应明确 `MEASUREMENT_BLOCKED`。Blocked 不是较轻的 Fail，更不能默认为 Pass。

### 为什么 Critical Failure 可以否决漂亮平均分

法律场景里，越权读取、重复高风险 Effect、正式引用无法回溯、stale WorkProduct 被错误发布等问题不能被高平均准确率抵消。

Release Evaluation 因此既看 aggregate metrics，也看 critical failure taxonomy。平均分很好但触发定义中的关键安全/正确性违规，发布资格仍然可以 Fail。

### 为什么要同时评质量、恢复、延迟和成本

Agent 复杂度常常在最终准确率以外付出代价：Retry 放大、P95 延迟、人工介入、token 和 Provider 费用。一个方案提高一点准确率，却让成本和恢复失败面翻倍，未必值得保留。

评测因此需要把 evidence sufficiency、citation correctness、unsupported claim、reviewer acceptance、recovery correctness、duplicate effect、Replan rate、reconcile duration、latency、token 和 cost 放在同一实验解释里。

### 为什么指标必须按 Task Class 分层

简单条文定位、跨文档争议分析、带现实副作用的任务目标不同。把它们混成一个“Agent Success Rate”，会让简单题数量掩盖复杂路径问题。

每个 EvalCase 应绑定 task class、difficulty / risk profile 和实际执行路径。这样才能回答 GraphRAG 是否只对某类 query 有价值，Native Runtime 是否只在长任务恢复上有收益。

### Evaluation 为什么应该主动帮助删除复杂度

团队已经实现的功能很容易获得沉没成本保护：有 GraphRAG 就只展示 GraphRAG 的分数，有 Reflection 就只证明它“能跑”。

09 应主动设计 baseline、ablation 和 kill test：GraphRAG vs Hybrid Retrieval、Memory on/off、Reflection on/off、Generic Host + Legal Backend vs Native Runtime。在尽量相同语料、模型和预算下比较真实边际收益。

### Provider-neutral Observability 为什么重要

Target 采用 OpenTelemetry / OTLP-compatible contract，让 LangSmith 可以作为 Agent / LLM Trace 与 Eval 的 preferred Provider，但核心运行和审计不能依赖单一 SaaS。

更换 OTel backend 或未来其他观测 Provider 时，稳定 correlation、redaction 和 semantic convention 不应改变业务 Owner。Provider 可替换才说明观测层没有绑架运行架构。

### Telemetry Provider outage 为什么不应该阻断普通业务

如果 Trace exporter 故障，09 可以 buffer / retry 或丢弃低优先级 telemetry；02 / 06 / 08 的耐久事实继续成立，普通业务不应因为 Dashboard 暂时不可用就全部停止。

只有安全策略明确要求的 Mandatory Audit 走独立 durable boundary。Tracing 可用性和合规审计可用性必须分开。

### Release Evidence 为什么不等于 Production Readiness

一组 Eval PASS 只能说明它覆盖的 Dataset、配置、commit 和 profile 达到门槛。生产成熟度还需要容量、HA / DR、安全 qualification、恢复演练、外部依赖和运维证据。

09 可以形成 ReleaseEvaluationEvidence，但不能单独宣布整个系统 production ready。测量越严谨，越应该明确它没有覆盖什么。

### 好的 Observability 为什么从问题出发，而不是从“所有地方都打日志”出发

如果没有稳定 correlation 和 Owner fact，日志越多越可能只是噪音。观测设计应先列关键问题：一次结果为什么被拒绝、哪一步扩大了成本、现实 Effect 是否重复、哪个版本导致质量回退、权限撤销后是否仍有访问。

然后为这些问题提供最小可关联事件、指标和 trace attributes。高基数字段、敏感正文和每个 token 的细节只有在确有诊断价值时才记录。Observability 的目标是缩短解释时间，不是最大化数据量。

同样，Dashboard 只是 projection。事故裁决仍然回到 durable owner facts，避免“图上没有 span，所以事情没发生”的错误结论。

### Eval 为什么必须先定义 Decision，再选择 Metric

“我们要测准确率”不是完整评测目标。先要说清这次实验要决定什么：是否启用 GraphRAG、是否升级模型、是否保留 Reflection、是否允许某 Capability 进入高风险任务。不同 Decision 需要不同 case、指标和阈值。

例如判断 GraphRAG 是否保留，需要在关系型 / multi-hop query class 上和 Hybrid baseline 比质量、延迟与成本；判断 Tool Runtime 是否安全，需要 fault injection 和 duplicate-effect 指标，而不是法律问答准确率。

Metric 因 Decision 而存在，可以防止团队只展示最容易变绿的数字。

### Counterfactual / Ablation 为什么是复杂 Agent 架构的核心证据

复杂系统通常多项机制同时开启：更强模型、GraphRAG、Reflection、Memory、Specialist。最终分数提高时，很难知道到底谁贡献了收益。

Ablation 在尽量相同条件下关闭一个机制，观察质量、成本和恢复变化。必要时做 factorial / 分层实验，至少保证关键架构选择有 simpler baseline。没有这种对照，团队只能证明“整套系统能跑”，不能证明每一层复杂度值得存在。

这也是 Kill Test 的来源：如果关闭某机制几乎不影响目标指标，应该认真考虑删除，而不是寻找更多理由保留。

### 线上指标和离线 Eval 为什么互相不能替代

离线 Dataset 可复现、适合版本比较，却可能覆盖不了真实分布和运维故障；线上 telemetry 反映真实流量，但缺少稳定 ground truth，且受用户行为和版本混杂影响。

两者应互补：离线 Eval 做发布前质量和回归门，线上观测检查 drift、latency、cost、recovery 和真实失败分布，再把重要线上失败沉淀为新的 Eval cases。生产反馈进入数据集时还要遵守隐私和标注 provenance。

只看线下分数会错过运行问题，只看线上成功率又无法公平比较模型和架构版本。

### Release Gate 为什么应该能够说“不知道”

工程团队常希望 CI 最终只有绿色或红色，但质量证据有时就是不完整：样本不足、Judge 不可用、数据政策禁止运行某 profile、baseline 版本不兼容。这时 BLOCKED 比假 Pass 或假 Fail 更准确。

Release policy 可以规定某些关键 gate BLOCKED 就不能发布，也可以允许低风险 profile 在明确 exception 下继续，但必须记录是谁接受了未知风险。系统不能为了流水线顺畅把“没有测”解释成“没有问题”。

Measurement honesty 是 Evaluation 的架构职责之一。

### 成本归因为什么必须沿因果链，而不是只看 Provider 月账单

总账单只能告诉团队花了多少钱，无法解释为什么。真正优化需要知道某个 task class、Plan、Step、Capability 或模型 fallback 消耗了多少，以及这些成本是否换来质量收益。

07 提供模型 Usage，03/05/06 提供各自执行事实，09 沿 correlation 做归因和趋势。04 负责单次 Run 的预算控制，但长期“哪个机制值得删”由 09 的跨运行数据回答。

只有成本和质量共享可比较的实验身份，团队才能判断一个额外 Reflection 或 Graph route 是投资还是浪费。

### 当前、目标与缺口

Current 到底有哪些 Trace、Metric、Dataset、Judge、release gate 和真实 benchmark，必须回到证据；没有样本或 Provider 条件时保持 BLOCKED，而不是从 Target 推断质量。

Target 已明确 Telemetry 与业务真相分离、Dataset / Eval 版本化、deterministic checker 优先、复杂度 kill test 和 provider-neutral observability。Gap 包括真实基准数据、Judge 校准、生产 telemetry 成本、隐私 redaction 验证、恢复与 Effect fault injection，以及复杂机制是否真正值得保留。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. Telemetry != Durable Audit != Business Truth。
2. Observability Provider 可替换；correlation / redaction semantics 稳定。
3. Trace 丢失不能让 Domain / Security / Effect facts 消失。
4. Mandatory Audit 不由普通 Trace 替代。
5. Eval 缺关键输入、zero sample 或不可比较时保持 BLOCKED。
6. Release Evidence 绑定 dataset / commit / config / sample count / threshold / failure taxonomy。
7. Secret NEVER EXPORT；敏感正文默认 ref/hash/redact。
8. 复杂机制必须接受 A/B / ablation / kill test。
9. 质量 Evidence 不自动把 Target 写成 Current。
10. 核心法院业务不硬依赖外部 SaaS observability。
11. OpenTelemetry Baggage 默认只携带 opaque correlation ref。
12. Sampling 只改变 Telemetry 细节，不改变 durable proof。

### B2 Responsibility / Ownership

**Owns**：Telemetry contract / projection、Trace / Span / correlation conventions、Metric definition、Sampling / Redaction policy、EvalDataset / DatasetVersion、EvalCase、EvalRun、EvaluationResult、Experiment / Baseline、ReleaseEvaluationEvidence、BlockedReason、quality / cost trend、export delivery status。

**Does not own**：Canonical Domain、Authorization / Approval / Audit durability、Effect truth、Runtime control、Model billing truth、Publication truth、Production Readiness without external evidence。

### B3 Upstream / Downstream

上游接收所有责任域的脱敏 telemetry / fact refs 与 Platform resource metrics。下游面向诊断、SLO/alerting、Release Gate、架构实验、回归、事故复盘和人工 Review。

### B4 Authoritative Facts / Core Objects

TraceId / SpanId / CorrelationRef、TelemetryEnvelope、MetricEvent / MetricSeries、SamplingDecision、RedactionMetadata、ExportAttempt / DeliveryFailure、EvalDataset、DatasetVersion、EvalCase、EvalRun、EvaluationResult、JudgeConfigurationRef、Experiment、BaselineRef、ReleaseEvaluationEvidence、BlockedReason。

### B5 Cross-boundary Contracts

#### TelemetryEnvelope

支持 module/operation、trace/span/correlation identity、request/run/plan/step/action refs、domain/knowledge/capability/model/tool/security refs、timing、status/error class、sampling、redaction、provider export metadata。不是每条事件都携带全部字段。

#### EvalDataset / DatasetVersion

绑定 case set、input/material refs、expected evidence / labels、task class、split、annotation provenance、data policy、version reason。

#### EvalRun / EvaluationResult

绑定 DatasetVersion、commit SHA、runtime/provider/model/capability/prompt config、Judge/deterministic checker versions、sample count、metrics、critical failures、blocked reason、run identity。

#### ReleaseEvaluationEvidence

汇总可复现 EvalRun、baseline comparison、threshold、critical gate 和 blocked state。它不是 Domain Admission，也不等于 Production Readiness。

### B6 Normal Flow

```text
owner module emits typed telemetry / fact refs
→ local normalize + redact
→ SamplingDecision
→ ObservabilityTracePort / OTLP-compatible export
→ Collector / LangSmith / other provider
→ traces / metrics support diagnosis

Eval:
DatasetVersion
→ bind commit + config + profile
→ deterministic checks + calibrated Judge + human review as required
→ metrics + failure taxonomy
→ baseline / experiment comparison
→ PASS / FAIL / BLOCKED Release Evidence
→ architecture keep / simplify / remove input
```

### B7 State / Lifecycle

```text
TelemetryEnvelope: CREATED → DROPPED_BY_POLICY / SAMPLED_OUT / QUEUED → EXPORTED / DELIVERY_FAILED
EvalDataset: DRAFT → VERSIONED → FROZEN_FOR_RUN → SUPERSEDED
EvalRun: CREATED → RUNNING → COMPLETED / FAILED / BLOCKED
ReleaseEvidence: CREATED → PASS / FAIL / BLOCKED → SUPERSEDED
Experiment: PLANNED → RUNNING → COMPARABLE / NOT_COMPARABLE / BLOCKED
```

### B8 Failure Taxonomy

| 失败 | Owner | 默认处理 | 不得推断 |
| --- | --- | --- | --- |
| trace exporter outage | 09 | retry/buffer/drop per priority | business failed |
| redaction failure | 09 | fail export / quarantine | export raw sensitive data |
| correlation ref missing | producer + 09 | mark incomplete / diagnose | fabricate owner identity |
| zero sample | 09 | BLOCKED | PASS |
| dataset version mismatch | 09 | NOT_COMPARABLE | trend improvement |
| Judge unavailable / uncalibrated | 09 | BLOCKED / deterministic subset | reliable score |
| critical security/effect failure | owner + 09 | FAIL gate | average score offsets it |
| benchmark credentials absent | 09 / external | BLOCKED | quality proven |
| telemetry late / duplicate | 09 | idempotent projection/dedupe | duplicate business fact |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Telemetry export Retry 只影响 projection delivery。Owner facts 的恢复不依赖 09。EvalRun 按 run identity + DatasetVersion + config hash 去重；same identity different config 必须冲突。

09 不触发业务 Replan / Effect Reconcile；它提供 failure / quality evidence，由 Architecture / Runtime / Owner 决定。恢复先从 Owner facts 重建必要 projection，再恢复 Telemetry / Eval index。

### B10 Security / Approval / Audit

Telemetry 默认 data minimization；Secret NEVER EXPORT。敏感 Prompt/Response、用户 PII、案件正文、tenant/matter names 进入 trace 需要明确 policy 和 redaction。

OpenTelemetry Baggage 只传播最小 opaque refs。AuditPersistenceReceipt 可以作为关联 ref，但普通 Trace 不成为 Mandatory Audit durability。

Eval Dataset 受 08 的访问、retention、egress 和 Legal Hold policy；Judge 外发必须单独满足模型 Egress 决定。

### B11 Persistence / Transaction Boundaries

Telemetry store、Eval store 与 Domain / Runtime / Effect / Security stores 分离。高吞吐 span 可以异步、采样或外置；DatasetVersion、EvalRun config、ReleaseEvidence 等需要可复现的耐久 metadata。

不跨 Owner 2PC。业务 commit 成功而 trace export 失败时记录 export failure / gap，不回滚业务。

### B12 Observability / Evaluation

核心技术契约优先 OTel / OTLP-compatible；LangSmith 是当前 preferred Agent/LLM trace + Eval Provider，不是不可替换 truth owner。

当前代码确切 Current：`ObservabilityTracePort`、Noop / InMemory / LangSmith adapters、metadata / span schema、redacted export、eval dataset schema、release baseline contract、sandbox audit span bridge。Full-chain wiring 与 formal Experiment integration 仍是 Target。

### B13 Current / Target / Gap / Evidence

**Current**：[`src/backend/zuno/platform/observability/README.md`](../../src/backend/zuno/platform/observability/README.md) 明确 PHASE10 `contract-foundation` 与已有 adapters / schemas；[`current-eval-baseline.md`](../evidence/current-eval-baseline.md) 明确正式 Eval 为 `MEASUREMENT_BLOCKED`。

**Target**：provider-neutral full-chain telemetry + versioned legal Eval + recovery/security fault Eval + Release Evidence + complexity kill tests。

**Gap**：formal dataset、real cases、full-chain runtime wiring、OTLP Collector profile、A/B/C benchmark、Judge calibration、SLO/DR metrics、long-term regression、court telemetry policy、release qualification。

**状态**：detail design candidate available；quality / production readiness not established。

### B14 Code / Database / Migration Constraints

- 不把 LangSmith / OTel schema 变成业务 Domain schema。
- 不建立第二套 Audit / Security / Effect store。
- 不要求所有 span 同步持久化后业务才能继续。
- 不把 eval score 直接写入 Domain current state。
- Provider migration 必须保留 correlation / redaction semantics。
- observability 独立服务拆分受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：TelemetryEnvelope / Correlation 字段组

TelemetryEnvelope 至少包含 `event_id`、`trace_id / span_id / parent_span_id`、`module`、`operation`、`timestamp / duration`、`status / error_class`、`correlation_refs`（request/run/plan/step/action/admission/delivery 等 opaque refs）、`version_refs`（必要 provider/model/capability/knowledge/tool/security refs）、`sampling_decision_ref`、`redaction_profile_ref`、`attributes`（受限 schema）、`export_priority`。

Correlation refs 不承担授权、幂等或业务完成语义。不同 Owner identity 不能因为共享 trace id 而被合并。

#### B14.2 Detail Freeze Candidate：Redaction / Sampling / Export

Redaction 在外部 export 前执行。`RedactionProfile` 至少表达允许字段类别、hash/reference 规则、正文 / PII / Secret handling、policy version。Redaction failure 默认阻止敏感 payload export，而不是降级成 raw export。

SamplingDecision 至少包含 profile/version、decision、reason、rate / priority。Error / critical security/effect diagnostic 可以提高保留率，但 durable owner receipts 不受 sampling 控制。

#### B14.3 Detail Freeze Candidate：EvalDataset / EvalCase 字段组

DatasetVersion 至少包含 `dataset_id / version`、`case_manifest_hash`、`task_class_distribution`、`split_policy`、`annotation_policy_version`、`data_policy_ref`、`created_at`、`supersedes?`。

EvalCase 至少绑定 `case_id`、input/material refs、task class / risk profile、expected evidence / citation / labels、deterministic assertions、human annotation provenance、exposure/split metadata、security / egress restrictions。

#### B14.4 Detail Freeze Candidate：EvalRun / Judge / Metric 字段组

EvalRun 至少包含 `eval_run_id`、DatasetVersion、commit SHA、runtime profile、model/provider/capability/prompt versions、retrieval config、JudgeConfig、checker versions、seed/config hash、sample_count planned/actual、started/completed、blocked reason。

EvaluationResult 绑定 metric definitions/version、aggregate + per-class values、confidence / sample metadata、critical failures、case-level refs。JudgeConfig 必须版本化 Provider/Model/Prompt/rubric 和 calibration evidence。

#### B14.5 Detail Freeze Candidate：Release / Experiment Guard

ReleaseEvidence 只有 actual_sample_count > 0、dataset/config 可复现、critical check 完成、required Judge / human calibration 满足时才能 PASS/FAIL；否则 BLOCKED。

Experiment 比较要求 baseline / candidate 的 dataset、task distribution、核心模型与预算条件达到事先定义的 comparability。不可比时标 `NOT_COMPARABLE`，不能用百分比差异做架构结论。

Complexity kill test 结果必须同时包含 quality、latency、cost、recovery / failure surface 和 manual intervention，不能只看一个平均分。

#### B14.6 Detail Freeze Candidate：Backpressure / Export Failure / Recovery

Telemetry exporter 可以 bounded queue / batch；队列满时按 priority sampling/drop，必须记录 drop metrics。不能让普通 tracing backpressure 消耗 Runtime 核心线程直到业务超时。

Crash 后不要求重放所有普通 spans。关键 Eval / Release metadata 持久化后可恢复；diagnostic projection 可以从 surviving events / owner refs 重建。Mandatory Audit 由 08-defined durable boundary 恢复，不从 trace 重建为“已审计”。

#### B14.7 Detail Freeze Candidate：Schema Evolution / Provider Migration

1. Telemetry schema 新字段默认 optional / versioned，旧 exporter 可忽略未知字段。
2. Correlation ref 语义稳定，不因 Provider 切换改 identity。
3. Redaction policy/version 与事件一同可追溯；历史事件不按新规则重解释成原本已安全导出。
4. Dataset 标签 / case set 修改创建新 DatasetVersion，不原地覆盖。
5. Metric / Judge rubric 修改版本化，趋势比较必须处理不可比区间。
6. LangSmith / OTel Provider migration 先双写 / shadow 验证时，双写只影响 Telemetry，不制造两个业务事实。
7. Eval store migration 保留 commit/config/dataset bindings。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| LangSmith / OTLP outage | 业务 Owner facts 不受影响；export failure 可观测 |
| redaction failure | Secret/PII 不 raw export |
| telemetry queue saturation | backpressure 不拖垮核心业务，drop 可计数 |
| duplicate / late telemetry | projection 幂等，不创造业务事实 |
| zero-sample benchmark | BLOCKED，不 PASS |
| Judge unavailable / drift | blocked / calibrated path，不伪造趋势 |
| DatasetVersion changed | baseline comparison 明确不可比或重新跑 |
| critical duplicate Effect | Release Gate FAIL 即使平均质量高 |
| Security violation | deterministic critical gate 优先 |
| Native Runtime A/B/C | commit/dataset/budget/config 可复现 |
| GraphRAG kill test | 按 query class 报质量/成本/延迟/故障面 |
| Provider observability migration | correlation / redaction semantics 不漂移 |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

09 的 Telemetry 完成只证明 projection/export；Eval PASS 只证明绑定 dataset/config 的测量。两者都不替代 Domain、Security、Effect、Runtime 或 Publication truth，也不自动证明 Production Readiness。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Telemetry 通过 opaque refs 串联 Owner facts；Eval 绑定 DatasetVersion、commit、runtime/provider/model/capability/prompt/checker/Judge versions 和 actual sample count。Correlation identity 与业务 idempotency namespace 分离。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

Run cancel 后允许晚到 telemetry / Usage / Effect refs进入诊断时间线，但 09 不修改业务状态。旧 EvalRun 不因新 DatasetVersion / ModelVersion 被覆盖；趋势比较需要明确版本兼容。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
recover owner durable facts first
→ recover 09 durable dataset/eval/release metadata
→ rebuild / resume telemetry projection where useful
→ mark gaps / delivery failures explicitly
→ never infer missing business success from traces
```

至少验证 exporter outage、redaction fail、queue saturation、late/duplicate telemetry、zero sample、Judge drift、dataset incompatibility、critical gates、A/B/C reproducibility 和 provider migration。