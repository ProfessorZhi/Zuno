# 07 Model Gateway（模型网关） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. Model Role 与具体 Provider / Model 解耦。
2. Provider failover 不绕过 Security、Quality、Budget / Quota、Egress。
3. Provider technically available != currently permitted != quality qualified。
4. 模型输出只产生 Proposal / Candidate / Draft / Critique。
5. deterministic Retrieval / Tool / schema / citation / security / approval 不默认模型化。
6. Retry / fallback Usage 与 Cost 累计，不重置。
7. Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published。
8. 上层不长期持有 Provider Secret。
9. ModelRequest 携带 role、quality、deadline、budget 和 security constraints。
10. Prompt / Capability / Plan ownership 不被 Gateway 吞并。
11. ModelAttempt / Usage 是历史调用事实，不因下游拒绝而删除。

### B2 Responsibility / Ownership

**Owns**：ModelRole mapping、Provider / Model qualification refs、ModelRoutingDecision、ModelCallAttempt、provider adapter compatibility、QuotaReservation / consumption、Usage / Cost Receipt、cancellation / timeout state、approved fallback execution、provider / model version refs。

**Does not own**：Authorization / Egress policy；Plan / Step Acceptance；Capability semantics；Domain；Tool Effect；legal Eval thresholds；Publication。

### B3 Upstream / Downstream

上游来自 04 / 05 / 03 / 01 的 ModelRole request / prompt/input refs / quality / budget / deadline，08 的 Egress / Credential decisions，09 的 Qualification / Eval evidence refs。

下游返回 typed model result / failure、RoutingDecision ref、Attempt ref、Usage / Cost；向 09 输出脱敏 telemetry；向 04 提供 budget / quota / fallback outcome。

### B4 Authoritative Facts / Core Objects

ModelRole、ProviderRef / ProviderVersion、ModelRef / ModelVersion、QualificationRef、ModelRoutingDecision、ModelCallAttempt、QuotaReservation、UsageReceipt、CostReceipt、CancellationState、FallbackDecision、ProviderErrorClass、UsageSettlementFact。

### B5 Cross-boundary Contracts

#### ModelRequest

至少包含 role、operation、prompt/input refs 或 controlled payload、required quality profile、structured-output schema、deadline、budget/quota constraints、security/egress decision ref、credential ref、generation config、causation refs。

#### ModelRoutingDecision

绑定 request、候选 qualification set、selected Provider / ModelVersion、routing reason、budget / quota snapshot、security refs、fallback policy。它不是质量结果。

#### ModelCallAttempt

绑定 routing decision、attempt identity/no、Provider/ModelVersion、request hash/schema、start/deadline/timeout、provider request ref、transport/result/error class、cancellation state。

#### Usage / Cost Receipt

区分 reserved / estimated / provider-reported / settled。绑定 Attempt / Run / Budget；重复或 fallback 调用都累计。

### B6 Normal Flow

```text
ModelRole request
→ current 08 Egress / Credential decision
→ resolve qualified provider/model set
→ check role quality + structured capability
→ reserve Budget / Quota
→ RoutingDecision
→ Attempt
→ provider-specific request
→ execute / stream
→ transport + structured schema validation
→ Usage / Cost capture
→ typed result
→ 04 / 05 / 01 performs semantic acceptance

failure:
→ bounded Retry
→ qualified fallback / stronger role
→ caller chooses Retry / Replan / Abstain
```

### B7 State / Lifecycle

```text
Qualification: UNKNOWN → QUALIFIED / RESTRICTED / DISABLED → SUPERSEDED
Routing: REQUESTED → SELECTED / REJECTED
Attempt: CREATED → IN_FLIGHT → COMPLETED / FAILED / TIMED_OUT
Attempt: IN_FLIGHT → CANCEL_REQUESTED → CANCELLED / COMPLETED_BEFORE_CANCEL / CANCEL_UNKNOWN
Usage: RESERVED → ESTIMATED / REPORTED → SETTLED / DISPUTED / UNKNOWN
```

### B8 Failure Taxonomy

