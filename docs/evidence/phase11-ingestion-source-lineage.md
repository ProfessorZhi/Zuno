# PHASE11 Ingestion Source Lineage Evidence

status: `reopened_partial_evidence`
phase_completion: `reopened_pending`

本文记录 PHASE11 Durable Ingestion and Source Lineage 的部分实现证据。当前证据证明 PostgreSQL ingestion schema、`IngestionUnitOfWork`、SourceObject 到 IndexableDocumentSnapshot 的持久化边界，以及本地 runtime batch 的若干行为线索；它不证明 PHASE11 已完成。

## Current Boundary

```text
infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py
src/backend/zuno/platform/database/schema_registry.py
src/backend/zuno/platform/database/ingestion/persistence.py
src/backend/zuno/knowledge/ingestion/source_object_commit.py
src/backend/zuno/knowledge/ingestion/source_object_upload.py
tools/scripts/verify_phase11_ingestion_source_lineage.py
tests/repo/test_phase11_ingestion_source_lineage.py
tests/integration/test_phase11_ingestion_persistence_runtime.py
tests/knowledge/test_ingestion_source_object_commit.py
tests/knowledge/test_ingestion_source_object_upload.py
docs/evidence/input-runtime-batch.md
```

## Verified Behavior

- Migration 串接到 `20260719_17`，避免产生第二个 Alembic head。
- `ingestion_*` 表统一归属 `Input / Document Ingestion`。
- SourceObject 保留 object manifest、hash、classification 和 security epoch。
- `SourceObjectUploadRuntime` 当前提供 PHASE11 upload init/stage/commit 编排：根据 tenant/workspace/source 构造 PHASE04 object path，拒绝路径穿越，上传内容在进入 PHASE04 durable object store 之前校验 hash 与 size，partial upload 与 hash mismatch 不会 stage/commit；提交后只保留 `s3://` ObjectRef，不把大 payload 保存进 SourceObject。
- `SourceObjectCommitRuntime` 消费 PHASE04 `ObjectStoreReceipt`，只接受 visible object receipt，并校验 object manifest ref、tenant/workspace object prefix、hash、size、mime type、classification 与 security epoch 后生成 PHASE11 `SourceObjectRecord`。
- SourceObject upload runtime 当前覆盖同一 tenant/workspace/source 的 immutable hash guard；相同 SourceObject 重复提交和同 tenant/workspace 相同 hash 的重复内容会返回 deduplicated receipt，不创建第二套对象事实源。
- DocumentVersion 与 ParseSnapshot 分离；ParseSnapshot 绑定 ParseJob、ParseAttempt 和 DocumentVersion。
- ParseAttempt 持久化 lease、fencing token、attempt number 和状态。
- SourceSpan 可回溯到 ParseSnapshot 与 DocumentVersion。
- Quality Gate 是 IndexableDocumentSnapshot 发布前置条件。
- Input migration 不创建 Chunk、Entity、Relation、KnowledgeVersion、BM25 或 Vector Index。
- `IngestionUnitOfWork` 可在同一 PostgreSQL transaction 中写入 SourceObject、DocumentVersion、ParsePlan、ParseJob、ParseAttempt、ParseSnapshot、SourceSpan、QualityDecision、IndexableDocumentSnapshot 和 outbox event。
- 同一 UoW 中后续 domain write 失败会回滚已写 SourceObject / DocumentVersion。
- 同一 tenant 的 ParseJob idempotency key 由数据库唯一约束保护；重复写入被拒绝且不会新增第二个 ParseJob。
- IndexableDocumentSnapshot 必须引用 QualityGateDecision；缺质量门时数据库 FK 拒绝 handoff。
- SourceObject 写入前验证 `source_sha256` 是 64 位 hash。
- LocalQueue ACK / retry / dead-letter / replay、ACK-after-domain-commit guard、RabbitMQ target-blocked probe、Redis fallback boundary 只作为线索；外部依赖不可用不能冒充 production dependency。`ParserWorker` 当前在领域提交成功后才 ACK；领域提交失败会 retry，重试耗尽进入 dead letter。需要人工审核的 OCR/VLM fallback 会进入 `review_pending`，不会 enqueue index。
- PHASE11 重新打开后，ParseAttemptControl、native/PDF parser、OCR/VLM、Office/archive、delete/legal hold/restore 等证据都只保留为部分证据，不能单独关闭 PHASE11。
- `local_office_archive` 当前提供 Office/Archive 的可执行本地 fallback：docx/xlsx 保留 heading/table projection，pptx 保留 slide/figure projection，archive 只读取 manifest、不自动解包；live Unstructured / MarkItDown provider 保持 measurement blocked。
- Parser Gateway 当前接受显式 `source_object_ref` 与 `source_object_manifest`，在 adapter 执行前校验 PHASE04 `s3://` ObjectRef、object manifest ref、content hash、size、parser policy、lineage ref、workspace scope，并把 ObjectRef、security policy、security epoch、timeout、source input mode 与质量 confidence 写入 ParseJobSnapshot；hash mismatch、oversized、encrypted、corrupt、sandbox denied 与 cancel-before-adapter 进入 typed failure / cancelled 状态。
- `CanonicalDocumentIR` 当前具备 schema round-trip helper、contract report、显式 `TransformLedgerEntry`、block order/style、SourceSpan region/page/slide/bbox/table/source text provenance、table/image refs，并验证 IR SourceSpan 不携带 Knowledge chunk id，Input IR 不创建 Chunk、Entity、Relation 或 KnowledgeVersion。
- `temporary.adapter.phase11.legacy_chunk_projection` 当前把 workspace 文档附件与 knowledge pipeline `_parse_chunks` 从隐式 `doc_parser.parse_doc_into_chunks` 默认调用迁移为：ParseGateway 先生成 `CanonicalDocumentIR`，再显式投影成旧 `ChunkModel` 给未迁移 RAG/Graph 消费；该 adapter 绑定 Input Parser Adapter Owner 与 PHASE16 removal，不得作为 PHASE11 完成证据。
- Snapshot handoff 当前对 Human Review fail-closed：`QualityGateResult` 为 REVIEW 时，未提供 approved `ReviewDecisionReceipt` 或 receipt 为 rejected/expired/cancelled 会拒绝生成 `IndexableDocumentSnapshotV1`；approved receipt 会写入 snapshot payload / security refs 后生成 pending outbox。
- Snapshot handoff 当前具备本地 outbox dispatch receipt：Knowledge publisher 不可用时 outbox 保持 pending 且 `replay_count` 增加；后续 replay 成功才返回 `handed_off` 与 acknowledged receipt。
- Human Review 当前具备本地 expiration sweep：`expire_pending_reviews()` 只把 overdue pending task 转换为 expired `ReviewDecisionReceipt`，已有 receipt 或未到期 task 会跳过；expired receipt 不能发布 snapshot。
- Delete/Restore runtime 当前覆盖解析中删除与 snapshot 后删除：`DeleteLifecycleReceipt` 可绑定 parse job、parse attempt、fencing token、IndexableDocumentSnapshot、handoff outbox event 与 projection cleanup ref；delete 会先撤销 visibility，后续 cleanup / physical delete / verification 必须确认 projection cleanup 和物理删除，verified 后拒绝 late worker result；legal hold 会阻止 cleanup / physical delete，且不会错误恢复授权。
- `ParseControlRuntime` 当前显式串起 ParsePlan / queued job / attempt lease / worker run：覆盖 planned → queued → leased → running → succeeded / cancelled / dead_letter，本地成功路径会用 fencing token 提交 lease，stale fencing token 被拒绝，failed parse 会按 retry policy 进入 dead_letter。

