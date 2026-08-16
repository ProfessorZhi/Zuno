# 07 Model Gateway（模型网关）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块解决的是“怎样受控使用模型”，不是“所有 AI 都放这里”

Zuno 会在规划、执行、改写、抽取、批评和综合等不同位置调用模型。把每个 Provider SDK 直接散落到 Runtime、Capability 和 Knowledge 里，短期开发很快，长期却无法统一回答：这次为什么选这个模型、数据能不能外发、失败以后能不能切换、花了多少预算、取消后有没有继续计费。

07 的职责是把模型调用变成一个稳定受控边界：**上层表达 ModelRole（模型角色）和质量 / 预算 / 安全要求，Gateway 选择当前合格 Provider / Model，记录 Attempt 和 Usage，再把 typed result 返回给上层验收。**

### 为什么 Model Role 与具体 Provider / Model 解耦

Planner 需要的是“复杂规划能力”，Query Rewriter 需要的是“快速改写”，Extractor 需要结构化抽取。它们不应该在业务代码里直接依赖某个厂商模型名。

因此 **Model Role 与具体 Provider / Model 解耦**。TASK_ANALYZER、PLANNER、PLAN_REPAIR、EXECUTOR_FAST、EXECUTOR_REASONING、QUERY_REWRITER、EXTRACTOR、CRITIC、SYNTHESIZER、FINAL_CRITIC 是语义角色；实际 Provider / Model 由当前资格、数据政策、预算和任务需要决定。

### 强模型和弱模型为什么要按任务价值分配

复杂规划、Plan Repair、关键 Reflection 和 Final Reflection 更值得使用强推理模型；Query Rewrite、提取、分类、格式转换和普通 ReAct 通常可以使用更快更便宜的模型。

这种区分不是固定“强模型永远好”，而是控制边际成本。09 应通过角色级 Eval 证明哪些任务值得升级；没有质量收益时不应因为模型更贵就默认使用。

### 为什么 deterministic 能力不应该被 Gateway 模型化

Retrieval execution、Tool execution、schema validation、citation check、测试、安全门禁和 Approval Gate 能通过确定性机制可靠完成时，就不应该转成“问模型是否通过”。

模型适合产生 Proposal、判断、摘要和 Critique；系统事实和安全事实尽量使用 deterministic owner。这样模型升级不会改变“权限是否允许”“引用是否存在”这类本应稳定的结果。

### Provider technically available 为什么不等于能用

一个 Provider API 返回健康，只证明技术可调用。它可能因为地域、数据分类或合同政策不允许接收当前材料；也可能没有通过当前 Role 的质量基线；还可能预算超限。

所以：

```text
Provider technically available != currently permitted != quality qualified
```

07 先消费 08 的 egress / credential 决定，再结合 Qualification、Role requirement、Budget / Quota 形成 RoutingDecision。

### 为什么模型输出永远只是 Proposal

模型即使给出很高置信度，也不能直接修改 Canonical Domain、批准权限、执行未经审批的 Tool、激活 PlanVersion、绕过 Budget 或写长期 Memory。

07 只负责“模型调用发生了什么、输出了什么 typed result”。05 / 04 判断 Capability / Step 是否接受，02 判断是否 Formal Admission，01 判断是否发布。

### 为什么调用成功还远远不够

Provider 返回 200、JSON schema 合法，只说明 ModelCallAttempt 技术完成。专业 Capability 可能认为结果不满足语义，Runtime Step 可能拒绝，Domain 更可能因为 Evidence / HumanDecision 不足而不准入。

因此必须显式保持：**Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published**。

### 弱模型失败后的升级链为什么要有边界

普通执行可以先用 EXECUTOR_FAST。失败后不是无限重试，而是先调整参数 / 格式做有限 Retry；仍不满足时升级 EXECUTOR_REASONING；之后由 Critic 或 Runtime 判断 Retry / Replan / Abstain。

升级链要受 Budget、deadline、quality floor 和 Security 约束。不能为了“总能给答案”把高成本模型当无限 fallback。

