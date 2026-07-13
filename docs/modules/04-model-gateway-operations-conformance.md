# 04 Model Gateway：Operations、Conformance 与 Lifecycle 附录

updated: 2026-07-13
status: normative-target-module-addendum
module_number: 04
formal_path: `docs/modules/04-model-gateway-operations-conformance.md`
agent_mirror: `.agent/modules/04-model-gateway-operations-conformance.md`
parent_document: `docs/modules/04-model-gateway.md`
companion_document: `docs/modules/04-model-gateway-contract-freeze.md`
dependency_baseline_sha: `729e439e29deadc101c5687fc47125104e62e2c1`

> 本附录补充 Model Gateway 在长期运行、Provider Adapter 一致性、配置发布、模型生命周期、租户隔离、公平调度、过载保护、缓存、运维命令、数据保留删除、SLO、兼容升级和质量治理方面的 Target 设计。
>
> 本附录不包含实施 Program、阶段计划、迁移批次、人员分工或 Codex 任务，也不声明相关运行时代码、Migration、Provider 集成或生产证据已经存在。

## 0. 文档边界与规范优先级

规范读取顺序：

```text
全局架构原则
→ Agent Core 正式 Target Contract
→ 04 Model Gateway 主文档
→ 04 Model Gateway Contract Freeze 附录
→ 本 Operations / Conformance / Lifecycle 附录
→ 已确认的跨模块 Contract / ADR
→ Program
→ 代码、Migration、测试与运行证据
```

本附录解决：

```text
Provider Adapter 是否真的符合公共 Contract
配置和模型变更如何安全激活、灰度、回滚与排空
多租户如何隔离容量并避免 noisy neighbor
高负载时如何背压、降级、拒绝而不绕过安全和预算
Provider Prompt Cache 与 Gateway Result Cache 如何区分
运维人员如何禁用 Provider / Model 而不直接改数据库
Prompt / Response / Stream / Usage 如何保留、删除和 Legal Hold
哪些 SLI / SLO / Readiness 才能证明 Gateway 可运行
SDK / API / Model Revision 变化如何保持兼容
Eval / Judge 调用如何避免循环证明和实验污染
```

本附录不改变以下 Owner：

- Agent Core 拥有 Plan、Step、控制决定、RunOutcome 和最终业务 Budget；
- Security 拥有 Authorization、Redaction、Secret Access、Security Epoch 和 Revocation；
- Infrastructure 拥有物理连接、事务、CAS、Clock、Secret 交付、Object Store 和恢复原语；
- Observability & Eval 拥有 Telemetry ingest、Projection、Eval、Evidence 和 Release Gate；
- Model Gateway 拥有 Provider / Model 执行语义、Routing、Call、Attempt、Usage、Quota、Health、Circuit、Adapter Conformance 和模型调用运维事实。

## 1. 四个运行平面

Model Gateway 逻辑上分为四个平面，初期仍可部署在同一 backend process，不要求拆微服务。

```text
Execution Plane
    接收 ModelCallRequest
    Routing / Admission / Attempt / Stream / Validation / Usage

Control Plane
    Role Routing Profile
    Provider / Model / Capability / Prompt Execution Binding
    Config Snapshot / Activation / Rollback

Operations Plane
    Drain / Disable / Force Circuit / Probe / Reconcile
    Capacity / Fairness / Backpressure / Readiness

Evidence Plane
    Attempt / Receipt / Event / Audit Ref
    Adapter Conformance / SLO / Eval Configuration Snapshot
```

平面边界：

1. Control Plane 变更不能直接修改执行中的不可变 Routing / Attempt；
2. Operations Plane 命令必须形成可审计领域事实，不允许直接更新数据库行；
3. Evidence Plane 保存证明引用，不反向批准执行；
4. Execution Plane 只消费已激活、版本化、未过期的配置；
5. Security Revocation 和强制 Disable 可以使未 Dispatch 的决定失效，但不能静默改写历史记录。

## 2. Provider Adapter Contract

### 2.1 Adapter 的职责

每个 Provider Adapter 必须实现统一 `ProviderAdapterContract`：

```text
adapter_id
adapter_version
provider_ref
supported_api_versions
supported_operation_kinds
supported_transport_modes
request_mapping_version
response_mapping_version
stream_mapping_version
usage_mapping_version
failure_mapping_version
cancellation_capability
reconciliation_capability
idempotency_capability
status
```

Adapter 负责：

- 将 Provider-neutral Request 映射为 Provider 请求；
- 显式配置 SDK retry、timeout、proxy、TLS 和 endpoint；
- 将 Response、Stream、Usage、Finish Reason 和 Error 归一化；
- 保存 Provider request ID、API version、SDK version 和 mapping version；
- 对未知字段、未知枚举和未知事件执行兼容策略；
- 产生 transport receipt、cancellation evidence 和 reconciliation evidence；
- 保证 Secret、Prompt、Response 和错误不因 SDK 日志泄漏。

Adapter 不负责：

```text
选择 Model Role
改变 Security Decision
扩大 Budget
决定 Agent Replan
批准 Tool Proposal
把 Provider success 当成业务 Acceptance
把 Provider 文档声明当成已验证 Capability
```

### 2.2 ProviderAdapterResult

```text
adapter_result_id
attempt_id
adapter_ref
provider_api_version
sdk_name
sdk_version
transport_request_id
provider_request_id
raw_response_ref
normalized_response_ref
stream_session_ref
usage_observation_refs
failure_ref
transport_receipt_ref
cancellation_evidence_ref
reconciliation_evidence_ref
mapping_warnings
created_at
```

规则：