## Package A Production Default Path Progress

2026-07-20 新增 PHASE11 Package A 生产默认链路实现进展：

- `src/backend/zuno/knowledge/ingestion/production_runtime.py` 新增 `PackageAProductionIngestionRuntime`，把 Workspace/File Upload accept 编排到 PHASE04 `DurableMinioObjectStore`、PostgreSQL `IngestionUnitOfWork`、PHASE04 infra outbox、RabbitMQ delivery payload、Parser Worker、Parser Gateway、ParseSnapshot、SourceSpan、Quality Gate、IndexableDocumentSnapshot 和 Snapshot Outbox。
- `src/backend/zuno/api/services/workspace_task_runtime.py` 新增可配置 `configure_package_a_production_ingestion(...)` 默认生产接线；配置存在时 workspace file register 返回 `ingest_accepted`，不再同步冒充解析完成。
- `contracts.py`、`gateway.py` 和 `parse_control.py` 修正 Package A 身份边界：ParsePlan、ParseJob、ParseAttempt 分离；Parser Gateway 尊重外部权威 Job/Attempt/DocumentVersion/Idempotency ID；`max_attempts` 包含初次执行，retry 不复用旧 Attempt。
- `infra/db/alembic/versions/20260720_19_ingestion_package_a_control.py` 新增 forward migration，补充 ParseAttempt 上下文绑定、lease/fencing 表、DLQ 关联、状态约束和索引；不重写历史 `20260719_18`。
- `src/backend/zuno/platform/database/ingestion/persistence.py` 新增同事务 infra outbox enqueue、worker inbox、Job context load、append-only Attempt lease claim、current fencing 条件更新、terminal DLQ receipt 等 Package A repository 操作。
- `tests/integration/test_phase11_package_a_production_runtime.py` 新增 Gate B/Gate C 测试入口，覆盖 PostgreSQL lease/fencing 与真实 MinIO/RabbitMQ upload-to-snapshot-outbox 路径。

已运行并通过：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/contracts.py src/backend/zuno/knowledge/ingestion/gateway.py src/backend/zuno/knowledge/ingestion/parse_control.py src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/platform/database/ingestion/persistence.py src/backend/zuno/api/services/workspace_task_runtime.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/knowledge/test_ingestion_parse_control.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
alembic -c infra/db/alembic.ini heads
git diff --check
python tools/scripts/verify_utf8_doc_encoding.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_current_program.py
python tools/scripts/verify_requirement_ledger_evidence_gate.py
python tools/scripts/verify_phase11_ingestion_source_lineage.py
```

真实依赖 Gate 当前未通过：

```text
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
failed: Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine

pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_postgres_attempt_lease_and_fencing_rejects_stale_worker -p no:cacheprovider
failed: environment_blocked, PostgreSQL localhost:5432 connection timeout during alembic upgrade

pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_c_real_minio_rabbitmq_upload_to_snapshot_outbox -p no:cacheprovider
failed: environment_blocked, PostgreSQL localhost:5432 connection timeout before MinIO/RabbitMQ step
```

边界：Package A production default path 已有 runtime、migration 和 focused tests，但 Gate B/C 在当前环境未通过；不得仅凭本节证据将 Package A 行提升为 `completion_candidate`。PHASE11 仍为 `in_progress`，Coordinator Approval 仍为 `pending_reopened`。

2026-07-20 follow-up 修正：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 改为领域 UoW 成功退出后才执行 RabbitMQ ACK；duplicate delivery、success、dead_letter 与 retryable failed 都在事务提交后 ACK 当前消息。retryable failed 不重投同一 RabbitMQ message，而是在同一事务写入新的 `parse.requested` outbox，避免 worker inbox 幂等把 redelivery 吞掉。
- `IngestionRepository.fail_parse_attempt(...)` 现在同事务关闭当前 `ingestion_parse_leases`，避免只关闭 Attempt 而留下 active lease。
- 该修正继续保持 Gateway 不拥有 ACK、Lease 或数据库终态。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/platform/database/ingestion/persistence.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/knowledge/test_ingestion_parse_control.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_postgres_attempt_lease_and_fencing_rejects_stale_worker -p no:cacheprovider
```

结果：

```text
py_compile passed
Gate A passed: 46 passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B remains environment_blocked at PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 retry-boundary test addition：

- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_retryable_failure_closes_lease_enqueues_retry_and_acks_after_commit`，覆盖 retryable parser failure 时当前 Attempt `failed`、Lease `released`、ParseJob 回到 `queued`、新增下一次 `parse.requested` outbox、当前 RabbitMQ delivery 事务提交后 ACK、且不 NACK/requeue 同一 message。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/platform/database/ingestion/persistence.py tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_retryable_failure_closes_lease_enqueues_retry_and_acks_after_commit -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B retry-boundary test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 duplicate-redelivery test addition：

- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_duplicate_delivery_acks_without_reparse_or_attempt`，覆盖 worker inbox 已存在时 duplicate/redelivery 不调用 Parser Gateway、不创建 ParseAttempt/Lease/Snapshot、不生成额外 Outbox，并在事务成功退出后 ACK 当前 delivery。

新增验证：

```text
python -m py_compile tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_duplicate_delivery_acks_without_reparse_or_attempt -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B duplicate-redelivery test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 non-retryable-DLQ test addition：

- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_non_retryable_failure_records_dlq_without_retry_outbox`，覆盖 non-retryable parser failure 直接进入 PostgreSQL DLQ：Attempt `dead_letter`、Lease `released`、ParseJob `dead_letter`、`ingestion_dead_letters` 记录 RabbitMQ DLQ ref、当前 delivery 事务提交后 ACK，且不创建 retry outbox。

新增验证：

```text
python -m py_compile tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_non_retryable_failure_records_dlq_without_retry_outbox -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B non-retryable-DLQ test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 worker-object-verifier hardening：

