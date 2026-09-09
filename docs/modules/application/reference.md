# 01 Application & Integration（应用与集成） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. 01 负责 External Intake / Composition / Zuno-side Publication / Delivery，不重新计算其他 Owner 的事实。
2. 负责组合，不负责重新发明事实。
3. Simple QA 不因统一入口被强制进入 Native Runtime。
4. RunOutcome != Domain Admission != AnswerPublication != Consumer Display。
5. WorkProduct formal eligibility 来自 02；01 只发布 / 交付合法版本。
6. 外部 Host 拥有其最终 UI / internal adoption truth。
7. Domain invalidation、InvalidationDelivery、ConsumerAckObservation 是三个事实。
8. Agent Version = 产品能力 / 配置版本；PlanVersion = 04 单次运行控制版本。
9. side-effecting Delivery outcome unknown 交 06 Reconcile，01 不 blind retry。
10. request / invocation / publication / delivery / ack identity namespace 分离。
11. Host Adapter 不改变 Authorization / Readiness / Domain / Effect semantics。
12. Cancel 不是 Domain / Effect / remote delivery rollback。

### B2 Responsibility / Ownership

**Owns**：ExternalRequestIdentity、TaskScope normalization、trusted Host assertion binding、AgentDefinition / AgentVersion product surface、InvocationDecision composition、Zuno-side AnswerPublicationDecision、DeliveryIdentity / DeliveryState、InvalidationDeliveryFact、ConsumerAcknowledgementObservation、HostContractVersion / AdapterRef、current-validity product query composition。

**Does not own**：Authorization / Approval；Knowledge Readiness / CitationLineage；Runtime / PlanVersion；Canonical Domain / AdmissionReceipt；Tool Effect；Model qualification / usage；外部 Host final display / adoption。

### B3 Upstream / Downstream

上游：用户、自有 UI、Generic Host、法院系统、batch/API clients、trusted identity providers。

下游消费：08 current Authorization / delivery policy；03 Readiness / Evidence / Citation；07 Model result for simple path；04 RunOutcome；02 DomainVersion / WorkProduct / invalidation / citation refs；06 Effect / Reconciliation for side-effect delivery；09 diagnosis/eval refs。

### B4 Authoritative Facts / Core Objects

ExternalRequestIdentity、NormalizedTask / TaskScopeContext、AgentDefinition、AgentVersion、InvocationIdentity / InvocationDecision、AnswerPublicationDecision、PublicationIdentity、DeliveryIdentity / DeliveryAttempt / DeliveryState、InvalidationDeliveryFact、ConsumerAcknowledgementObservation、HostContractVersion、AdapterRef。

### B5 Cross-boundary Contracts

#### InvocationDecision

绑定 normalized request / scope、AgentVersion、AuthorizationDecision ref、ReadinessDecision ref、必要 Capability / Model / Runtime routing facts，输出 `SIMPLE_PATH | NATIVE_RUNTIME | WAIT | REVIEW | REJECT` 等语义。01 不重新计算底层判断。

#### AnswerPublicationDecision

普通答案由 01 根据 AnswerPolicy、current Authorization、Readiness / citation / model result eligibility 组合。正式 WorkProduct 的 publication input 必须包含 02 matching AdmissionReceipt / WorkProductVersion / current validity。

#### Delivery / InvalidationDelivery

绑定 target system / endpoint contract、business object version、payload hash/schema、idempotency identity、attempts 和必要 06 action/effect refs。Invalidation delivery 不修改 02 invalidation truth。

#### ConsumerAcknowledgementObservation

只记录 Zuno 观察到的 remote ack / no-ack / remote correlation，不推断外部 internal adoption。

### B6 Normal Flow

**Simple QA**

```text
ExternalRequest
→ trusted identity + Scope normalization
→ 08 Authorization
→ 03 task-level Readiness / Retrieval
→ 07 controlled Model call
→ citation / answer eligibility
→ 01 AnswerPublicationDecision
→ typed response
```

**Complex WorkProduct**