1. HTTP 2xx 只代表 Transport / Provider 层接受或响应，不代表 Structured Output、Security 或业务成功；
2. SDK 自动 Retry 必须禁用或转换为显式 Attempt 子记录；
3. Provider 返回未知 finish reason 时不得映射为普通成功；
4. 原始 Provider payload 使用受控 object ref，不进入跨模块公共 Contract；
5. Adapter mapping warning 必须可计量，持续出现时 Capability 降级或打开版本级 Circuit。

## 3. Adapter Conformance

### 3.1 AdapterConformanceProfile

```text
adapter_conformance_profile_id
profile_version
adapter_ref
provider_ref
provider_api_version
sdk_version
operation_kind
capability_profile_ref
conformance_suite_version
status
passed_case_refs
failed_case_refs
waived_case_refs
known_limitations
verified_at
expires_at
evidence_refs
```

状态：

```text
DECLARED
VALIDATING
CONFORMANT
CONFORMANT_WITH_LIMITATIONS
NON_CONFORMANT
STALE
REVOKED
```

### 3.2 最小 Conformance Suite

每个 Adapter / Operation 至少验证：

```text
request serialization
response normalization
error normalization
hidden retry accounting
timeout layering
cancellation semantics
stream event ordering
unknown event handling
structured output local validation
usage and cost mapping
idempotency / request-id behavior
response-lost reconciliation
redaction and secret leakage
large payload / context boundary
rate-limit header interpretation
```

Operation-specific 验证：

| Operation | 附加验证 |
| --- | --- |
| `TEXT_GENERATION` | finish reason、stop、truncation、reasoning summary policy |
| `STRUCTURED_GENERATION` | schema subset、local validation、repair、additional properties |
| `EMBEDDING` | dimension、normalization、batch order、partial failure |
| `RERANK` | score direction/range、candidate identity、tie-break、partial result |
| `VISION_EXTRACTION` | media type、size、orientation、partial extraction、classification |
| `AUDIO_TRANSCRIPTION` | duration、language、timestamps、partial transcript |
| `CLASSIFICATION` | label set、unknown label、confidence/calibration |
| `JUDGE` | rubric version、structured verdict、abstention、position bias |

### 3.3 Conformance 失效

以下变化必须使 Profile 进入 `STALE` 或重新验证：

```text
SDK major/minor behavior change
Provider API version change
endpoint / region change
Model revision change
stream protocol change
structured output mode change
usage receipt schema change
error-code mapping change
proxy / transport implementation change
Security redaction or logging policy change
```

高风险 Role 不得把 `DECLARED`、`NON_CONFORMANT` 或过期 Profile 作为唯一候选。

## 4. 配置快照与激活生命周期

### 4.1 ModelGatewayConfigSnapshot

```text
config_snapshot_id
config_version
parent_config_version
role_routing_profile_refs
provider_definition_refs
model_definition_refs
capability_profile_refs
adapter_conformance_profile_refs
prompt_execution_binding_refs
routing_policy_refs
quota_policy_refs
health_policy_refs
circuit_policy_refs
retention_policy_refs
service_level_profile_refs
security_policy_snapshot_ref
content_hash
created_by_ref
created_at
status
```

状态：

```text
DRAFT
VALIDATING
READY
CANARY
ACTIVE
DRAINING
ROLLED_BACK
REJECTED
RETIRED
```

### 4.2 Config 激活流程

```text
Draft Config
→ Schema / Referential Validation
→ Security Compatibility Validation
→ Adapter Conformance Check
→ Offline Routing Replay
→ Canary Readiness Check
→ Activation CAS
→ Active Snapshot
→ Drain Previous Snapshot
→ Retire when no pinned Call remains
```

不变量：

1. 每个 `ModelCall` 固定一个 `config_snapshot_id`；
2. 激活使用 expected generation / CAS；
3. 新配置不能原地修改旧 Snapshot；
4. Canary 只接收被 Policy 明确允许的流量；
5. 回滚创建新的 Activation Record，不删除失败配置证据；
6. 旧配置在仍有 Call、Attempt 或 Reconciliation 引用时不能物理删除；
7. Security Epoch 变化可以使 Config 不再可用，但不改写历史 Config；
8. 配置激活不得绕过 Provider / Model lifecycle、Capability、Budget 或 Security Gate。

### 4.3 GatewayConfigActivation

```text
activation_id
config_snapshot_ref
previous_active_snapshot_ref
activation_scope
canary_assignment_ref
expected_generation
activation_status
validation_evidence_refs
readiness_snapshot_ref
rollback_of_ref
activated_at
draining_deadline_at
retired_at
```

## 5. Provider 与 Model 生命周期

### 5.1 生命周期状态

```text
DISCOVERED
DECLARED
PROBING
ENABLED
DEPRECATED
DRAINING
DISABLED
RETIRED
```

状态含义：

- `DISCOVERED`：仅发现 Provider / Model 标识，不可路由；
- `DECLARED`：定义已录入，能力尚未验证；
- `PROBING`：执行 Conformance / Capability Probe；
- `ENABLED`：允许进入候选集；
- `DEPRECATED`：不再用于新默认路由，但已有 Pin 可按 Policy 完成；
- `DRAINING`：拒绝新 Call，等待在途 Attempt / Reconcile 收口；
- `DISABLED`：立即从候选移除；在途结果按原因决定取消或隔离；
- `RETIRED`：不再运行，仅保留历史定义和证据。

### 5.2 ModelLifecycleRecord

```text
lifecycle_record_id
provider_ref
model_ref
previous_status
new_status
reason_code
trigger_ref
security_epoch
config_version
effective_at
drain_deadline_at
replacement_model_refs
created_at
```

### 5.3 Deprecation 与强制下线

正常 Deprecation：

