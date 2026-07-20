# Goal01 Closure Matrix

status: reopened
reopened_at: 2026-07-20
branch: `integration/goal01-control-plane-model-ingestion`
start_sha_after_fetch: `5156ed944eb797a8c41210cef19b04f023c756c0`

说明：本文记录 PHASE05、PHASE06、PHASE07、PHASE11 的有限 Closure Matrix。PHASE05、PHASE06、PHASE07 保留 `fd43babd` 中原始 Matrix 内容；PHASE11 经 Goal01 audit 重新打开，本节全部 Mandatory 行降为 `target_not_current`，不得作为 Closure Evidence 使用。

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

| 范围 | Current | Gap | Owner | 默认入口 | 状态转换 | Failure / Retry / Recovery | 测试 | Evidence | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SourceObject upload init / commit | 已有 source-lineage schema/repository 与 input runtime batch 线索 | 仍需证明生产默认 upload init/commit 进入 PostgreSQL UoW 与 PHASE04 Object Store，不以 SQLite/local object 作为完成证据 | Input / Document Ingestion | workspace/file upload commit path | initialized → committed / rejected | partial upload、hash mismatch、dedup conflict、tenant violation | 待补 PHASE11 focused integration/fault tests | `docs/evidence/phase11-ingestion-source-lineage.md` partial | `target_not_current` |
| DocumentVersion 与 ParseSnapshot 分离 | 已有表和 repository 线索 | 需证明默认路径中文档内容版本与 parser/model/config/schema snapshot 不混用，并覆盖 reparse/concurrency | Input / Document Ingestion | canonical ingestion runtime | document_version_created → parse_snapshot_created | duplicate source、reparse、optimistic conflict | 待补 persistence/concurrency tests | partial source-lineage evidence | `target_not_current` |
| ParsePlan / ParseJob / ParseAttempt | 已有 ParseAttemptControl 和 runtime batch 线索 | 需证明 ParsePlan/Job/Attempt 是生产默认 parser 调度路径，不只是本地 worker fixture | Input / Document Ingestion | parser gateway / worker | planned → queued → leased → running → succeeded / failed / cancelled | duplicate delivery、deadline、cancel、retry exhausted | 待补 integration/fault tests | partial runtime batch evidence | `target_not_current` |
| PostgreSQL Repository/UoW | 已有 ingestion persistence 线索 | 需证明完整 SourceObject→Snapshot→Outbox 在正式 PostgreSQL transaction/UoW 内提交，禁止 `create_all()` 代替 migration | Input / Platform Database | IngestionUnitOfWork | begin → commit / rollback | transaction rollback、FK violation、idempotency conflict | 待补 PostgreSQL integration tests | partial migration evidence | `target_not_current` |
| Object Store | PHASE04 已有 S3/MinIO adapter | PHASE11 默认 upload/parser 仍需接入同一 PHASE04 Object Store；不得建设第二套 Object 事实源 | Input / Infrastructure | object ref commit path | staged → committed → visible | partial upload、hash mismatch、duplicate/conflict、large payload ObjectRef | 待补 MinIO integration tests | PHASE04 evidence 可复用但未证明 PHASE11 cutover | `target_not_current` |
| RabbitMQ dispatch / ACK / retry / DLQ / replay | LocalQueue 与 RabbitMQ target-blocked probe 只保留为线索 | 缺真实 RabbitMQ production default dispatch、publisher confirm、consumer ACK、retry exhausted、DLQ、replay、reconnect、cancel/deadline、worker crash 证据 | Input / Infrastructure Queue | outbox dispatcher / parser worker consumer | outbox_pending → published → delivered → acked / nacked / dead_lettered | duplicate、redelivery、connection loss、late ACK、crash | 待补 RabbitMQ fault tests | PHASE04 queue evidence 不能自动证明 PHASE11 default path | `target_not_current` |
| Lease / Heartbeat / Fencing / Crash Recovery | 已有 lease/fencing/late-result rejection 线索 | 需证明生产 worker lease claim/renew/expire、heartbeat、fencing token、orphan reconciliation、idempotent commit | Input / Infrastructure Lease | parser worker attempt lease | claim → renew → expire / release → reconciled | lease loss、stale worker late result、worker restart | 待补 lease/crash fault tests | partial ParseAttemptControl evidence | `target_not_current` |
| Parser Adapter Contract | Native/PDF 线索存在；新增 `local_ocr_vlm` 可执行本地 OCR/VLM fallback，保留 live MinerU `measurement_blocked` 边界 | 仍缺统一 Native/PDF/Layout/OCR/VLM/Office/Archive contract 的 ObjectRef production input、timeout/cancel、安全策略、质量指标、Archive，以及 Office/Layout 生产 adapter 证据 | Input Parser Adapter Owner | parser adapter router | routed → parsed_ir / typed_failure / fallback_review | empty OCR content typed failure、corrupt/encrypted/oversized/provider failure/sandbox denial | `tests/knowledge/test_parse_gateway_runtime.py`; `tests/knowledge/test_document_ingestion_contract.py`; `tests/api/test_workspace_durable_ingest_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/router.py`; `src/backend/zuno/knowledge/ingestion/adapters.py`; `src/backend/zuno/knowledge/ingestion/gateway.py` | `target_not_current` |
| CanonicalDocumentIR | 已有 ingestion contract tests 线索 | 需证明 schema round-trip、page/block/region/order/style/table/image refs，且 IR 不等于 Knowledge Chunk | Input / Document Ingestion | parser output contract | parsed → canonical_ir_validated | schema mismatch、normalization failure | 待补 golden/contract tests | partial contract evidence | `target_not_current` |
| SourceSpan / TransformLedger | SourceSpan provenance 与 TransformRecord 线索存在 | 需证明 PDF citation、OCR bbox、table span、normalization provenance 可稳定回溯原始证据 | Input / Document Ingestion | source span builder | source_span_created → transform_recorded | missing coordinate、unstable span、normalization loss | 待补 golden/source-lineage tests | partial input runtime batch evidence | `target_not_current` |
| Quality Gate / Human Review | 新增 `HumanReviewRuntime`、QualityMetric、ReviewTask、ReviewDecisionReceipt 与 SQLite baseline 持久化；workspace OCR fallback 进入 `review_pending`，未批准前不写 IndexManifest/IndexChunk | 仍缺 PostgreSQL production default review tables/receipts、跨 worker 并发、expiration scheduler、review approval 后 snapshot handoff，以及 RabbitMQ/MinIO 默认链路证据 | Input Quality / Human Review | quality gate before snapshot publish | measured → pass / block / review / fallback → approved / rejected / expired / cancelled | low confidence、reviewer scope mismatch、security epoch mismatch、duplicate decision、expiration、cancelled | `tests/knowledge/test_ingestion_human_review.py`; `tests/api/test_workspace_durable_ingest_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/review.py`; `src/backend/zuno/api/services/workspace_task_runtime.py`; local SQLite review tables | `target_not_current` |
| IndexableDocumentSnapshot Outbox Handoff | Indexable snapshot persistence 与 outbox handoff 线索存在 | 需证明 immutable snapshot hash、version/span/security/delete refs、idempotency key、duplicate handoff、outbox replay、Knowledge unavailable recovery | Input / Knowledge Handoff | snapshot handoff outbox | snapshot_ready → outbox_pending → handed_off / replayed | duplicate handoff、knowledge unavailable、outbox replay | 待补 handoff integration/fault tests | partial source-lineage evidence | `target_not_current` |
| Delete / Legal Hold / Restore / Verification | 删除 receipt、legal hold、restore verification 线索存在 | 需证明 visibility revoke → cleanup request → physical delete → verification 的完整顺序，覆盖 delete during parse/after snapshot/duplicate/late result/restore 不恢复撤销授权 | Input / Security / Knowledge Handoff | delete lifecycle command | visibility_revoked → cleanup_requested → physically_deleted → verified / restored | legal hold、orphan attempt、late worker result、duplicate delete | 待补 delete/restore fault tests | partial input runtime batch evidence | `target_not_current` |
| Legacy upload/parser Cutover | default worker uses ParseGateway 的线索存在；活跃入口清单已记录 `/upload`、workspace attachment、knowledge pipeline、legacy doc_parser、ParseGateway 与 local durable runtime | 仍需迁移 `workspace/attachment_service.py` 与 `pipeline/manager.py` 的 legacy parser 默认调用，并把旧 doc_parser 版本化为统一 Parser Adapter 或删除；禁止永久 dual-write/dual-runtime/implicit fallback | Input / Product Surface | active upload/parser API and worker entrypoints | legacy_active → canonical / versioned_adapter / removed | hidden fallback、dual runtime、ownerless parser | `tests/repo/test_phase11_legacy_upload_parser_cutover.py` | `.agent/programs/work-products/phase11-legacy-upload-parser-cutover-inventory.md`; `tools/scripts/verify_phase11_legacy_upload_parser_cutover.py`; cutover inventory | `target_not_current` |

## 2026-07-20 PHASE11 Reopen Audit

PHASE11 section 的旧 `completion_candidate` 全部降为 `target_not_current`。已有证据保留为线索，但 LocalQueue、SQLite runtime batch、target-blocked OCR/VLM 和不完整 Human Review 不能关闭 PHASE11。

PHASE08 保持 `ready`，因为它只依赖 PHASE04–PHASE07。PHASE12 保持 `planned`，等待 PHASE08 completed 与 PHASE11 completed。