```text
ExternalRequest
→ InvocationDecision
→ 04 AgentRun
→ optional 02 Formal Admission
→ matching WorkProductVersion / AdmissionReceipt
→ 01 publication / Delivery
→ later 02 invalidation
→ 01 invalidation push + pull validity
```

### B7 State / Lifecycle

```text
Request: RECEIVED → NORMALIZED → ACCEPTED / REJECTED / NEEDS_CLARIFICATION
Invocation: CREATED → ALLOWED_SIMPLE / ROUTED_RUNTIME / WAITING / REVIEW_REQUIRED / REJECTED → TERMINAL
Publication: DRAFT → ELIGIBLE → PUBLISHED / REJECTED / REVIEW_REQUIRED
Delivery: PENDING → IN_FLIGHT → SENT / FAILED / OUTCOME_UNKNOWN / RETRYING
InvalidationDelivery: PENDING → SENT / FAILED / RETRYING
ConsumerObservation: UNKNOWN → ACKNOWLEDGED / NO_ACK / ACK_INVALID
```

Domain `STALE` 不属于 Delivery lifecycle。

### B8 Failure Taxonomy

| 失败 | Owner / Detection | 01 动作 | Recovery anchor |
| --- | --- | --- | --- |
| principal / matter / scope 缺失 | 01 / 08 | reject / clarify | request identity |
| Authorization denied / expired | 08 | reject / wait | decision ref |
| Knowledge PARTIAL / BLOCKED | 03 | wait / explicitly narrow scope / reject formal route | ReadinessDecision |
| Model unavailable simple path | 07 | qualified fallback / review / fail | routing/attempt refs |
| Runtime failed / abstained | 04 | typed failure / review | RunOutcome |
| WorkProduct not admitted | 02 | 不作为 formal 发布 | AdmissionReceipt absence |
| publication evidence incomplete | 01 | DRAFT / REVIEW | publication identity |
| duplicate request | 01 | dedupe / return existing invocation | request/idempotency |
| response lost after accepted | 01 | replay lookup | invocation identity |
| Host contract drift | 01 | compatible adapter / explicit reject | HostContractVersion |
| Delivery known-not-sent | 01 / 06 if effectful | idempotent Retry | delivery/action identity |
| Delivery outcome unknown | 06 | Reconcile | Effect/Reconciliation refs |
| Consumer offline | 01 | keep pending / retry | DeliveryIdentity |
| invalidation notify failure | 01 | retry independently | InvalidationDeliveryFact |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

语义 / Scope 不清不 Retry。重复 transport request 使用 stable request idempotency；same key + same canonical task hash 返回同一 invocation，same key + different task hash 冲突。

Replan 属于 04。普通明确未发送 Delivery 可按 delivery identity Retry；现实 Effect outcome unknown 交 06 Reconcile。Recovery 优先读取 02 current validity / 06 Effect，再修复 01 Delivery projection。

### B10 Security / Approval / Audit

Intake、受保护结果发布、current-validity query、跨系统 Delivery 都消费当前 08 Decision。Host credential 使用受控 refs / Lease。高风险 Delivery 的 Approval / Mandatory Audit / Effect control 由 08 + 06 负责。

对外响应最小化 / 脱敏，不泄露 Secret、未授权 evidence 或 hidden chain-of-thought。

### B11 Persistence / Transaction Boundaries

External request / invocation 是否全量耐久化取决于恢复需要；异步长任务受理、Publication、Delivery、InvalidationDelivery、AckObservation 必须有足够持久化支持幂等恢复。

02 Domain transaction 不等待外部 Consumer。Outbox / Queue 可以服务 Delivery，但不拥有 Domain truth。01 与外部 Host 不默认 2PC。

### B12 Observability / Evaluation

至少观测 intake latency、scope clarification、simple/runtime routing、publication outcome、Delivery attempts / retries / unknown、Consumer ack lag、Host contract rejection、stale-result prevented、current-validity latency、duplicate suppression、outbox lag。