- `PackageAProductionIngestionRuntime` 现在在 worker 读取 ParseJob context 后校验 delivery `security_epoch_ref` 必须匹配 PostgreSQL SourceObject `security_epoch_ref`。
- `_read_and_verify_object(...)` 现在重新校验 S3 ObjectRef 必须位于 `tenant_id/workspace_id/` scope 内，并继续校验 hash、size 和 SourceObject visibility/status。
- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility`，覆盖 scope escape、hash mismatch 和 revoked visibility 被拒绝。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility -p no:cacheprovider
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_c_real_minio_rabbitmq_upload_to_snapshot_outbox -p no:cacheprovider
```

结果：

```text
py_compile passed
worker object verifier fault test passed: 1 passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate C real MinIO/RabbitMQ E2E remains environment_blocked: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 crash-after-commit-before-ACK replay hardening：

- `IngestionRepository.load_parse_job_replay_receipt(...)` 新增 PostgreSQL replay receipt 查询，读取 Job 当前状态、最新 Attempt、IndexableSnapshot outbox 和 DeadLetter receipt。
- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 在 worker inbox duplicate/redelivery 分支优先返回既有终态 receipt；已提交成功的 redelivery 返回 `succeeded`、原 Attempt、IndexableSnapshot 和 Snapshot outbox，不再只返回泛化 `duplicate`。
- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_redelivery_after_commit_returns_existing_success_without_reparse`，覆盖领域事务已提交但 ACK 丢失时，redelivery 不调用 Parser Gateway、不新建 Attempt/Snapshot，并返回既有 succeeded receipt 后 ACK 当前 delivery。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/platform/database/ingestion/persistence.py tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_redelivery_after_commit_returns_existing_success_without_reparse -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B crash-after-commit-before-ACK replay test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 cancel-deadline worker path：

- `PackageAProductionIngestionRuntime` 现在在 Attempt/Lease claimed 并标记 running 后、读取 ObjectRef 和调用 Parser Gateway 前处理 `cancel_requested` 与过期 `deadline_at`。
- cancel/deadline 路径通过 PostgreSQL fencing 更新 Attempt `cancelled`、Lease `released`、ParseJob `cancelled`，不写 ParseSnapshot、SourceSpan、QualityDecision、IndexableSnapshot 或 Snapshot Outbox，事务成功后 ACK 当前 delivery。
- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_cancel_requested_closes_attempt_and_lease_without_snapshot`，覆盖 cancel 不调用 Parser Gateway、不生成 Snapshot/Outbox、关闭 Attempt/Lease 并 ACK。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_cancel_requested_closes_attempt_and_lease_without_snapshot -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B cancel test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 lease-heartbeat-reconcile path：

- `IngestionRepository.renew_parse_attempt_lease(...)` 新增 PostgreSQL heartbeat/renew 语义：仅当前 worker、fencing token、claimed/renewed 且未过期 lease 可续租，更新 Lease `renewed`、heartbeat 和 Attempt lease expiry。
- `IngestionRepository.reconcile_expired_parse_attempt_lease(...)` 新增过期 lease reconciliation：过期 Lease 置 `expired`，Attempt 置 `lease_lost`，ParseJob 回到 `queued`，为后续新 Attempt reclaim 提供持久事实。
- `PackageAProductionIngestionRuntime` 在 Attempt running、取消检查通过后，读取 ObjectRef 和调用 Parser Gateway 前执行一次 fencing heartbeat/renew。
- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_heartbeat_renews_lease_and_expiry_reconciles_attempt`，覆盖 renew 和 expired lease reconciliation 的数据库状态转换。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/platform/database/ingestion/persistence.py tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_heartbeat_renews_lease_and_expiry_reconciles_attempt -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate B heartbeat/reconcile test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 outbox-publish-failure replay coverage：

- 新增 `tests/integration/test_phase11_package_a_production_runtime.py::test_gate_c_outbox_publish_failure_keeps_parse_request_replayable`，使用 Package A `parse.requested` outbox 和 `PostgresOutboxRabbitMQPublisher.publish_batch(...)` 生产发布路径，模拟 RabbitMQ publish/publisher-confirm failure。
- 测试断言 publish failure 后 `infra_outbox_events` 保持 `pending`、释放 claim、记录 `publish_attempts/retry_count/last_error_code`，并可由后续 publisher 重新 claim/replay。

新增验证：

```text
python -m py_compile tests/integration/test_phase11_package_a_production_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_c_outbox_publish_failure_keeps_parse_request_replayable -p no:cacheprovider
```

结果：