```text
announce deprecation
→ stop new default assignments
→ update compatibility / replacement
→ canary replacement
→ drain pinned calls
→ disable
→ retire after retention conditions
```

强制下线触发：

```text
Security revocation
credential compromise
provider policy violation
critical adapter defect
systematic malformed output
unbounded duplicate billing risk
provider service termination
```

强制下线规则：

- 停止新 Routing；
- 使未 Dispatch Decision 失效；
- 请求取消在途 Attempt；
- 已返回结果按风险标记 `TAINTED` / `REVOKED`；
- 仍需记录真实 Usage 和 Provider 成本；
- Gateway 只通知 Agent Core 仲裁，不自行重写 Plan 或 RunOutcome。

## 6. 多租户隔离与公平 Admission

### 6.1 Admission 层级

```text
Global Gateway Capacity
→ Provider / Region Capacity
→ Provider Credential Scope
→ Tenant Capacity
→ Workspace Capacity
→ Run / Step Capacity
→ Operation / Role Capacity
```

每层都可以有：

```text
max_concurrency
request_rate
token_rate
cost_rate
burst_limit
queue_limit
reserved_capacity
weight
priority_class
max_wait
```

### 6.2 TenantAdmissionPolicy

```text
tenant_admission_policy_id
policy_version
tenant_id
workspace_scope
priority_class
weight
reserved_capacity
max_concurrency
request_rate_limit
token_rate_limit
cost_rate_limit
burst_limit
queue_limit
max_queue_wait
operation_overrides
role_overrides
status
```

### 6.3 Fairness 不变量

1. Tenant / Workspace 必须显式进入 Quota、Queue、Metric 和 Usage Attribution；
2. 一个租户不能占满所有 Provider 并发槽；
3. 高优先级不能绕过 Security、Budget、Residency 或 Provider Circuit；
4. Reserved capacity 未使用时能否借用必须由 Policy 明确；
5. 借用容量在原 Owner 需要时可被收回，但不能取消已 Dispatch 的普通模型调用来“抢占”；
6. Queue 顺序必须稳定、可解释，不能依赖进程本地无持久化列表；
7. 防饥饿机制必须有最大等待时间或 age boost；
8. 跨租户 Prompt、Response、Cache 和 Credential 严格隔离。

### 6.4 AdmissionQueueItem

```text
queue_item_id
model_call_id
tenant_id
workspace_id
provider_candidate_scope
operation_kind
role_ref
priority_class
base_priority
age_boost
estimated_tokens
estimated_cost
deadline_at
enqueued_at
not_before_at
queue_status
lease_owner
lease_expires_at
version
```

状态：

```text
QUEUED
LEASED
ADMITTED
DEFERRED
EXPIRED
CANCELLED
REJECTED
```

## 7. 过载、背压与降级

### 7.1 Overload Signals

```text
admission queue depth
queue wait p50 / p95 / p99
provider concurrency saturation
rate-limit rejection
quota reservation conflict
first-token latency
stream open count
usage settlement backlog
reconciliation backlog
outbox backlog
object store latency
adapter mapping error rate
```

### 7.2 OverloadState

```text
NORMAL
ELEVATED
SATURATED
SHEDDING
RECOVERING
```

### 7.3 背压顺序

```text
Reject invalid / expired requests
→ Stop non-essential probes
→ Reduce experiment traffic
→ Disable optional streaming detail retention
→ Defer low-priority batch work
→ Queue within deadline and fairness policy
→ Route compatible fallback
→ Deterministic load shedding
```

禁止行为：

- 过载时跳过 Security、Schema Validation、Usage 或 Audit；
- 通过隐藏 SDK retry 放大负载；
- 无限增长内存 Queue；
- 把超时 Call 留在 Queue 中继续 Dispatch；
- 为提高成功率把高质量 Role 静默降级为不满足 required capability 的模型；
- 将丢弃请求计为 Provider failure。

### 7.4 LoadSheddingDecision

```text
load_shedding_decision_id
model_call_id
overload_state_ref
priority_class
fairness_policy_ref
selected_action
reason_codes
alternative_candidates
retry_after_at
created_at
```

动作：

```text
ADMIT
QUEUE
DEFER
FALLBACK
REJECT_OVERLOADED
REJECT_DEADLINE
```

## 8. Cache 与结果复用

### 8.1 三类 Cache 必须分开

```text
Provider-managed Prompt Cache
    Provider 内部缓存输入 token / prefix

Gateway Transport / Metadata Cache
    Catalog、Capability、Pricing、Health 等有 TTL 的读缓存

Gateway Result Cache
    对完整模型结果的复用；默认关闭，必须显式 Policy 才能开启
```

### 8.2 Provider Prompt Cache

Provider Prompt Cache 仍属于真实 Provider Attempt：

- Routing、Security、Quota 和 Budget 仍需通过；
- Provider 返回 cached input tokens 时写入 `UsageReceipt`；
- Cache hit 不等于本地 Result Cache hit；
- Provider cache key 和 retention 未必可见，Capability Profile 必须表达不确定性；
- 机密数据是否允许 Provider cache 由 Security Decision 决定；
- Credential、region、model revision 或 security policy 变化时不得假定 cache 可复用。

### 8.3 GatewayResultCachePolicy

```text
result_cache_policy_id
policy_version
enabled
allowed_operation_kinds
allowed_roles
allowed_data_classifications
scope_type
max_age
required_determinism
temperature_constraint
security_epoch_binding
prompt_binding_version_binding
model_revision_binding
output_schema_hash_binding
retention_policy_ref
status
```

默认规则：

