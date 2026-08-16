# 09 Observability & Evaluation（可观测性与评测）

<!-- status: design-baseline-v1; implementation: not-authorized; quality: not-established; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块其实回答两个不同问题

Observability（可观测性）回答“系统刚才发生了什么”；Evaluation（评测）回答“结果好不好、复杂度值不值得保留”。两者都需要统一版本、关联和数据治理，但不能混成一个 Dashboard。

如果一次任务失败，工程师需要沿 request → run → step → retrieval → capability → model → tool → domain → delivery 找到事实；如果要决定 GraphRAG、Reflection 或 Native Runtime 是否值得长期保留，则需要可复现数据集和对照实验。

### 为什么 Telemetry 不能成为业务真相

Trace 很适合串联调用链，但它可能因为 Provider 不可用、采样、网络中断或 redaction 丢失细节。因此必须明确：

```text
Telemetry != Durable Audit != Business Truth
```

AdmissionReceipt、EffectReceipt、AuthorizationDecision、ApprovalDecision、AuditPersistenceReceipt 都由各自 Owner 保存。09 只引用这些 identity，不能用一条漂亮 span 替代它们。

### 一次事故调查为什么要先找 Owner Fact

用户报告“系统重复提交了两次”，第一步不是数 Trace 里有几个 Tool span，而是查 06 的 PreparedAction / Attempt / EffectReceipt / ReconciliationReceipt，确认现实世界到底发生了几个逻辑动作和几个效果。

然后再用 04 的 Plan / Step、08 的 Authorization / Approval、01 的 Delivery 和 09 的 Trace 对齐时间线。Telemetry 的价值是解释，不是裁决。

### 为什么统一 correlation 很重要

九个责任域各自拥有事实，如果没有稳定关联，就无法回答“哪一次模型调用产生了哪个 Capability output、属于哪个 Step、最后是否被 Domain 准入”。

因此跨模块传播 opaque correlation refs，例如 request / run / plan / step / action / admission 等 identity。它们帮助定位，但 correlation id 不拥有业务含义，也不能成为幂等 key 或授权 token。

### OpenTelemetry Baggage 为什么不能塞案件信息

OpenTelemetry Baggage（上下文行李）可以跨进程传播，但传播范围很广。如果为了排障方便把 tenant 名称、案件名称、用户 PII、材料正文或授权结果直接放进去，就可能在无意中扩散敏感信息。

默认只传播最小 opaque ref，在可信边界内回查真实事实。Secret NEVER EXPORT。必要业务文本只有在策略明确允许、redaction 完成并且真的对诊断有价值时才进入受控 Telemetry。

### Sampling 为什么只能影响观测细节

高吞吐环境不可能永久保存所有成功 span，Sampling 是合理成本控制。可以全量保留 error，抽样普通成功请求，也可以按任务等级调整采样率。

但 Sampling 不能影响 Domain / Effect / Security / Mandatory Audit 的耐久事实。关闭 tracing 不应该让系统失去恢复能力或安全证明。

### 为什么 Eval Dataset 本身也需要版本

如果今天 100 个 case、明天修改其中 20 个标签，再把两次分数直接比较，就无法知道变化来自模型还是数据集。

EvalDataset / DatasetVersion 必须绑定 case identity、材料 refs、task class、expected evidence / labels、annotation provenance、split 和 data policy。case set 或标签改变产生新 DatasetVersion。

### 训练数据和评测数据为什么必须区分

Prompt tuning、few-shot 选择或模型训练已经看过的样本不能在不说明的情况下继续冒充独立 test。数据集要标注 split 和 exposure / provenance，避免“测试集泄漏”让质量看起来异常好。

法院真实材料如果因为数据政策不能进入云 Judge，也不能偷偷换成合成数据后仍声称法院质量已验证；应明确标记测量范围和 blocked reason。

### 为什么 LLM Judge 不能成为万能裁判

引用是否存在、JSON schema 是否满足、action hash 是否匹配、重复 Effect 是否发生，这些问题应该优先使用 deterministic checker。开放式法律表达、适用性、论证质量可以用 LLM Judge，但 Judge 本身也有偏差和漂移。

