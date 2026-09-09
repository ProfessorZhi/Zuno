# 06 Tool Runtime & Effects（工具运行与外部效果） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. Action Proposal != PreparedAction != ToolAttempt != EffectReceipt。
2. Transport Success 不等于 Effect Success。
3. Outcome Unknown（结果未知）不得映射为普通 Failed，也不得 Blind Retry。
4. known-not-executed 与 outcome-unknown 必须分开。
5. same key + same action hash 才能进入同一逻辑动作；same key + different action hash 必须拒绝。
6. Approval / Audit 必须绑定当前 PreparedAction / action hash。
7. Secret Material 不进入普通 PreparedAction、Receipt、Prompt、Trace 或普通业务表。
8. Cancel 不重写已经发生或可能已经发生的现实 Effect。
9. 06 拥有 Effect semantics，不拥有 08 policy、05 professional correctness、04 Plan、02 Domain Admission 或远端系统内部最终 truth。
10. 跨远端系统默认不使用 2PC。
11. 高风险 Tool 没有幂等或可信 Reconciliation 路径时，不允许自动 Retry。
12. ToolVersion / effect semantics drift 可以触发 Replan。

### B2 Responsibility / Ownership

**Owns**：ToolDefinition / ToolVersion binding、PreparedAction / PreparedToolAction、ActionIdentity / ActionHash、EffectClass、RetrySafety、IdempotencyIdentity、ToolAttempt、ExternalOperationRef、EffectReceipt、ReconciliationReceipt、duplicate suppression、remote correlation、effect confirmation semantics。

**Does not own**：Authorization / Approval / AuditRequirement；Capability semantic correctness；Plan / Replan；Canonical Domain Admission；Publication；远端系统内部状态机。

### B3 Upstream / Downstream

上游接收 04 / 05 Action Proposal，08 AuthorizationDecision / ApprovalDecision / AuditRequirement / Credential refs，Platform network / secret-delivery primitives。

下游向 04 返回 typed effect outcome；向 02 提供可用于正式准入的外部事实 / receipts；向 01 返回交付类 Effect；向 09 输出脱敏 telemetry；Tool semantic drift 时通知 04 re-resolve / Replan。

### B4 Authoritative Facts / Core Objects

核心对象族：ToolDefinitionRef、ToolVersionRef、OperationRef、EffectClass、PreparedAction / PreparedToolAction、ActionIdentity、ActionHash、IdempotencyIdentity、ToolAttempt、ExternalOperationRef、EffectReceipt、ReconciliationReceipt、RetrySafety、ReconciliationCapability、CompensationRef（仅有业务定义时）。

### B5 Cross-boundary Contracts

#### PreparedAction / PreparedToolAction

至少绑定 ToolDefinition / ToolVersion / operation、规范化非敏感参数、target resource、action identity / hash、effect class、retry safety、idempotency identity、run / plan / step causation、security / approval / audit requirements。

#### ToolAttempt

每次实际调用产生独立 attempt identity，绑定 PreparedAction、dispatch time、transport phase、provider request / external operation correlation、response / error class。Attempt 完成不能证明 Effect。

#### EffectReceipt

绑定 action identity / hash、confirmed outcome、attempt / external operation refs、confirmation source、remote business identity / version（可得时）、idempotency identity、confirmed_at。Receipt 只保存必要结果和 refs，不保存 Secret。

#### ReconciliationReceipt

绑定 action identity、reconcile attempt、evidence / query source、结论 `CONFIRMED_EXECUTED | CONFIRMED_NOT_EXECUTED | STILL_UNKNOWN | MANUAL_REQUIRED` 及时间。它可以导致 Effect state 收敛，但不替代远端系统内部 truth。

### B6 Normal Flow

```text
Action Proposal
→ resolve ToolDefinition / ToolVersion
→ canonicalize non-secret parameters
→ classify EffectClass / RetrySafety / ReconciliationCapability
→ create PreparedAction + action_hash + idempotency identity
→ current Authorization
→ Approval when required
→ committed AuditPersistenceReceipt when required
→ acquire current Secret Lease
→ create durable ToolAttempt before dangerous send
→ execute external operation
→ interpret transport + business response
→ persist EffectReceipt when confirmed
→ OUTCOME_UNKNOWN: Reconcile
→ persist ReconciliationReceipt / repaired effect state
→ return typed outcome to 04 / 02 / 01
```

### B7 State / Lifecycle

