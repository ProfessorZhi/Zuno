# 06 Tool Runtime & Effects（工具运行与外部效果）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块真正保护的是“现实世界到底发生了什么”

Tool 调用和普通函数调用最大的不同，是它可能改变现实世界：发送通知、提交材料、写外部数据库、触发审批、调用法院外围系统、修改第三方资源。一个 Python 函数抛异常通常可以重试，但一个 HTTP POST 超时并不能告诉我们远端到底有没有执行。

因此 06 的核心不是“统一封装工具”，而是让每个外部动作都拥有稳定身份、明确副作用分类、可确认的效果事实，以及在结果未知时可恢复的对账路径。

### 为什么 HTTP 200 也不能自动叫“执行成功”

Transport Success 不等于 Effect Success。远端可能返回 200 但业务状态仍是 rejected / pending；也可能返回 500，但实际写入已经在远端提交；甚至网络超时后远端已经执行，只是响应没有回来。

所以 Tool Runtime 必须把传输结果、一次调用尝试和现实效果分开。HTTP / SDK response 只是一次 Attempt 的 observation，最终 Effect truth 取决于该工具的业务语义、远端可查询事实和必要的 Reconciliation。

### 一个外部 POST 超时以后为什么绝不能立即重试

假设系统向外围法院系统提交一份工作成果。请求发送后本地等待超时。如果立刻 Retry，同一成果可能被提交两次；如果直接标记 Failed，又可能掩盖其实已经提交成功的事实。

这类状态必须进入 Outcome Unknown（结果未知）。**Outcome Unknown（结果未知）不得映射为普通 Failed**。接下来要用稳定 action identity、远端 operation id、业务唯一键、幂等键或查询 API 对账；无法自动确认时进入人工 Reconciliation。

### Action Proposal 为什么不能直接进入网络调用

模型、Capability 或 Runtime 可以提出“把结果发送到系统 X”的 Action Proposal，但 Proposal 可能包含幻觉参数、旧资源版本、未经授权的目标或高风险副作用。

06 要先把它解析成 PreparedAction / PreparedToolAction：选择明确 ToolDefinition / ToolVersion，规范化参数，去除 Secret，计算 action hash，声明 effect class、retry safety、idempotency identity、target resource 和必要 security / approval / audit requirements。只有这个稳定动作才能进入执行门禁。

### action hash 为什么是审批与幂等的共同锚点

动作 identity 说明“这是哪个逻辑动作”，action hash 说明“这个动作的安全与现实语义具体是什么”。如果目标、关键参数、ToolVersion、operation 或 effect class 改变，就不能继续引用旧 Approval。

同样，幂等不能只看一个用户传入的 key。**same key + different action hash 必须拒绝**。否则调用方可以拿旧幂等 key 换参数，系统却错误返回旧结果或执行另一个动作。

### ToolAttempt 为什么不等于 Effect

一个 PreparedAction 可以有多个 ToolAttempt：第一次连接失败且明确没有发出；第二次请求发出但响应丢失；第三次其实不应该发生，因为第二次结果还未知，需要先 Reconcile。

Attempt 记录执行过程；EffectReceipt 记录 Zuno 已经可靠确认的现实效果。多个 Attempt 不会创造多个逻辑 Action，除非明确创建了新的 action identity。

### 已知未执行和结果未知为什么是两种完全不同的失败

如果 DNS 解析失败、连接在请求发送前被拒绝，并且 Adapter 能可靠证明远端没有收到动作，那么它属于 known-not-executed，在授权、预算、deadline 和 ToolVersion 仍然有效时可以 Retry。

如果请求是否到达不可确定，就必须进入 Outcome Unknown。可靠系统的重试策略不是“遇到异常就 exponential backoff”，而是先回答“上一次是否有可能已经产生 Effect”。

### 外部系统不支持幂等时怎么办

并不是所有外围系统都支持 idempotency key。此时 06 不能假装拥有 exactly-once。可以使用远端业务唯一键、提交编号、查询 API、CAS、唯一约束、补偿流程或人工对账来降低重复风险。

