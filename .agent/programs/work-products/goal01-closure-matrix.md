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
| SourceObject upload init / commit | 已有 source-lineage schema/repository 与 input runtime batch 线索；新增 `SourceObjectUploadRuntime` 编排 upload init → stage → commit，进入 PHASE04 durable object store ticket/receipt 后再交给 `SourceObjectCommitRuntime`，覆盖 content hash、mime、size、classification、object manifest、tenant/workspace prefix、partial upload、hash mismatch、dedup receipt、immutable SourceObject 与 ObjectRef-only payload | 仍需证明 workspace/file upload 生产默认入口接入 PostgreSQL UoW、PHASE04 `DurableMinioObjectStore` 与 object manifest 同事务；当前 fake durable store 测试只证明合约编排，不证明真实 MinIO / PostgreSQL 端到端 | Input / Document Ingestion | workspace/file upload commit path | initialized → staged → committed / rejected / deduplicated | partial upload、hash mismatch、dedup conflict、tenant violation、immutable hash conflict | `tests/knowledge/test_ingestion_source_object_upload.py`; `tests/knowledge/test_ingestion_source_object_commit.py` | `src/backend/zuno/knowledge/ingestion/source_object_upload.py`; `src/backend/zuno/knowledge/ingestion/source_object_commit.py`; `docs/evidence/phase11-ingestion-source-lineage.md` partial | `target_not_current` |
| DocumentVersion 与 ParseSnapshot 分离 | 已有表和 repository 线索 | 需证明默认路径中文档内容版本与 parser/model/config/schema snapshot 不混用，并覆盖 reparse/concurrency | Input / Document Ingestion | canonical ingestion runtime | document_version_created → parse_snapshot_created | duplicate source、reparse、optimistic conflict | 待补 persistence/concurrency tests | partial source-lineage evidence | `target_not_current` |
| ParsePlan / ParseJob / ParseAttempt | 已有 ParseAttemptControl 和 runtime batch 线索；新增 `ParseControlRuntime` 显式串起 ParsePlan / queued job / attempt lease / worker run，覆盖 planned → queued → leased → running → succeeded / cancelled / dead_letter，成功路径用 fencing token 提交 lease，stale fencing token 被拒绝，failed parse 可按 retry policy 进入 dead_letter | 仍缺生产默认 parser worker 接入 PostgreSQL UoW、RabbitMQ delivery/ACK、deadline/cancel 跨 worker、duplicate delivery 和真实 worker crash fault evidence；当前仍是本地 control runtime 证据 | Input / Document Ingestion | parser gateway / worker | planned → queued → leased → running → succeeded / failed / cancelled / dead_letter | duplicate delivery、deadline、cancel、retry exhausted、stale fencing token | `tests/knowledge/test_ingestion_parse_control.py`; `tests/knowledge/test_parse_gateway_runtime.py`; `tests/knowledge/test_ingestion_lease_recovery.py` | `src/backend/zuno/knowledge/ingestion/parse_control.py`; `src/backend/zuno/knowledge/ingestion/gateway.py`; `src/backend/zuno/knowledge/ingestion/lease.py`; partial runtime batch evidence | `target_not_current` |
| PostgreSQL Repository/UoW | 已有 `IngestionUnitOfWork` 与 PostgreSQL migration；integration test 覆盖 SourceObject→DocumentVersion→ParsePlan→ParseJob→ParseAttempt→ParseSnapshot→SourceSpan→QualityDecision→IndexableSnapshot→Outbox 同 transaction 写入、quality FK 拒绝、source hash validation、rollback 与 tenant-scoped idempotency conflict | 仍缺 workspace/file upload 与 parser worker 的生产默认接线、真实 PostgreSQL 环境下与 PHASE04 Object Store / RabbitMQ outbox publisher 的端到端故障证据；禁止 `create_all()` 代替 migration | Input / Platform Database | IngestionUnitOfWork | begin → commit / rollback | transaction rollback、FK violation、idempotency conflict | `tests/integration/test_phase11_ingestion_persistence_runtime.py`; `tests/repo/test_phase11_ingestion_source_lineage.py` | `src/backend/zuno/platform/database/ingestion/persistence.py`; `infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py`; `docs/evidence/phase11-ingestion-source-lineage.md` | `target_not_current` |
| Object Store | PHASE04 已有 S3/MinIO adapter；新增 `SourceObjectUploadRuntime` 与 `SourceObjectCommitRuntime` 消费 PHASE04 ticket / `ObjectStoreReceipt` 并生成 PHASE11 `SourceObjectRecord`，覆盖 visible receipt、object manifest ref、tenant/workspace prefix、hash、size、mime、classification、security epoch、ObjectRef-only payload 与本地 dedup receipt | 仍缺 workspace/file upload 默认入口真实接入 PHASE04 `DurableMinioObjectStore`、PostgreSQL manifest 同事务 evidence、large multipart、partial upload cleanup、duplicate/conflict 的数据库唯一约束、真实 MinIO fault/restart 与 parser worker 读前 re-verify | Input / Infrastructure | object ref commit path | initialized → staged → committed → visible | partial upload、hash mismatch、duplicate/conflict、large payload ObjectRef、manifest drift | `tests/knowledge/test_ingestion_source_object_upload.py`; `tests/knowledge/test_ingestion_source_object_commit.py` | `src/backend/zuno/knowledge/ingestion/source_object_upload.py`; `src/backend/zuno/knowledge/ingestion/source_object_commit.py`; PHASE04 `src/backend/zuno/platform/storage/object_store.py`; PHASE04 `src/backend/zuno/platform/storage/durable.py` | `target_not_current` |
| RabbitMQ dispatch / ACK / retry / DLQ / replay | LocalQueue 与 RabbitMQ target-blocked probe 只保留为线索；新增本地 `ack_after_domain_commit` guard，领域提交成功后才 ACK，领域提交失败先 retry/requeue，重试耗尽进入 dead letter；ParserWorker 的 OCR/VLM review-required 成功结果进入 `review_pending`，不会 enqueue index | 缺真实 RabbitMQ production default dispatch、publisher confirm、consumer ACK、retry exhausted、DLQ、replay、reconnect、cancel/deadline、worker crash 证据；当前 LocalQueue guard 只证明 consumer ACK 协议语义，不证明 broker confirm / reconnect / redelivery | Input / Infrastructure Queue | outbox dispatcher / parser worker consumer | outbox_pending → published → delivered → domain_committed → acked / retrying / dead_lettered | duplicate、redelivery、connection loss、late ACK、crash、domain commit failure | `tests/knowledge/test_ingestion_async_infrastructure.py` | `src/backend/zuno/knowledge/ingestion/async_runtime.py`; PHASE04 queue evidence 不能自动证明 PHASE11 default path | `target_not_current` |
| Lease / Heartbeat / Fencing / Crash Recovery | 新增 `ParseAttemptLeaseRuntime`、`ParseAttemptLeaseReceipt` 与 SQLite baseline；覆盖 claim、heartbeat renew、expire、orphan reconciliation、worker restart 后新 fencing token、stale worker late result rejection、current-token commit 与 idempotent duplicate commit | 仍缺生产 parser worker 默认接线、PostgreSQL UoW lease table/migration、RabbitMQ delivery/ACK 边界下的 crash fault、lease loss 后真实 worker restart/replay 证据 | Input / Infrastructure Lease | parser worker attempt lease | claim → renew → expire / release → reconciled / committed | lease loss、stale worker late result、worker restart、duplicate commit | `tests/knowledge/test_ingestion_lease_recovery.py` | `src/backend/zuno/knowledge/ingestion/lease.py`; local SQLite parse attempt lease table | `target_not_current` |
| Parser Adapter Contract | Native/PDF 线索存在；新增 `local_ocr_vlm` 可执行本地 OCR/VLM fallback；新增 `local_office_archive` 可执行 Office/Archive fallback，覆盖 docx/xlsx heading/table、pptx slide/figure、archive manifest-only no-unpack、unsafe archive typed failure；Parser Gateway 已接受显式 `source_object_ref` / manifest 输入并在 adapter 前校验 ObjectRef、hash、size、parser policy、lineage、workspace scope，ParseJobSnapshot 记录 security policy、security epoch、timeout、source input mode、quality confidence，hash mismatch、oversized、encrypted、corrupt、sandbox denied 与 cancel-before-adapter 进入 typed failure / cancelled；live MinerU 与 Unstructured / MarkItDown 保留 `measurement_blocked` 边界 | 仍缺生产默认 worker 从 PHASE04 Object Store 读取 ObjectRef 并写入 PostgreSQL UoW 的端到端接线、安全策略跨 worker 强制、真实 Office/Layout production adapter、真实 provider failure 与真实 sandbox runtime fault evidence | Input Parser Adapter Owner | parser adapter router | routed → parsed_ir / typed_failure / fallback_review | empty OCR content typed failure、unsafe archive、ObjectRef hash mismatch、cancel before adapter、corrupt/encrypted/oversized/provider failure/sandbox denial | `tests/knowledge/test_parse_gateway_runtime.py`; `tests/knowledge/test_document_ingestion_contract.py`; `tests/api/test_workspace_durable_ingest_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/contracts.py`; `src/backend/zuno/knowledge/ingestion/router.py`; `src/backend/zuno/knowledge/ingestion/adapters.py`; `src/backend/zuno/knowledge/ingestion/gateway.py` | `target_not_current` |
| CanonicalDocumentIR | 新增 schema round-trip helper 与 contract report；`CanonicalDocumentIR` 显式携带 TransformLedgerEntry、block order/style、table/image refs，contract tests 证明 round-trip、page/block/region/order/style/table/image refs，且 IR SourceSpan 不携带 Knowledge chunk id、Input IR 不创建 Chunk/Entity/Relation/KnowledgeVersion | 仍缺覆盖全部 parser golden fixtures 的 schema mismatch / normalization failure fault tests，以及 PostgreSQL ParseSnapshot 默认持久化后的 round-trip 证据 | Input / Document Ingestion | parser output contract | parsed → canonical_ir_validated | schema mismatch、normalization failure | `tests/knowledge/test_document_ingestion_contract.py`; `tests/knowledge/test_parse_gateway_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/contracts.py`; `src/backend/zuno/knowledge/ingestion/gateway.py`; `docs/evidence/phase11-ingestion-source-lineage.md` | `target_not_current` |
| SourceSpan / TransformLedger | SourceSpan provenance 与 TransformRecord 线索存在；新增 gateway 成功路径 TransformLedgerEntry，绑定 source hash、parser/version/config/schema、block/table/figure counts 与输出 hash；contract tests 覆盖 PDF page/bbox/region、slide bbox、table span、image ref、normalization raw/normalized text 与 no Knowledge chunk id | 仍缺 PostgreSQL ParseSnapshot / SourceSpan 表默认写入后的 stable backlink 证据、OCR bbox golden、跨 parser normalization-loss fault、TransformLedger 持久化与 replay evidence | Input / Document Ingestion | source span builder | source_span_created → transform_recorded | missing coordinate、unstable span、normalization loss | `tests/knowledge/test_document_ingestion_contract.py`; `tests/knowledge/test_parse_gateway_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/contracts.py`; `src/backend/zuno/knowledge/ingestion/gateway.py`; partial input runtime batch evidence | `target_not_current` |
| Quality Gate / Human Review | 新增 `HumanReviewRuntime`、QualityMetric、ReviewTask、ReviewDecisionReceipt 与 SQLite baseline 持久化；workspace OCR fallback 进入 `review_pending`，未批准前不写 IndexManifest/IndexChunk；ParserWorker 现在对 review-required OCR/VLM fallback 进入 `review_pending` 且不 enqueue index；Snapshot handoff 现在对 REVIEW gate fail-closed，只有 approved `ReviewDecisionReceipt` 才允许生成 `IndexableDocumentSnapshotV1`；新增本地 expiration sweep，只把 overdue pending task 转换为 expired receipt，已有 receipt 或未到期 task 会跳过 | 仍缺 PostgreSQL production default review tables/receipts、跨 worker 并发、review approval 后生产 worker handoff、expiration sweep 的持久化调度接线，以及 RabbitMQ/MinIO 默认链路证据 | Input Quality / Human Review | quality gate before snapshot publish | measured → pass / block / review / fallback → approved / rejected / expired / cancelled / review_pending | low confidence、reviewer scope mismatch、security epoch mismatch、duplicate decision、expiration sweep、cancelled、unapproved handoff rejected | `tests/knowledge/test_ingestion_human_review.py`; `tests/knowledge/test_ingestion_snapshot_handoff.py`; `tests/knowledge/test_ingestion_async_infrastructure.py`; `tests/api/test_workspace_durable_ingest_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/review.py`; `src/backend/zuno/knowledge/ingestion/handoff.py`; `src/backend/zuno/knowledge/ingestion/async_runtime.py`; `src/backend/zuno/api/services/workspace_task_runtime.py`; local SQLite review tables | `target_not_current` |
| IndexableDocumentSnapshot Outbox Handoff | 新增 `IndexableDocumentSnapshotV1`、canonical hash、idempotency key、security/delete refs 与 pending outbox；workspace 成功路径先生成 snapshot/outbox，再由本地 consumer index；REVIEW gate 未批准时 handoff 层拒绝 snapshot，批准 receipt 会写入 snapshot payload / security refs 并生成 pending outbox；新增本地 outbox dispatch receipt，Knowledge unavailable 时保持 pending 并增加 replay_count，后续 replay 成功才返回 handed_off / acknowledged | 仍缺 PostgreSQL production UoW 默认写入、RabbitMQ outbox publisher/confirm/replay 接线、review approval 后生产 worker handoff，以及真实 duplicate delivery/replay fault evidence | Input / Knowledge Handoff | snapshot handoff outbox | snapshot_ready → outbox_pending → replay_pending / handed_off | duplicate handoff、knowledge unavailable、outbox replay、unapproved review handoff blocked | `tests/knowledge/test_ingestion_snapshot_handoff.py`; `tests/api/test_workspace_durable_ingest_runtime.py` focused subset | `src/backend/zuno/knowledge/ingestion/handoff.py`; `src/backend/zuno/api/services/workspace_task_runtime.py`; local SQLite snapshot/outbox tables | `target_not_current` |
| Delete / Legal Hold / Restore / Verification | 新增 `DeleteRestoreRuntime`、DeleteLifecycleReceipt 与 SQLite baseline；覆盖 visibility revoke → cleanup request → physical delete → verification、legal hold、duplicate delete、late worker result rejection、restore 不恢复授权；snapshot handoff 可携带 delete refs；delete during parse 现在绑定 parse job、parse attempt 与 fencing token；delete after snapshot 现在绑定 IndexableDocumentSnapshot、handoff outbox event 与 projection cleanup ref，verification 必须确认 projection cleanup 和物理删除；verified delete 后拒绝 late worker result，legal hold 阻止 cleanup / physical delete | 仍缺 PostgreSQL production UoW 默认写入、对象存储真实物理删除、delete during parse/after snapshot 的真实跨 worker fault evidence、RabbitMQ cleanup/replay 与恢复审批接线 | Input / Security / Knowledge Handoff | delete lifecycle command | visibility_revoked → cleanup_requested → physically_deleted → verified / legal_hold / restored | legal hold、delete during parse、delete after snapshot、duplicate delete、late worker result、restore authorization isolation、verification evidence missing | `tests/knowledge/test_ingestion_delete_restore.py`; `tests/knowledge/test_ingestion_lease_recovery.py`; `tests/knowledge/test_ingestion_snapshot_handoff.py` focused subset | `src/backend/zuno/knowledge/ingestion/delete_restore.py`; `src/backend/zuno/knowledge/ingestion/lease.py`; local SQLite delete lifecycle table; snapshot delete_refs | `target_not_current` |
| Legacy upload/parser Cutover | default worker uses ParseGateway 的线索存在；活跃入口清单已记录 `/upload`、workspace attachment、knowledge pipeline、legacy doc_parser、ParseGateway 与 local durable runtime；新增 `temporary.adapter.phase11.legacy_chunk_projection`，workspace 文档附件与 knowledge pipeline `_parse_chunks` 已先经 ParseGateway 生成 CanonicalDocumentIR，再显式投影为旧 ChunkModel | 仍需迁移 workspace 图片 `_image_to_text`、旧 Knowledge RAG/Graph chunk/fact 写入、legacy doc_parser 其他调用，并把默认生产路径接入 SourceObject / PostgreSQL UoW / Quality Gate / IndexableDocumentSnapshot / Outbox；禁止永久 dual-write/dual-runtime/implicit fallback | Input / Product Surface | active upload/parser API and worker entrypoints | legacy_active → canonical / versioned_adapter / removed | hidden fallback、dual runtime、ownerless parser、legacy chunk projection removal | `tests/repo/test_phase11_legacy_upload_parser_cutover.py`; `tests/knowledge/test_legacy_cutover_adapter.py`; `tests/storage/test_pipeline.py` focused subset | cutover inventory：`.agent/programs/work-products/phase11-legacy-upload-parser-cutover-inventory.md`; `tools/scripts/verify_phase11_legacy_upload_parser_cutover.py`; `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` | `target_not_current` |