E2E Eval：Simple QA、Complex WorkProduct、new-evidence invalidation、Consumer offline、duplicate request、response loss、Host version drift、side-effect Delivery unknown、Authorization change before publication。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-runtime-baseline.md`](../../evidence/current-runtime-baseline.md) 证明 Product Application Owner 已分离，主 Runtime path 不再由一个 Product God Facade 统一拥有；Current 仍不等于完整 publication/delivery/invalidation E2E。

**Target**：External Intake + Scope + AgentVersion + Invocation Composition + Publication + WorkProduct Delivery + Invalidation/Ack + Multi-Host Integration。

**Gap**：Simple QA Host E2E、Invocation / Publication qualification、push+pull invalidation、idempotent Delivery/outbox、Consumer offline fault、Host contract versioning、AgentVersion/PlanVersion compatibility、Effect handoff。

**状态**：detail design candidate available；production integration not established。

### B14 Code / Database / Migration Constraints

- 不建立 Application God Service。
- 通过 typed ports 消费各 Owner facts，不复制底层规则。
- 不要求 Zuno 自己拥有 UI/Login/Session/Conversation。
- 不把 AgentVersion 与 PlanVersion 放进同一生命周期。
- Outbox / Queue 不成为第二套 Domain truth。
- Host Adapter 只处理 transport/payload compatibility。
- 不默认微服务化；物理拆分受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：ExternalRequest / TaskScope 字段组

`ExternalRequest` candidate 至少包含 `external_request_id`、`request_idempotency_key`、`canonical_task_hash`、`host_ref / host_contract_version`、`trusted_identity_assertion_ref`、`principal_ref`、`tenant_ref`、可选 `matter_ref`、`desired_result_type`、`agent_version_ref`、`raw_input_ref / normalized_input_ref`、`received_at`。

`TaskScopeContext` 至少绑定 `scope_ref`、Matter / DocumentVersion selection、allowed result class、language / locale（如影响行为）、security scope refs、caller constraints、created_from_request`。Scope 变化形成新 scope ref，不原地扩大。

#### B14.2 Detail Freeze Candidate：Invocation 字段组与 Guard

`Invocation` 至少包含 `invocation_id`、request/scope/AgentVersion refs、route、AuthorizationDecision ref、ReadinessDecision ref、Capability/Model eligibility refs（如需要）、AgentRun ref（runtime path）、state、accepted_at/terminal_at、result_ref。

Guard：底层 refs 过期或不满足时不能由 01 改成 ALLOW；Simple path 必须证明无需 Native Runtime；正式复杂路径没有必要 Domain/Runtime capability 时不能假装降级完成。

#### B14.3 Detail Freeze Candidate：AgentDefinition / AgentVersion

AgentVersion 至少包含 `agent_id`、`agent_version`、`supported_task_classes`、`default_capability_profile_ref`、`model_role_profile_ref`、`runtime_profile_ref`、`answer_policy_ref`、`security_policy_profile_ref`、`compatibility_ref`、`activated_at / retired_at`。

已激活 AgentVersion 不原地改变影响行为的配置；新配置创建新 version。既有 AgentRun 继续绑定原 AgentVersion；与新 Runtime / Capability schema 不兼容时明确 drain / compatibility / Replan，不静默重绑定。

#### B14.4 Detail Freeze Candidate：Publication 字段组

`AnswerPublicationDecision` 至少绑定 `publication_id`、result/draft ref、request/invocation ref、AnswerPolicy ref、Authorization ref、Readiness/citation eligibility refs、Domain/Admission refs（formal result only）、decision/outcome、reason、decided_at。

普通 Answer Publication 与 Formal WorkProduct admission 分开。`PUBLISHED` 不能反向创造 DomainVersion；formal delivery 必须引用具体 WorkProductVersion 和 current-validity evidence。

#### B14.5 Detail Freeze Candidate：Delivery / Invalidation / Ack 字段组