如果高风险动作既没有远端幂等，也没有可信查询 / 对账 / 补偿路径，那么架构上就不应允许自动 Retry。宁可进入人工确认，也不能把“自动化率”放在重复副作用风险之前。

### Security / Approval / Audit 为什么发生在 PreparedAction 之后

只有 PreparedAction 稳定以后，08 才能准确回答“当前主体是否允许执行这个具体动作”“是否需要审批”“审计必须保存什么”。如果先审批一个模糊 Proposal，再由 Tool Adapter 修改参数，审批就失去对象。

高风险动作的正确链是 PreparedAction → 当前 Authorization → matching Approval → matching AuditPersistenceReceipt → Secret Lease → Attempt。任何一个绑定变化，都必须重新验证门禁。

### Secret 为什么不能进入 PreparedAction 和 Receipt

外部工具经常需要 Token、密码或证书。为了重放而把 Secret 放进 PreparedAction，会让持久化 Action 本身变成 Secret 仓库；把它写进 EffectReceipt 又会把审计事实和敏感材料混在一起。

06 只保存 Credential / Secret Lease ref。真正 Secret 通过受控 delivery 在执行时临时取得。恢复时重新校验 Lease / rotation，而不是从历史记录里取回明文。

### Cancel 为什么不是“撤销外部请求”

如果请求尚未发出，Cancel 可以阻止新的 Attempt；如果请求已经发出，Cancel 最多尝试调用远端 cancellation API，但本地 `cancelled=true` 不能证明现实效果被撤销。

尤其当请求正在飞行且结果未知时，取消以后仍然要继续 Reconcile。真实世界不会因为 Runtime 分支被标成 stale 或 cancelled 就自动回滚。

### 旧 Plan 的 Tool 结果晚到以后怎么办

Replan 以后旧分支可能收到远端响应。对于纯计算结果，Runtime 可以因为 PlanVersion 过期而丢弃；对于 Effect，则不能因为旧 Plan 已失效就否认现实动作。

06 仍按 action identity / Attempt / external correlation 记录 EffectReceipt。04 决定这个 Effect 是否还能影响当前 Plan，02 决定它是否需要进入 Domain Admission，但现实发生过什么由 06 保留。

### 为什么 Tool schema drift 可能需要 Replan 而不是 Retry

如果 ToolVersion 改变了参数、目标资源语义、effect class 或返回含义，原 PreparedAction 的假设可能已经不成立。此时“换个参数再试”不是 Retry，而是在改变计划里的动作。

06 应返回 typed semantic drift；04 重新解析 capability / tool requirement 并创建新 PlanVersion。旧 PreparedAction 和 Effect 历史不被新版本覆盖。

### 为什么外部 Effect 不能塞进数据库事务

将“本地 INSERT + 远端 POST”写在一个数据库 transaction 里，并不能获得跨系统原子性。数据库可以 rollback，本地却无法强迫第三方回滚；长事务还会持有锁并放大故障。

目标架构采用 durable intent / attempt → external call → durable receipt 的恢复链，通过 action identity、远端 correlation 和 Reconciliation 收敛，而不是默认建设跨远端 2PC。

### Reconciliation 为什么是一级机制而不是异常兜底

只要存在外部副作用，Outcome Unknown 就是正常故障模型的一部分，而不是“极端情况”。每一种高风险 Tool 都应该在接入时说明能否查询远端结果、使用什么业务唯一键、如何判断 executed / not-executed，以及何时必须人工确认。

没有 Reconciliation Contract 的高风险 Tool，不应该被宣称为可恢复 Tool Runtime。

### Tool Registry 为什么不能变成工具市场

06 需要稳定 ToolDefinition / ToolVersion 和 effect metadata，但并不意味着要建设产品级工具市场、插件商店或独立 Sandbox 平台。第一阶段只需要把已经存在的 MCP、HTTP、CLI 或受控 Adapter 包装进一致 effect contract。