1. Generation、Planner、Critic、Tool Proposal 和 Final Synthesis 默认不启用 Result Cache；
2. 可复用场景更适合 deterministic classification、embedding 或经领域 Owner 批准的 extraction；
3. Cache key 至少包含 tenant/workspace scope、operation、model revision、prompt/input hash、schema、security epoch、config version 和 relevant policy version；
4. 跨租户 cache sharing 默认禁止；
5. Cache hit 产生独立 `ModelCacheReuseReceipt`，不能伪装成 Provider Attempt；
6. Cache hit 不产生 Provider Usage，但可以产生内部 attribution；
7. Security Revocation、ResultValidity 变化、模型退休或输入删除必须使相关 entry 不可服务；
8. 缓存内容仍受 Retention、Deletion 和 Legal Hold 约束。

### 8.4 ModelCacheReuseReceipt

```text
cache_reuse_receipt_id
model_call_id
cache_entry_ref
cache_policy_ref
source_response_ref
source_model_revision
source_security_epoch
cache_key_hash
scope_ref
reused_at
validity_status
```

## 9. Operations Command 与人工干预

### 9.1 禁止直接改数据库

以下操作必须通过版本化 `ModelGatewayOperationalCommand`：

```text
ENABLE_PROVIDER
DEPRECATE_PROVIDER
DRAIN_PROVIDER
DISABLE_PROVIDER
ENABLE_MODEL
DEPRECATE_MODEL
DRAIN_MODEL
DISABLE_MODEL
FORCE_CIRCUIT_OPEN
RELEASE_FORCED_CIRCUIT
ROTATE_CONFIG
ROLLBACK_CONFIG
START_CONFORMANCE_PROBE
START_RECONCILIATION
CANCEL_CALL
QUARANTINE_ADAPTER_VERSION
```

### 9.2 ModelGatewayOperationalCommand

```text
operational_command_id
command_type
target_ref
requested_by_ref
authorization_decision_ref
approval_ref
security_epoch
expected_generation
reason_code
parameters_hash
status
created_at
accepted_at
completed_at
failure_ref
result_receipt_ref
```

状态：

```text
REQUESTED
AUTHORIZED
APPROVAL_PENDING
ACCEPTED
EXECUTING
SUCCEEDED
FAILED
CANCELLED
EXPIRED
```

规则：

1. 运维命令是 Command，不是事实成功；
2. Command 执行结果形成独立 Receipt / Lifecycle Record；
3. 高风险 Disable、Credential、跨租户或 Retention 操作需要 Security Authorization 和 Mandatory Audit；
4. Break-glass 只能缩短响应路径，不能绕过审计和事后复核；
5. expected generation 冲突时拒绝，不能覆盖并发变更；
6. 人工强制 Circuit 需要 reason、expiry 和解除条件；
7. Command 不得直接批准 Agent Tool Effect 或修改 AgentRun。

## 10. Retention、Deletion 与 Legal Hold

### 10.1 数据分类

| 数据 | 默认性质 | 关键约束 |
| --- | --- | --- |
| Prompt / Input | 敏感业务数据 | Security classification、object encryption、最小保留 |
| Response | 模型结果 | validity、consumer refs、删除传播 |
| Stream Chunk | 高容量临时数据 | 聚合优先、可短期保留 |
| Raw Provider Payload | Debug / reconcile evidence | 强访问控制、短期保留 |
| UsageReceipt | 财务和审计事实 | append-only、更正记录、较长保留 |
| Failure / Attempt | 运行证据 | 可审计、脱敏、支持故障分析 |
| Routing / Config / Lifecycle | 决策证据 | 版本化、不可原地覆盖 |
| AuditEvent | 合规事实 | 由 Security / Observability retention 决定 |

### 10.2 ModelDataRetentionBinding

```text
retention_binding_id
aggregate_type
aggregate_ref
data_classification
retention_policy_ref
legal_hold_refs
payload_ref
payload_hash
expires_at
purge_eligible_at
created_at
```

### 10.3 删除状态机

```text
REQUESTED
AUTHORIZED
LEGAL_HOLD_CHECKING
TOMBSTONED
QUERY_VISIBILITY_REVOKED
OBJECT_DELETE_PENDING
OBJECT_DELETING
VERIFYING
COMPLETED
BLOCKED_BY_HOLD
FAILED
```

删除规则：

1. 领域 Tombstone 与对象物理删除分离；
2. Query visibility 撤销优先于后台物理清理；
3. Usage、Audit、Billing 和 Security 事实可依据法规保留，但必须移除不必要的 Prompt / Response 内容；
4. Legal Hold 优先于 purge；
5. Object Store delete receipt 只证明物理操作，不自动证明所有 Projection / Cache 已清理；
6. Cache、Search Projection 和外部 Sink 的删除传播必须有目标清单和 Verification；
7. 删除失败不得恢复内容对普通查询可见；
8. content hash 可以在不保留明文的前提下支持完整性和去重证明，但是否保留由 Policy 决定。

### 10.4 ModelDataDeletionRecord

```text
deletion_record_id
request_ref
target_refs
retention_binding_refs
legal_hold_check_ref
visibility_revocation_ref
physical_delete_receipts
cache_invalidation_receipts
projection_delete_receipts
verification_ref
status
created_at
completed_at
```

## 11. SLI、SLO、Readiness 与 Degradation

### 11.1 ModelGatewayServiceLevelProfile

```text
service_level_profile_id
profile_version
scope_type
scope_ref
operation_kind
role_ref
availability_target
admission_latency_target
first_token_latency_target
total_latency_target
structured_validity_target
unknown_execution_limit
usage_settlement_lag_target
reconciliation_backlog_limit
error_budget_policy_ref
measurement_window
status
```

### 11.2 必须测量的 SLI

