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