```text
py_compile passed
Docker daemon unavailable at npipe:////./pipe/dockerDesktopLinuxEngine
Gate C outbox publish failure test failed before assertions: PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

## Validation

```powershell
python tools/scripts/verify_phase11_ingestion_source_lineage.py
pytest -q tests/repo/test_phase11_ingestion_source_lineage.py tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_source_object_commit.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_source_object_upload.py tests/knowledge/test_ingestion_source_object_commit.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
pytest -q tests/knowledge/test_document_ingestion_contract.py -p no:cacheprovider
pytest -q tests/repo/test_phase11_legacy_upload_parser_cutover.py tests/knowledge/test_legacy_cutover_adapter.py tests/storage/test_pipeline.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_snapshot_handoff.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_human_review.py tests/knowledge/test_ingestion_snapshot_handoff.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py tests/knowledge/test_ingestion_delete_restore.py tests/knowledge/test_ingestion_snapshot_handoff.py tests/knowledge/test_ingestion_human_review.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_delete_restore.py tests/knowledge/test_ingestion_snapshot_handoff.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_delete_restore.py tests/knowledge/test_ingestion_lease_recovery.py tests/knowledge/test_ingestion_snapshot_handoff.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_parse_control.py tests/knowledge/test_parse_gateway_runtime.py tests/knowledge/test_ingestion_lease_recovery.py -p no:cacheprovider
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
python tools/scripts/verify_input_runtime_batch.py
pytest -q tests/knowledge/test_input_runtime_batch.py tests/knowledge/test_ingestion_async_infrastructure.py tests/integration/test_phase11_ingestion_persistence_runtime.py tests/repo/test_phase11_ingestion_source_lineage.py -p no:cacheprovider
```

## Boundary

PHASE11 completed 只能表示完整 Phase Scope 内 implementation available；不表示 production ready、quality proven、PHASE12 Knowledge completed 或外部 RabbitMQ/OCR/VLM 生产依赖已在本地环境可用。外部依赖不可用时必须保留 target-blocked diagnostics，不能用 mock 冒充生产能力。

## 2026-07-20 Goal01 Reopen Audit

本文证据保留为 PHASE11 的部分实现线索，但不再证明完整 Phase completed。剩余缺口包括真实 RabbitMQ 生产默认 dispatch/ACK/retry/DLQ/replay、生产默认 worker 接入 PostgreSQL UoW 与 PHASE04 Object Store、真实 OCR/VLM 与 Office/Layout provider 集成、Human Review task/decision/receipt 生产表与 worker 接线、完整 delete/legal hold/restore fault coverage，以及 legacy upload/parser 默认路径继续从过渡 ChunkModel 投影迁移到 IndexableDocumentSnapshot / Outbox handoff。

2026-07-20 workspace upload production-default bootstrap：

- `WorkspaceTaskRuntimeService.register_file(...)` 已有 Package A 分支，本次将应用启动配置接入该分支：`init_config()` 使用当前 PostgreSQL `engine` 和 `storage.mode=minio` 配置构造 `PackageAProductionIngestionRuntime`。
- 新增 `build_package_a_production_ingestion_runtime(...)`：配置齐备时组装 PHASE04 `MinioObjectStore`、`DurableMinioObjectStore` 和 Package A runtime；配置缺失或非 MinIO 时返回 `None`，避免把本地/测试 adapter 冒充为生产默认路径。
- 新增 `tests/api/test_workspace_package_a_production_bootstrap.py`，验证默认 factory 绑定 PostgreSQL engine、MinIO object store、Durable manifest owner `workspace.file_upload` 和 Package A runtime worker `workspace-file-upload`。

新增验证：

```text
python -m py_compile src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/main.py
pytest -q tests/api/test_workspace_package_a_production_bootstrap.py -p no:cacheprovider
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A bootstrap tests passed: 2 passed
Worker ObjectRef verifier fault test passed: 1 passed
Gate C real MinIO/RabbitMQ/PostgreSQL E2E remains environment_blocked in this machine because Docker daemon and PostgreSQL localhost:5432 are unavailable
```

2026-07-20 Package A RabbitMQ worker bootstrap：

- 新增 `PackageAProductionQueueWorker`，把 PHASE04 transactional outbox publisher、RabbitMQ topology/consumer 和 `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 接成一个生产 worker pump。
- `publish_and_consume_once(...)` 顺序为声明 topology、用 `PostgresOutboxRabbitMQPublisher.publish_batch(...)` 发布 pending outbox、从 canonical ingestion parse queue 获取 RabbitMQ delivery、交给 Package A runtime 处理；ACK/NACK/Reject 仍只由 runtime 在领域事务边界后执行。
- `platform/services/queue/runner.py` 新增 `run_package_a_ingestion_worker_forever(...)`，`rabbitmq.enabled` 且未显式关闭 `package_a_ingestion_enabled` 时默认启动 Package A ingestion worker，不再默认落到旧 parse/index/graph worker。
- 新增 `tests/knowledge/test_package_a_queue_worker.py`，覆盖 canonical RabbitMQ topology 默认值、worker pump 的 publish -> consume -> runtime handoff 顺序，以及 queue runner 默认选择 Package A worker。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/worker.py src/backend/zuno/knowledge/ingestion/__init__.py src/backend/zuno/platform/services/queue/runner.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker tests passed: 3 passed
```

2026-07-20 Package A outbox tenant dispatch fix：

- `PostgresOutboxRabbitMQPublisher` 支持 `tenant_id=None` 的跨租户 dispatcher 模式：固定 tenant 时仍拒绝不匹配 outbox record；跨租户模式下使用 outbox record 自身 `tenant_id` 写入 RabbitMQ header。
- `PackageAProductionQueueWorker` 默认不再携带 `system` tenant，避免真实 workspace upload 以用户 tenant 写入的 `ingestion.parse.requested` outbox 在 dispatch 阶段被误拒绝。
- `run_package_a_ingestion_worker_forever(...)` 只有在 `rabbitmq.tenant_id` 显式配置时才启用固定 tenant 发布，否则使用 record tenant，保持 Workspace/File Upload -> Outbox -> RabbitMQ 主链路的 tenant scope。
- `tests/knowledge/test_package_a_queue_worker.py` 新增覆盖跨租户 publisher 使用 outbox record tenant，并保留固定 tenant 模式拒绝不匹配 record 的保护；原 queue worker 测试同步验证默认 publisher `tenant_id=None`。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/queue/outbox.py src/backend/zuno/knowledge/ingestion/worker.py src/backend/zuno/platform/services/queue/runner.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker tenant dispatch tests passed: 5 passed
```

2026-07-20 Package A bounded RabbitMQ pump：

- `PackageAProductionQueueWorker.publish_and_consume_once(...)` 支持 `consume_limit`，默认与 `publish_limit` 对齐；一次 pump 可在发布 pending outbox batch 后消费有界数量的 RabbitMQ delivery，避免生产 worker 每轮只处理一条消息。
- 每条 delivery 仍逐一交给 `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)`；ACK/NACK/Reject 和 PostgreSQL 领域事务边界不移出 runtime。
- `run_package_a_ingestion_worker_forever(...)` 透传 `ingestion_publish_limit`、`ingestion_consume_limit` 和 `ingestion_consume_timeout_seconds` 配置，允许生产部署控制 outbox dispatch 与 consumer backpressure。
- `tests/knowledge/test_package_a_queue_worker.py` 新增 bounded batch 覆盖，验证同一 pump 可处理多条 delivery，并在空队列时停止而不重复处理。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/worker.py src/backend/zuno/platform/services/queue/runner.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker bounded batch tests passed: 6 passed
```

2026-07-20 Package A topic-scoped outbox dispatch：

- `InfrastructureRepository.claim_outbox(...)` 新增 optional topic filter，在 PostgreSQL `FOR UPDATE SKIP LOCKED` claim 阶段只选目标 topic，避免 claim 后再丢弃造成错误占用。
- `PostgresOutboxRabbitMQPublisher` 新增 `topics` 参数并下推到 repository claim；未配置 topics 时保留 PHASE04 通用 publisher 行为。
- `PackageAProductionQueueWorker` 固定传入 `("ingestion.parse.requested",)`，确保 Package A RabbitMQ dispatcher 只把 parse requested outbox 发布到 canonical parse queue，不会把 Snapshot handoff 或其他模块 outbox 发布到 parser worker。
- `tests/knowledge/test_package_a_queue_worker.py` 新增 topic-scoped claim 覆盖，并验证 Package A worker 创建 publisher 时携带 parse requested topic filter。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/database/foundation.py src/backend/zuno/platform/queue/outbox.py src/backend/zuno/knowledge/ingestion/worker.py src/backend/zuno/knowledge/ingestion/__init__.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker topic dispatch tests passed: 7 passed
```