```text
valid request admission availability
model call selected-response success rate
provider attempt success rate
queue wait latency
first-token latency
total latency
stream completion rate
structured output first-pass validity
repair success rate
unknown execution rate
reconciliation age
usage receipt completeness
usage settlement lag
estimated vs settled token/cost error
fallback and escalation rate
security denial and stale-epoch rejection
adapter mapping warning rate
config rollback rate
```

指标解释：

- Call success 与 Attempt success 分开；
- Provider failure 与 Security denial、client cancellation、load shedding 分开；
- SLO 按 Operation / Role / Tenant tier 分层，不能用全局平均掩盖关键路径；
- 没有固定 workload、统计窗口和完整数据时只能写 `measurement blocked`；
- 成功率高不代表答案质量、Groundedness 或安全性已证明。

### 11.3 GatewayReadinessSnapshot

```text
readiness_snapshot_id
config_snapshot_ref
provider_readiness
model_readiness
adapter_conformance_readiness
security_dependency_readiness
persistence_readiness
outbox_readiness
usage_settlement_readiness
reconciliation_readiness
capacity_readiness
measurement_completeness
status
reason_codes
captured_at
expires_at
```

状态：

```text
READY
DEGRADED
NOT_READY
UNKNOWN
```

Readiness 不变量：

1. 无证据不得默认 READY；
2. 只有 Mock Provider 可用不能声明生产 Ready；
3. Usage / Audit / Reconciliation 依赖不可用时不能只看生成成功；
4. 非关键 Eval worker 不可用可以降级，但不能污染生产调用事实；
5. Security 或 Secret 依赖失败默认 NOT_READY / fail-closed；
6. Readiness 只决定是否接收流量，不把模块提升为 production ready 文档状态。

## 12. 兼容性、SDK 与 Provider API 升级

### 12.1 ModelGatewayCompatibilityEntry

```text
compatibility_entry_id
entry_version
adapter_ref
provider_api_version
sdk_version
model_revision
operation_kind
prompt_binding_version_range
output_contract_version_range
known_incompatibilities
required_migrations
status
verified_at
evidence_refs
```

状态：

```text
SUPPORTED
SUPPORTED_WITH_LIMITATIONS
CANARY_ONLY
INCOMPATIBLE
UNKNOWN
```

### 12.2 升级规则

1. SDK / API 升级不得与业务调用代码同时无证据切换；
2. 新旧 Adapter Version 可以并行存在，通过 Config Snapshot 指定；
3. Canary 必须固定流量 assignment，避免实验漂移；
4. Mapping、Error、Usage 和 Streaming 的变化必须重新跑 Conformance；
5. Unknown enum / event 不得因“向前兼容”直接当成功；
6. 回滚必须保留新版本产生的 Attempt / Usage / Failure 事实；
7. Provider API sunset 需要在 deadline 前完成替代验证，不能依赖最后时刻强制切换；
8. Public cross-module Contract 采用版本和兼容窗口，不暴露 SDK 类型。

## 13. Eval、Judge 与实验治理

### 13.1 Judge 调用仍走 Model Gateway

Eval 的 `JUDGE` 调用：

- 使用独立 Role / Operation / Prompt Execution Binding；
- 经过 Security、Budget、Quota、Usage 和 Trace；
- 产生普通 `ModelCall` / `Attempt` / `UsageReceipt`；
- 不能因为属于 Eval 就直接构造 Provider SDK；
- Judge 结果属于 Eval Proposal / Evidence，不直接改变生产 Routing Policy。

### 13.2 防循环证明

以下结论不成立：

```text
模型 A 判断模型 A 很好
→ 因而模型 A 已被证明质量优秀
```

Eval 至少记录：

```text
judge model definition / revision
judge prompt / rubric version
case set version
candidate output ordering
randomization / position control
human calibration refs
inter-judge agreement
abstention rate
known bias profile
```

高风险质量结论需要：

- 多 Judge 或人工校准；
- 固定 Case Set；
- Blind / randomized candidate order；
- 失败 bucket；
- Confidence / Abstention；
- 与业务确定性检查组合。

### 13.3 Routing Experiment

`ModelRoutingExperimentAssignment`：

```text
assignment_id
experiment_ref
unit_type
unit_ref
variant_ref
assignment_hash
random_seed_ref
security_eligibility_ref
budget_eligibility_ref
assigned_at
expires_at
```

规则：

1. Security、Residency、Capability、Budget 和 Deadline Gate 先于实验；
2. Assignment 可重放且 sticky scope 明确；
3. 实验不得让同一逻辑 Call 同时对多个 Provider 产生未授权重复成本；
4. Shadow call 必须有独立 Budget、Security 和 Usage，结果不得进入业务输出；
5. 实验 Metric 由 Observability / Eval 计算，Gateway 只拥有 assignment 和调用事实；
6. 未达到完整样本和比较条件时不得自动激活获胜配置。

## 14. 目标存储扩展

逻辑 schema 仍可使用 `model_gateway`：

