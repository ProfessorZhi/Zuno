# 04 Model Gateway：Wave 1 Contract Freeze 附录

updated: 2026-07-13
status: normative-target-module-addendum
module_number: 04
formal_path: `docs/modules/04-model-gateway-contract-freeze.md`
agent_mirror: `.agent/modules/04-model-gateway-contract-freeze.md`
parent_document: `docs/modules/04-model-gateway.md`
dependency_baseline_sha: `729e439e29deadc101c5687fc47125104e62e2c1`

> 本附录补充并细化 `docs/modules/04-model-gateway.md` 中与跨模块 Contract、Model Operation、ModelCall 聚合、Budget / Usage / Quota、一致性、事件、Streaming、Routing Replay、Capability 生命周期和 Result Validity 相关的 Target 设计。
>
> 本附录不声明任何新运行时代码、Migration、Provider 集成、Trace、Eval 或生产证据已经存在。Current、Gap、Measurement 和 Production Readiness 仍以当前代码、测试、Migration、运行证据和 `docs/status/production-readiness.md` 为事实源。

## 0. 规范优先级与适用范围

规范读取顺序：

```text
全局架构原则
→ Agent Core 正式 Target Contract
→ 04 Model Gateway 主文档
→ 本 Contract Freeze 附录
→ 已确认的 Wave 1 跨模块 Registry / ADR
→ Program
→ 代码、Migration、测试与运行证据
```

本附录细化主文档以下主题：

```text
Ownership 与跨模块 Contract
Model Role / Operation / Provider 分离
ModelCall 与 ModelCallAttempt 状态关系
Budget / Quota / Usage 的崩溃和结算语义
Model Gateway 领域事件目录
Provider / Gateway / Product 三层 Streaming
Routing 的可解释与确定性重放
Capability Profile 生命周期
ResultValidity 传播
实现前 Contract Freeze Gate
```

发生冲突时：

1. 已合并的全局 Contract Registry 或 ADR 高于本附录；
2. 在尚未存在已合并共享 Contract 时，本附录对 Model Gateway 内部设计具有细化优先级；
3. PR #17、#19、#20 仍是 `Parallel Proposal`，其对象名称只作为协调输入，不能写成 Current；
4. 本附录不能改变 Agent Core 的 Single Controller、Plan、Trace、Budget、AnswerPolicy 和 RunOutcome 原则。

## 1. Wave 1 协调快照

本附录审阅的并行提案快照：

| 模块 | Draft PR | Reviewed Head | 协调状态 |
| --- | --- | --- | --- |
| 11 Infrastructure | `#17` | `2a02a91108b6e713f5c04639c64c6745ccd485cc` | `ALIGNED_PENDING_FIELDS` |
| 09 Security | `#19` | `44048c964877b0f4276f09e9984bf97191728c9e` | `ALIGNED_PENDING_FIELDS` |
| 10 Observability & Eval | `#20` | `cc59913cc891c2b5325d214d03f437c090bd1329` | `ALIGNED_PENDING_FIELDS` |
| 04 Model Gateway | `#18` | 本附录所在 Head | 本模块 Target 补充 |

这些 SHA 仅用于说明审阅输入，不把并行提案提升为已确认共享 Contract。合并前仍需集中字段级审计。

## 2. Canonical Ownership 收口

### 2.1 Security 决策只能有一个 Owner

`ModelSecurityDecision` 是 Security 拥有、面向模型调用的不可变 Decision View。它不是 Gateway 重新计算出的第二份授权事实。

```text
Security owns
    AuthorizationDecision
    EffectiveSecurityPolicySnapshot
    RedactionDecision
    SecretAccessDecision
    SecurityEpoch
    ModelSecurityDecision

Model Gateway consumes
    ModelSecurityDecisionRef
    and performs deterministic admission enforcement
```

建议字段：

```text
model_security_decision_id
contract_version
tenant_id
workspace_id
principal_context_ref
authorization_decision_ref
effective_policy_snapshot_ref
redaction_decision_ref
secret_access_decision_ref
security_epoch
allowed_provider_refs
allowed_model_refs
data_classification
residency_constraints
cross_border_allowed
credential_scope_ref
purpose_limit
retention_constraints
mandatory_audit_requirement_ref
issued_at
expires_at
decision_hash
```

Gateway 必须：

- 验证 Decision hash、expiry、tenant/workspace、purpose、Security Epoch；
- 在 Routing 和每次 Dispatch 前检查 Provider / Model allowlist；
- 固定 `ModelSecurityDecisionRef` 到 Routing 和 Attempt；
- 对 revoke、stale epoch 和 credential scope 变化 fail-closed；
- 只保存 Security 决策引用，不修改授权、脱敏或 Credential Scope 结论。

Gateway 不得：

- 根据 Provider 价格或健康情况扩大 allowlist；
- 自行降低数据等级或 Residency 要求；
- 将 Prompt redaction 失败解释为可选 warning；
- 以旧 Credential 或全局 Key 绕过 `SecretAccessDecision`。