## 2026-07-20 PHASE11 Reopen Audit

PHASE11 section 的旧 `completion_candidate` 全部降为 `target_not_current`。已有证据保留为线索，但 LocalQueue、SQLite runtime batch、target-blocked OCR/VLM 和不完整 Human Review 不能关闭 PHASE11。

### Package A implementation progress 2026-07-20

已新增 Package A runtime、migration 与测试入口：

- `PackageAProductionIngestionRuntime` 串接 Workspace/File Upload accept、PHASE04 `DurableMinioObjectStore`、PostgreSQL `IngestionUnitOfWork`、PHASE04 infra outbox、RabbitMQ delivery payload、Parser Worker、Parser Gateway、ParseSnapshot、SourceSpan、Quality Gate、IndexableDocumentSnapshot 和 Snapshot Outbox。
- `WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(...)` 提供生产默认接线；配置存在时 file register 返回 `ingest_accepted`，不进行同步解析完成。
- Parser Gateway 与 ParseControl 修正权威 Job/Attempt ID、Plan/Job/Attempt 分离、retry 新 Attempt 和 `max_attempts` off-by-one。
- 新 migration `20260720_19_ingestion_package_a_control.py` 补充 ParseAttempt 上下文绑定、lease/fencing 表、DLQ 关联、状态约束与索引。
- 新测试 `tests/integration/test_phase11_package_a_production_runtime.py` 覆盖 Gate B/Gate C 入口。