| 对象 | 目标表 | 关键约束 / 索引 |
| --- | --- | --- |
| Adapter | `model_provider_adapters` | `UNIQUE(adapter_id, adapter_version)` |
| Conformance Profile | `model_adapter_conformance_profiles` | adapter/api/sdk/operation/version unique |
| Conformance Run | `model_adapter_conformance_runs` | suite/status/started_at index |
| Config Snapshot | `model_gateway_config_snapshots` | `UNIQUE(config_version)`；content hash |
| Config Activation | `model_gateway_config_activations` | active scope 条件唯一；generation CAS |
| Lifecycle | `model_lifecycle_records` | provider/model/status/effective_at index |
| Tenant Admission | `model_tenant_admission_policies` | tenant/workspace/version unique |
| Queue Item | `model_admission_queue_items` | status/priority/not_before/deadline indexes |
| Load Shedding | `model_load_shedding_decisions` | call/reason/created_at index |
| Cache Policy | `model_result_cache_policies` | scope/version/status index |
| Cache Receipt | `model_cache_reuse_receipts` | call/cache key/source response indexes |
| Operational Command | `model_operational_commands` | command/status/target/created_at indexes |
| Retention Binding | `model_data_retention_bindings` | aggregate/purge_eligible/legal hold indexes |
| Deletion | `model_data_deletion_records` | request/status/created_at index |
| SLO Profile | `model_service_level_profiles` | scope/operation/role/version unique |
| Readiness | `model_readiness_snapshots` | config/status/captured_at index |
| Compatibility | `model_compatibility_entries` | adapter/api/sdk/model/operation composite |
| Experiment Assignment | `model_routing_experiment_assignments` | experiment/unit unique；assignment hash |

共同约束：

```text
tenant / workspace scope
UTC timestamp
append-only decision and receipt
state CHECK constraints
optimistic version / generation / fencing
no plaintext Secret
large payload via encrypted object ref
retention / legal hold binding
outbox for source-domain events
```

## 15. 目标代码边界扩展

```text
src/backend/zuno/model_gateway/
├── conformance/
│   ├── contracts.py
│   ├── suites.py
│   ├── runner.py
│   └── evidence.py
├── control_plane/
│   ├── config_snapshot.py
│   ├── activation.py
│   ├── compatibility.py
│   └── experiment.py
├── lifecycle/
│   ├── provider_lifecycle.py
│   ├── model_lifecycle.py
│   └── drain.py
├── admission/
│   ├── fairness.py
│   ├── queue.py
│   ├── overload.py
│   └── load_shedding.py
├── caching/
│   ├── policy.py
│   ├── key.py
│   └── receipts.py
├── operations/
│   ├── commands.py
│   ├── readiness.py
│   ├── service_level.py
│   └── reconciliation.py
├── retention/
│   ├── binding.py
│   ├── deletion.py
│   └── verification.py
└── adapters/
    ├── base.py
    ├── openai_adapter.py
    ├── anthropic_adapter.py
    ├── gemini_adapter.py
    └── local_adapter.py
```

这些是目标模块边界，不要求每个目录成为独立进程或服务。

## 16. Operations Failure Decision Matrix

| Failure | 状态变化 | 默认恢复 | Owner | 禁止行为 |
| --- | --- | --- | --- | --- |
| Hidden SDK Retry | Attempt accounting invalid | quarantine adapter version | Gateway Adapter | 忽略额外成本 |
| Adapter Mapping Drift | Conformance `STALE/NON_CONFORMANT` | canary old/new mapping | Gateway | 把 unknown enum 当成功 |
| Config Activation Race | activation CAS conflict | reload active generation | Gateway Control Plane | last-write-wins 覆盖 |
| Canary Regression | Config `CANARY → REJECTED` | retain previous active | Gateway | 自动全量切流 |
| Provider Deprecation | lifecycle `DEPRECATED` | replacement canary / drain | Gateway | 新默认路由继续增加 |
| Emergency Disable | lifecycle `DISABLED` | cancel/isolate/replan proposal | Security + Gateway | 删除历史事实 |
| Noisy Tenant | queue / overload rises | fairness limits / shed tenant scope | Gateway | 全局随机丢请求 |
| Queue Deadline Expired | item `EXPIRED` | return deadline failure | Gateway | 过期后 Dispatch |
| Overload Saturation | state `SHEDDING` | deterministic shed/fallback | Gateway | 跳过安全和 Usage |
| Cross-tenant Cache Attempt | cache denied | miss + security violation event | Security + Gateway | 返回他租户结果 |
| Stale Cache after Revocation | receipt invalid | invalidate / validity change | Gateway | 继续服务旧结果 |
| Provider Cache Usage Mismatch | usage pending/corrected | reconcile provider receipt | Gateway | 写 0 成本 |
| Direct DB Operational Change | command evidence missing | reject/reconcile/admin alert | Gateway | 接受无审计改动 |
| Legal Hold Active | deletion `BLOCKED_BY_HOLD` | retain and report | Security + Infrastructure | 强制 purge |
| Object Delete Partial Failure | deletion `FAILED/VERIFYING` | retry physical targets | Infrastructure | 恢复查询可见性 |
| Readiness Evidence Missing | readiness `UNKNOWN` | stop/limit admission | Gateway | 默认 READY |
| SDK Upgrade Incompatible | compatibility `INCOMPATIBLE` | rollback adapter/config | Gateway | 扩大 canary |
| Judge Circularity | eval evidence invalid | require independent calibration | Observability & Eval | 自动提升质量结论 |
| Experiment Assignment Drift | comparison invalid | quarantine experiment result | Gateway + Eval | 合并不可比样本 |
| Drain Deadline Exceeded | lifecycle remains `DRAINING` | cancel/reconcile/escalate ops | Gateway | 直接 Retire 丢失 Attempt |

## 17. Requirement Registry

