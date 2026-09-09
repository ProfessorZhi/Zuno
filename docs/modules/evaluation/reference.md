# 09 Observability & Evaluation（可观测性与评测） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

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

**Current**：[`src/backend/zuno/platform/observability/README.md`](../../../src/backend/zuno/platform/observability/README.md) 明确 PHASE10 `contract-foundation` 与已有 adapters / schemas；[`current-eval-baseline.md`](../../evidence/current-eval-baseline.md) 明确正式 Eval 为 `MEASUREMENT_BLOCKED`。

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