### Fallback 为什么不能只看 API 兼容

Provider B 即使实现了相同 Chat Completion API，也不代表它对某个 Role 等价。Structured output、上下文、工具调用、语言、法律任务质量和安全地域都可能不同。

只有当前 Qualification / Eval 证明 B 满足该 Role 的最低质量和行为要求，并且 08 允许当前数据外发，07 才能把它作为 fallback。否则通知 04 / 05 当前路径不可用，由上层 Replan / Review。

### Budget / Quota 为什么必须跟 Retry 一起累计

如果每次 Retry 或 fallback 都重新拿一份预算，失败链会把一次任务的成本放大而不被发现。07 记录 reservation、estimate、settled usage；04 的 BudgetState 消费这些事实。

两家 Provider 都实际被调用时，两边费用都要累计，即使最终只采用一个结果。Usage 是发生过的资源事实，不因 Step 后来失败而消失。

### Cancellation 为什么不是本地 flag

调用方请求取消后，Provider 可能已经完成、可能正在生成、也可能不支持可靠取消。`CANCEL_REQUESTED` 只说明本地意图，不能推断费用为零或 Provider 停止。

07 至少要区分 provider-confirmed cancelled、completed-before-cancel、cancel unknown 和 billing / usage unknown，并在必要时做 provider-level settlement。

### Timeout 后 fallback 为什么会产生竞态

Provider A timeout 后启动 Provider B，A 的响应可能晚到。如果不保留 Attempt identity，上层会误以为只有一次调用；如果只记最终采用结果，又会漏掉 A 的 Usage。

07 保存两个独立 Attempt 和各自 Usage。04 / 05 判断晚到 A 是否仍有资格被接受，07 只保证历史调用事实不被覆盖。

### 模型升级为什么不能偷偷改变上层语义

V1 → V2 即使 API 完全兼容，Planner 可能生成更大的 Step，Extractor 可能改变字段倾向，Critic 阈值也可能漂移。模型升级必须形成新的 ModelVersion / Qualification evidence，并在关键 Role 上做回归。

如果行为变化使 Capability / Runtime 假设失效，上层调整 Contract / Prompt / Plan；Gateway 不应该用隐藏后处理把变化伪装成旧模型。

### Prompt ownership 为什么不应该全部归 Gateway

Gateway 统一模型调用，但具体 Prompt 的业务语义属于使用场景：Capability 的抽取 Prompt 属于 05 的专业实现，Runtime Planner Prompt 属于 04，产品回答 Prompt 可能属于对应产品 / Capability。

07 可以管理 provider formatting、system safety wrapper 和通用 request schema，但不成为所有 Prompt 的 God Repository。

### Structured output 为什么需要两层校验

07 可以检查 JSON / schema / transport-level structured output；05 / 04 还要检查专业语义和 Step Acceptance。字段齐全不代表内容正确。

把 schema success 与 semantic success 分开后，Gateway 可以稳定处理 Provider 兼容问题，而不把法律质量逻辑塞进 SDK Adapter。

### Cache 为什么默认不能假设 LLM 调用幂等

同一 prompt 在模型版本、temperature、seed、provider backend 或时间变化时可能返回不同结果。只有 caller 明确允许且操作具有可接受确定性时，才能缓存 / duplicate suppress。

Cache identity 需要绑定 ModelRole、Provider / ModelVersion、prompt/input hash、generation config、structured schema 和必要 security / tenant scope。缓存结果被重新使用时，仍由调用方做当前业务新鲜度判断。

### Secret 和数据外发为什么分别治理

API Key 属于 Secret；Prompt 中的案件材料属于受保护业务数据。两者风险不同。07 从 08 / Platform 得到 Credential ref / Lease，同时消费 ModelEgressDecision 决定哪些数据允许发给哪个 Provider / region。

Secret 不进 Prompt / Trace；敏感 Prompt / Response 是否能进入 Telemetry 由数据分类和 redaction policy 决定。