### 2.2 Infrastructure 只拥有物理能力和执行 Receipt

```text
Infrastructure owns
    ProviderConnectionFactory port implementation
    SecretLease delivery
    Transaction / UoW primitive
    UTC / monotonic / authoritative clock
    Transport timeout and cancellation primitive
    CAS / generation / fencing primitive
    encrypted object storage
    physical persistence and recovery

Model Gateway owns
    Provider definition semantics
    ModelRoutingDecision
    ModelCall and ModelCallAttempt
    QuotaReservation semantics
    UsageReceipt semantics
    ProviderHealth and CircuitBreaker
    CancellationReceipt semantics
    reconciliation decisions
```

以下等价关系禁止成立：

```text
Transport request accepted != ModelCallAttempt succeeded
Queue ACK != Usage settled
Database commit != Provider request completed
Cancellation requested != Cancellation confirmed
Object stored != ModelResponse valid
```

### 2.3 Observability 不成为调用事实 Owner

```text
Model Gateway produces source-domain events
Observability owns TelemetryEnvelope ingest and projections
Observability accepts immutable AuditEvent where policy requires
Infrastructure provides durable Outbox / Inbox / Store primitives
Security defines redaction and mandatory audit requirements
```

Observability 可以检测缺口、重复、乱序和 delivery failure，但不能重写：

```text
ModelRoutingDecision
ModelCallAttempt
UsageReceipt
ProviderHealth
CircuitBreakerState
ModelResultValidity
```

## 3. Model Role、Model Operation、Provider 和 Model 四维分离

### 3.1 ModelRoleContract

`ModelRoleContract` 表达模型在 Agent 控制流程中的业务职责，由 Agent Core 或对应领域模块拥有语义定义。

```text
role_id
role_version
purpose
allowed_result_kinds
required_quality_tier
risk_tier
acceptance_policy_ref
control_semantics_ref
active_from
active_to
status
```

正式角色保持：

```text
TASK_ANALYZER
PLANNER
PLAN_REPAIR
EXECUTOR_FAST
EXECUTOR_REASONING
QUERY_REWRITER
EXTRACTOR
CRITIC
SYNTHESIZER
FINAL_CRITIC
TOOL_CALL
```

### 3.2 ModelRoleRoutingProfile

Gateway 拥有 `ModelRoleRoutingProfile`，负责把 Role 的执行要求映射到模型候选，不改变 Role 的业务语义。

```text
role_routing_profile_id
profile_version
role_ref
allowed_operation_kinds
required_capabilities
preferred_capabilities
latency_class
cost_class
same_model_retry_policy_ref
provider_fallback_policy_ref
role_escalation_policy_ref
prompt_execution_binding_policy_ref
active_from
active_to
status
```

禁止：

```text
Gateway 修改 PLANNER 的职责
Gateway 把 CRITIC 变成最终业务批准者
运维路由配置改变 Agent Core 控制语义
ModelRoleContract 保存 Provider Secret 或 SDK Client
```

### 3.3 ModelOperationKind

Role 回答“为什么调用”；Operation 回答“执行何种模型操作”。两者必须分别版本化。

```text
TEXT_GENERATION
STRUCTURED_GENERATION
EMBEDDING
RERANK
VISION_EXTRACTION
AUDIO_TRANSCRIPTION
CLASSIFICATION
JUDGE
```

规则：

- `CRITIC` 或 `FINAL_CRITIC` 通常使用 `JUDGE` 或 `STRUCTURED_GENERATION`；
- `QUERY_REWRITER` 通常使用 `TEXT_GENERATION` 或 `STRUCTURED_GENERATION`；
- Knowledge / Memory 的向量生成使用 `EMBEDDING`，不得伪装成 Agent Role；
- Knowledge 检索排序使用 `RERANK`，其 score 语义必须版本化；
- VLM 抽取使用 `VISION_EXTRACTION`；
- Operation 不能授权 Tool 副作用或发布最终答案。

### 3.4 Operation-specific Request / Result

公共 Envelope 统一，但 Payload 必须按 Operation 区分：

```text
GenerationRequest / GenerationResult
StructuredGenerationRequest / StructuredGenerationResult
EmbeddingRequest / EmbeddingResult
RerankRequest / RerankResult
VisionExtractionRequest / VisionExtractionResult
AudioTranscriptionRequest / AudioTranscriptionResult
ClassificationRequest / ClassificationResult
JudgeRequest / JudgeResult
```

Batch Operation 必须包含：

```text
batch_id
item_id
item_idempotency_key
input_payload_ref
input_hash
item_deadline_at
item_status
item_failure_ref
item_usage_ref
```

Batch 不变量：

1. Batch transport success 不等于每个 item success；
2. 每个 item 的结果、失败和 usage 可独立审计；
3. 部分失败重试只重试失败 item，除非 Provider 无法证明拆分语义；
4. Embedding 必须固定 dimension、normalization 和 model revision；
5. Rerank 必须固定 score direction、range、calibration version 和 tie-break；
6. Batch split / merge 必须保持 item 顺序、ID 和幂等键；
7. 不支持的 Provider batch 只能由 Gateway 显式拆分，不能由 SDK 隐式扩展调用次数。