验证结果：

```text
Gate A passed: pytest -q tests/knowledge/test_ingestion_parse_control.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
Alembic heads: 20260720_19
Gate B environment_blocked: PostgreSQL localhost:5432 connection timeout
Gate C environment_blocked: Docker daemon unavailable, PostgreSQL localhost:5432 connection timeout before MinIO/RabbitMQ step
```

本注记不改变上表 `target_not_current` 状态；Package A 行只有在真实 PostgreSQL、MinIO、RabbitMQ Gate B/C 通过后才能逐项提升为 `completion_candidate`。

2026-07-20 follow-up：

```text
RabbitMQ ACK moved after IngestionUnitOfWork commit boundary.
retryable failed closes current Attempt/Lease, writes a new parse.requested outbox for the next Attempt, then ACKs the current message after commit.
duplicate/succeeded/dead_letter/retryable_failed ACK only after domain transaction exits successfully.
fail_parse_attempt now updates ingestion_parse_leases to released/lost terminal state in the same transaction.
Gate A remains passed; Gate B remains environment_blocked at PostgreSQL localhost:5432.
```

2026-07-20 retry-boundary test addition：

```text
Added Gate B integration coverage for retryable failure:
failed Attempt + released Lease + queued Job + new parse.requested outbox + ACK current delivery after commit + no same-message NACK/requeue.
py_compile passed.
Docker daemon remains unavailable; the new Gate B test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 duplicate-redelivery test addition：

```text
Added Gate B integration coverage for duplicate/redelivery:
existing worker inbox receipt + no Parser Gateway call + no Attempt/Lease/Snapshot creation + no extra Outbox + ACK current delivery after commit.
py_compile passed.
Docker daemon remains unavailable; the new Gate B test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 non-retryable-DLQ test addition：

```text
Added Gate B integration coverage for non-retryable failure:
dead_letter Attempt + released Lease + dead_letter Job + PostgreSQL dead-letter receipt with RabbitMQ DLQ ref + ACK current delivery after commit + no retry outbox.
py_compile passed.
Docker daemon remains unavailable; the new Gate B test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 worker-object-verifier hardening：

```text
Runtime now checks delivery security_epoch_ref against SourceObject security_epoch_ref before leasing.
Worker ObjectRef verifier now rejects tenant/workspace scope escape, hash mismatch, size mismatch, and non-committed/revoked source visibility.
Added fault coverage for scope escape + hash mismatch + revoked visibility.
py_compile passed; worker object verifier fault test passed: 1 passed.
Docker daemon remains unavailable; Gate C real MinIO/RabbitMQ E2E is still environment_blocked at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 crash-after-commit-before-ACK replay hardening：