| 失败 | Detection | 默认处理 | 上层含义 |
| --- | --- | --- | --- |
| provider 503 | 07 | bounded Retry / qualified fallback | Replan if no path |
| rate limit | 07 | backoff / alternate qualified | deadline/budget may fail |
| timeout | 07 | retry/fallback if policy permits | late result possible |
| invalid structured output | 07 | repair/retry/stronger model | semantic acceptance still separate |
| quality floor not met | 05/09/04 | stronger model/review/abstain | Replan possible |
| egress denied | 08 | allowed provider or stop | no bypass |
| credential unavailable | 08/Platform | wait / allowed alternative | stop if none |
| quota / budget exhausted | 07+04 | deny / cheaper route / stop | Replan/abstain |
| fallback non-equivalent | 07+quality evidence | reject | review/stop |
| cancellation ambiguous | 07 | settlement | caller treats result late |
| usage mismatch | 07 | provider reconciliation | budget repair |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Retry 前确认 Role、input/prompt refs、SecurityDecision、quality floor、deadline、budget 仍成立；每次新 Attempt，Usage 累计。Replan 由 04 处理无合规模型、quality assumption / budget structure 失效。

模型不使用 06 Effect Reconcile，但 Cancellation / Billing / Usage unknown 需要 provider settlement。Recovery 使用 RoutingDecision + Attempt + provider request ref + Usage facts，不依赖 SDK session。

### B10 Security / Approval / Audit

08 拥有 provider/data classification/region/credential policy；07 只执行。Secret NEVER EXPORT，敏感 Prompt/Response telemetry 最小化。

高敏数据外发如果需要额外 Human Approval，由 08 决定；07 不把“模型调用非 Tool Effect”解释成不需要安全门禁。

### B11 Persistence / Transaction Boundaries

RoutingDecision、Attempt、Usage / Cost、Cancellation / Settlement 达到预算和恢复所需耐久度。模型远端调用不与 Runtime Checkpoint / Domain Store 做 2PC。

Request 发出但本地 Attempt/Usage 写入失败时，恢复依赖 provider request id / usage API / settlement；不能把模型输出写进 Domain 作为恢复捷径。

### B12 Observability / Evaluation

至少观测 role、provider/model/version、routing reason、latency / TTFT、tokens、cost、retry/fallback、quota rejection、schema failure、cancel outcome、quality eval ref、security denial reason ref。

09 做 role-level quality/cost benchmark、fallback regression、provider outage simulation、budget/quota fault test、cancel race、usage reconciliation、no-egress verification。

### B13 Current / Target / Gap / Evidence

**Current**：存在 ModelRoutingDecision、ModelCallAttempt、Quota / Usage / Cancellation 等 Contract / implementation surface；完整 Current 仍以代码、测试和 `docs/evidence/` 为准，正式 benchmark 仍 blocked。

**Target**：role-driven + security-bound + budget-aware + provider-neutral model invocation。

**Gap**：formal qualification、production credentials、role-quality evidence、fallback equivalence、usage settlement、budget/quota fault tests、cancel race、real provider outage、四 Profile runtime / attestation。

**状态**：detail design candidate available；quality / production readiness not established。

### B14 Code / Database / Migration Constraints

- Provider SDK/model name 只在 Gateway adapter/config 边界。
- 上层依赖 typed role/request/routing/result/usage contracts。
- Gateway 不建立第二套 Planner / Capability / Tool / Release Gate。
- Prompt ownership留在具体 use case。
- 不默认独立微服务；受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：ModelRequest / Routing 字段组

`ModelRequest` 至少包含 `model_request_id`、`role`、`operation`、`prompt_template_ref/version`、`input_refs / canonical_input_hash`、`structured_schema_ref/hash`、`generation_config_ref/hash`、`quality_profile_ref`、`deadline_at`、`budget_limit / quota_class`、`egress_decision_ref`、`credential_ref`、`run/plan/step/capability causation refs`。

`ModelRoutingDecision` 至少包含 `routing_id`、request、candidate qualification refs、selected provider/model version、reason、security / egress refs、quota snapshot、reserved budget、fallback policy/version、decided_at。

#### B14.2 Detail Freeze Candidate：Attempt / Cancellation 字段组

`ModelCallAttempt` 至少包含 `attempt_id`、routing/request refs、attempt_no、provider/model refs、provider_request_ref?、started_at、deadline/timeout、transport status、schema status、result_ref/hash?、error_class?、cancel_state、completed_at?。

Cancellation 必须区分 `NOT_REQUESTED / REQUESTED / PROVIDER_CONFIRMED / COMPLETED_BEFORE_CANCEL / UNKNOWN`。本地 requested 不得直接写 provider-confirmed。

#### B14.3 Detail Freeze Candidate：Usage / Cost / Budget Settlement

Usage 至少记录 `usage_receipt_id`、attempt、source=`ESTIMATE|PROVIDER_REPORTED|SETTLED`、input/output/cache/reasoning token classes（Provider 可得时）、cost currency/value、pricing version/ref、reported_at / settled_at、dispute state。

