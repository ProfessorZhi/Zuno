# Goal01 Closure Matrix

status: frozen

frozen_at: 2026-07-19

branch: `integration/goal01-control-plane-model-ingestion`

start_sha_after_fetch: `36130924f5602c894d3d89eaaf6cefc3c8624a89`

origin_main_sha_after_fetch: `ed787ee962f7f567163388188e56b4b765c27877`

说明：本文冻结 PHASE05、PHASE06、PHASE07、PHASE11 的有限 Closure Matrix。后续只处理本文中 `mandatory_open` 或 `completion_candidate` 行；除非测试证明架构缺陷，不继续开放式扩范围。

## PHASE05 PEP/PDP Cutover Matrix

| 入口 | 当前归类 | 状态 | 证据 | 剩余处理 |
| --- | --- | --- | --- | --- |
| Execute / Side Effect | `canonical_security_guard` | `completion_candidate` | Tool Runtime approval fact sink、pre-effect hash/epoch/deadline validation、sink outage fail-closed fault tests | Pre-Closure 前聚合验证 |
| Approval / Resume | `canonical_security_guard` | `completion_candidate` | workspace approval resume `task.resume.*` product action guard 与 403 deny test | Pre-Closure 前聚合验证 |
| Artifact Read / Download | `canonical_security_guard` | `completion_candidate` | workspace `artifact.read` / `artifact.download` product action guard、startup Postgres guard wiring | Pre-Closure 前聚合验证 |
| Citation / Source Access | `canonical_security_guard` | `completion_candidate` | workspace `citation.read` guard for artifact response and task snapshot | Pre-Closure 前聚合验证 |
| Admin 管理面：MCP HTTP/SSE + stdio | `canonical_security_guard` | `completion_candidate` | MCP admin override guard、startup guard wiring、deny-before-DAO tests | Pre-Closure 前聚合验证 |
| Admin 管理面：Agent / Tool / Dialog / MCP Agent / LLM / Knowledge / Knowledge File | `canonical_security_guard` | `completion_candidate` | 共享 `security_admin_actions`、verifier、evidence 和 `test_phase05_admin_action_reauthorization.py` 已覆盖 Agent/Tool/Dialog/MCP Agent/LLM/Knowledge/Knowledge File admin override deny-before-DAO | Pre-Closure 前聚合验证 |
| Secret Lease | `canonical_security_guard` | `completion_candidate` | `SecurityRepository.record_secret_ref` / `issue_secret_lease` / `validate_secret_lease` 覆盖 wrong audience、expired lease、revoked secret | Pre-Closure 前聚合验证 |
| External Export | `future_runtime_not_current` | `not_current` | 当前 active runtime 无正式 external export 默认路径；PHASE06 external sink isolation 已证明外部 sink 不冒充业务成功 | 归属后续 Product/Publication/Integration Phase，不能阻塞 PHASE05 当前默认路径 closure |
| Legacy Approval Boolean 到 Decision/Ref | `temporary_versioned_adapter` | `completion_candidate` | Tool Runtime `approved: bool` 已绑定 `temporary.adapter.tool_runtime.approved_bool` 与删除 Phase `PHASE16`；workspace 默认 resume path 已传入 `security-approval-decision:*` decision ref；PHASE05 verifier 阻止新增 legacy boolean owner | Pre-Closure 前聚合验证 |

## PHASE06 Adapter Cutover Matrix

| 运行域 | Producer | Envelope / Adapter | 默认接线点 | 失败策略 | 状态 | 剩余处理 |
| --- | --- | --- | --- | --- | --- | --- |
| Agent | Agent runtime / workspace runtime | typed runtime event / span adapter | workspace runtime security and retrieval spans | local append-only first | `completion_candidate` | 聚合验证 |
| Model | Model Gateway runtime | model attempt / runtime event envelope | Gateway-owned call path | provider failure becomes attempt failure, not audit success | `completion_candidate` | `PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event` 已消费 Gateway trace_event 写入 model span/runtime event/audit；PHASE06 verifier 防断线；PHASE07 closure 仍需独立依赖批准 |
| Knowledge | Agentic retrieval / ingestion | retrieval trace / citation metrics | workspace retrieval observability | raw event retained, query freshness exposed | `completion_candidate` | 聚合验证 |
| Capability | Capability / Skill runtime | capability plan/runtime event | workspace capability snapshot | local facts persist before external sink | `completion_candidate` | 聚合验证 |
| Tool | Tool Runtime | approval/security span adapter | Tool Runtime approval path | sink outage fail-closed before side effect | `completion_candidate` | 聚合验证 |
| Security | Security repository / audit | immutable audit ledger adapter | Security pre-effect/audit facts | audit not sampled; failure visible | `completion_candidate` | 聚合验证 |
| Infrastructure | DB / outbox / external sink | dead-letter and local fact envelope | observability persistence adapter | external sink failure does not roll back local facts | `completion_candidate` | 聚合验证 |
| Product Query | Observability query service | read-only freshness/completeness response | `/api/v1/observability/traces/{trace_id}` + product query service | returns freshness/completeness and dead letters; non-admin API access returns 403 | `completion_candidate` | 聚合验证 |

## PHASE07 Runtime Closure Matrix