## 4. Prompt Ownership 再拆分

```text
Agent Core / Capability / Domain owns
    PromptArtifact
    PromptTemplate semantics
    few-shot content
    business instruction
    expected result meaning

Model Gateway owns
    PromptExecutionBinding
    rendered prompt hash
    output schema binding
    Provider / Model compatibility
    tokenization profile
    redaction binding reference
    execution parameter policy
```

`PromptExecutionBinding`：

```text
prompt_execution_binding_id
binding_version
prompt_artifact_ref
prompt_artifact_hash
role_ref
operation_kind
output_contract_ref
output_schema_hash
redaction_decision_ref
provider_compatibility_rules
model_compatibility_rules
tokenization_profile_ref
execution_parameter_policy_ref
created_at
status
```

Gateway 可以拒绝不兼容 Prompt，但不能静默重写业务意图。Parameter Repair 只能修改已授权字段，例如：

```text
temperature
max_output_tokens
schema transport mode
provider-specific harmless framing
```

改变 system policy、业务约束、Tool 权限、事实目标或 Acceptance 标准必须回到对应 Owner。

## 5. ModelCall 聚合与 Attempt 的关系

### 5.1 ModelCall Aggregate

`ModelCall` 表示调用方的一次逻辑模型请求；多个 Provider Attempt、Repair、Fallback 或 Role Escalation 可以属于同一逻辑调用链。

```text
model_call_id
request_id
idempotency_key
role_ref
operation_kind
output_contract_ref
security_decision_ref
security_epoch
budget_reservation_ref
status
selected_response_ref
selection_decision_ref
active_routing_decision_ref
attempt_refs
usage_settlement_status
cancellation_state
reconciliation_state
created_at
updated_at
version
```

### 5.2 ModelCallStatus

```text
CREATED
VALIDATING
ROUTING
WAITING_ADMISSION
ACTIVE
WAITING_QUOTA
RECONCILING
SUCCEEDED
FAILED
EXHAUSTED
CANCELLED
UNKNOWN
```

语义：

| 状态 | 含义 |
| --- | --- |
| `FAILED` | 当前路径出现终止失败，但 Policy 可能仍能创建新的 Routing / Attempt |
| `EXHAUSTED` | 所有允许的 Retry、Repair、Fallback 和 Escalation 路径均耗尽 |
| `UNKNOWN` | Provider 是否执行或结果是否提交无法证明 |
| `RECONCILING` | 正在通过 request ID、receipt 或迟到响应恢复事实 |
| `SUCCEEDED` | 已选择唯一可消费 Response；Usage 可以仍为 settlement pending |

### 5.3 ModelCall 状态转换

| From | Trigger | Guard | To |
| --- | --- | --- | --- |
| `CREATED` | request accepted | idempotency claim acquired | `VALIDATING` |
| `VALIDATING` | contract/security validation passed | Role、Operation、Prompt、Security 均有效 | `ROUTING` |
| `ROUTING` | routing committed | candidate and policy snapshot fixed | `WAITING_ADMISSION` |
| `WAITING_ADMISSION` | quota/budget/circuit admission passed | dispatch allowed | `ACTIVE` |
| `WAITING_ADMISSION` | quota unavailable but deadline permits | wait policy exists | `WAITING_QUOTA` |
| `WAITING_QUOTA` | reservation acquired | deadline and security epoch valid | `ACTIVE` |
| `ACTIVE` | selected response committed | validation passed | `SUCCEEDED` |
| `ACTIVE` | attempt result unknown | provider may have executed | `UNKNOWN` |
| `UNKNOWN` | reconciliation started | recovery evidence available | `RECONCILING` |
| `RECONCILING` | authoritative success selected | no conflicting selection | `SUCCEEDED` |
| `RECONCILING` | no proof and no legal retry path | policy exhausted | `EXHAUSTED` |
| non-terminal | cancellation confirmed | no selected response | `CANCELLED` |
| retryable state | new path authorized | remaining policy/budget/deadline | `ROUTING` |
| retryable state | all paths exhausted | failure aggregate complete | `EXHAUSTED` |

### 5.4 SelectionDecision

多个 Attempt 可能因为迟到响应或并发 Reconcile 同时产生有效结果。Gateway 必须创建唯一 `ModelResponseSelectionDecision`：

```text
selection_decision_id
model_call_id
selected_response_ref
candidate_response_refs
selection_policy_version
selection_reason_codes
security_epoch
expected_call_version
created_at
```

不变量：

