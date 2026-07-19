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
| Admin 管理面：Agent / Tool / Dialog / MCP Agent / LLM / Knowledge / Knowledge File | `canonical_security_guard` | `mandatory_open` | 当前 worktree 已接入共享 `security_admin_actions`，focused tests 已初步通过，尚未写入 verifier/evidence/commit | 完成 verifier、Evidence、Audit、focused tests、commit |
| Secret Lease | `canonical_security_guard` | `completion_candidate` | `SecurityRepository.record_secret_ref` / `issue_secret_lease` / `validate_secret_lease` 覆盖 wrong audience、expired lease、revoked secret | Pre-Closure 前聚合验证 |
| External Export | `future_runtime_not_current` | `not_current` | 当前 active runtime 无正式 external export 默认路径；PHASE06 external sink isolation 已证明外部 sink 不冒充业务成功 | 归属后续 Product/Publication/Integration Phase，不能阻塞 PHASE05 当前默认路径 closure |
| Legacy Approval Boolean 到 Decision/Ref | `temporary_versioned_adapter` | `completion_candidate` | Tool Runtime `approved: bool` 已绑定 `temporary.adapter.tool_runtime.approved_bool` 与删除 Phase `PHASE16`；workspace 默认 resume path 已传入 `security-approval-decision:*` decision ref；PHASE05 verifier 阻止新增 legacy boolean owner | Pre-Closure 前聚合验证 |

## PHASE06 Adapter Cutover Matrix

| 运行域 | Producer | Envelope / Adapter | 默认接线点 | 失败策略 | 状态 | 剩余处理 |
| --- | --- | --- | --- | --- | --- | --- |
| Agent | Agent runtime / workspace runtime | typed runtime event / span adapter | workspace runtime security and retrieval spans | local append-only first | `completion_candidate` | 聚合验证 |
| Model | Model Gateway runtime | model attempt / runtime event envelope | Gateway-owned call path | provider failure becomes attempt failure, not audit success | `mandatory_open` | 与 PHASE07 closure dependency 对齐 |
| Knowledge | Agentic retrieval / ingestion | retrieval trace / citation metrics | workspace retrieval observability | raw event retained, query freshness exposed | `completion_candidate` | 聚合验证 |
| Capability | Capability / Skill runtime | capability plan/runtime event | workspace capability snapshot | local facts persist before external sink | `completion_candidate` | 聚合验证 |
| Tool | Tool Runtime | approval/security span adapter | Tool Runtime approval path | sink outage fail-closed before side effect | `completion_candidate` | 聚合验证 |
| Security | Security repository / audit | immutable audit ledger adapter | Security pre-effect/audit facts | audit not sampled; failure visible | `completion_candidate` | 聚合验证 |
| Infrastructure | DB / outbox / external sink | dead-letter and local fact envelope | observability persistence adapter | external sink failure does not roll back local facts | `completion_candidate` | 聚合验证 |
| Product Query | Observability query service | read-only freshness/completeness response | product query service | returns freshness/completeness and dead letters | `completion_candidate` | FastAPI route wiring 若 Matrix 审核要求，否则作为 service-level default evidence |

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
| Trace / Audit 接入 | `depends_on_phase06` | `mandatory_open` | PHASE06 adapter closure 未正式批准 | 等 PHASE06 Closure |
| Chat / Embedding / Rerank / Judge 默认路径 | `canonical_gateway_runtime` | `completion_candidate` | default entry tests and bypass guard | PHASE05/06 Closure 后进入 PHASE07 closure review |

## PHASE11 Ingestion Closure Matrix

| 范围 | 当前归类 | 状态 | 证据 | 剩余处理 |
| --- | --- | --- | --- | --- |
| SourceObject upload init / commit | `canonical_ingestion_runtime` | `partial_evidence` | source-lineage schema/repository partial | PHASE05 closure 后继续实现/验证 |
| DocumentVersion / ParseSnapshot 分离 | `canonical_ingestion_runtime` | `partial_evidence` | source-lineage schema partial | PHASE05 closure 后继续实现/验证 |
| ParsePlan / Job / Attempt | `canonical_ingestion_runtime` | `partial_evidence` | existing parse gateway/runtime tests | 补 durable runtime evidence |
| RabbitMQ dispatch / ACK / Retry / Dead Letter | `canonical_ingestion_runtime` | `mandatory_open` | 当前目标文件明确禁止 schema 冒充完成 | PHASE05 closure 后实现/验证 |
| Lease / Heartbeat / Fencing / Worker Crash Recovery | `canonical_ingestion_runtime` | `mandatory_open` | async infrastructure partial | PHASE05 closure 后实现/验证 |
| Native / PDF / Layout / OCR / VLM / Office / Archive Adapter | `mixed_current_future` | `mandatory_open` | native/PDF/Office partial tests, OCR/VLM/archive 未完整 closure | PHASE05 closure 后按 adapter owner 收口 |
| CanonicalDocumentIR | `canonical_ingestion_runtime` | `completion_candidate` | ingestion contract tests | 聚合验证 |
| SourceSpan / TransformLedger | `canonical_ingestion_runtime` | `partial_evidence` | source span tests; TransformLedger incomplete | PHASE05 closure 后补齐 |
| Quality Gate / Human Review | `canonical_ingestion_runtime` | `mandatory_open` | quality threshold partial | PHASE05 closure 后实现/验证 |
| IndexableDocumentSnapshot Outbox Handoff | `canonical_ingestion_runtime` | `partial_evidence` | index handoff tests | PHASE05 closure 后补 durable outbox handoff |
| Visibility Revoke | `canonical_ingestion_runtime` | `mandatory_open` | no closure evidence | PHASE05 closure 后实现/验证 |
| Legal Hold | `canonical_ingestion_runtime` | `mandatory_open` | no closure evidence | PHASE05 closure 后实现/验证 |
| Physical Delete / Restore / Verification | `canonical_ingestion_runtime` | `mandatory_open` | no closure evidence | PHASE05 closure 后实现/验证 |
| Legacy upload/parser 默认路径 Cutover | `temporary_versioned_adapter` | `mandatory_open` | legacy upload/parser paths still exist | PHASE05 closure 后 migrate/cutover/verify |