| 范围 | 当前归类 | 状态 | 证据 | 剩余处理 |
| --- | --- | --- | --- | --- |
| Provider SDK bypass | `canonical_gateway_boundary` | `completion_candidate` | `verify_model_gateway_bypass.py --strict` 目标已达到 strict-zero，但只允许 Pre-Closure 前运行一次 | PHASE05/06 closure 后运行一次 strict gate |
| Model / Role / Capability Registry | `canonical_gateway_runtime` | `completion_candidate` | Model Gateway runtime batch evidence | PHASE07 Pre-Closure 聚合验证 |
| Routing Policy / Immutable Snapshot | `canonical_gateway_runtime` | `completion_candidate` | Routing snapshot and policy tests | PHASE07 Pre-Closure 聚合验证 |
| Provider Adapter SPI | `canonical_gateway_runtime` | `completion_candidate` | adapter boundary and conformance tests | PHASE07 Pre-Closure 聚合验证 |
| ModelAttempt lifecycle | `canonical_gateway_runtime` | `completion_candidate` | attempt lifecycle tests | PHASE07 Pre-Closure 聚合验证 |
| Structured Output Validation | `canonical_gateway_runtime` | `completion_candidate` | structured validation / repair evidence | PHASE07 Pre-Closure 聚合验证 |
| Streaming / Timeout / Cancel | `canonical_gateway_runtime` | `completion_candidate` | streaming, timeout, cancel tests | PHASE07 Pre-Closure 聚合验证 |
| Usage Reservation / Settlement | `canonical_gateway_runtime` | `completion_candidate` | reservation and settlement tests | PHASE07 Pre-Closure 聚合验证 |
| Retry / Fallback / Circuit | `canonical_gateway_runtime` | `completion_candidate` | retry/fallback/circuit tests | PHASE07 Pre-Closure 聚合验证 |
| Trace / Audit 接入 | `depends_on_phase06` | `completion_candidate` | PHASE06 Coordinator Closure 已批准；`PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event` 与 PHASE06 persistence verifier 已证明 Gateway trace/audit 接入 | PHASE07 Pre-Closure 聚合验证 |
| Chat / Embedding / Rerank / Judge 默认路径 | `canonical_gateway_runtime` | `completion_candidate` | default entry tests and bypass guard | PHASE05/06 Closure 后进入 PHASE07 closure review |

## PHASE11 Ingestion Closure Matrix

| 范围 | 当前归类 | 状态 | 证据 | 剩余处理 |
| --- | --- | --- | --- | --- |
| SourceObject upload init / commit | `canonical_ingestion_runtime` | `completion_candidate` | source-lineage schema/repository + input runtime batch evidence | PHASE11 Pre-Closure 聚合验证 |
| DocumentVersion / ParseSnapshot 分离 | `canonical_ingestion_runtime` | `completion_candidate` | source-lineage schema/repository + persistence runtime tests | PHASE11 Pre-Closure 聚合验证 |
| ParsePlan / Job / Attempt | `canonical_ingestion_runtime` | `completion_candidate` | parse gateway/runtime tests + source-lineage persistence evidence | PHASE11 Pre-Closure 聚合验证 |
| RabbitMQ dispatch / ACK / Retry / Dead Letter | `canonical_ingestion_runtime` | `completion_candidate` | LocalQueue ACK/retry/dead-letter/replay verified；RabbitMQ target-blocked dependency probe does not fake production dependency | PHASE11 Pre-Closure 聚合验证 |
| Lease / Heartbeat / Fencing / Worker Crash Recovery | `canonical_ingestion_runtime` | `completion_candidate` | ParseAttemptControl lease/fencing/late-result rejection and async worker/reconciler tests | PHASE11 Pre-Closure 聚合验证 |
| Native / PDF / Layout / OCR / VLM / Office / Archive Adapter | `mixed_current_future` | `completion_candidate` | Native/PDF current adapters verified；OCR/VLM external target blocked with stable diagnostics and no fake index; Office/archive preservation boundary covered by input runtime batch | PHASE11 Pre-Closure 聚合验证 |
| CanonicalDocumentIR | `canonical_ingestion_runtime` | `completion_candidate` | ingestion contract tests | 聚合验证 |
| SourceSpan / TransformLedger | `canonical_ingestion_runtime` | `completion_candidate` | SourceSpan provenance and TransformRecord loss/lineage evidence in input runtime batch | PHASE11 Pre-Closure 聚合验证 |
| Quality Gate / Human Review | `canonical_ingestion_runtime` | `completion_candidate` | QualityReport PASS/DEGRADED/BLOCK and IndexableDocumentSnapshot quality FK gate verified; human review remains explicit degraded/block boundary | PHASE11 Pre-Closure 聚合验证 |
| IndexableDocumentSnapshot Outbox Handoff | `canonical_ingestion_runtime` | `completion_candidate` | Indexable snapshot persistence + outbox handoff tests | PHASE11 Pre-Closure 聚合验证 |
| Visibility Revoke | `canonical_ingestion_runtime` | `completion_candidate` | deletion receipts and visibility revocation sequence covered by input runtime batch | PHASE11 Pre-Closure 聚合验证 |
| Legal Hold | `canonical_ingestion_runtime` | `completion_candidate` | Legal Hold blocks purge only and does not restore revoked access | PHASE11 Pre-Closure 聚合验证 |
| Physical Delete / Restore / Verification | `canonical_ingestion_runtime` | `completion_candidate` | Input/Knowledge/Object/Verification delete receipts and persistence restore tests | PHASE11 Pre-Closure 聚合验证 |
| Legacy upload/parser 默认路径 Cutover | `temporary_versioned_adapter` | `completion_candidate` | legacy chunks normalize to CanonicalDocumentIR with ACL/source-span provenance; default worker uses ParseGateway and durable store handoff | PHASE11 Pre-Closure 聚合验证 |