| Requirement | 规范 | Runtime Control | Unit | Integration | Fault | E2E | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ARCH-MODEL-OPS-001` | Gateway 必须区分 Execution、Control、Operations、Evidence Plane | `RC-MODEL-OPS-001` | `MODEL-OPS-001-UT` | `MODEL-OPS-001-IT` | `MODEL-OPS-001-FT` | `MODEL-OPS-001-E2E` | `EV-MODEL-OPS-001` |
| `ARCH-MODEL-OPS-002` | 每个 Provider 必须通过版本化 Adapter Contract | `RC-MODEL-OPS-002` | `MODEL-OPS-002-UT` | `MODEL-OPS-002-IT` | `MODEL-OPS-002-FT` | `MODEL-OPS-002-E2E` | `EV-MODEL-OPS-002` |
| `ARCH-MODEL-OPS-003` | Adapter 必须显式核算 SDK retry / timeout / cancellation | `RC-MODEL-OPS-003` | `MODEL-OPS-003-UT` | `MODEL-OPS-003-IT` | `MODEL-OPS-003-FT` | `MODEL-OPS-003-E2E` | `EV-MODEL-OPS-003` |
| `ARCH-MODEL-OPS-004` | Adapter Conformance 必须按 Operation 验证 | `RC-MODEL-OPS-004` | `MODEL-OPS-004-UT` | `MODEL-OPS-004-IT` | `MODEL-OPS-004-FT` | `MODEL-OPS-004-E2E` | `EV-MODEL-OPS-004` |
| `ARCH-MODEL-OPS-005` | SDK/API/Model Revision 变化必须使 Conformance 重新评估 | `RC-MODEL-OPS-005` | `MODEL-OPS-005-UT` | `MODEL-OPS-005-IT` | `MODEL-OPS-005-FT` | `MODEL-OPS-005-E2E` | `EV-MODEL-OPS-005` |
| `ARCH-MODEL-OPS-006` | 所有调用必须固定不可变 Config Snapshot | `RC-MODEL-OPS-006` | `MODEL-OPS-006-UT` | `MODEL-OPS-006-IT` | `MODEL-OPS-006-FT` | `MODEL-OPS-006-E2E` | `EV-MODEL-OPS-006` |
| `ARCH-MODEL-OPS-007` | Config Activation 必须使用 Validation、Canary、CAS、Drain 和 Rollback | `RC-MODEL-OPS-007` | `MODEL-OPS-007-UT` | `MODEL-OPS-007-IT` | `MODEL-OPS-007-FT` | `MODEL-OPS-007-E2E` | `EV-MODEL-OPS-007` |
| `ARCH-MODEL-OPS-008` | Provider / Model 必须有完整生命周期 | `RC-MODEL-OPS-008` | `MODEL-OPS-008-UT` | `MODEL-OPS-008-IT` | `MODEL-OPS-008-FT` | `MODEL-OPS-008-E2E` | `EV-MODEL-OPS-008` |
| `ARCH-MODEL-OPS-009` | 强制下线必须停止新路由并保留历史事实 | `RC-MODEL-OPS-009` | `MODEL-OPS-009-UT` | `MODEL-OPS-009-IT` | `MODEL-OPS-009-FT` | `MODEL-OPS-009-E2E` | `EV-MODEL-OPS-009` |
| `ARCH-MODEL-OPS-010` | Admission 必须按 Provider/Tenant/Workspace/Run/Operation 分层 | `RC-MODEL-OPS-010` | `MODEL-OPS-010-UT` | `MODEL-OPS-010-IT` | `MODEL-OPS-010-FT` | `MODEL-OPS-010-E2E` | `EV-MODEL-OPS-010` |
| `ARCH-MODEL-OPS-011` | 公平调度必须防 noisy neighbor 和 starvation | `RC-MODEL-OPS-011` | `MODEL-OPS-011-UT` | `MODEL-OPS-011-IT` | `MODEL-OPS-011-FT` | `MODEL-OPS-011-E2E` | `EV-MODEL-OPS-011` |
| `ARCH-MODEL-OPS-012` | Admission Queue 必须持久化、可过期、可恢复 | `RC-MODEL-OPS-012` | `MODEL-OPS-012-UT` | `MODEL-OPS-012-IT` | `MODEL-OPS-012-FT` | `MODEL-OPS-012-E2E` | `EV-MODEL-OPS-012` |
| `ARCH-MODEL-OPS-013` | 过载必须通过确定性背压和 Load Shedding | `RC-MODEL-OPS-013` | `MODEL-OPS-013-UT` | `MODEL-OPS-013-IT` | `MODEL-OPS-013-FT` | `MODEL-OPS-013-E2E` | `EV-MODEL-OPS-013` |
| `ARCH-MODEL-OPS-014` | 过载不得跳过 Security、Usage、Validation 或 Audit | `RC-MODEL-OPS-014` | `MODEL-OPS-014-UT` | `MODEL-OPS-014-IT` | `MODEL-OPS-014-FT` | `MODEL-OPS-014-E2E` | `EV-MODEL-OPS-014` |
| `ARCH-MODEL-OPS-015` | Provider Prompt Cache 与 Gateway Result Cache 必须分离 | `RC-MODEL-OPS-015` | `MODEL-OPS-015-UT` | `MODEL-OPS-015-IT` | `MODEL-OPS-015-FT` | `MODEL-OPS-015-E2E` | `EV-MODEL-OPS-015` |
| `ARCH-MODEL-OPS-016` | Result Cache 默认关闭并严格绑定租户、安全和版本 | `RC-MODEL-OPS-016` | `MODEL-OPS-016-UT` | `MODEL-OPS-016-IT` | `MODEL-OPS-016-FT` | `MODEL-OPS-016-E2E` | `EV-MODEL-OPS-016` |
| `ARCH-MODEL-OPS-017` | 运维变更必须通过 OperationalCommand 而非直接改库 | `RC-MODEL-OPS-017` | `MODEL-OPS-017-UT` | `MODEL-OPS-017-IT` | `MODEL-OPS-017-FT` | `MODEL-OPS-017-E2E` | `EV-MODEL-OPS-017` |
| `ARCH-MODEL-OPS-018` | 高风险运维命令必须授权、审批和 Mandatory Audit | `RC-MODEL-OPS-018` | `MODEL-OPS-018-UT` | `MODEL-OPS-018-IT` | `MODEL-OPS-018-FT` | `MODEL-OPS-018-E2E` | `EV-MODEL-OPS-018` |
| `ARCH-MODEL-OPS-019` | Prompt/Response/Stream/Usage 必须有独立 Retention Binding | `RC-MODEL-OPS-019` | `MODEL-OPS-019-UT` | `MODEL-OPS-019-IT` | `MODEL-OPS-019-FT` | `MODEL-OPS-019-E2E` | `EV-MODEL-OPS-019` |
| `ARCH-MODEL-OPS-020` | 删除必须先撤销可见性并完成跨存储 Verification | `RC-MODEL-OPS-020` | `MODEL-OPS-020-UT` | `MODEL-OPS-020-IT` | `MODEL-OPS-020-FT` | `MODEL-OPS-020-E2E` | `EV-MODEL-OPS-020` |
| `ARCH-MODEL-OPS-021` | Legal Hold 必须阻止物理 Purge | `RC-MODEL-OPS-021` | `MODEL-OPS-021-UT` | `MODEL-OPS-021-IT` | `MODEL-OPS-021-FT` | `MODEL-OPS-021-E2E` | `EV-MODEL-OPS-021` |
| `ARCH-MODEL-OPS-022` | SLI/SLO 必须区分 Call、Attempt、Operation、Role 和 Tenant tier | `RC-MODEL-OPS-022` | `MODEL-OPS-022-UT` | `MODEL-OPS-022-IT` | `MODEL-OPS-022-FT` | `MODEL-OPS-022-E2E` | `EV-MODEL-OPS-022` |
| `ARCH-MODEL-OPS-023` | 无完整依赖证据时 Readiness 不得为 READY | `RC-MODEL-OPS-023` | `MODEL-OPS-023-UT` | `MODEL-OPS-023-IT` | `MODEL-OPS-023-FT` | `MODEL-OPS-023-E2E` | `EV-MODEL-OPS-023` |
| `ARCH-MODEL-OPS-024` | SDK/API 升级必须支持并行版本、Canary 和 Rollback | `RC-MODEL-OPS-024` | `MODEL-OPS-024-UT` | `MODEL-OPS-024-IT` | `MODEL-OPS-024-FT` | `MODEL-OPS-024-E2E` | `EV-MODEL-OPS-024` |
| `ARCH-MODEL-OPS-025` | Unknown Version / Enum / Event 必须 fail-closed 或 quarantine | `RC-MODEL-OPS-025` | `MODEL-OPS-025-UT` | `MODEL-OPS-025-IT` | `MODEL-OPS-025-FT` | `MODEL-OPS-025-E2E` | `EV-MODEL-OPS-025` |
| `ARCH-MODEL-OPS-026` | Judge 调用必须通过 Gateway 并记录独立配置和成本 | `RC-MODEL-OPS-026` | `MODEL-OPS-026-UT` | `MODEL-OPS-026-IT` | `MODEL-OPS-026-FT` | `MODEL-OPS-026-E2E` | `EV-MODEL-OPS-026` |
| `ARCH-MODEL-OPS-027` | Eval 不得使用单一自评形成循环质量证明 | `RC-MODEL-OPS-027` | `MODEL-OPS-027-UT` | `MODEL-OPS-027-IT` | `MODEL-OPS-027-FT` | `MODEL-OPS-027-E2E` | `EV-MODEL-OPS-027` |
| `ARCH-MODEL-OPS-028` | Routing Experiment 必须先通过强制 Gate 且可重放 | `RC-MODEL-OPS-028` | `MODEL-OPS-028-UT` | `MODEL-OPS-028-IT` | `MODEL-OPS-028-FT` | `MODEL-OPS-028-E2E` | `EV-MODEL-OPS-028` |

## 18. 强制 Fault / Recovery 场景

实现证据至少覆盖：

```text
SDK hidden retry creates extra provider charge
Provider API introduces unknown finish reason
Adapter mapping changes usage token semantics
Config activation CAS race
Canary regression after partial traffic
Rollback while old calls remain pinned
Provider deprecated with active long stream
Security emergency disables a model mid-call
Noisy tenant saturates provider concurrency
High-priority tenant starves ordinary queue
Queued call expires before admission
Overload shedding with Security and Usage still enforced
Cross-tenant result-cache key collision attempt
Security Epoch changes after cache entry creation
Provider prompt-cache usage disagrees with estimate
Operational direct database mutation is detected
Forced circuit command expires without release
Legal Hold blocks prompt deletion
Object deletion succeeds but cache invalidation fails
Readiness lacks usage-settlement dependency evidence
SDK upgrade breaks stream event ordering
Unknown Provider event reaches adapter
Judge model exhibits position bias
Routing experiment assignment changes between retries
Drain deadline expires with UNKNOWN attempts
```

## 19. Target 到 Current 的证据

本附录从 Target 变为 Current，至少需要：

```text
Provider Adapter implementation
Adapter conformance suite and evidence
Config Snapshot / Activation implementation
Provider / Model lifecycle persistence
Tenant fairness and durable admission queue
Overload / backpressure fault tests
Cache isolation and invalidation tests
OperationalCommand authorization and audit tests
Retention / deletion / legal-hold integration tests
SLI completeness and measured SLO windows
Readiness dependency failure tests
SDK/API canary and rollback evidence
Judge calibration and experiment comparability evidence
PostgreSQL Migration
Trace / Audit / Eval evidence
```

推荐状态：

```text
design available
cross-module alignment in progress
implementation not established
measurement blocked
quality not yet proven
production ready not established
```