```text
Duplicate/redelivery branch now queries PostgreSQL replay receipt and returns existing terminal result when the domain transaction already committed.
Succeeded redelivery can return original Attempt, IndexableSnapshot, and Snapshot outbox without reparsing.
Added Gate B integration coverage for committed-domain redelivery after lost ACK.
py_compile passed.
Docker daemon remains unavailable; the new Gate B replay test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 cancel-deadline worker path：

```text
Runtime now handles cancel_requested and expired deadline after Attempt/Lease claim and before ObjectRef read/Parser Gateway call.
Cancel/deadline closes Attempt as cancelled, releases Lease, sets Job cancelled, emits no Snapshot/IndexableSnapshot/SnapshotOutbox, and ACKs after domain commit.
Added Gate B integration coverage for cancel_requested path.
py_compile passed.
Docker daemon remains unavailable; the new Gate B cancel test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 lease-heartbeat-reconcile path：

```text
Runtime now performs a fenced heartbeat/lease renew after running state and before ObjectRef read / Parser Gateway call.
Repository now supports renew_parse_attempt_lease and reconcile_expired_parse_attempt_lease.
Expired Lease reconciliation sets Lease expired, Attempt lease_lost, and Job queued for later reclaim.
Added Gate B integration coverage for heartbeat renewal and expired lease reconciliation.
py_compile passed.
Docker daemon remains unavailable; the new Gate B heartbeat/reconcile test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 outbox-publish-failure replay coverage：

```text
Added Gate C integration coverage for Package A parse.requested outbox publish failure:
PostgresOutboxRabbitMQPublisher.publish_batch records failure, leaves outbox pending/replayable, releases claim, and allows later publisher reclaim.
py_compile passed.
Docker daemon remains unavailable; the new Gate C outbox publish failure test is environment_blocked before assertions at PostgreSQL localhost:5432 alembic upgrade.
```

2026-07-20 workspace upload production-default bootstrap：

```text
Application startup now configures WorkspaceTaskRuntimeService with PackageAProductionIngestionRuntime when production MinIO storage configuration is complete.
The factory binds the current PostgreSQL engine, PHASE04 MinioObjectStore/DurableMinioObjectStore, and worker owner workspace.file_upload.
Workspace /file registration therefore has a production-default path into SourceObject -> DocumentVersion -> ParsePlan -> ParseJob -> Outbox when MinIO credentials are configured.
If MinIO config is absent or incomplete, the runtime remains unconfigured instead of silently falling back to SQLite/LocalQueue as completion evidence.
py_compile passed.
Package A bootstrap tests passed: 2 passed.
Worker ObjectRef verifier fault test passed: 1 passed.
Docker daemon and PostgreSQL localhost:5432 remain unavailable, so real Gate C MinIO/RabbitMQ/PostgreSQL E2E remains environment_blocked.
```

2026-07-20 Package A RabbitMQ worker bootstrap：

```text
Added PackageAProductionQueueWorker to connect the PHASE04 Postgres outbox publisher, canonical RabbitMQ topology/consumer, and PackageAProductionIngestionRuntime.process_rabbitmq_delivery.
ACK/NACK/Reject ownership remains inside PackageAProductionIngestionRuntime after the PostgreSQL domain transaction boundary.
Queue runner now defaults to Package A ingestion worker when rabbitmq.enabled is true unless package_a_ingestion_enabled is explicitly false.
Added tests for canonical topology defaults, publish -> consume -> runtime handoff order, and queue runner default selection.
py_compile passed.
Package A queue worker tests passed: 3 passed.
PHASE11 remains in_progress; real Gate C still needs Docker/PostgreSQL/MinIO/RabbitMQ runtime availability.
```

2026-07-20 Package A outbox tenant dispatch fix：

```text
PostgresOutboxRabbitMQPublisher now supports tenant_id=None for cross-tenant dispatcher workers while keeping fixed-tenant mismatch protection when tenant_id is configured.
PackageAProductionQueueWorker and the queue runner no longer default the dispatcher tenant to system; RabbitMQ message tenant headers come from each outbox record.
This removes the default Outbox -> RabbitMQ blocker for workspace uploads created under real user tenant IDs.
py_compile passed.
Package A queue worker tenant dispatch tests passed: 5 passed.
PHASE11 remains in_progress; this is implementation evidence for Package A dispatch wiring, not real Gate C completion.
```

2026-07-20 Package A bounded RabbitMQ pump：

```text
PackageAProductionQueueWorker now consumes a bounded delivery batch after publishing a pending outbox batch.
consume_limit defaults to publish_limit, and runner config can override ingestion_publish_limit, ingestion_consume_limit, and ingestion_consume_timeout_seconds.
Each RabbitMQ delivery still enters PackageAProductionIngestionRuntime separately, preserving ACK-after-domain-commit ownership inside the runtime.
py_compile passed.
Package A queue worker bounded batch tests passed: 6 passed.
PHASE11 remains in_progress; real Gate C still needs live PostgreSQL/MinIO/RabbitMQ verification.
```

2026-07-20 Package A topic-scoped outbox dispatch：

```text
InfrastructureRepository.claim_outbox now supports topic-scoped claiming before FOR UPDATE SKIP LOCKED.
PostgresOutboxRabbitMQPublisher passes optional topics into the claim step while retaining generic behavior when topics is unset.
PackageAProductionQueueWorker claims only ingestion.parse.requested events for the parse queue, preventing unrelated Snapshot or module outbox events from being published to the parser worker.
py_compile passed.
Package A queue worker topic dispatch tests passed: 7 passed.
PHASE11 remains in_progress; this is Package A dispatch correctness evidence, not Gate C completion.
```

2026-07-20 Package A RabbitMQ DLQ settlement：

```text
PackageAProductionIngestionRuntime now settles dead_letter receipts with delivery.reject(requeue=False) after the PostgreSQL domain transaction exits successfully.
Success, retry-enqueued, cancelled, and duplicate/redelivery receipts continue to ACK after domain commit.
PackageAWorkerReceipt.acked_after_domain_commit is false for dead_letter so runtime evidence no longer claims RabbitMQ ACK for DLQ cases.
Updated non-retryable DLQ integration expectations to require reject instead of ACK.
py_compile passed.
Package A delivery settlement tests passed: 2 passed.
Worker ObjectRef verifier fault test passed: 1 passed.
PHASE11 remains in_progress; live RabbitMQ DLQ verification still belongs to Gate C.
```

2026-07-20 Package A poison delivery rejection：

```text
Invalid Package A RabbitMQ deliveries now reject(requeue=false) before PostgreSQL UoW when CanonicalOutboxDelivery schema validation, payload hash verification, or envelope consistency fails.
Poison messages do not claim ParseAttempt/Lease and do not loop forever on the canonical parse queue.
py_compile passed.
Package A delivery settlement poison-message tests passed: 4 passed.
PHASE11 remains in_progress; live RabbitMQ poison-message behavior still needs Gate C.
```

2026-07-20 Package A retry exhaustion boundary：

```text
PackageAProductionIngestionRuntime now centralizes retry/DLQ terminal status classification.
max_attempts includes the first execution: retryable first failure with max_attempts=2 queues retry, second failure dead-letters.
Non-retryable failure dead-letters on the first attempt.
py_compile passed.
Package A retry boundary tests passed: 3 passed.
PHASE11 remains in_progress; PostgreSQL-backed retry/DLQ integration remains Gate B/C evidence.
```

2026-07-20 Package A misrouted delivery rejection：

```text
PackageAProductionIngestionRuntime now rejects(requeue=false) deliveries whose RabbitMQ topic, envelope contract_name, or consumer_module does not match the Package A parse request contract.
Misrouted deliveries are rejected before PostgreSQL inbox, ParseJob lookup, or Attempt/Lease claim.
PackageAProductionQueueWorker reuses the runtime parse-requested topic constant for dispatch scope.
py_compile passed.
Package A delivery settlement misroute tests passed: 7 passed.
PHASE11 remains in_progress; live RabbitMQ misroute handling still needs Gate C.
```

2026-07-20 Package A delivery lineage gate：

```text
PackageAProductionIngestionRuntime now verifies first-seen RabbitMQ parse-request payload lineage against PostgreSQL ParseJob context before claiming ParseAttempt/Lease.
The check covers tenant, workspace, SourceObject, DocumentVersion, ParsePlan, ParseJob, ObjectRef, ObjectManifest, content hash, size, mime type, and Security Epoch.
Lineage mismatch raises PackageARejectDeliveryError and rejects(requeue=false) after UoW rollback, leaving worker inbox, attempts, leases, snapshots, and Parser Gateway untouched.
Added Gate B focused integration coverage for forged source_object_id rejection before attempt creation.
py_compile passed.
Package A delivery settlement and lineage unit tests passed: 9 passed.
Gate B lineage mismatch integration was attempted and is environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade.
PHASE11 remains in_progress; this is Package A completion_candidate implementation evidence, not Gate B completion.
```

2026-07-20 Package A ObjectRef verification DLQ：

```text
ObjectRef scope, hash/size, visibility, and invalid s3:// verification failures now raise PackageAObjectVerificationError with stable failure_code.
PackageAProductionIngestionRuntime catches these failures after ParseAttempt/Lease creation and records terminal PostgreSQL dead_letter receipts in the same UoW.
After domain commit, RabbitMQ settlement rejects(requeue=false), so deterministic bad source objects go to DLQ instead of looping through redelivery.
Added Gate B focused integration coverage for object hash mismatch -> dead_letter without Parser Gateway execution.
py_compile passed.
Worker ObjectRef verifier fault test passed: 1 passed.
Gate B object hash mismatch DLQ integration was attempted and is environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade.
PHASE11 remains in_progress; this is Package A completion_candidate implementation evidence, not Gate B completion.
```

2026-07-20 Package A Quality Gate blocks handoff：

```text
PackageAProductionIngestionRuntime now records ParseSnapshot, SourceSpan, and Quality Decision before indexable handoff.
If HumanReviewRuntime.can_publish_snapshot is false, the runtime closes Attempt/Lease as failed with failure_code quality_gate_<verdict>, ACKs after domain commit, and does not create IndexableDocumentSnapshot or Snapshot Outbox.
This prevents low-quality parse results from requeue looping or entering Knowledge handoff without an approved quality path.
Added Gate B focused integration coverage for low-confidence Markdown parse -> quality review required without indexable handoff.
py_compile passed.
Package A delivery settlement and quality helper tests passed: 10 passed.
Gate B quality review integration was attempted and is environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade.
PHASE11 remains in_progress; this is Package A completion_candidate implementation evidence, not Gate B completion.
```

2026-07-20 Package A Parser Gateway identity gate：

```text
PackageAProductionIngestionRuntime now validates Parser Gateway result.job_id against the PostgreSQL ParseJob and successful snapshot.parse_attempt_id against the current append-only ParseAttempt.
Identity mismatch raises PackageAParserIdentityError and is recorded as a terminal PostgreSQL dead_letter receipt in the same UoW.
After domain commit, RabbitMQ settlement rejects(requeue=false), so parser-generated alternate Job/Attempt IDs cannot enter ParseSnapshot, SourceSpan, QualityDecision, or Indexable handoff.
Added Gate B focused integration coverage for successful parse with mismatched snapshot attempt -> dead_letter without snapshot persistence.
py_compile passed.
Package A delivery settlement and parser identity unit tests passed: 11 passed.
Gate B parser identity integration was attempted and is environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade.
PHASE11 remains in_progress; this is Package A completion_candidate implementation evidence, not Gate B completion.
```

2026-07-20 Package A Workspace upload hash gate：

```text
WorkspaceTaskRuntimeService.register_file now computes SHA256 from actual upload content before creating file state or calling PackageAProductionIngestionRuntime.
Provided file_hash mismatch returns HTTP 400 and does not create UploadedFileContract, _file_text, or Package A upload command.
Matching hash keeps Workspace file contract, file_status.source_sha256, and Package A SourceObject content lineage on the same actual content hash.
py_compile passed.
Workspace Package A upload hash gate tests passed: 2 passed.
PHASE11 remains in_progress; this is Package A default upload path implementation evidence, not Gate C completion.
```

2026-07-20 Package A Workspace upload bucket config gate：

```text
WorkspaceTaskRuntimeService now carries the Package A upload bucket as runtime configuration instead of hardcoding zuno-ingestion in PackageAUploadCommand.
Application startup resolves the bucket from the existing PHASE04 MinIO setting storage.minio.bucket_name and passes it into the Workspace default upload path.
If the bucket is absent in a test substitute, the service keeps the historical zuno-ingestion default; production deployments with configured MinIO bucket no longer diverge from deployment config.
py_compile passed.
Workspace Package A production bootstrap and upload hash/bucket tests passed: 4 passed.
PHASE11 remains in_progress; this is Package A default upload path implementation evidence, not Gate C completion.
```

2026-07-20 Package A Worker Inbox identity gate：

```text
PackageAProductionIngestionRuntime now records worker inbox entries with the configured runtime worker_id instead of a hidden fixed consumer string.
The same worker identity now spans Inbox duplicate/redelivery detection, ParseAttempt lease claim, running mark, renew, and terminal commit/fail paths.
This prevents RabbitMQ runner configuration rabbitmq.ingestion_worker_id from diverging from PostgreSQL Inbox idempotency ownership.
py_compile passed.
Package A delivery settlement, lineage, parser identity, and worker inbox identity tests passed: 12 passed.
PHASE11 remains in_progress; this is Package A worker identity implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A PostgreSQL expected-state fencing：