04 BudgetState 使用聚合后的 authoritative usage refs。Fallback / late provider response 产生的实际使用仍累计；下游未采用结果不冲销已发生费用。

#### B14.4 Detail Freeze Candidate：Qualification / Role Guard

Qualification 至少绑定 ProviderVersion、ModelVersion、supported roles / structured-output/tool capabilities、context limits、region/security class、Eval evidence version、quality floor、effective/expiry。Routing 只有在 Qualification + current Egress + Budget / Quota 全部满足时 SELECTED。

模型版本或关键 provider behavior config 变化产生新 qualification；不能把旧 QUALIFIED 标签直接继承。

#### B14.5 Detail Freeze Candidate：Retry / Fallback / Cache Guard

Retry = same semantic request + same Role / input / schema / security / quality assumption，new Attempt + accumulated Usage。Fallback 必须重新检查目标 Provider 的 Egress、Qualification、Budget、deadline。

Cache / duplicate suppression 只有 caller policy 允许时，key 至少绑定 Role、Provider/ModelVersion 或可接受等价组、prompt/input hash、structured schema、generation config、tenant/security scope class。缓存命中不证明 Step / Domain freshness。

#### B14.6 Detail Freeze Candidate：Crash / Timeout / Late Result Matrix

| Window | 恢复 | 禁止 |
| --- | --- | --- |
| Routing reserved 后、call 前 crash | release/reconcile reservation | 计作 completed usage |
| provider request sent、本地 result 前 crash | provider request ref / usage query / safe retry policy | 假设未调用 |
| timeout 后 fallback 启动，A 晚到 | 两 Attempt + Usage 均记录；caller revalidates | 覆盖 B 事实或漏计 A |
| cancel requested，provider 已完成 | completed-before-cancel + settle usage | 记 zero cost |
| Usage reported、本地 budget checkpoint fail | usage truth 修复 04 Budget | 重置预算 |
| SecurityEpoch 在 retry 前变化 | 新 egress gate | 复用旧 allow |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Provider Upgrade

1. Model / Provider version 不原地覆盖历史 Attempt refs。
2. Usage schema 扩展要保留 Provider 不支持字段的 UNKNOWN，而不是填 0。
3. Pricing version 变化不重算覆盖历史 settled cost；需要新视图时另建 derived estimate。
4. Prompt / generation config 影响语义时必须版本化。
5. Qualification schema升级保留旧 decision 可解释性。
6. Provider adapter 下线前处理 in-flight / cancel-unknown / unsettled usage。
7. 新的 unique/idempotency constraints 上线前扫描历史冲突。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| provider 503 / rate limit | bounded Retry + budget accumulation |
| fallback Provider non-equivalent | route rejected |
| egress denied | 无绕过调用 |
| credential unavailable | no secret fallback bypass |
| timeout then A late + B fallback | two attempts / two usage facts，caller freshness check |
| cancel race | requested 与 provider outcome 分离 |
| Usage settlement mismatch | budget可修复，不污染 Domain |
| model version upgrade | cache/qualification 不误复用 |
| schema-valid but Capability-invalid | 07 success 不升级 05/04 success |
| budget exhausted | Retry / fallback 不 reset |
| SecurityEpoch change before retry | reauthorize |
| production credential absent | measurement / qualification remains BLOCKED |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

07 只能证明模型调用与用量事实。Attempt COMPLETED / valid JSON 不证明 Capability Contract、Step Acceptance、Domain Admission 或 Publication。Usage/Cost 只证明资源事实。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Request / Routing / Attempt 绑定 Role、input/prompt refs、Provider/ModelVersion、Qualification、current Egress/Credential、Budget/Quota、deadline、run/plan/step/capability causation。Routing、Attempt、Usage settlement identities 分离。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

`CANCEL_REQUESTED` 不等于 Provider stopped / cost zero。Late model result 由 07 保存调用事实，04/05/01 判断当前接受性。Provider / Model 资格变化影响未来 routing 和尚未接受结果，不改写历史 Attempt。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
RoutingDecision / Attempt identity
→ provider request / model version
→ reported / settled Usage
→ current 08 Egress / Credential before new call
→ current 07 Qualification / fallback eligibility
→ 04 / 05 / 01 acceptance
→ 09 telemetry / eval
```

至少覆盖 cancel race、timeout + late result + fallback、双 Provider cost、SecurityEpoch drift、non-equivalent fallback、cache versioning、budget exhaustion、schema-vs-semantic split 和 usage settlement mismatch。