Delivery 至少包含 `delivery_id`、publication/work_product/invalidation ref、target_system_ref`、HostContractVersion、payload_schema_version、payload_hash/ref、delivery_idempotency_key、state、attempt_no、next_retry_at、effect_action_ref（如 side-effecting）、remote_correlation_ref、last_error_class、created/updated_at。

AckObservation 至少包含 observation id、delivery ref、remote correlation、observed outcome、observed_at、raw ack hash/ref（必要时）。Ack 不升级成 remote adoption truth。

#### B14.6 Detail Freeze Candidate：Outbox / Crash / Idempotency

候选恢复链：同一 Application Store transaction 中形成需要可靠交付的 Publication/Delivery intent 与 outbox record；Worker at-least-once 消费，以 DeliveryIdentity/idempotency 去重。若真正发送属于现实副作用，06 的 PreparedAction / Effect truth 优先于 outbox ack。

| Crash Window | 恢复 | 禁止 |
| --- | --- | --- |
| request accepted 后 response 丢失 | request key 查既有 invocation | 启动第二个 Run |
| Runtime completed 后 publication 前 crash | 读取 RunOutcome + owner refs 重算 publication eligibility | 把 completed 直接发布 |
| Domain admitted 后 Delivery 前 crash | WorkProductVersion + durable Delivery intent 恢复 | 回滚 Domain |
| Delivery send 后 response lost | 06 Reconcile（effectful）或协议级查询 | blind resend |
| invalidation committed / consumer offline | retry push + pull validity stale | 恢复 Domain current |

#### B14.7 Detail Freeze Candidate：API / Host Contract / Schema Evolution

1. HostContractVersion 语义变化创建新版本；优先 additive compatibility。
2. 状态拆分 / renamed semantics 必须给旧消费者兼容映射或明确 unsupported，不用一个旧字段隐藏新语义。
3. request/task canonical hash algorithm version 化；历史 idempotency 按原算法解释。
4. AgentVersion 不因数据库 cleanup 重编号；旧 Run refs 可读。
5. Publication / Delivery payload schema 升级保留旧 WorkProductVersion 可重新解释，不重写历史正文。
6. Outbox schema migration 不丢 pending / unknown delivery；下线旧 Adapter 前完成 disposition。
7. 外部 API Migration 不能放宽内部 Security / Domain / Effect invariants。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| Simple QA | 不进入 Native Runtime 也仍有 Authorization/Readiness/Citation/Publication 资格 |
| duplicate external request | 同 task hash 不启动第二 Run；不同 hash 冲突 |
| accepted request response loss | client replay 返回既有 invocation |
| Authorization revoked before publication | publication blocked / re-evaluated |
| Readiness becomes PARTIAL | 不冒充 full-scope answer |
| Runtime complete but Admission absent | formal WorkProduct 不发布 |
| Domain invalidated while consumer offline | pull stale；push 独立重试 |
| side-effect Delivery response lost | 06 Reconcile，不 blind retry |
| HostContractVersion mismatch | compatible adapter 或明确 reject |
| AgentVersion upgrade during active Run | old Run 仍绑定旧版本 |
| Delivery Worker duplicate | stable delivery idempotency 防重复 |
| Cancel after Domain/Effect exists | 不伪造全局 rollback |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

01 的 InvocationDecision 只证明调用组合；PublicationDecision 只证明 Zuno-side publication；Delivery / Ack 只证明 01 自己的交付 / 观察事实。它们都不能替代 Authorization、Readiness、Admission、Effect 或外部 Host adoption。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Request → Scope → AgentVersion → Invocation → optional Run / Domain / Effect → Publication → Delivery 使用独立 identity / version refs 串联。新的 publication / delivery 前检查其所依赖 Owner facts 当前仍适用；request、invocation、delivery idempotency namespace 不共用。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

取消只停止未来可取消入口 / Run / Delivery 工作。已经成立的 Domain / Effect / Usage / sent Delivery 按各 Owner 继续解释。晚到 Run / Delivery / Ack 先匹配 causation 和 current validity，再更新 01 projection；stale WorkProduct 不因为旧 Ack 晚到而恢复有效。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
request / invocation / delivery durable identities
→ current 08 Authorization as required
→ 02 Domain / WorkProduct current validity
→ 04 RunOutcome / 06 Effect facts as applicable
→ repair Publication / Delivery / Invalidation projection
→ retry eligible transport work
→ 09 telemetry
```

一致性测试至少覆盖 duplicate request、response loss、simple-path no-runtime、publication security drift、Domain invalidation + offline consumer、Delivery outcome unknown、Host schema drift、AgentVersion upgrade 和 cancel after durable facts。