```text
IngestionRepository._update_attempt_if_current now includes expected Attempt status in the PostgreSQL conditional update.
Running requires lease_claimed, renew/commit/fail require running, and expired lease reconciliation requires claimed or running before lease_lost.
This makes worker, token, unexpired lease, highest fencing generation, Attempt ID, tenant, and expected state part of the database-side fencing contract.
py_compile passed.
Package A persistence expected-state fencing tests passed: 4 passed.
Package A delivery settlement tests passed: 12 passed.
PHASE11 remains in_progress; this is Package A PostgreSQL fencing implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A rejected delivery batch resilience：

```text
PackageAProductionIngestionRuntime now raises PackageARejectDeliveryError for deterministic deliveries it has already rejected without requeue: invalid schema/hash, misrouted topic/contract/consumer, and tenant header mismatch.
PackageAProductionQueueWorker catches only that already-rejected error class, counts rejected deliveries, and continues the bounded consume batch so a poison message does not block following valid parse requests.
Database transaction, object verification, fencing, and parser failures still propagate unless the runtime returns a domain receipt, preserving crash-before-commit no-ACK semantics.
py_compile passed.
Package A queue worker and delivery settlement tests passed: 20 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ worker resilience implementation evidence, not Gate C completion.
```

2026-07-20 Package A retry parent lineage：

```text
PackageAProductionIngestionRuntime retry parse-request envelopes now include retry_attempt_no, retry_parent_attempt_id, retry_parent_message_id, and retry_parent_idempotency_key in payload.
Retry messages keep the same PostgreSQL ParseJob aggregate while using a new message id, idempotency key, causation id, and recomputed canonical payload_hash.
This makes retry parentage auditable from the outbox/RabbitMQ payload itself instead of inferring it from DB attempt_count alone.
py_compile passed.
Package A retry boundary and delivery settlement tests passed: 16 passed.
PHASE11 remains in_progress; this is Package A retry lineage implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Snapshot handoff idempotency persistence：

