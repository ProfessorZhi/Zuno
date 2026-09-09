# 08 Security & Governance（安全与治理） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. `Continuous Authorization（持续授权）`：新的受保护访问必须消费当前有效安全事实。
2. AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同。
3. Approval 必须绑定 action identity / action hash；动作语义变化后不得复用旧批准。
4. Model Provider technically available != data egress permitted。
5. Secret Material 不进入普通 Prompt、Checkpoint、Trace、业务 payload 或普通数据库列。
6. `MANDATORY_BEFORE_EFFECT` 要求存在时，committed AuditPersistenceReceipt 是 06 执行的必要条件。
7. Retention != Recall Eligibility != Physical Purge Completion。
8. Policy / Security service 不可用时，高风险路径默认 fail closed。
9. 08 拥有 policy decision；目标 Store / Module 拥有 execution fact。
10. 安全决定不能被 Model、Runtime、Application、Tool 或 Provider 本地默认值放宽。
11. 历史合法事实不因后续撤权被改写；撤权控制新的受保护使用。
12. 不建立跨所有 Store 的安全 2PC。

### B2 Responsibility / Ownership

**Owns**：PrincipalRef / trusted identity assertion policy、Tenant / Matter Scope、SecurityEpoch / PolicyVersion、AuthorizationDecision、ApprovalDecision、ModelEgressDecision、ToolPermissionDecision、Credential / Secret usage policy、EffectiveLifecycleDecision、AuditRequirement、DecisionReason、expiry / refresh semantics、security qualification / policy compatibility。

**Does not own**：02 HumanDecision / Domain Admission；03 knowledge facts；04 Plan / Budget control；06 Effect truth；07 Model usage truth；01 publication / delivery truth；各 Store 的 purge / enforcement completion；09 Telemetry truth。

### B3 Upstream / Downstream

上游接收 01 的 trusted principal / request context、02 / 03 / 04 / 05 / 06 / 07 提交的 resource/action context、Platform 提供的 identity directory / secret-delivery / clock primitives。

下游：03 消费材料读取和检索授权；04 在 resume / retry / replan 后消费新决定；05 消费 capability scope；06 消费 tool authorization / approval / audit / credential refs；07 消费 model-egress / provider / credential decisions；02 在正式准入时消费当前授权；01 在 publication / delivery / validity query 时消费安全事实；09 只消费脱敏 refs。

### B4 Authoritative Facts / Core Objects

核心事实族：PrincipalRef、TrustedIdentityAssertionRef、TenantScopeRef、MatterScopeRef、SecurityEpoch、PolicyVersion、AuthorizationDecision、ApprovalDecision、ModelEgressDecision、ToolPermissionDecision、CredentialVersionRef、SecretRef、SecretLeaseRef、EffectiveLifecycleDecision、AuditRequirement、AuditPersistenceReceiptRef、LifecycleEnforcementRef、DecisionReasonCode、expiry / refresh requirement。

字段和物理表仍是 Target Candidate，不表示 Current 实现已经存在。

### B5 Cross-boundary Contracts

#### AuthorizationDecision

至少绑定 principal、tenant / matter / resource scope、requested action、purpose、data classification、policy epoch、decision outcome、reason、issued / expiry、refresh requirement 和 decision identity。调用方只能消费或重新请求，不能自行放宽。

#### ApprovalDecision

至少绑定 approver principal、approval identity、prepared action identity / hash、operation / ToolVersion、target resource、policy epoch、decision、issued / expiry、revocation / invalidation reason。安全相关参数或 action hash 改变后重新审批。

#### ModelEgressDecision

至少绑定 source data classification / scope、allowed provider / region / processing class、purpose、policy epoch、decision expiry。07 fallback 只能从允许集合中选。

#### EffectiveLifecycleDecision

表达 retention、recall eligibility、purge obligation、legal hold、compliance exception、decision priority / reason 和生效时间。Store 产生自己的 enforcement fact。

#### AuditRequirement / AuditPersistenceReceipt

08 拥有 Requirement；Audit persistence boundary 拥有实际持久化 Receipt。`MANDATORY_BEFORE_EFFECT` 时 06 只接受与当前 action hash / policy epoch 匹配的 committed receipt。

### B6 Normal Flow

```text
protected operation requested
→ resolve trusted principal / tenant / matter / resource / action / purpose
→ load current SecurityEpoch / policy
→ evaluate Authorization
→ evaluate egress / tool / secret restrictions when applicable
→ determine Approval requirement
→ bind Approval to action hash when required
→ determine AuditRequirement
→ require durable AuditPersistenceReceipt when required
→ issue typed decision refs / Secret Lease refs
→ target module re-checks freshness and executes
→ target module records its own execution fact
```