1. 一个 `ModelCall` 最多一个 active selected response；
2. selected response 使用 generation / CAS 提交；
3. 迟到成功不能静默覆盖已选择结果；
4. 冲突结果写入 `ModelResponseSupersessionRecord` 或 Reconciliation Record；
5. 已取消 Call 的迟到结果默认 `TAINTED` 或 `NOT_SELECTED`；
6. `SUCCEEDED` 与 `usage_settlement_status=SETTLEMENT_PENDING` 可以同时存在；
7. `UNKNOWN` 未解决前，高成本或 Tool Proposal 请求不得默认盲目重发。

## 6. Budget、Quota、Usage 与崩溃语义

### 6.1 Ownership

```text
Agent Core / Budget Ledger owns
    BudgetReservation
    BudgetConsumption
    BudgetSettlement
    Run-level budget policy

Model Gateway owns
    ModelCostQuote
    AttemptBudgetAllocation
    QuotaReservation semantic state
    UsageReceipt
    UsageCorrection

Infrastructure owns
    atomic persistence
    CAS / generation
    durable outbox
    clock
    recovery primitive
```

### 6.2 AttemptBudgetAllocation

```text
attempt_budget_allocation_id
model_call_id
attempt_id
budget_reservation_ref
quoted_input_tokens
quoted_output_tokens
quoted_cost
currency
pricing_version_ref
allocation_status
expires_at
version
```

`allocation_status`：

```text
RESERVED
CONSUMPTION_PENDING
CONSUMED
RELEASED
EXPIRED
RECONCILING
```

### 6.3 Usage 结算事件

```text
UsageObserved
BudgetConsumptionRequested
BudgetConsumptionAccepted
BudgetConsumptionRejected
UsageSettlementPending
UsageSettled
UsageCorrected
BudgetSettlementCorrectionRequested
```

建议幂等键：

```text
tenant_id
+ workspace_id
+ run_id
+ step_run_id
+ model_call_id
+ attempt_id
+ usage_receipt_id
+ receipt_version
```

不得只使用 Provider Request ID，因为不同 Provider 的稳定性、作用域和重复语义不同。

### 6.4 崩溃矩阵

| 故障点 | Gateway 事实 | 必须动作 | 禁止动作 |
| --- | --- | --- | --- |
| Budget 已授权，Quota 创建失败 | Call=`WAITING_ADMISSION` 或 `WAITING_QUOTA` | 释放未使用 Allocation；保留失败事实 | 直接 Dispatch |
| Quota 已创建，Routing Commit 失败 | orphan reservation candidate | CAS 释放或 Recovery 扫描 | 永久占用 Quota |
| Routing 已提交，Attempt 未提交 | recoverable routing | 恢复创建 Attempt 或使 Routing 失效 | 无 Attempt 直接调用 Provider |
| Attempt 已提交，请求可证明未发送 | Attempt failure=`NOT_DISPATCHED` | 可按 Policy 创建新 Attempt | 把失败计为 Provider 质量问题 |
| 请求可能已发送，响应丢失 | Attempt=`UNKNOWN` | Reconcile；冻结或估算 usage | 盲目重发高成本请求 |
| Response 已提交，Usage 未提交 | Call 可 `SUCCEEDED`，settlement pending | 创建估算 Receipt 和补偿任务 | 丢失成本或伪造 settled |
| Usage 已提交，Outbox 未发布 | domain commit 已完成 | Outbox replay | 再写一份 UsageReceipt |
| Usage Event 重复交付 | Receipt version 已存在 | Consumer inbox dedup | Budget 重复扣费 |
| Provider 迟到 Usage Correction | append-only correction | 请求 Budget correction | 覆盖原 Receipt |
| Fallback 多次调用 | 每个 Attempt 独立 Usage | 分别结算并汇总到 Call | 只记录最终成功 Attempt |
| RunOutcome 已完成，Usage 后到 | pending settlement ref | 追加 Settlement Correction | 改写历史 RunOutcome 事实 |
| Security revoke 发生在结算前 | result validity 变化 | usage 仍按真实调用结算 | 因结果不可用而抹掉成本 |

### 6.5 Quota 与 Rate Limit

- `QuotaReservation` 是 Gateway 领域 Aggregate；Infrastructure 提供 CAS 和 Clock；
- Provider Header 是 observation，不是绝对事实；
- 并发 Admission 使用 conservative reservation；
- Reservation lease 过期必须经过 version / fencing 检查；
- 429 不能在业务模块自行 sleep；
- WAIT_QUOTA、Fallback 或 Fail 的选择必须受 Deadline、Budget 和 Security 约束；
- Quota release receipt 只证明本地配额状态，不证明 Provider 未计费。

## 7. Model Gateway 领域事件目录

### 7.1 Canonical Event Catalog