Judge Provider / Model / PromptVersion 必须进入 Eval Run 配置，并用人工金标准样本做校准。Judge 失去可靠性时，相关指标应 BLOCKED / unreliable，而不是为了保持绿色继续产出分数。

### PASS / FAIL / BLOCKED 为什么必须严格区分

PASS 表示在冻结的数据集、配置、样本数和阈值下真正达标；FAIL 表示评测有效执行但结果不达标；BLOCKED 表示根本没有资格判断，例如 sample_count=0、credentials 缺失、Judge 不可用或 baseline 不可比。

当前正式 benchmark 就属于 **MEASUREMENT_BLOCKED**。这不是较轻的失败，也不是默认通过。

### 为什么 critical failure 可以否决平均分

法律场景里某些失败不能被高平均分抵消：越权读取、重复高风险 Effect、正式引用无法回溯、stale WorkProduct 被错误发布等都是架构级错误。

Release Evaluation Evidence 需要同时记录 aggregate metrics 和 critical failure taxonomy。即使总体准确率很高，只要出现定义中的 critical violation，发布资格也可以 FAIL。

### 为什么要同时评质量、恢复和成本

Agent 复杂度常常不会直接反映在最终准确率上。一个方案可能提高 1% 准确率，却把 Retry 放大十倍、P95 延迟翻三倍、每题多调用十几次模型。

所以评测还要看 evidence sufficiency、citation correctness、unsupported claim、reviewer acceptance、recovery correctness、duplicate effect、Replan rate、reconcile duration、latency、token、cost、manual intervention 等。

### 指标为什么必须按 Task Class 分层

简单条文定位、跨文档争议分析、外部执行任务的成功标准不同。如果把所有请求混成一个“Agent Success Rate”，数据会掩盖真正的问题。

每个 EvalCase / Metric 要绑定 task class、difficulty / risk profile、版本和执行路径，才能解释 GraphRAG 是否只对某类 query 有用，或 Native Runtime 是否只在长任务恢复上有价值。

### 为什么 Eval 应该主动帮助删除复杂度

团队已经实现的功能容易获得“沉没成本保护”：有 GraphRAG，就只评 GraphRAG 自己的分数；有 Multi-Agent，就只展示它能跑。

09 应设计 removal-oriented experiment：GraphRAG vs Hybrid Retrieval、Specialist vs 普通并行 Step、Long-term Memory on/off、Native Runtime vs Generic Host + Legal Backend。在尽量相同语料、模型和预算下比较质量、恢复、成本与维护失败面。

### Native Runtime 的 A/B/C 为什么是架构决策证据

总体架构明确保留三类比较：A Generic Host + Legal Skills，B Generic Host + Zuno Legal Backend，C Zuno Native Runtime + first-class Domain State。

如果 C 没有稳定收益，就应该缩小 Native Runtime；如果 B 已经满足法院任务的恢复与正式状态需要，就不要为了“自研”重复宿主能力。09 的职责是让这种删除决定有证据。

### GraphRAG 为什么不能用“图数据库已部署”证明价值

GraphRAG 只有在特定 query class 上相对简单 retrieval baseline 稳定提高质量，而且成本、延迟和故障面可接受时才值得保留。

同一语料、同模型、可比预算的对照实验是最低要求。构图成功、Neo4j 有数据、demo 看起来丰富都不是 quality proof。

### 观测 Provider 为什么必须可替换

目标采用 OpenTelemetry / OTLP-compatible provider-neutral contract，LangSmith 可以作为 Agent/LLM trace 与 Eval 的默认 / preferred Provider，但法院或 on-prem 环境不能因为 SaaS 不可用就失去核心运行和审计能力。

Provider 可替换要求 correlation、redaction、span semantic 和 Eval identity 稳定。换成其他 OTel backend 或未来 Langfuse 不应改变业务 Owner。

### Provider outage 为什么不能影响业务完成