### 为什么 Model Gateway 不需要默认成为独立微服务

Provider SDK 集中并不自动要求网络服务。默认可以在模块化 backend / worker 中通过 adapter 实现；只有 Secret isolation、独立吞吐扩缩、Provider 网络出口或部署生命周期出现明确证据时，再按 ADR-0012 拆分。

逻辑统一比服务数量更重要。

### Streaming 输出为什么需要单独处理“部分结果、取消和计费”

流式模型调用会让“调用完成”变得更细。Provider 可能已经返回前几百个 token，随后连接中断；用户也可能在流式输出中途取消。此时前端已经看到一段文本，不代表它通过了完整 structured validation、Capability Acceptance 或 Final Gate，更不能因为“看起来像答案”就自动进入 Domain 或 Publication。普通 UI 可以显示明确标记的 transient stream，但正式结果只能使用达到 caller completion contract 的完整 result。

与此同时，流式中断仍可能产生真实 Usage。Provider 可能按已生成 token 计费，取消也可能晚于 provider completion。因此 07 需要把 partial delivery、Attempt terminal state、result eligibility 和 Usage settlement 分开：部分 token 可以作为诊断 / UX 事件，但不是完整模型结果；Usage 则按 provider 报告或 settlement 进入预算。这样“用户没看到完整答案”不会被错误解释为“没有产生费用”，也不会让一段半截输出进入 04 / 05 的成功路径。

### 模型调用为什么只能做到“可追溯”，不能承诺字节级可复现

为了复盘，07 应记录 Provider / ModelVersion、PromptTemplateVersion、输入 hash / refs、generation config、structured schema、时间、必要 seed 和 routing / qualification。这样可以解释“当时调用了什么条件”，并在 Eval 中尽量重现环境。

但多数远端模型的后端部署、采样实现和服务版本可能继续变化，即使请求参数相同，也不能据此承诺未来得到完全相同的 token 序列。因此历史正确性不能依赖“以后再调用一次模型重建原答案”。需要长期负责的业务结果由 02 保存正式版本和依据；07 保存的是调用 provenance 和资源事实。测试中可以对 deterministic adapter / fixed fixtures 做严格 replay，对真实 LLM 更适合验证 schema、关键语义、quality distribution 和 owner invariants，而不是把逐字一致当生产契约。

### Quota Reservation 为什么要和最终 Usage Settlement 分开

并行 Runtime 在派发多个模型 Step 前需要知道预算和 Provider quota 是否还有空间，所以 07 可能先做 reservation；但 reservation 只是“预留最多可以消耗多少”，不是实际发生的 Usage。调用成功后按真实 tokens / pricing 结算，多余 reservation 释放；调用未发出则释放；请求已经发送但 billing outcome 不清楚时，reservation 不能立即当作零，而应进入 settlement / disputed / unknown 路径。

这个分层对并发尤其重要。如果三个分支都只读取同一个旧余额，再分别启动大模型，很容易合计超限；reservation 可以帮助控制并发上限，而 04 最终仍以 settled / authoritative usage refs 修复 BudgetState。Provider 晚报 Usage 时，预算事实可以向上修正，却不能修改已经发生的历史 Attempt；如果修正导致剩余预算不足，影响的是后续 dispatch / Replan，而不是伪造过去“其实没调用”。

### 当前、目标与缺口

Current 代码 / Wave 1 Contract 已有 ModelRoutingDecision、ModelCallAttempt、Quota / Usage / Cancellation 等基础表面，但正式 credentials、四 Profile runtime、Provider qualification、真实 fallback、budget / quota fault test、cancellation race 和角色级质量测量并未完整证明。

Target 是 role-driven、security-bound、budget-aware、provider-neutral 的统一模型边界。Gap 包括正式 Qualification Matrix、role-quality evidence、usage settlement、fallback equivalence、no-egress E2E、真实限流 / timeout / cancel 故障和 production attestation。

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