```text
ModelCallRequested
ModelCallValidated
ModelRoutingDecided
ModelRoutingInvalidated
ModelAttemptAdmitted
ModelAttemptDispatched
ModelAttemptStreaming
ModelAttemptSucceeded
ModelAttemptFailed
ModelAttemptTimedOut
ModelAttemptCancelled
ModelAttemptUnknown
ModelAttemptReconciliationStarted
ModelAttemptReconciled
ModelFallbackSelected
ModelRoleEscalationRequested
ModelResponseSelected
ModelResultValidityChanged
ModelStreamOpened
ModelStreamCheckpointed
ModelStreamDisconnected
ModelStreamCompleted
StructuredOutputRejected
StructuredOutputRepairRequested
StructuredOutputRepaired
StructuredOutputExhausted
UsageObserved
UsageSettlementPending
UsageSettled
UsageCorrected
ProviderHealthChanged
CircuitBreakerChanged
QuotaReservationChanged
CancellationRequested
CancellationConfirmed
```

### 7.2 Event Envelope

每个事件至少携带：

```text
contract_name
contract_version
message_id
aggregate_type
aggregate_id
aggregate_version
event_type
event_version
tenant_id
workspace_id
run_id
step_run_id
correlation_id
causation_id
idempotency_key
security_epoch
data_classification
deadline_at
trace_id
producer_module
occurred_at
payload_ref
payload_hash
redaction_decision_ref
mandatory_audit_requirement_ref
```

### 7.3 Event 发布与消费

1. Gateway 在领域事实提交时通过 transactional outbox 或等价原子机制记录事件；
2. 普通 telemetry 至少一次交付，Observability 通过 message ID / aggregate version 去重；
3. Mandatory Audit 的 durability 由 Security Requirement 决定；
4. Event delivery failure 不得回滚已完成的 Provider 调用；
5. Mandatory-before-effect 只适用于安全策略指定的操作，普通模型生成不得自动升级为副作用；
6. Replay 不得重新触发 Provider 调用，只能重建 Projection 或重新交付已存在事件；
7. Unknown event version 默认 quarantine，不得猜测字段含义。

## 8. 三层 Streaming Contract

必须区分：

```text
Provider Stream
    SDK / SSE / WebSocket 原始事件

Gateway Internal Stream
    Provider-neutral ModelStreamChunk

Product Delivery Stream
    Product Surface 对用户或调用方的 SSE / WebSocket
```

### 8.1 Provider Stream

Gateway Adapter 负责：

- SDK event 归一化；
- unknown event 保存与兼容判断；
- first-token、idle、total timeout；
- Provider error inside HTTP 200 stream；
- usage delta 与 terminal receipt；
- transport cancellation receipt。

### 8.2 Gateway Internal Stream

```text
stream_session_id
attempt_id
sequence_no
provider_event_id
chunk_type
content_ref
content_hash
provisional
checkpoint_no
usage_delta
finish_reason
received_at
```

规则：

- sequence 在 session 内唯一单调；
- dedup 使用 provider event ID 与 sequence；
- partial chunk 永远是 provisional；
- Tool Proposal 只有完整 schema 验证后才能成为 Proposal；
- Gateway 重启后的 replay 只重放已持久化 chunk，不伪造 Provider continuation；
- reconnect 只有 Provider 能证明 continuation semantics 时才续接。

### 8.3 Product Delivery Stream

Product Surface 决定用户连接和显示策略，但不得改变 Gateway 事实：

- 用户断开不必然取消后台 Call；
- 是否取消由 caller cancellation policy 决定；
- 慢消费者需要 bounded buffer、backpressure 和 disconnect policy；
- Product replay cursor 不能被误当成 Provider stream cursor；
- 用户已看到 provisional 内容时，最终失败必须有明确 terminal error；
- FinalCandidate 只能来自 selected and validated ModelResponse。

## 9. Routing 可解释与确定性重放

`ModelRoutingDecision` 增加：

```text
routing_policy_version
decision_input_hash
candidate_set_hash
candidate_score_components
candidate_rank_before_policy
candidate_rank_after_policy
rejection_reason_codes
tie_break_rule
experiment_assignment_ref
random_seed_ref
availability_snapshot_refs
security_decision_ref
budget_quote_ref
quota_snapshot_ref
health_snapshot_ref
circuit_snapshot_ref
created_at
valid_until
```

重放要求：

1. 使用相同 Policy、Config、Catalog、Capability、Security、Availability 和 Seed 可以重建相同排序；
2. 动态 Health / Quota 只能通过固定 Snapshot 重放；
3. 无法重放时必须给出缺失证据，不得声称 deterministic；
4. 实验 assignment 必须在强制 Security、Capability 和 Budget Gate 之后；
5. Tie-break 必须稳定，不能依赖无序 Map 或进程随机性；
6. Routing replay 只解释历史决定，不重新 Dispatch。

## 10. Capability Profile 生命周期

### 10.1 状态

```text
DECLARED_UNVERIFIED
PROBE_PENDING
VERIFIED
DEGRADED
STALE
REVOKED
```

### 10.2 转换