2026-07-20 Package A RabbitMQ DLQ settlement：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 现在在 PostgreSQL 领域 UoW 成功退出后按 worker receipt settlement：成功、retryable retry-enqueued、cancelled 和 duplicate/redelivery 继续 ACK；`dead_letter` 改为 `delivery.reject(requeue=False)`，交给 RabbitMQ DLX。
- `PackageAWorkerReceipt.acked_after_domain_commit` 对 `dead_letter` 返回 `False`，避免把 DLQ 语义误写成 ACK 成功。
- 保留 PostgreSQL `ingestion_dead_letters.rabbitmq_dead_letter_ref`，并把 RabbitMQ DLQ disposition 与领域 dead-letter receipt 对齐。
- 新增 `tests/knowledge/test_package_a_delivery_settlement.py`，不依赖数据库验证 success ACK 与 dead_letter reject(requeue=false) 的分流。
- 更新 Gate B non-retryable DLQ integration 断言：dead_letter 后不 ACK、不 NACK、reject 到 RabbitMQ DLQ。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_delivery_settlement.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement tests passed: 2 passed
Worker ObjectRef verifier fault test passed: 1 passed
```

2026-07-20 Package A poison delivery rejection：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 在 `CanonicalOutboxDeliveryV1` schema validation、payload hash verification 或 envelope consistency check 失败时，先 `delivery.reject(requeue=False)`，再抛出 `IngestionPersistenceError`。
- 这类 poison delivery 不进入 PostgreSQL UoW、不 claim ParseAttempt/Lease，也不会无限 requeue 阻塞 canonical parse queue。
- `tests/knowledge/test_package_a_delivery_settlement.py` 新增 invalid schema 与 payload hash mismatch 覆盖，验证两类坏消息均 reject(requeue=false) 且不 ACK。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_delivery_settlement.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement poison-message tests passed: 4 passed
```

2026-07-20 Package A retry exhaustion boundary：

- `PackageAProductionIngestionRuntime` 将 retryable failure 的 terminal status 判定抽为 `_failure_terminal_status(...)`，保持 `max_attempts` 包含初次执行：`prior_attempt_count=0` 的首次 retryable failure 进入 `failed` 并 enqueue retry；`prior_attempt_count=1` 且 `max_attempts=2` 时进入 `dead_letter`。
- non-retryable failure 无论 attempt count 都直接进入 `dead_letter`，不创建 retry outbox。
- 新增 `tests/knowledge/test_package_a_retry_boundary.py`，覆盖 retryable first attempt、retry exhausted、non-retryable first attempt，以及负 attempt count 拒绝。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_retry_boundary.py
pytest -q tests/knowledge/test_package_a_retry_boundary.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A retry boundary tests passed: 3 passed
```

2026-07-20 Package A misrouted delivery rejection：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 在进入 PostgreSQL UoW 前校验 delivery topic、envelope contract name 和 consumer module。
- 只有 `ingestion.parse.requested` / `zuno.ingestion.parse.requested` / `ingestion.parser_worker` 的 canonical delivery 能进入 inbox 和 ParseJob 处理；误路由的 Snapshot、Knowledge index 或其他模块 envelope 会 `reject(requeue=False)`。
- `PackageAProductionQueueWorker` 复用 runtime 导出的 `PACKAGE_A_PARSE_REQUESTED_TOPIC`，避免 dispatcher topic 和 consumer validation 分叉。
- `tests/knowledge/test_package_a_delivery_settlement.py` 新增 wrong topic、wrong contract、wrong consumer 覆盖，验证误路由消息 reject 且不 ACK。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/knowledge/ingestion/worker.py src/backend/zuno/knowledge/ingestion/__init__.py tests/knowledge/test_package_a_delivery_settlement.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement misroute tests passed: 7 passed
```

2026-07-20 Package A delivery lineage gate：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 在 first-seen delivery 进入 ParseAttempt/Lease claim 前，逐项校验 RabbitMQ envelope payload 与 PostgreSQL ParseJob context 的 lineage 一致性。
- 校验范围包括 tenant、workspace、SourceObject、DocumentVersion、ParsePlan、ParseJob、ObjectRef、ObjectManifest、content hash、size、mime type 和 Security Epoch。
- 不一致的 delivery 抛出 `PackageARejectDeliveryError` 并在 PostgreSQL UoW rollback 后 `reject(requeue=False)`；不会持久化 worker inbox、不会创建 append-only ParseAttempt、不会 claim Lease，也不会调用 Parser Gateway。
- 新增 Gate B focused integration test `test_gate_b_rejects_delivery_lineage_mismatch_before_attempt`，覆盖伪造 `source_object_id` 的 parse request 在 attempt/lease 前被拒收。
- 当前环境已真实尝试运行该 Gate B 测试，但 PostgreSQL `localhost:5432` 连接超时，测试在 Alembic upgrade 前阻塞；因此该项 PostgreSQL runtime evidence 仍为 environment_blocked，不计为 Gate B passed。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/knowledge/ingestion/__init__.py tests/knowledge/test_package_a_delivery_settlement.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_rejects_delivery_lineage_mismatch_before_attempt -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement and lineage unit tests passed: 9 passed
Gate B lineage mismatch integration attempted; environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 Package A ObjectRef verification DLQ：

- `_read_and_verify_object(...)` 的 scope、hash/size、visibility 和 invalid `s3://` 校验失败现在抛出 `PackageAObjectVerificationError`，并携带稳定 `failure_code`。
- `PackageAProductionIngestionRuntime._process_first_seen_delivery(...)` 在已创建 ParseAttempt/Lease 后捕获该异常，在同一个 PostgreSQL UoW 内关闭 Attempt/Lease，写入 `ingestion_dead_letters`，并返回 `dead_letter` worker receipt。
- 领域事务提交后，既有 settlement 逻辑会对该 receipt 执行 `delivery.reject(requeue=False)`，把确定性坏对象交给 RabbitMQ DLQ，而不是不 ACK 后无限重投。
- 新增 Gate B focused integration test `test_gate_b_object_hash_mismatch_records_dlq_without_requeue`，覆盖 MinIO/ObjectRef bytes mismatch 不调用 Parser Gateway、attempt/lease/job/dead_letter receipt 全部进入 terminal DLQ 语义。
- 当前环境已真实尝试运行该 Gate B 测试，但 PostgreSQL `localhost:5432` 连接超时，测试在 Alembic upgrade 前阻塞；因此 PostgreSQL-backed object verification DLQ evidence 仍为 environment_blocked，不计为 Gate B passed。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/knowledge/ingestion/__init__.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility -p no:cacheprovider
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_object_hash_mismatch_records_dlq_without_requeue -p no:cacheprovider
```

结果：

```text
py_compile passed
Worker ObjectRef verifier fault test passed: 1 passed
Gate B object hash mismatch DLQ integration attempted; environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 Package A Quality Gate blocks handoff：