```text
Added forward migration 20260720_20_package_a_handoff_idempotency.py for PostgreSQL handoff idempotency persistence.
ingestion_indexable_document_snapshots now has handoff_idempotency_key and ingestion_outbox_events now has idempotency_key, with existing outbox/snapshot backfill and tenant-scoped partial unique indexes.
Package A success path passes IndexableDocumentSnapshotV1.idempotency_key and SnapshotOutboxEvent.idempotency_key into PostgreSQL repository writes.
py_compile passed.
Package A persistence and delivery settlement tests passed: 18 passed.
Alembic heads passed: 20260720_20 (head).
Alembic upgrade head was attempted; local PostgreSQL connection did not return before manual interruption, so runtime migration verification is environment_blocked.
PHASE11 remains in_progress; this is Package A snapshot handoff idempotency implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Snapshot handoff replay receipt：

```text
IngestionRepository.load_parse_job_replay_receipt now returns handoff_idempotency_key and outbox_idempotency_key for duplicate/redelivery receipts.
Added load_snapshot_handoff_replay_receipt to recover IndexableDocumentSnapshot plus indexable_snapshot.ready outbox state by tenant_id + handoff_idempotency_key.
This connects persisted handoff idempotency to the PostgreSQL replay/read path needed for duplicate handoff and crash-after-commit-before-ACK recovery.
py_compile passed.
Package A persistence replay and delivery settlement tests passed: 20 passed.
PHASE11 remains in_progress; this is Package A snapshot handoff replay implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Worker receipt handoff idempotency：

```text
PackageAWorkerReceipt now carries handoff_idempotency_key and outbox_idempotency_key.
First-seen success receipts use IndexableDocumentSnapshotV1.idempotency_key and SnapshotOutboxEvent.idempotency_key; duplicate/redelivery receipts reuse the PostgreSQL replay fields.
This makes ACK-after-domain-commit receipts expose the handoff/outbox idempotency facts needed to audit crash-after-commit-before-ACK recovery.
py_compile passed.
Package A delivery settlement and queue worker tests passed: 20 passed.
PHASE11 remains in_progress; this is Package A worker receipt replay implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ Security Epoch header contract：

```text
RabbitMQTransport.publish now accepts security_epoch_ref and writes it to message headers.
PostgresOutboxRabbitMQPublisher maps CrossModuleEnvelope effective_security_epoch_ref into that RabbitMQ header when publishing outbox records.
PackageAProductionIngestionRuntime rejects deliveries before Worker Inbox / ParseAttempt transaction if RabbitMQ header, envelope effective_security_epoch_ref, and payload security_epoch_ref do not match.
py_compile passed.
Package A delivery settlement and queue worker tests passed: 22 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ Security Epoch boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A PostgreSQL Lease heartbeat and successful Worker path：

```text
IngestionRepository.heartbeat_parse_attempt_lease now records explicit PostgreSQL heartbeat facts without extending lease expiry.
The heartbeat update is fenced by tenant, ParseJob, ParseAttempt, worker_id, fencing_token, unexpired lease, and running Attempt state.
PackageAProductionIngestionRuntime records heartbeat after ObjectRef verification and after Parser Gateway returns, before ParseSnapshot/SourceSpan/Quality/Indexable Snapshot/Outbox commit.
The success path now uses the same local visibility_ref for handoff creation and PostgreSQL indexable snapshot persistence instead of reading a nonexistent IndexableDocumentSnapshotV1.visibility_ref field.
py_compile passed.
Package A persistence fencing and delivery settlement tests passed: 23 passed.
PHASE11 remains in_progress; this is Package A heartbeat and success-path runtime implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A ObjectRef revoked/deleted visibility boundary：

```text
PackageAProductionIngestionRuntime now checks PostgreSQL source_status before reading MinIO/S3 object bytes.
revoked / visibility_revoked produce object_visibility_revoked; deleted / physically_deleted produce object_deleted; other non-visible statuses remain object_not_visible.
The focused ObjectRef verifier test asserts scope mismatch, revoked, and deleted statuses do not read object content, while committed and hash mismatch paths still perform the expected byte read.
py_compile passed.
Package A ObjectRef verifier and delivery settlement tests passed: 15 passed.
PHASE11 remains in_progress; this is Package A ObjectRef visibility/dead-letter boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Workspace upload replay idempotency：

```text
IngestionRepository.load_workspace_upload_replay_receipt now resolves an existing upload by tenant_id + ParseJob idempotency key back to SourceObject, DocumentVersion, ParsePlan, ParseJob, and the PHASE04 infra_outbox_events parse-request outbox.
PackageAProductionIngestionRuntime.accept_workspace_upload computes the content-addressed parse idempotency key before object writes and returns the existing receipt when PostgreSQL already proves the same tenant/workspace/content upload.
Replay validates workspace, content hash, size, classification, Security Epoch, and parse-request outbox presence before returning accepted facts; conflicts fail explicitly.
py_compile passed.
Package A upload replay, persistence fencing, and workspace upload hash gate tests passed: 14 passed.
PHASE11 remains in_progress; this is Package A upload idempotency/default-path implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Outbox publish failure pump boundary：

```text
PackageAProductionQueueWorker.publish_and_consume_once now stops before RabbitMQ consumption when the PHASE04 outbox publisher returns failed events.
The receipt exposes failed_publish_count and delivery_received=false, leaving failed outbox rows on PostgreSQL retry/replay instead of masking publish failure by consuming unrelated queued deliveries.
Existing success publish/consume, bounded consume, and deterministic rejected-delivery continuation tests still pass.
py_compile passed.
Package A queue worker tests passed: 10 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ dispatcher/consumer failure-boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ DLQ replay hook：