是否拆独立服务、是否建立集中 Registry，要由独立扩缩容、安全隔离和部署生命周期证据决定，而不是因为“Tool 很多”就自动微服务化。

### exactly-once 为什么不是本模块可以单方面承诺的属性

工程讨论里经常会问“这个 Tool 能不能做到 exactly-once”。只看 Zuno 本地数据库，答案很容易被说成“有唯一键就可以”；但只要动作跨过网络边界，本地唯一约束最多保证不创建第二个逻辑 PreparedAction，不能阻止第一次请求已经到达远端却在响应回来前丢失。如果远端既没有幂等键，也没有稳定业务唯一键或可查询状态，本地系统没有办法从物理世界中证明“只发生一次”。

因此 06 的目标不是宣称 exactly-once，而是组合可验证的 weaker guarantees：同一 action identity 不被本地重复创建；same key + different action hash 明确冲突；已知未发送才允许普通 Retry；远端支持幂等时复用同一业务动作身份；结果未知进入 Reconciliation；无法自动判断就显式交人工。这样系统不会把无法证明的分布式语义包装成营销式保证。未来如果某个具体外围系统能够提供原子幂等提交和查询，ToolDefinition 可以记录更强能力，但那是该 integration 的 Evidence，不是整个 Tool Runtime 的默认属性。

### 补偿动作为什么必须是新的 Effect，而不是修改旧 Receipt

某些外部副作用可以“撤销”，例如已经创建的临时记录可以删除、已经提交的草稿可以发起撤回。但这种撤销本身也是新的现实动作，有自己的权限、审批、失败和对账风险。把原 `EffectReceipt=EXECUTED` 改写成 `NOT_EXECUTED`，会破坏历史：现实里第一步确实发生过，只是后来又发生了一个反向动作。

所以 Compensation（补偿）如果存在，应创建新的 PreparedAction，引用原 Effect 作为 causation，重新计算 action hash、Authorization、Approval、AuditRequirement 和 idempotency，再形成自己的 EffectReceipt。两个 Receipt 组合后才能说明当前外部状态“可能已经恢复到业务上等价的结果”。如果补偿失败或 outcome unknown，也独立 Reconcile。这样审计、恢复和人工复核能看到完整历史，而不是通过修改旧记录制造一个从未发生过的世界。

### 远端幂等为什么仍然不能替代 Reconciliation

远端支持 idempotency key 可以显著降低重复提交风险，但它只回答“相同 key 的重复请求如何处理”，不一定回答“第一次请求最终产生了什么业务效果”。例如远端可能接受 key，却返回 `PENDING`；也可能把请求去重到一个后来被业务规则拒绝的 operation；查询 idempotency status 还可能暂时不可用。

因此 ToolDefinition 仍需要 ReconciliationCapability：怎样通过 operation id、业务唯一键或 query API 取得最终状态，什么结果算 confirmed executed，什么算 confirmed not executed，什么只能继续 unknown。远端幂等让安全 Retry 的条件更强，但不能把所有 timeout 直接降级成“重发就好”。这也是 EffectReceipt 与 transport / idempotency receipt 分离的原因。

### 当前、目标与缺口

Current Runtime Baseline 已证明 unknown external effect → `RECONCILE`、禁止 blind retry，以及 tool gateway / side-effect contract 的有限行为；当前测试基线也保留未知外部效果 reconciliation、duplicate command / tool claim 等行为。它们仍不是完整外围系统 E2E。

Target 是完整 PreparedAction → Authorization / Approval / Audit → ToolAttempt → EffectReceipt → Reconciliation chain。Gap 包括 durable action / receipt storage、真实外围幂等和 query、crash-window fault injection、approval invalidation、Secret Lease、audit-before-effect、manual reconciliation、Tool semantic drift 和生产运行证据。

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

**Current**：[`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 明确保留 unknown external effect → `RECONCILE` / no blind retry；[`current-test-baseline.md`](../evidence/current-test-baseline.md) 保留 duplicate claim 与未知外部效果 reconciliation 等行为。真实外围系统 E2E、durable effect ledger 和 crash window 尚未证明。

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