### B7 State / Lifecycle

最终 enum 名称在实现任务中可以调整，但语义必须覆盖：

```text
Policy: ACTIVE → SUPERSEDED / RETIRED
Authorization: EVALUATED → ALLOW / DENY; ALLOW → EXPIRED / REVOKED / SUPERSEDED
Approval: REQUIRED → PENDING → GRANTED / DENIED; GRANTED → EXPIRED / REVOKED / INVALIDATED
Secret Lease: ISSUED → ACTIVE → EXPIRED / REVOKED
Lifecycle: EVALUATED → RETAIN / NO_RECALL / PURGE_REQUIRED / LEGAL_HOLD
Store Enforcement: PENDING → ENFORCED / FAILED / BLOCKED_BY_HOLD
```

### B8 Failure Taxonomy

| 失败 | 权威边界 | 默认处理 | 可自动继续条件 |
| --- | --- | --- | --- |
| identity / tenant / scope 缺失 | 08 | deny / clarification | 获得可信上下文后重新评估 |
| policy engine unavailable | 08 | fail closed | 仅显式低风险降级策略 |
| stale SecurityEpoch | 08 | re-evaluate | 新决定成立后 |
| authorization revoked | 08 + target | block new protected use | 新授权成立后 |
| approval missing / expired | 08 | wait / deny | 新批准成立后 |
| action hash mismatch | 08 + 06 | invalidate approval | 重新审批 |
| model egress denied | 08 | deny / alternate allowed route | 只能使用允许 Provider |
| Secret Lease unavailable | 08 / Platform | wait / stop | 新 lease / allowed credential |
| Mandatory Audit write failed | audit boundary | block Effect | committed matching receipt |
| cross-tenant resource | 08 | deny + durable audit when required | 不自动继续 |
| lifecycle policy conflict | 08 | fail closed / compliance review | 明确新决定 |
| Store purge failed | target Store | keep pending / failed | Store-level Retry |
| prompt injection proposes high-risk Tool | 04/05/06 + 08 | proposal remains non-executable | 全部门禁通过后才执行 |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Authorization 在相同 principal / resource / action / purpose / policy epoch 下可以稳定重算，但不能无限缓存。SecurityEpoch、资源版本或动作语义变化后必须新评估。

Approval 只在 action hash、ToolVersion、policy epoch、有效期和审批范围仍匹配时复用。Replan 产生新的 PreparedAction 时重新审批。Reconcile 若需要再次访问远端或 Secret，也重新消费当前授权。

恢复锚点是 durable policy / decision / approval / audit facts，而不是 Trace。08 不承担 02 Admission、03 rebuild、06 Effect Reconcile 或 01 Delivery recovery，只在这些恢复过程继续提供当前安全资格。

### B10 Security / Approval / Audit

这是本模块主责。所有门禁都必须明确 fail-open / fail-closed 策略；法律材料越权、模型敏感外发、Secret、高风险 Effect、Formal Admission 和 Mandatory Audit 默认不得因为 Provider 故障而自动放行。

普通日志、Trace 和 Eval 必须数据最小化；Secret NEVER EXPORT。安全审计需要的 durable facts 与 09 Telemetry 分离。

### B11 Persistence / Transaction Boundaries

Policy / SecurityEpoch、需要历史复核的 Authorization / Approval、EffectiveLifecycleDecision、AuditRequirement 和必要 audit refs 需要达到治理要求的耐久度。单个安全决定写入可以在 08 自己的 Store 内事务化，但不与 02 / 03 / 04 / 06 / 07 建立全局 2PC。

高风险 Effect 前的 AuditPersistenceReceipt 必须在独立耐久边界成功；Store 生命周期通过 per-store enforcement facts 收敛。Platform 提供 PostgreSQL、CAS、Lease、Fencing、Secret Delivery、Clock 等物理原语，不改变政策结果。

### B12 Observability / Evaluation

至少观测 decision identity、SecurityEpoch、resource / action class、allow / deny / revoke / expiry reason、approval wait、egress denial、Secret Lease error、audit gate failure、lifecycle enforcement lag、cross-tenant denial。默认只输出 opaque refs 和分类结果。