- `PackageAProductionIngestionRuntime._process_first_seen_delivery(...)` 在 Parser Gateway 成功返回 CanonicalDocumentIR 后，先持久化 ParseSnapshot、SourceSpan 和 Quality Decision。
- 当 `HumanReviewRuntime.can_publish_snapshot(...)` 为 false 时，runtime 在同一个 PostgreSQL UoW 内关闭 Attempt/Lease 为 `failed`，写入稳定 `failure_code=quality_gate_<verdict>`，并返回 ACK-after-domain-commit receipt。
- 质量不可发布时不再抛异常导致 RabbitMQ 重投，也不会生成 IndexableDocumentSnapshot 或 Snapshot Outbox；因此低质量解析结果不会进入 Knowledge handoff。
- 新增 Gate B focused integration test `test_gate_b_quality_review_records_snapshot_without_indexable_handoff`，覆盖低置信度 Markdown parse 只留下 parse/quality 证据，不发布 indexable handoff。
- 当前环境已真实尝试运行该 Gate B 测试，但 PostgreSQL `localhost:5432` 连接超时，测试在 Alembic upgrade 前阻塞；因此 PostgreSQL-backed quality gate evidence 仍为 environment_blocked，不计为 Gate B passed。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_delivery_settlement.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_quality_review_records_snapshot_without_indexable_handoff -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement and quality helper tests passed: 10 passed
Gate B quality review integration attempted; environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 Package A Parser Gateway identity gate：

- `PackageAProductionIngestionRuntime._validate_parser_identity(...)` 校验 Parser Gateway 返回的 `result.job_id` 必须等于 PostgreSQL `ParseJob`，成功 snapshot 的 `parse_attempt_id` 必须等于当前 append-only `ParseAttempt`。
- 身份不一致时抛出 `PackageAParserIdentityError`，runtime 在同一 PostgreSQL UoW 内关闭 Attempt/Lease，写入 `ingestion_dead_letters`，并返回 `dead_letter` worker receipt。
- 领域事务提交后 settlement 执行 `delivery.reject(requeue=False)`，防止另一套 Parser Gateway Job/Attempt ID 进入 ParseSnapshot、SourceSpan、QualityDecision 或 Indexable handoff。
- 新增 Gate B focused integration test `test_gate_b_parser_attempt_identity_mismatch_dead_letters_without_snapshot`，覆盖成功 parse 但 snapshot attempt ID 不匹配时不写 ParseSnapshot、不生成 handoff。
- 当前环境已真实尝试运行该 Gate B 测试，但 PostgreSQL `localhost:5432` 连接超时，测试在 Alembic upgrade 前阻塞；因此 PostgreSQL-backed parser identity evidence 仍为 environment_blocked，不计为 Gate B passed。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/knowledge/ingestion/__init__.py tests/knowledge/test_package_a_delivery_settlement.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_parser_attempt_identity_mismatch_dead_letters_without_snapshot -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement and parser identity unit tests passed: 11 passed
Gate B parser identity integration attempted; environment_blocked by PostgreSQL localhost:5432 connection timeout during alembic upgrade
```

2026-07-20 Package A Workspace upload hash gate：

- `WorkspaceTaskRuntimeService.register_file(...)` 现在先基于实际 upload content 计算 SHA256。
- 如果调用方提供 `file_hash` 且与实际 content hash 不一致，入口返回 HTTP 400，且不会创建 `UploadedFileContract`、不会写 `_file_text`、不会调用 `PackageAProductionIngestionRuntime.accept_workspace_upload(...)`。
- 若 hash 匹配或未提供 hash，前台 file contract、`file_status.source_sha256` 和 Package A `PackageAUploadCommand.content` 共享同一份实际内容 hash，避免 Workspace/File Upload 与 PostgreSQL SourceObject lineage 分叉。
- 新增 focused service tests `tests/api/test_workspace_package_a_upload_hash_gate.py`，覆盖 mismatch 拒绝和 match 后进入 Package A production runtime。

新增验证：

```text
python -m py_compile src/backend/zuno/api/services/workspace_task_runtime.py tests/api/test_workspace_package_a_upload_hash_gate.py
pytest -q tests/api/test_workspace_package_a_upload_hash_gate.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Workspace Package A upload hash gate tests passed: 2 passed
```

2026-07-20 Package A Workspace upload bucket config gate：

- `WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(...)` 现在保存 Package A upload bucket，`register_file(...)` 创建 `PackageAUploadCommand` 时使用该配置，不再写死 `zuno-ingestion`。
- `resolve_package_a_upload_bucket(...)` 从现有 `storage.minio.bucket_name` 解析 PHASE04 MinIO bucket；配置缺失时保留历史默认值，避免破坏无 MinIO bucket 字段的本地测试替身。
- 应用启动 `init_config()` 在构造 Package A production runtime 后，将同一份 `app_settings.storage.minio.bucket_name` 传入 Workspace 默认上传路径，防止 Workspace/File Upload 写入的 ObjectRef bucket 与部署配置分叉。
- 新增 focused service/bootstrap coverage，验证自定义 MinIO bucket 被解析并进入 Package A upload command。

新增验证：

```text
python -m py_compile src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/main.py tests/api/test_workspace_package_a_production_bootstrap.py tests/api/test_workspace_package_a_upload_hash_gate.py
pytest -q tests/api/test_workspace_package_a_production_bootstrap.py tests/api/test_workspace_package_a_upload_hash_gate.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Workspace Package A production bootstrap and upload hash/bucket tests passed: 4 passed
```

2026-07-20 Package A Worker Inbox identity gate：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 记录 worker inbox 时现在使用 runtime 配置的 `worker_id`，与同一执行中的 ParseAttempt lease claim、running mark、renew、terminal commit/fail 使用同一个 worker identity。
- 这修正了 Inbox 幂等 consumer 固定为 `phase11-package-a-parser-worker`，但实际 worker 可由 RabbitMQ runner 配置为 `rabbitmq.ingestion_worker_id` 的身份分叉问题。
- 新增 focused settlement test 覆盖 duplicate/redelivery replay 路径：RabbitMQ delivery 被判定为已处理时，`record_worker_inbox.consumer` 必须等于 runtime worker id，随后在领域事务退出后 ACK。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_delivery_settlement.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement, lineage, parser identity, and worker inbox identity tests passed: 12 passed
```

2026-07-20 Package A PostgreSQL expected-state fencing：