```text
PackageAProductionQueueWorker.replay_dead_letter_once now declares the Package A topology, reads one delivery from the parse DLQ, replays it through PHASE04 RabbitMQTransport.replay_dead_letter, then ACKs the original DLQ delivery after replay publish succeeds.
Empty DLQ returns replayed=false without invoking replay.
Replay is deliberately scoped to RabbitMQ movement only; the replayed message still flows through the normal Package A consumer path for schema, tenant, Security Epoch, Inbox idempotency, PostgreSQL Lease/Fencing, domain commit, and ACK.
py_compile passed.
Package A queue worker tests passed: 12 passed.
PHASE11 remains in_progress; this is Package A DLQ replay hook implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Worker terminal failure code receipts：

```text
PackageAWorkerReceipt now carries failure_code for first-seen terminal outcomes and duplicate/redelivery replay receipts.
IngestionRepository.load_parse_job_replay_receipt selects latest_attempt.failure_code, so crash-after-commit-before-ACK replay can report the already-persisted terminal reason.
cancel_requested focused test proves the worker closes Attempt/Lease with failure_code=cancel_requested and does not read ObjectRef bytes, call Parser Gateway, or write Snapshot/SourceSpan/Quality/Indexable Snapshot/Outbox.
py_compile passed.
Package A delivery, persistence replay, and queue worker tests passed: 37 passed.
PHASE11 remains in_progress; this is Package A terminal receipt implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A ACK-before-domain-commit guard：

```text
PackageAProductionIngestionRuntime._settle_delivery_after_domain_commit now raises before RabbitMQ ACK when the Worker receipt does not prove a successful domain commit.
The guard preserves dead-letter reject no-requeue behavior and normal ACK behavior for committed receipts.
Focused settlement coverage proves the guard leaves the delivery unacked/unrejected instead of falsely settling it.
py_compile passed.
Package A delivery settlement and queue worker tests passed: 28 passed.
PHASE11 remains in_progress; this is Package A ACK/domain-commit ordering evidence, not Gate B/C completion.
```

2026-07-20 Package A transport message identity gate：

```text
PackageAProductionIngestionRuntime now rejects RabbitMQ deliveries whose transport message_id does not match the canonical outbox envelope message_id.
The check happens before Worker Inbox, ParseAttempt, Lease, and Parser Gateway, preserving duplicate/redelivery and crash-after-commit replay identity.
Gate B delivery fixture now includes RabbitMQ security_epoch_ref header from the canonical envelope, matching the production ingress contract.
py_compile passed.
Package A delivery settlement and queue worker tests passed: 29 passed.
Gate B focused PostgreSQL test was attempted once; environment_blocked by localhost:5432 connection timeout during alembic upgrade head.
PHASE11 remains in_progress; this is Package A RabbitMQ/Inbox identity-boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A retry policy identity gate：

```text
PackageAProductionIngestionRuntime now rejects parse-request deliveries whose payload max_attempts is missing, non-positive, or different from the configured Package A Worker retry budget.
The check happens before Worker Inbox, ParseAttempt, Lease, and Parser Gateway, so stale or forged retry policy cannot alter max_attempts semantics.
Gate B adds retry-policy mismatch before-inbox coverage; it expects no Inbox, Attempt, or Lease facts when PostgreSQL is available.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 34 passed.
Gate B focused PostgreSQL test was attempted once; environment_blocked by localhost:5432 connection timeout during alembic upgrade head.
PHASE11 remains in_progress; this is Package A retry policy identity-boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A retry parent Attempt lineage gate：

```text
IngestionRepository.load_parse_job_context now exposes latest PostgreSQL ParseAttempt ID and status to the Package A Worker.
PackageAProductionIngestionRuntime validates retry_attempt_no against PostgreSQL attempt_count + 1, and requires retry_parent_attempt_id to match the latest failed Attempt.
Forged retry delivery cannot create a new append-only Attempt from a stale or non-failed parent.
py_compile passed.
Package A delivery settlement, persistence fencing, and retry boundary tests passed: 33 passed.
Gate B focused PostgreSQL test was attempted once; environment_blocked by localhost:5432 connection timeout during alembic upgrade head.
PHASE11 remains in_progress; this is Package A retry parent/Attempt lineage implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A retry envelope identity gate：

```text
PackageAProductionIngestionRuntime now validates retry delivery envelope message_id, causation_id, and idempotency_key against retry payload parent/attempt fields before Worker Inbox.
This prevents RabbitMQ/Outbox envelope identity from diverging from retry payload lineage.
The integration/fault causation mismatch test passes without PostgreSQL because the rejection occurs before IngestionUnitOfWork.
py_compile passed.
Package A retry boundary and delivery settlement tests passed: 24 passed.
Package A retry envelope causation mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A retry envelope identity-boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A outbox header identity gate：

```text
PackageAProductionIngestionRuntime now validates RabbitMQ outbox headers before Worker Inbox: ordering_key must match the ParseJob aggregate ID, ordering_sequence must be positive, and outbox publish/retry/replay counters must be present and valid.
This preserves PHASE04 Outbox publisher -> RabbitMQ -> Package A Worker identity continuity.
The integration/fault ordering_key mismatch test passes without PostgreSQL because the rejection occurs before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement and queue worker tests passed: 32 passed.
Package A outbox ordering header mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ outbox header identity-boundary implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A Worker Inbox ordering persistence：

```text
IngestionRepository.record_worker_inbox now forwards ordering_key and ordering_sequence to PHASE04 InfrastructureRepository.record_inbox_receipt.
PackageAProductionIngestionRuntime passes validated RabbitMQ outbox ordering headers into PostgreSQL Worker Inbox.
Duplicate/redelivery receipts now preserve ParseJob ordering lineage instead of using message_id-only Inbox facts.
py_compile passed.
Package A delivery settlement, persistence fencing, and queue worker tests passed: 42 passed.
PHASE11 remains in_progress; this is Package A Worker Inbox persistence implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A ordered Inbox buffered delivery boundary：

```text
PackageAProductionIngestionRuntime now treats only non-processable Inbox status=received as duplicate/redelivery replay.
PHASE04 ordered Inbox status=buffered stays unacked and unrejected; Package A does not load ParseJob replay receipts for it.
This prevents buffered ordered deliveries from being falsely ACKed before the Inbox watermark makes them processable.
py_compile passed.
Package A delivery settlement, persistence fencing, and queue worker tests passed: 43 passed.
PHASE11 remains in_progress; this is Package A ordered Inbox settlement implementation evidence, not Gate B/C completion.
```

2026-07-20 Package A buffered Inbox commit-before-no-ACK boundary：

```text
PackageAProductionIngestionRuntime now defers buffered Inbox errors until after the PostgreSQL UoW exits cleanly.
The focused settlement test proves record_worker_inbox is followed by UoW exit:none, then the runtime raises IngestionPersistenceError without ACK, reject, or replay receipt lookup.
This preserves PHASE04 ordered Inbox receipt facts while keeping RabbitMQ settlement blocked until the delivery becomes processable.
py_compile passed.
Package A delivery settlement, persistence fencing, and queue worker tests passed: 43 passed.
PHASE11 remains in_progress; this is Package A ordered Inbox commit/settlement boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A retry attempt number pre-Inbox gate：

```text
PackageAProductionIngestionRuntime now rejects retry delivery envelopes with retry_attempt_no < 2 before Worker Inbox.
The focused retry boundary test proves forged retry:1 cannot pass the retry envelope identity gate.
This keeps initial execution identity separate from retry Attempts before PostgreSQL Inbox/Attempt mutation.
py_compile passed.
Package A retry boundary, delivery settlement, and queue worker tests passed: 39 passed.
PHASE11 remains in_progress; this is Package A retry identity-boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A retry budget pre-Inbox gate：