| From | Trigger | To | 规则 |
| --- | --- | --- | --- |
| `DECLARED_UNVERIFIED` | verification scheduled | `PROBE_PENDING` | 不得作为关键 Role 的唯一候选 |
| `PROBE_PENDING` | conformance passed | `VERIFIED` | 保存 evidence、SDK、model revision |
| `PROBE_PENDING` | partial mismatch | `DEGRADED` | 降低 capability，不伪装完整支持 |
| `VERIFIED` | TTL / SDK / model revision changed | `STALE` | 重新 probe 前限制高风险调用 |
| `VERIFIED`/`DEGRADED` | runtime mismatch | `DEGRADED` 或 `REVOKED` | 产生 CapabilityMismatch event |
| 非终态 | admin/security disable | `REVOKED` | 立即退出候选集 |

### 10.3 Evidence

```text
capability_profile_id
profile_version
model_definition_ref
provider_adapter_version
sdk_version
model_revision
probe_suite_version
probe_run_ref
evidence_refs
verified_at
expires_at
status
```

要求：

- Provider 文档声明只形成 `DECLARED_UNVERIFIED`；
- Runtime success 可以作为被动证据，但不能替代完整 conformance；
- SDK 或 Adapter 升级必须重新评估 Profile；
- Probe 成本计入明确的 Eval / Operations Budget；
- Capability stale 时 Planner 的 Feasibility 结果必须表达风险和有效期；
- runtime mismatch 需要负缓存，防止同一不兼容路径持续失败。

## 11. ResultValidity 传播

`ModelResultValidity`：

```text
VALID
PARTIAL
TAINTED
REVOKED
UNKNOWN
NOT_SELECTED
SUPERSEDED
```

`ModelResultValidityChanged`：

```text
validity_record_id
model_response_ref
previous_validity
new_validity
reason_code
security_epoch
trigger_ref
affected_consumer_refs
occurred_at
```

传播规则：

```text
Gateway commits validity change
→ Outbox publishes ModelResultValidityChanged
→ Agent Core locates consuming Step / Candidate
→ Decision Guard chooses invalidate / retry / replan / abstain / disclose
→ Product Surface handles publication correction where applicable
```

Gateway 不直接修改 Step、Plan、FinalCandidate、Publication 或 RunOutcome。

必须覆盖：

- Security Revocation；
- late Provider error；
- reconciliation finds duplicate or conflicting result；
- selected response later superseded by authoritative receipt；
- structured validation defect discovered after initial acceptance；
- data retention or legal-hold rules changing payload availability。

已发布答案的撤回或更正由 Product Surface 与 Agent Core 决定；Observability 保存投影和证据，不成为 Validity Owner。

## 12. Failure Code 对齐

### 12.1 Security / Admission

```text
MODEL_SECURITY_DECISION_MISSING
MODEL_SECURITY_DECISION_EXPIRED
SECURITY_EPOCH_STALE
MODEL_PROVIDER_NOT_ALLOWED
MODEL_NOT_ALLOWED
MODEL_RESIDENCY_DENIED
MODEL_CLASSIFICATION_UNSUPPORTED
MODEL_CREDENTIAL_SCOPE_DENIED
MODEL_PROMPT_REDACTION_REQUIRED
MODEL_MANDATORY_AUDIT_UNAVAILABLE
```

### 12.2 Routing / Capability

```text
MODEL_ROLE_UNSUPPORTED
MODEL_OPERATION_UNSUPPORTED
MODEL_CAPABILITY_UNVERIFIED
MODEL_CAPABILITY_STALE
MODEL_CAPABILITY_MISMATCH
MODEL_PROMPT_INCOMPATIBLE
MODEL_SCHEMA_INCOMPATIBLE
MODEL_NO_ROUTABLE_CANDIDATE
MODEL_ROUTING_SNAPSHOT_EXPIRED
```

### 12.3 Attempt / Transport

```text
MODEL_CONNECT_TIMEOUT
MODEL_READ_TIMEOUT
MODEL_STREAM_IDLE_TIMEOUT
MODEL_ATTEMPT_DEADLINE_EXCEEDED
MODEL_TRANSPORT_CANCEL_UNCONFIRMED
MODEL_PROVIDER_RATE_LIMITED
MODEL_PROVIDER_UNAVAILABLE
MODEL_PROVIDER_AUTH_FAILED
MODEL_PROVIDER_RESPONSE_MALFORMED
MODEL_PROVIDER_RESULT_UNKNOWN
```

### 12.4 Structured Output / Stream

```text
MODEL_STRUCTURED_OUTPUT_INVALID
MODEL_STRUCTURED_OUTPUT_REPAIR_EXHAUSTED
MODEL_STREAM_SEQUENCE_GAP
MODEL_STREAM_DISCONNECTED
MODEL_STREAM_PROVIDER_ERROR
MODEL_STREAM_TERMINAL_MISSING
```

### 12.5 Usage / Quota / Reconciliation

```text
MODEL_BUDGET_ALLOCATION_UNAVAILABLE
MODEL_QUOTA_RESERVATION_CONFLICT
MODEL_QUOTA_EXPIRED
MODEL_USAGE_RECEIPT_DELAYED
MODEL_USAGE_SETTLEMENT_CONFLICT
MODEL_USAGE_CORRECTION_REJECTED
MODEL_RECONCILIATION_PROOF_UNAVAILABLE
MODEL_FALLBACK_EXHAUSTED
MODEL_CALL_EXHAUSTED
```