评测至少覆盖 cross-tenant、no-egress、revocation-during-run、stale credential、secret leakage、approval action-hash invalidation、prompt-injection-to-tool、duplicate effect gate、mandatory audit failure、legal-hold / deletion、policy-engine outage 与恢复后重新授权。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-test-baseline.md`](../../evidence/current-test-baseline.md) 证明当前测试入口保留 Security fail-closed、approval binding、artifact authorization、tenant isolation 等有限行为；`docs/evidence/` 仍明确 Full CI、法院 QA、production qualification 未建立。

**Target**：Continuous Authorization + action-bound Approval + Model Egress + Secret Lease + Mandatory Audit + lifecycle governance + tenant isolation 的统一安全边界。

**Gap**：正式 Policy Engine、cross-tenant / no-egress E2E、撤权传播、approval invalidation、credential rotation、prompt injection、legal hold / purge enforcement、audit recovery、法院部署安全资格和生产证据。

**状态**：detail design candidate available；implementation / qualification / production readiness not established。

### B14 Code / Database / Migration Constraints

- 不预冻结独立 Security Service；优先模块化实现和 typed decision ports。
- 不允许任何消费者用本地默认值放宽安全策略。
- 不允许明文 Secret 进入普通业务持久化、Checkpoint、Prompt 或 Trace。
- 不把 HumanDecision 合并进 ApprovalDecision。
- 不把 Store 生命周期执行压成一条全局 `deleted=true`。
- 不默认引入跨 Store 2PC、全局分布式锁或事件溯源。
- 物理服务拆分继续受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：Authorization / Approval 字段组

`AuthorizationDecision` candidate 至少包含：`decision_id`、`principal_ref`、`tenant_scope_ref`、可选 `matter_scope_ref`、`resource_ref / resource_version_ref`、`action`、`purpose`、`data_classification`、`policy_version / security_epoch`、`outcome`、`reason_code`、`issued_at`、`expires_at / refresh_after`、必要 `provider / region / tool class constraints`。

`ApprovalDecision` candidate 至少包含：`approval_id`、`approver_principal_ref`、`prepared_action_ref`、`action_hash`、`tool_version / operation_ref`、`target_resource_ref`、`policy_version / security_epoch`、`outcome`、`issued_at`、`expires_at`、`revoked_at`、`invalidation_reason`。

Decision identity 与 execution identity 分离。`ALLOW` / `GRANTED` 不能直接作为 ToolAttempt、ModelCall、DomainVersion 或 Publication completion proof。

#### B14.2 Detail Freeze Candidate：Policy / SecurityEpoch 与缓存新鲜度

安全缓存 key 必须覆盖真正影响语义的 principal、tenant / matter、resource version、action、purpose、policy epoch 和必要数据分类。缓存 TTL 只能进一步缩短资格，不能超过 Decision 自身 expiry。

策略变更如果影响授权语义，必须产生新的 SecurityEpoch / PolicyVersion；旧 Decision 在新的受保护访问中重新评估。消费者可以持有 decision ref 做历史关联，但不得把旧 ref 当永久 capability token。

#### B14.3 Detail Freeze Candidate：Secret / Credential / Lease

Credential metadata 与 Secret Material 分离。候选字段至少包括 `credential_ref`、`credential_version`、`allowed_consumer / operation class`、`lease_id`、`issued_at`、`expires_at`、`revoked_at`、`rotation_epoch`；明文 Secret 只通过受控 delivery channel 在短生命周期内出现。

任何持久化对象只保存 ref / version / lease outcome。Retry / Resume 如果原 Lease 已失效，重新取得资格，不复用旧 Secret Material。

#### B14.4 Detail Freeze Candidate：Mandatory Audit 与动作绑定

`AuditRequirement` 至少绑定 `requirement_id`、`action_hash / protected_operation_ref`、`policy_epoch`、`minimum_fact_set`、`durability_class`、`timing=MUST_BEFORE_EFFECT | MAY_BE_AFTER` 等语义。

`AuditPersistenceReceipt` 至少能证明 `audit_record_id`、matching action / requirement、持久化边界、committed_at 和不可否认的 outcome。06 在 `MANDATORY_BEFORE_EFFECT` 下必须检查 Receipt 与当前 PreparedAction / action hash 匹配。

#### B14.5 Detail Freeze Candidate：生命周期与 per-store enforcement

EffectiveLifecycleDecision 至少表达 `subject_ref`、`policy_version`、`retention_until`、`recall_eligible`、`purge_required`、`legal_hold_refs`、`compliance_exception_refs`、`effective_at`、`reason_code`。

每个 Store 的 `LifecycleEnforcementFact` 独立表达 `store_owner`、`subject_ref`、`decision_ref`、`state`、`attempt`、`completed_at / failed_at`、`failure_class`。08 不伪造全局 purge complete；治理查询通过多个 Store facts 汇总。

#### B14.6 Detail Freeze Candidate：Crash Window / Revocation Matrix

| Window | Durable truth | 恢复 / 下一步 | 禁止 |
| --- | --- | --- | --- |
| Decision 形成后响应丢失 | durable decision 可查 | 同输入查询 / 重算 | 产生语义不同的隐式 allow |
| Approval granted 后 action hash 改变 | 旧 Approval 历史仍在 | INVALIDATED + 新审批 | 复用旧批准 |
| Readiness 后、模型外发前撤权 | 新 SecurityEpoch 生效 | 07 重新 egress gate | 使用旧 allow |
| Tool 发出后撤权且 outcome unknown | 现实结果未知 | 06 Reconcile；阻止新 Attempt | 写成未执行 |
| Audit write 失败 | 无 matching receipt | block Effect | 事后用 Trace 补票 |
| Purge 部分 Store 成功 | per-store facts 不一致 | 继续剩余 enforcement | 宣称全局已删除 |
| Secret rotation 发生在 Retry 前 | 旧 Lease 过期 / revoked | 获取新 lease | 重放旧 Secret |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Policy Rollout

1. Policy / Decision schema 必须向后读取历史记录；旧 Decision 按当时 policy version 解释。
2. 新的 mandatory 字段采用 add → backfill / derive when valid → verify → tighten constraint；不能伪造历史审批或授权默认值。
3. action-hash / canonicalization 算法带版本；算法升级不能让旧 Approval 失去可解释性。
4. Policy rollout 需要支持 canary / shadow evaluation 只用于比较，不得让未激活 policy 静默执法。
5. Credential / Secret schema migration 不把 Secret Material 搬进普通表。
6. 生命周期策略 schema 升级不得把 Legal Hold、No-Recall 和 Purge 合并成单一状态。
7. Policy Engine / Store 物理迁移必须证明历史 decision/audit refs 仍可查询。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

08 进入 Module Detail Freeze Review 前至少验证：

| 场景 | 必须证明 |
| --- | --- |
| cross-tenant read / retrieval | fail closed，且无旁路缓存泄露 |
| SecurityEpoch 在 Runtime interrupt 期间变化 | Resume 后重新门禁 |
| Readiness 后 egress 前撤权 | 07 不外发 |
| Approval 后 action hash / ToolVersion 改变 | 旧 Approval 无效 |
| Secret Lease 过期 / rotation | Retry 获取新 lease，不泄露旧 Secret |
| Policy Engine outage | 高风险路径 fail closed |
| Mandatory Audit persistence failure | 06 不产生 Effect |
| Tool 已发出后撤权 + timeout | 继续 Reconcile，不伪造未执行 |
| Legal Hold + No-Recall 同时存在 | 禁止召回但保留要求仍执行 |
| 多 Store purge 一个失败 | 全局状态不虚报 complete |
| Prompt Injection 诱导高风险 Action | Proposal 无法绕过 04/06/08 gates |
| cached old authorization | 新受保护访问因 epoch/version 检查拒绝复用 |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

08 的 Decision 证明政策判断，不证明目标动作已经执行。`AuthorizationDecision=ALLOW` 不证明材料已读取、模型已调用、工具已执行或 Domain 已准入；`ApprovalDecision=GRANTED` 只证明指定 action hash 的审批成立。

`AuditRequirement` 不等于审计已经持久化；`EffectiveLifecycleDecision=PURGE_REQUIRED` 不等于 Store 已 purge。真正 execution proof 分别来自 AuditPersistenceReceipt 和各 Store enforcement facts。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Authorization / Approval / Egress / Secret / Lifecycle 决定必须绑定 principal、tenant / matter / resource、action、SecurityEpoch / PolicyVersion、decision identity、expiry / refresh；Approval 额外绑定 action identity / hash / ToolVersion。

旧 SecurityEpoch 的 allow 不能因为进入 Checkpoint、cache、PreparedAction 或 ModelRoutingDecision 就自动延长。AuthorizationDecision、ApprovalDecision、Secret Lease、Audit Receipt、LifecycleDecision 使用不同 identity namespace，通过 causation refs 关联。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

撤权、PolicyVersion 更新或 Approval 失效只约束新的受保护访问和尚未执行动作，不重写过去合法历史。已经载入内存的数据是否允许继续纯计算必须由显式政策决定。

晚到结果如果要被继续使用、发布、外发、执行 Effect 或 Formal Admission，必须消费当前安全决定。任务取消不等于撤销既有 Effect / Admission；02 / 06 各自保存现实与业务历史。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
current SecurityEpoch / PolicyVersion
→ historical decision / approval / audit refs needed for reconstruction
→ current Authorization / Egress / Secret / Approval eligibility for next protected action
→ matching AuditPersistenceReceipt when required
→ target module resumes and records its own execution fact
→ 09 records redacted correlation
```

一致性测试至少覆盖：撤权发生在 interrupt / retrieval / model / tool / admission 不同阶段；Approval action-hash drift；Secret rotation；Audit failure；Legal Hold + No-Recall；partial purge；旧缓存 Decision；Prompt Injection；Tool outcome unknown 与撤权并发。