```text
PreparedAction:
PROPOSED → PREPARED → BLOCKED / AWAITING_APPROVAL / READY
READY → ATTEMPTING

ToolAttempt:
CREATED → DISPATCHING → REQUEST_SENT / KNOWN_NOT_SENT
REQUEST_SENT → RESPONSE_RECEIVED / TIMED_OUT / CONNECTION_LOST

Effect:
UNCONFIRMED → CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / OUTCOME_UNKNOWN
OUTCOME_UNKNOWN → RECONCILING → CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / MANUAL_RECONCILIATION
```

状态名可在实现时调整，但不能把 Attempt terminal state 与 Effect terminal state合并。

### B8 Failure Taxonomy

| 失败 | 权威判断 | 控制动作 | 恢复锚点 |
| --- | --- | --- | --- |
| schema / parameter invalid | 06 | reject / re-resolve | ToolVersion + validation |
| Tool semantic drift | 06 + 04 | Replan | ToolVersion / PreparedAction |
| authorization denied / revoked | 08 | stop / review | AuthorizationDecision |
| approval missing / invalid | 08 + 06 | wait / reapprove | Approval + action hash |
| Secret Lease failure | 08 / Platform | wait / stop | lease ref |
| known not sent | 06 | bounded Retry possible | Attempt phase fact |
| rate limit / transient | 06 | Retry only if safe | Attempt + retry policy |
| timeout after possible send | 06 | Outcome Unknown → Reconcile | action / external correlation |
| duplicate logical action | 06 | return existing effect / continue reconcile | idempotency + action hash |
| remote inconsistent result | 06 + remote/human | Manual Reconciliation | all receipts |
| mandatory audit missing | 08/audit boundary | block send | AuditReceipt absence |
| remote effect then local crash | 06 | Reconcile | durable Attempt + remote id |
| compensation required | business owner + 06 | new controlled action | original Effect + compensation ref |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

**Retry**：只有能证明未执行，或远端有可信幂等去重，并且 ToolVersion、参数、安全、Approval、Audit、Secret 和计划假设仍成立时。

**Replan**：Tool schema / semantics / effect class / capability availability / target assumption 变化。04 创建新 PlanVersion；06 不“猜参数”修计划。

**Reconcile**：Outcome Unknown 的必经机制。优先远端 query / business key / idempotency status，再人工。没有结论时保持 unknown。

**Recovery**：PreparedAction → durable Attempt → existing Effect / Reconciliation facts → remote query → fresh security gate before any new Attempt。Runtime Checkpoint 只做关联。

### B10 Security / Approval / Audit

执行前消费当前 08 决定。Approval 与 AuditReceipt 绑定 action hash；安全相关参数变化后重新审批 / 审计。Secret 仅通过 ref / lease 临时获得。

Prompt Injection 产生的 Proposal 仍要经过 Tool schema、Effect classification、Authorization、Approval、Mandatory Audit 和 idempotency gates。

### B11 Persistence / Transaction Boundaries

PreparedAction、Attempt、EffectReceipt、ReconciliationReceipt 和幂等记录必须达到 crash recovery 所需耐久度。外部网络调用不放在本地 DB transaction 里冒充原子提交。

候选边界：

```text
TX1: persist PreparedAction / idempotency + durable Attempt intent
COMMIT
→ external call
TX2: persist transport observation + EffectReceipt / OutcomeUnknown
COMMIT
→ if unknown, independent reconciliation attempts / receipts
```

TX1 在真正可能产生 Effect 前要完成，使进程崩溃后至少知道“可能发出了哪个动作”。具体“REQUEST_SENT”落盘时机需要 Adapter 级 fault test；不能承诺消除网络栈与持久化之间的所有不可观测纳秒窗口，而要依赖远端幂等 / correlation / reconciliation。

### B12 Observability / Evaluation

至少观测 tool/version、effect class、action ref、attempt count、send phase、latency、known-not-executed vs unknown、reconcile duration、duplicate suppression、approval wait、audit gate failure、Secret Lease error、remote error class、manual reconciliation rate。