Failure 映射规则：

1. Provider SDK error 映射为稳定 Gateway Failure Code；
2. 原始错误只保存在受控、脱敏的 debug ref；
3. Security failure 不计入普通 Provider Health；
4. Adapter / SDK compatibility failure 可按 adapter version 打开 Circuit；
5. Gateway 返回 suggested control action，Agent Core 提交 Retry / Replan / Abstain；
6. Unknown enum 和 unknown failure version 默认 fail-closed / quarantine。

## 13. 实现前 Contract Freeze Gate

Model Gateway 进入大规模实现 Program 前必须满足：

1. `ModelSecurityDecision` 字段与 Security PR 完成字段级审计；
2. `ProviderConnectionFactory`、`SecretLease`、Clock、Cancellation 和 CAS Port 与 Infrastructure 对齐；
3. `TelemetryEnvelope`、Audit、Event version 和 delivery receipt 与 Observability 对齐；
4. `ModelOperationKind` 与 Knowledge、Memory、Eval 的真实调用清单对齐；
5. `ModelCall` 与 `ModelCallAttempt` 状态和选择语义冻结；
6. Budget / Usage / Quota 崩溃矩阵有 Integration 和 Fault Test 设计；
7. Event Catalog 有 Owner、Version、Idempotency、Ordering、Redaction 和 Replay 规则；
8. Routing replay、Capability lifecycle、ResultValidity propagation 有稳定 Contract；
9. legacy bypass 清理拆为可验证 Program，而不是一次性全量替换；
10. 未运行真实 Provider、Migration、Fault、E2E、Trace 和 Eval 前，不得提升为 implementation available 或 production ready。

## 14. Requirement Registry