- `IngestionRepository._update_attempt_if_current(...)` 现在把 expected Attempt status 纳入 PostgreSQL 条件更新，和 tenant、ParseJob、Attempt、worker、fencing token、最高 token、未过期 lease、非终态一起作为同一次数据库更新的拒绝条件。
- `mark_parse_attempt_running(...)` 只允许 `lease_claimed -> running`；`renew_parse_attempt_lease(...)` 只允许续租已 running attempt；`commit_parse_attempt_if_current(...)` 和 `fail_parse_attempt(...)` 只允许 running attempt 进入 terminal 状态；expired lease reconciliation 只允许 claimed/running attempt 进入 `lease_lost`。
- 这补齐了 Package A 目标里的 “Fencing 提交必须由数据库同时校验当前 token、owner、有效 Lease、expected state 和 Attempt ID” 中 expected state 的数据库条件，防止 Runtime 调用顺序错误时越级提交成功。
- 新增 focused repository tests 覆盖 running、commit、failure 三条路径传入 expected status，并拒绝空 expected-state 集合。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/database/ingestion/persistence.py tests/knowledge/test_package_a_persistence_fencing.py
pytest -q tests/knowledge/test_package_a_persistence_fencing.py -p no:cacheprovider
pytest -q tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A persistence expected-state fencing tests passed: 4 passed
Package A delivery settlement tests passed: 12 passed
```

2026-07-20 Package A rejected delivery batch resilience：

- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 现在对 schema/hash、topic/contract/consumer 和 tenant header mismatch 这类已执行 `reject(requeue=False)` 的确定性坏消息统一抛出 `PackageARejectDeliveryError`。
- `PackageAProductionQueueWorker.publish_and_consume_once(...)` 只捕获该已拒收错误并继续消费本轮 batch 后续 delivery；数据库 UoW、fencing、object verification 或 Parser Gateway 等未完成领域事务的错误仍会冒泡，不会被 worker 当作成功 ACK。
- `PackageAQueuePumpReceipt` 新增 `rejected_delivery_count`，用于区分“本轮收到并拒收坏消息”和“没有收到消息”，同时保留成功 worker receipts。
- 新增 focused worker test 覆盖第一条 poison delivery 被拒收后，第二条正常 delivery 仍进入 runtime 并返回成功 receipt。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/knowledge/ingestion/worker.py tests/knowledge/test_package_a_queue_worker.py tests/knowledge/test_package_a_delivery_settlement.py
pytest -q tests/knowledge/test_package_a_queue_worker.py tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker and delivery settlement tests passed: 20 passed
```

2026-07-20 Package A retry parent lineage：

- `PackageAProductionIngestionRuntime._retry_parse_requested_envelope(...)` 现在接收失败的 `retry_parent_attempt_id`，并把 `retry_attempt_no`、`retry_parent_attempt_id`、`retry_parent_message_id` 和 `retry_parent_idempotency_key` 写入 retry parse-request payload。
- Retry outbox message 仍保留同一个 PostgreSQL `ParseJob` aggregate，但使用新的 message id、idempotency key 和 causation id；payload 更新后同步重算 canonical `payload_hash`。
- 这让 retry message 本身携带“由哪个 append-only ParseAttempt 失败后产生”的可审计 lineage，避免只靠外层 idempotency key 推断 retry parent。
- 新增 focused retry boundary test 覆盖 retry parent attempt、message、idempotency 和 payload hash。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_retry_boundary.py
pytest -q tests/knowledge/test_package_a_retry_boundary.py tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A retry boundary and delivery settlement tests passed: 16 passed
```

2026-07-20 Package A Snapshot handoff idempotency persistence：

- 新增 forward migration `20260720_20_package_a_handoff_idempotency.py`，在 `ingestion_indexable_document_snapshots` 增加 `handoff_idempotency_key`，在 `ingestion_outbox_events` 增加 `idempotency_key`。
- Migration 对既有 snapshot handoff outbox 做回填：从 `payload.idempotency_key` 回填 outbox，再通过 `aggregate_ref = indexable_snapshot_id` 回填 indexable snapshot；同时增加 tenant-scoped partial unique indexes，避免重复 handoff/outbox idempotency。
- `IngestionRepository.record_indexable_snapshot(...)` 和 `enqueue_outbox_event(...)` 现在持久化 handoff idempotency；Package A success path 将 `IndexableDocumentSnapshotV1.idempotency_key` / `SnapshotOutboxEvent.idempotency_key` 写入 PostgreSQL。
- 这让 Snapshot handoff 的 duplicate/replay 判定从内存模型扩展到 PostgreSQL 事实层。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/database/ingestion/persistence.py src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_persistence_fencing.py infra/db/alembic/versions/20260720_20_package_a_handoff_idempotency.py
pytest -q tests/knowledge/test_package_a_persistence_fencing.py tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
alembic -c infra/db/alembic.ini heads
alembic -c infra/db/alembic.ini upgrade head
```

结果：

```text
py_compile passed
Package A persistence and delivery settlement tests passed: 18 passed
Alembic heads passed: 20260720_20 (head)
Alembic upgrade head attempted; local PostgreSQL connection did not return before manual interruption, so upgrade runtime verification remains environment_blocked
```

2026-07-20 Package A Snapshot handoff replay receipt：

- `load_parse_job_replay_receipt(...)` 现在返回 `indexable.handoff_idempotency_key` 和 `outbox.idempotency_key AS outbox_idempotency_key`，duplicate/redelivery receipt 不再只暴露 snapshot/outbox id。
- 新增 `load_snapshot_handoff_replay_receipt(...)`，按 `tenant_id + handoff_idempotency_key` 从 PostgreSQL 找回 IndexableDocumentSnapshot 与对应 `ingestion.indexable_snapshot.ready` outbox 状态。
- 这把上轮落库的 handoff idempotency 接入 repository replay/read path，使 crash-after-commit-before-ACK 或 duplicate handoff 可以从数据库事实层恢复既有 snapshot/outbox。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/database/ingestion/persistence.py tests/knowledge/test_package_a_persistence_fencing.py
pytest -q tests/knowledge/test_package_a_persistence_fencing.py tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A persistence replay and delivery settlement tests passed: 20 passed
```

2026-07-20 Package A Worker receipt handoff idempotency：

- `PackageAWorkerReceipt` 新增 `handoff_idempotency_key` 和 `outbox_idempotency_key`。
- first-seen success path 返回 `IndexableDocumentSnapshotV1.idempotency_key` / `SnapshotOutboxEvent.idempotency_key`；duplicate/redelivery replay path 从 `load_parse_job_replay_receipt(...)` 返回的 PostgreSQL 字段填充同样的 receipt 字段。
- 这让 RabbitMQ ACK 后的 worker receipt 明确携带它复用或创建的 Snapshot handoff/outbox 幂等事实，补齐 crash-after-commit-before-ACK 的可审计返回面。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_delivery_settlement.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement and queue worker tests passed: 20 passed
```

2026-07-20 Package A RabbitMQ Security Epoch header contract：