```text
PackageAProductionIngestionRuntime now rejects retry delivery envelopes whose retry_attempt_no exceeds max_attempts before Worker Inbox.
The focused retry boundary test proves retry_attempt_no=3 is rejected when Package A max_attempts=2.
The integration/fault test proves the RabbitMQ delivery is rejected before IngestionUnitOfWork, so no Inbox, Lease, or Attempt mutation can occur.
py_compile passed.
Package A retry boundary, delivery settlement, and queue worker tests passed: 40 passed.
Package A retry attempt beyond budget integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A retry budget-boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A retry outbox counter pre-Inbox gate：

```text
PackageAProductionIngestionRuntime now validates RabbitMQ outbox_retry_count against retry payload lineage before Worker Inbox.
Initial deliveries require outbox_retry_count=0; retry deliveries require outbox_retry_count=retry_attempt_no - 1.
The integration/fault test proves payload retry_attempt_no=2 with header outbox_retry_count=0 is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 40 passed.
Package A retry header counter mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ retry lineage-boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A producer lineage pre-Inbox gate：

```text
PackageAProductionIngestionRuntime now validates producer lineage before Worker Inbox.
Initial parse-request deliveries must come from workspace.file_upload; retry parse-request deliveries must come from ingestion.parser_worker.
The integration/fault test proves a retry payload from workspace.file_upload is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 42 passed.
Package A retry producer mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A producer lineage-boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ workspace header lineage：

```text
PostgresOutboxRabbitMQPublisher now forwards canonical workspace_id into RabbitMQ delivery headers.
PackageAProductionIngestionRuntime validates header workspace_id, envelope workspace_id, and payload workspace_id before Worker Inbox.
The integration/fault test proves a workspace-b header on a workspace-a delivery is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 44 passed.
Package A workspace header mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ workspace lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ trace header lineage：

```text
PostgresOutboxRabbitMQPublisher now forwards canonical envelope trace_id into RabbitMQ delivery headers.
PackageAProductionIngestionRuntime validates header trace_id against envelope trace_id before Worker Inbox.
The integration/fault test proves a mismatched trace header is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 46 passed.
Package A trace header mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ trace lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ data classification header lineage：

```text
PostgresOutboxRabbitMQPublisher now forwards canonical envelope data_classification into RabbitMQ delivery headers.
PackageAProductionIngestionRuntime validates header data_classification against envelope data_classification before Worker Inbox.
The integration/fault test proves a mismatched classification header is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 48 passed.
Package A data classification header mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ classification lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ message version header lineage：

```text
PostgresOutboxRabbitMQPublisher now forwards canonical envelope contract_version as RabbitMQ message_version.
PackageAProductionIngestionRuntime validates header message_version against envelope contract_version before Worker Inbox.
The integration/fault test proves a mismatched message_version header is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 50 passed.
Package A message version header mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ contract-version lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A payload tenant pre-Inbox lineage：

```text
PackageAProductionIngestionRuntime now validates payload tenant_id against envelope/header tenant_id before Worker Inbox.
The integration/fault test proves a payload tenant-b delivery with tenant-a envelope/header is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 51 passed.
Package A payload tenant mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A tenant lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A ParseJob aggregate pre-Inbox lineage：

```text
PackageAProductionIngestionRuntime now validates envelope aggregate_type=ParseJob and payload parse_job_id == envelope aggregate_id before Worker Inbox.
The integration/fault test proves a forged payload parse_job_id is rejected before IngestionUnitOfWork.
py_compile passed.
Package A delivery settlement, retry boundary, and queue worker tests passed: 52 passed.
Package A ParseJob identity mismatch integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A ParseJob lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A upload default no-local-fallback gate：

```text
WorkspaceTaskRuntimeService now records when Package A production ingestion has been configured as the default upload path.
When that default is configured but unavailable, register_file returns 503 before writing in-memory file state, SQLite durable records, or LocalObjectStore content.
The focused API test proves the production default path does not silently fall back to the local durable adapter.
py_compile passed.
Package A upload hash/default no-local-fallback and explicit durable adapter tests passed: 4 passed.
PHASE11 remains in_progress; this is Package A upload default-path boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A RabbitMQ DLQ replay counter lineage：

```text
RabbitMQTransport.replay_dead_letter now increments outbox_replay_count while preserving DLQ delivery headers.
PackageAProductionIngestionRuntime rejects replayed_from_dlq=True deliveries whose outbox_replay_count is still below 1 before Worker Inbox.
The focused queue-worker test proves replay publish headers carry outbox_replay_count=1.
The integration/fault test proves a forged replay marker without a replay counter is rejected before IngestionUnitOfWork.
py_compile passed.
Package A queue worker and delivery settlement tests passed: 47 passed.
Package A DLQ replay counter integration/fault test passed: 1 passed.
PHASE11 remains in_progress; this is Package A RabbitMQ replay lineage evidence, not Gate B/C completion.
```

2026-07-20 Package A upload deadline propagation and worker cancel boundary：

```text
PackageAUploadCommand now carries deadline_at into the canonical parse-request envelope emitted by PackageAProductionIngestionRuntime.
PackageAProductionIngestionRuntime handles expired deadline deliveries after Attempt/Lease claim but before ObjectRef read or Parser Gateway, closing the Attempt/Lease as cancelled with failure_code=deadline_expired.
The focused unit tests prove deadline propagation and no object/parser/snapshot side effects on expired deadline.
py_compile passed.
Package A upload replay/deadline and delivery settlement tests passed: 34 passed.
Gate B expired deadline PostgreSQL test was added but environment_blocked locally because localhost:5432 timed out and docker compose postgres could not start without Docker daemon.
PHASE11 remains in_progress; this is Package A deadline/cancel boundary evidence, not Gate B/C completion.
```

2026-07-20 Package A Workspace/File Upload deadline default wiring：

```text
WorkspaceFileBody now accepts deadline_at and WorkspaceTaskRuntimeService forwards it into PackageAUploadCommand.
The API/service tests prove /api/v1/workspace/file can carry an ISO deadline into the Package A production default upload command.
This connects Workspace/File Upload to the existing Package A parse-request deadline propagation and worker deadline cancel boundary.
py_compile passed.
Package A Workspace/File Upload deadline default wiring tests passed: 5 passed.
PHASE11 remains in_progress; this is Package A default upload wiring evidence, not Gate B/C completion.
```

2026-07-20 Package A filename lineage in parse-request envelope：

```text
PackageAProductionIngestionRuntime now emits upload filename in the canonical parse-request payload.
PackageAProductionIngestionRuntime validates payload filename against PostgreSQL SourceObject.filename before Lease claim, ObjectRef read, or Parser Gateway.
The focused tests prove filename is present in the upload envelope and forged filename payload is rejected by the worker lineage validator.
py_compile passed.
Package A upload replay/filename and delivery settlement lineage tests passed: 35 passed.
PHASE11 remains in_progress; this is Package A source filename lineage evidence, not Gate B/C completion.
```

PHASE08 保持 `ready`，因为它只依赖 PHASE04–PHASE07。PHASE12 保持 `planned`，等待 PHASE08 completed 与 PHASE11 completed。