| Requirement | 规范 | Runtime Control | Unit | Integration | Fault | E2E | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ARCH-MODEL-CF-001` | Security Decision 只有 Security 一个 Owner | `RC-MODEL-CF-001` | `MODEL-CF-001-UT` | `MODEL-CF-001-IT` | `MODEL-CF-001-FT` | `MODEL-CF-001-E2E` | `EV-MODEL-CF-001` |
| `ARCH-MODEL-CF-002` | Infrastructure primitive 与 Gateway 语义事实分离 | `RC-MODEL-CF-002` | `MODEL-CF-002-UT` | `MODEL-CF-002-IT` | `MODEL-CF-002-FT` | `MODEL-CF-002-E2E` | `EV-MODEL-CF-002` |
| `ARCH-MODEL-CF-003` | Observability 不成为模型调用事实 Owner | `RC-MODEL-CF-003` | `MODEL-CF-003-UT` | `MODEL-CF-003-IT` | `MODEL-CF-003-FT` | `MODEL-CF-003-E2E` | `EV-MODEL-CF-003` |
| `ARCH-MODEL-CF-004` | ModelRoleContract 与 Routing Profile 分离 | `RC-MODEL-CF-004` | `MODEL-CF-004-UT` | `MODEL-CF-004-IT` | `MODEL-CF-004-FT` | `MODEL-CF-004-E2E` | `EV-MODEL-CF-004` |
| `ARCH-MODEL-CF-005` | Role 与 ModelOperationKind 分离 | `RC-MODEL-CF-005` | `MODEL-CF-005-UT` | `MODEL-CF-005-IT` | `MODEL-CF-005-FT` | `MODEL-CF-005-E2E` | `EV-MODEL-CF-005` |
| `ARCH-MODEL-CF-006` | Batch item 独立状态、失败、Usage 和幂等 | `RC-MODEL-CF-006` | `MODEL-CF-006-UT` | `MODEL-CF-006-IT` | `MODEL-CF-006-FT` | `MODEL-CF-006-E2E` | `EV-MODEL-CF-006` |
| `ARCH-MODEL-CF-007` | Prompt Artifact 与 Execution Binding 分离 | `RC-MODEL-CF-007` | `MODEL-CF-007-UT` | `MODEL-CF-007-IT` | `MODEL-CF-007-FT` | `MODEL-CF-007-E2E` | `EV-MODEL-CF-007` |
| `ARCH-MODEL-CF-008` | ModelCall 聚合必须有完整状态机 | `RC-MODEL-CF-008` | `MODEL-CF-008-UT` | `MODEL-CF-008-IT` | `MODEL-CF-008-FT` | `MODEL-CF-008-E2E` | `EV-MODEL-CF-008` |
| `ARCH-MODEL-CF-009` | 多响应只能 CAS 选择一个结果 | `RC-MODEL-CF-009` | `MODEL-CF-009-UT` | `MODEL-CF-009-IT` | `MODEL-CF-009-FT` | `MODEL-CF-009-E2E` | `EV-MODEL-CF-009` |
| `ARCH-MODEL-CF-010` | Budget / Quota / Usage 必须有崩溃恢复语义 | `RC-MODEL-CF-010` | `MODEL-CF-010-UT` | `MODEL-CF-010-IT` | `MODEL-CF-010-FT` | `MODEL-CF-010-E2E` | `EV-MODEL-CF-010` |
| `ARCH-MODEL-CF-011` | 每个 Attempt 独立记录并结算 Usage | `RC-MODEL-CF-011` | `MODEL-CF-011-UT` | `MODEL-CF-011-IT` | `MODEL-CF-011-FT` | `MODEL-CF-011-E2E` | `EV-MODEL-CF-011` |
| `ARCH-MODEL-CF-012` | Event Catalog 必须版本化且可重放 | `RC-MODEL-CF-012` | `MODEL-CF-012-UT` | `MODEL-CF-012-IT` | `MODEL-CF-012-FT` | `MODEL-CF-012-E2E` | `EV-MODEL-CF-012` |
| `ARCH-MODEL-CF-013` | Event replay 不得重新触发 Provider 调用 | `RC-MODEL-CF-013` | `MODEL-CF-013-UT` | `MODEL-CF-013-IT` | `MODEL-CF-013-FT` | `MODEL-CF-013-E2E` | `EV-MODEL-CF-013` |
| `ARCH-MODEL-CF-014` | Provider、Gateway、Product Streaming 分层 | `RC-MODEL-CF-014` | `MODEL-CF-014-UT` | `MODEL-CF-014-IT` | `MODEL-CF-014-FT` | `MODEL-CF-014-E2E` | `EV-MODEL-CF-014` |
| `ARCH-MODEL-CF-015` | Routing 必须可解释并可确定性重放 | `RC-MODEL-CF-015` | `MODEL-CF-015-UT` | `MODEL-CF-015-IT` | `MODEL-CF-015-FT` | `MODEL-CF-015-E2E` | `EV-MODEL-CF-015` |
| `ARCH-MODEL-CF-016` | Capability Profile 必须有验证生命周期 | `RC-MODEL-CF-016` | `MODEL-CF-016-UT` | `MODEL-CF-016-IT` | `MODEL-CF-016-FT` | `MODEL-CF-016-E2E` | `EV-MODEL-CF-016` |
| `ARCH-MODEL-CF-017` | ResultValidity 变化必须可靠传播 | `RC-MODEL-CF-017` | `MODEL-CF-017-UT` | `MODEL-CF-017-IT` | `MODEL-CF-017-FT` | `MODEL-CF-017-E2E` | `EV-MODEL-CF-017` |
| `ARCH-MODEL-CF-018` | Failure Code 必须稳定且 Provider-neutral | `RC-MODEL-CF-018` | `MODEL-CF-018-UT` | `MODEL-CF-018-IT` | `MODEL-CF-018-FT` | `MODEL-CF-018-E2E` | `EV-MODEL-CF-018` |
| `ARCH-MODEL-CF-019` | Unknown Version / Enum 默认 fail-closed 或 quarantine | `RC-MODEL-CF-019` | `MODEL-CF-019-UT` | `MODEL-CF-019-IT` | `MODEL-CF-019-FT` | `MODEL-CF-019-E2E` | `EV-MODEL-CF-019` |
| `ARCH-MODEL-CF-020` | Contract Freeze 完成前不得大规模实现 | `RC-MODEL-CF-020` | `MODEL-CF-020-UT` | `MODEL-CF-020-IT` | `MODEL-CF-020-FT` | `MODEL-CF-020-E2E` | `EV-MODEL-CF-020` |

## 15. 强制 Fault / Recovery 场景

实现证据至少覆盖：

```text
Security Decision expired between Routing and Dispatch
Security Epoch revoked during stream
Quota reserved but Routing commit fails
Routing committed but Attempt commit fails
Provider accepted request but local response is lost
Two late valid responses race for selection
Response committed but UsageReceipt commit fails
Usage event delivered twice
Usage correction arrives after RunOutcome
Batch embedding partial failure
Rerank score profile changes after routing
Provider stream succeeds but Product client disconnects
Gateway restart during stream checkpoint
Capability profile becomes stale after SDK upgrade
ResultValidity becomes REVOKED after Step consumed response
Unknown event version reaches Observability
Routing replay misses a required snapshot
Cancellation requested but Provider cannot confirm
Fallback Exhausted with settlement pending
Mandatory Audit unavailable for restricted model call
```

## 16. Target 到 Current 的证据

本附录由 Target 变为 Current 不能只凭文档或类型定义，至少需要：

```text
Contract implementation
PostgreSQL Migration
Unit Test
Integration Test
Fault Injection
E2E
Provider Adapter conformance
Trace / Audit evidence
Usage and Budget reconciliation evidence
Security revocation evidence
Streaming disconnect / recovery evidence
Routing replay evidence
Capability probe evidence
ResultValidity propagation evidence
```

推荐状态表达：

```text
design available
cross-module alignment in progress
implementation not established
measurement blocked
quality not yet proven
production ready not established
```