- `PostgresOutboxRabbitMQPublisher` 现在从 CrossModuleEnvelope 的 `effective_security_epoch_ref`（或 payload fallback）提取 `security_epoch_ref`，并交给 `RabbitMQTransport.publish(...)` 写入 RabbitMQ headers。
- `PackageAProductionIngestionRuntime.process_rabbitmq_delivery(...)` 在进入 PostgreSQL Worker Inbox 和 ParseAttempt 事务前校验 RabbitMQ header、Envelope `effective_security_epoch_ref`、payload `security_epoch_ref` 三者一致；缺失或不一致时 reject 且不 requeue。
- 这把 PHASE11 Package A 的 Security Epoch 校验从 payload/lineage 层前移到队列交付边界，防止错误重放或跨安全纪元投递进入领域事务。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/queue/rabbitmq.py src/backend/zuno/platform/queue/outbox.py src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_delivery_settlement.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery settlement and queue worker tests passed: 22 passed
```

2026-07-20 Package A PostgreSQL Lease heartbeat and successful Worker path：

- `IngestionRepository.heartbeat_parse_attempt_lease(...)` 新增明确的 heartbeat 持久化入口：只更新 `ingestion_parse_leases.heartbeat_at` 和当前 `ingestion_parse_attempts.heartbeat_at`，不延长 `lease_expires_at`。
- heartbeat 由 PostgreSQL 同时校验 `tenant_id`、`parse_job_id`、`parse_attempt_id`、`worker_id`、`fencing_token`、未过期 lease 和 `running` Attempt 状态。
- `PackageAProductionIngestionRuntime` 在 MinIO ObjectRef 校验后、Parser Gateway 返回后各记录一次 heartbeat，再继续写 ParseSnapshot / SourceSpan / Quality Decision / Indexable Snapshot / Snapshot Outbox。
- 修复 Package A success path 中对 `IndexableDocumentSnapshotV1.visibility_ref` 的错误读取；visibility ref 现在由同一个局部事实传给 handoff 和 PostgreSQL snapshot 写入。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/database/ingestion/persistence.py src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_persistence_fencing.py tests/knowledge/test_package_a_delivery_settlement.py
pytest -q tests/knowledge/test_package_a_persistence_fencing.py tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A persistence fencing and delivery settlement tests passed: 23 passed
```

2026-07-20 Package A ObjectRef revoked/deleted visibility boundary：

- `PackageAProductionIngestionRuntime._read_and_verify_object(...)` 现在先校验 PostgreSQL `source_status`，只有 `committed` 才读取 MinIO/S3 bytes。
- `revoked` / `visibility_revoked` 映射为 `object_visibility_revoked`，`deleted` / `physically_deleted` 映射为 `object_deleted`，其他非可见状态仍映射为 `object_not_visible`。
- 这让 revoked/delete 状态在进入 Parser Gateway 前稳定进入现有 ObjectRef dead-letter 路径，并避免在访问已撤销或已删除 SourceObject 时触碰对象内容。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py tests/integration/test_phase11_package_a_production_runtime.py
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility tests/knowledge/test_package_a_delivery_settlement.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A ObjectRef verifier and delivery settlement tests passed: 15 passed
```

2026-07-20 Package A Workspace upload replay idempotency：

- `IngestionRepository.load_workspace_upload_replay_receipt(...)` 新增按 `tenant_id + ParseJob.idempotency_key` 读取既有 SourceObject、DocumentVersion、ParsePlan、ParseJob 和 PHASE04 `infra_outbox_events` parse-request outbox 的 replay receipt。
- `PackageAProductionIngestionRuntime.accept_workspace_upload(...)` 现在先根据上传内容计算 `parse:{tenant}:{workspace}:{sha256}:1`，命中既有 PostgreSQL 事实时直接返回 replay receipt，不再重复写 MinIO/S3，也不再撞 `ingestion_source_objects` 或 `ingestion_parse_jobs` 的唯一约束。
- replay 会校验 workspace、content hash、size、classification、Security Epoch 和 parse-request outbox 是否一致；冲突时明确失败，不伪造重复 accepted。

新增验证：

```text
python -m py_compile src/backend/zuno/platform/database/ingestion/persistence.py src/backend/zuno/knowledge/ingestion/production_runtime.py tests/knowledge/test_package_a_upload_replay.py tests/knowledge/test_package_a_persistence_fencing.py tests/api/test_workspace_package_a_upload_hash_gate.py
pytest -q tests/knowledge/test_package_a_upload_replay.py tests/knowledge/test_package_a_persistence_fencing.py tests/api/test_workspace_package_a_upload_hash_gate.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A upload replay, persistence fencing, and workspace upload hash gate tests passed: 14 passed
```

2026-07-20 Package A Outbox publish failure pump boundary：

- `PackageAProductionQueueWorker.publish_and_consume_once(...)` 现在在 PHASE04 outbox publish batch 出现失败时立即返回 `failed_publish_count`，不再继续消费 RabbitMQ deliveries。
- 这保持 publisher confirm failure / broker outage 下的语义清晰：失败 outbox 留在 PostgreSQL 的 retry/replay 路径，本轮不会通过消费旧队列消息来掩盖 dispatch 失败。
- 已有成功 publish/consume、bounded consume 和 rejected delivery continuation 语义保持不变。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/worker.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker tests passed: 10 passed
```

2026-07-20 Package A RabbitMQ DLQ replay hook：

- `PackageAProductionQueueWorker.replay_dead_letter_once(...)` 新增 Package A topology 下的 DLQ replay 入口：声明 topology，从 `zuno.ingestion.parse.dlq` 取一条 dead-letter delivery，调用 PHASE04 `RabbitMQTransport.replay_dead_letter(...)` 重投到主 parse queue，并在 replay publish 成功后 ACK 原 DLQ delivery。
- 空 DLQ 返回 `replayed=false`，不调用 replay，也不伪装有 delivery。
- 该方法只负责 RabbitMQ DLQ replay，不声明解析成功；重投后的消息仍由正常 `publish_and_consume_once(...)` / worker consumer 路径执行 schema、tenant、Security Epoch、Inbox 幂等、PostgreSQL Lease/Fencing 和 ACK-after-domain-commit。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/worker.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A queue worker tests passed: 12 passed
```

2026-07-20 Package A Worker terminal failure code receipts：

- `PackageAWorkerReceipt` 新增 `failure_code`，first-seen terminal paths 现在把 cancel/deadline、ObjectRef verification、Parser identity、Parser failure 和 Quality Gate failure 的原因直接带回 receipt。
- `IngestionRepository.load_parse_job_replay_receipt(...)` 现在读取 latest ParseAttempt `failure_code`，duplicate/redelivery replay receipt 可恢复既有 terminal reason。
- `cancel_requested` focused test 覆盖：Worker 创建/运行 Attempt 后持久化 cancelled failure code，不读取对象、不调用 Parser Gateway、不写 ParseSnapshot / SourceSpan / Quality / Indexable Snapshot / Outbox。

新增验证：

```text
python -m py_compile src/backend/zuno/knowledge/ingestion/production_runtime.py src/backend/zuno/platform/database/ingestion/persistence.py tests/knowledge/test_package_a_delivery_settlement.py tests/knowledge/test_package_a_persistence_fencing.py tests/knowledge/test_package_a_queue_worker.py
pytest -q tests/knowledge/test_package_a_delivery_settlement.py tests/knowledge/test_package_a_persistence_fencing.py tests/knowledge/test_package_a_queue_worker.py -p no:cacheprovider
```

结果：

```text
py_compile passed
Package A delivery, persistence replay, and queue worker tests passed: 37 passed
```