Telemetry 不能替代 EffectReceipt。Failure Eval 必须覆盖 response loss、remote-success/local-crash、duplicate action、cancel-in-flight、approval drift、audit failure、remote query outage 和 Tool semantic drift。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-runtime-baseline.md`](../../evidence/current-runtime-baseline.md) 明确保留 unknown external effect → `RECONCILE` / no blind retry；[`current-test-baseline.md`](../../evidence/current-test-baseline.md) 保留 duplicate claim 与未知外部效果 reconciliation 等行为。真实外围系统 E2E、durable effect ledger 和 crash window 尚未证明。

**Target**：PreparedAction → Security / Approval / Audit → durable Attempt → EffectReceipt → Reconciliation 的完整 Effect Control。

**Gap**：真实 remote idempotency / query、durable action/effect schema、duplicate-effect fault injection、crash recovery、Secret Lease、audit-before-effect、manual reconcile、provider semantic drift、compensation protocol 和生产 evidence。

**状态**：detail design candidate available；implementation / production readiness not established。

### B14 Code / Database / Migration Constraints

- 不默认建设工具市场、独立 Sandbox 或 Tool 微服务。
- 优先薄 Adapter 复用 MCP / HTTP / CLI / existing sandbox。
- 上层通过 stable Tool Contract，不直接依赖各 Provider SDK。
- 不使用 Checkpoint、HTTP 2xx 或 SDK success 代替 EffectReceipt。
- 不默认跨 Store / remote 2PC、全局分布式锁或 exactly-once 宣称。
- 物理服务拆分受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：PreparedAction 字段组

候选至少包含：`action_id`、`tool_definition_ref`、`tool_version_ref`、`operation_ref`、`target_resource_ref`、规范化 `non_secret_parameters` 或 payload ref、`canonical_action_hash`、`hash_algorithm_version`、`effect_class`、`retry_safety`、`reconciliation_capability`、`idempotency_key`、`run_id / plan_version / step_run_id`（如 runtime-driven）、`authorization_requirement_ref`、`approval_requirement_ref`、`audit_requirement_ref`、`credential_requirement_ref`、`created_at`。

Secret 不进入 canonical hash payload；使用稳定 secret/credential reference 或明确排除 secret value，使 rotation 不改变同一业务动作的 action hash，除非凭证版本本身改变业务语义。

#### B14.2 Detail Freeze Candidate：Attempt / Effect / Reconciliation 字段组

`ToolAttempt` 至少包含 `attempt_id`、`action_id`、`attempt_no`、`transport_phase`、`started_at`、`request_sent_at?`、`provider_request_ref / external_operation_ref?`、`response_received_at?`、`transport_status`、`business_status?`、`error_class?`、`credential_lease_ref`。

`EffectReceipt` 至少包含 `effect_receipt_id`、`action_id / action_hash`、`confirmed_outcome`、`confirmation_source`、`remote_business_ref / remote_version?`、`attempt_refs`、`confirmed_at`。

`ReconciliationReceipt` 至少包含 `reconciliation_id`、`action_id`、`attempt_no`、`method`、`evidence_refs`、`outcome`、`performed_at`、`manual_actor_ref?`。

#### B14.3 Detail Freeze Candidate：EffectClass / RetrySafety

第一阶段至少区分：`READ_ONLY`、`IDEMPOTENT_WRITE`、`NON_IDEMPOTENT_WRITE`、`IRREVERSIBLE_OR_HIGH_RISK`。EffectClass 不由调用方自报，来自 ToolDefinition / Operation contract，并可被 08 风险策略进一步收紧。

RetrySafety 至少表达 `SAFE_IF_NOT_SENT`、`SAFE_WITH_REMOTE_IDEMPOTENCY`、`REQUIRES_RECONCILIATION`、`MANUAL_ONLY`。任何异常映射到 Retry 前必须先得到一个 RetrySafety 证明。

#### B14.4 Detail Freeze Candidate：Idempotency / action hash

逻辑 namespace 以 tenant / tool operation / idempotency key 或等价受控范围隔离。规则：same key + same canonical action hash → 返回 existing action/effect 或继续其 reconciliation；same key + different action hash → conflict；不得新建第二个不相关 Action。

Canonical action hash 的字段集合和算法必须版本化。会改变现实语义的 target、operation、关键参数、ToolVersion / semantic version 必须进入 hash；Trace id、时间戳、Secret value 等偶然字段不进入。

#### B14.5 Detail Freeze Candidate：Send Boundary / Transaction Candidate

候选持久化顺序：

```text
BEGIN TX1
→ idempotency + action-hash check
→ persist PreparedAction
→ persist Attempt intent / dispatch token
COMMIT
→ re-check current security / approval / audit / lease if dispatch delayed
→ send external operation
→ capture provider correlation as early as possible
BEGIN TX2
→ persist transport observation
→ confirmed result: EffectReceipt
→ ambiguous result: OUTCOME_UNKNOWN
COMMIT
```

不得持有 DB lock 等待远端。若进程在 send 与 correlation 持久化之间崩溃，恢复仍依赖远端 idempotency / business key / query；这是需要 fault test 管理的不可避免窗口，不允许以“事务已覆盖”掩盖。

#### B14.6 Detail Freeze Candidate：Crash / Cancel / Late Result Matrix

| Window | 恢复 | 禁止 |
| --- | --- | --- |
| TX1 前崩溃 | 无 durable action，重新准备 | 推断已发送 |
| TX1 后、send 前崩溃 | 读取 Attempt intent；新 dispatch 前刷新安全 | 自动标 Effect 成功 |
| send 后响应前崩溃 | Outcome unknown；remote query / idempotency reconcile | blind retry |
| remote 成功、本地 Receipt 前崩溃 | Reconcile 收敛为 executed | 重发高风险 POST |
| Cancel 在 send 前 | 阻止 Attempt | 创造假 Effect |
| Cancel 在 send 后 | 尝试 cancel 可选；仍 Reconcile | 写 confirmed-not-executed |
| old Plan response late | 保存真实 Effect；04 决定计划接受性 | 因 stale branch 丢弃现实事实 |
| Approval / SecurityEpoch 在排队期失效 | 新 send 前重门禁 | 复用旧批准 |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Tool Upgrade

1. ToolVersion / operation semantic change 产生新版本，不原地覆盖旧 PreparedAction 的解释。
2. action hash algorithm version 可向后读取；禁止重算历史 hash 后覆盖。
3. Effect / Reconciliation outcome enum 扩展必须向后兼容 UNKNOWN / legacy values；不能把旧 unknown 批量改成 failed。
4. 新的 idempotency unique constraint 上线前扫描历史冲突并显式处理。
5. 外部 correlation 字段新增采用 nullable → backfill where provable → verify；不能伪造 remote id。
6. Provider / Tool adapter migration 必须证明旧 EffectReceipt 和待 Reconcile Action 仍可查询 / 恢复。
7. 无法恢复的 pending unknown 在下线旧 Adapter 前必须进入人工 disposition，而不是删除。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| same key + same action hash replay | 不产生第二个逻辑 Effect |
| same key + different action hash | fail closed conflict |
| known-not-sent transient failure | 满足门禁后才 Retry |
| response timeout after possible send | Outcome Unknown → Reconcile |
| remote success then process crash | 恢复不重复提交 |
| cancel while in flight | 不把 cancel 当 confirmed-not-executed |
| old Plan response late | Effect fact 保留，Runtime 可拒绝计划使用 |
| Approval 后参数 / ToolVersion drift | send 前重新审批 |
| SecurityEpoch / Secret Lease 失效 | send 前阻断 |
| Mandatory Audit failure | 无 Effect send |
| remote query unavailable | 保持 unknown / manual，不 blind retry |
| Tool semantic drift | 04 Replan，不由 06 猜参数 |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

06 的完成只由 effect 语义证明。ToolAttempt finished、HTTP 2xx、SDK success、Runtime Step accepted、Trace exported 都不能单独证明现实效果。EffectReceipt / ReconciliationReceipt 说明 Zuno 已确认了什么；若该外部事实还要成为法律业务事实，仍由 02 Formal Admission 决定。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

PreparedAction 必须绑定 action / hash、ToolDefinition / ToolVersion、规范化参数摘要、target、effect class、idempotency identity、run / PlanVersion / StepRun、当前 Authorization / Approval / Audit refs 和必要 CredentialVersionRef。

Action、Attempt、Reconciliation 使用独立 identity namespace。任何改变现实或安全语义的参数、版本、target、effect class 或 policy change 都不能复用旧 Approval / RetrySafety。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

取消只阻止未来可停止的 dispatch。已发出但未知的调用继续 Reconcile；已确认 Effect 不因 Run cancel、Replan 或 stale branch 被删除。晚到响应按 action / attempt / external correlation 归属，再由 04 / 02 / 01 决定如何消费。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
PreparedAction / action hash / idempotency
→ durable Attempt / external correlation
→ existing Effect / Reconciliation receipts
→ remote query / manual reconciliation if unknown
→ refresh 08 Authorization / Approval / Audit / Secret before any new Attempt
→ typed effect fact to 04 / 02 / 01
→ 09 telemetry
```

至少覆盖 cancel-in-flight、remote-success/local-crash、same-key-different-hash、Approval drift、SecurityEpoch / Secret rotation、old-plan late result、remote query outage、manual reconciliation、Mandatory Audit failure 和 Tool semantic drift。