如果 LangSmith / OTLP exporter 故障，09 可以记录 delivery failure、buffer / retry 或丢弃低优先级 telemetry；但 02 / 06 / 08 的耐久事实继续成立，Runtime 也不应为了普通 telemetry 阻断低风险业务。

只有策略明确要求的 Mandatory Audit 由相应 durable audit boundary 控制，不能把普通 tracing provider availability 等同于审计可用性。

### 成本归因为什么要沿因果链

Provider 月账单只能说明总花费。真正优化需要把 Usage / Cost 关联到 request / run / step / capability / model attempt，才能回答 Reflection 是否过度触发、某个 Capability 是否总在 fallback、GraphRAG 是否值得额外 token。

09 提供归因与趋势，04 / 07 按既定 Budget 做运行控制。长期观测不直接修改单次任务预算政策。

### Release Evidence 为什么不能等于 Production Readiness

一组 Eval Run PASS 只说明它覆盖的 dataset / config / commit / profile 达标。Production Readiness 还需要运维、HA / DR、安全 qualification、容量、恢复演练、外部依赖等证据。

09 可以提供 ReleaseEvaluationEvidence，但不能单独宣布整个系统 production ready。

### SLO 为什么不能只盯一个 API 的 P95 延迟

Zuno 的复杂任务可能几秒返回简单问答，也可能因为知识构建、人工审批或外部 Reconciliation 持续很久。如果只定义“HTTP endpoint P95 < 2s”，系统很容易通过异步受理把延迟藏到 Queue 里，却无法说明用户真正多久拿到可用结果。09 因此需要把入口受理延迟、queue wait、Step execution、model / retrieval latency、approval wait、reconcile duration、publication / delivery lag 分层观测，再由产品场景定义 end-to-end SLO。

同样，恢复能力需要自己的 SLI：例如 crash 后到 Run 可继续的时间、Outcome Unknown 到确认的时间、stale WorkProduct 到 invalidation delivery 的时间。它们不应该和普通 request latency 混成一个数字。Target 可以定义这些测量结构，但没有真实 workload、RPO / RTO 目标和故障演练就不能宣称“系统满足某 SLO”。09 的职责是让以后每个可靠性承诺都能对应明确 measurement，而不是用单一 Dashboard 绿色状态代替系统行为。

### 多个 Reviewer 对同一法律样本意见不一致时怎么办

法律任务的 ground truth 并不总是天然唯一。两名专业 Reviewer 可能对争议点重要性、法条适用性或答案表达给出不同判断。如果数据集强行把第一次标注写成唯一 label，Eval 会把合理分歧误判成模型错误；反过来，如果“有分歧就都算对”，评测又失去约束力。

DatasetVersion 应保存 annotation provenance、Reviewer identity ref、rubric version、分歧和 adjudication（裁决）过程。可以对明确事实使用 deterministic label，对开放判断保存允许集合、等级评分或由第三位 Reviewer adjudicate。没有完成必要 adjudication 的 case 可以标记 uncertain / excluded from release-critical metric，而不是偷偷取平均。Judge calibration 也要使用这些人工样本验证一致性。这样“质量分”不仅可复现，还能解释它到底代表专业共识、确定事实还是仍有争议的判断。

### 当前、目标与缺口

Current 是 `contract-foundation`：`ObservabilityTracePort`、`NoopTraceAdapter`、`InMemoryTraceAdapter`、修正后的 `LangSmithTraceAdapter`、LangSmith-compatible metadata、OTel / LangSmith-compatible span schema、redacted export adapter、eval dataset schema、release baseline contract 和 sandbox audit span bridge 已存在。代码 README 仍明确 Target 待完成 AgentRunGraph、StepExecutionGraph、Retrieval Round、Tool Gateway、Final Gate span wiring 和 LangSmith Experiment integration。

Target 是 provider-neutral telemetry + full-chain correlation + reproducible legal Eval + failure/recovery Evaluation + release evidence + complexity kill tests。Gap 包括正式数据集、真实 case、production full-chain tracing、Collector deployment、A/B/C benchmark、Judge calibration、SLO / DR metrics、法院 telemetry policy 和 release qualification。

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