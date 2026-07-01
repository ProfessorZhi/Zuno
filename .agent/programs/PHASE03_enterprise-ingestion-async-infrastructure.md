# PHASE03 Enterprise Ingestion Async Infrastructure

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE03_enterprise-ingestion-async-infrastructure
status: completed

## 目标

把 Program 2 的 SQLite / local synchronous durable baseline 推进为本地可运行的 enterprise async ingestion baseline，并为 PostgreSQL、Object Store、RabbitMQ、Redis、OCR / VLM 和 external index 保留 adapter boundary 与 dependency probe。

## 范围

- DurableIngestionStore interface / protocol 与 SQLite 默认实现。
- ObjectStore abstraction with binary support：`save_bytes`、`read_bytes`、`open_stream`、`verify_sha256`、mime sniffing、size_bytes、content_type、storage_uri、source_sha256 和 object_missing diagnostics。
- LocalObjectStore 在 Product Baseline 中支持 bytes round-trip；当前 Program 2 的 `save_text()` 保留兼容路径。
- QueueBackend abstraction：`QueueMessage`、enqueue、consume、ack、fail、dead_letter 和 replay。
- LocalQueueBackend 可运行；RabbitMQQueueBackend 只做 boundary / dependency probe / target-blocked evidence，不能要求真实 RabbitMQ 才能过 tests。
- Runtime state boundary，local fallback 可运行，Redis runtime state boundary 可 probe。
- ParserWorker / IndexWorker local runner。
- OutboxEvent、DeadLetterRecord、Reconciler local baseline。
- OCR / VLM worker boundary，缺 provider 时 blocked，不创建 fake index。
- PDF / Office / image / scanned / binary async ingestion target：source object 可保存、dependency probe 可见、blocked reason 可追溯。
- file status lifecycle：`uploaded -> queued -> parsing -> parsed -> indexing -> indexed -> failed / blocked / dead_letter / cancelled`。
- ingest status / retry / cancel / replay service contract。

## 目标架构拼接点

本 phase 拼到目标架构的 Infrastructure Layer 和 Document & User Input Layer。它的输出必须能被 Knowledge Layer 和 E2E phase 消费：

- ObjectStore 保存 raw source、derived artifact、parse snapshot reference。
- DurableIngestionStore 保存 source object、workspace file、parse job、document version、blocks、index manifest、chunks、citation lineage。
- QueueBackend 和 workers 把 `/workspace/ingest` 从同步请求线程中拆出来。
- Outbox / DeadLetter / Reconciler 给后续 restart recovery、repair、retry、replay 提供事实依据。
- OCR / VLM boundary 为多模态输入保留 blocked / succeeded / failed 语义，不伪造能力。
- File lifecycle status 给 PHASE11 产品 UI、PHASE12 E2E summary 和 PHASE13 IngestionMetrics 共同消费。

本 phase 不负责 Agent Planning，但它必须保证 Agent 后续检索看到的是可追溯、可恢复、可重建的数据事实。

## 并行开发可行性

本 phase 可以由 Workstream A 独立推进，前提是 PHASE02 的 source object、parse job、index job、trace / status contract 已冻结。

可并行：

- ObjectStore bytes support 与 QueueBackend local lifecycle 可分小 agent 并行。
- ParserWorker / IndexWorker 可以在 queue contract 稳定后并行。
- Reconciler / DeadLetter 可以在 store contract 稳定后并行。

不可并行：

- `workspace_task_runtime.py` 由 Coordinator 控制，Workstream A 只能提交 patch request 或在独立分支中等待合并。
- 不能同时改 parse/index persistence schema 与 API response contract。
- 不能让 worker 重试逻辑绕过 idempotency key。

## 详细执行卡

- 输入依赖：PHASE02 的 source object、parse job、index job、status、trace 和 object URI contract；Program 2 durable ingestion tests。
- 主要交付物：ObjectStore bytes support、QueueBackend local lifecycle、ParserWorker、IndexWorker、OutboxEvent、DeadLetterRecord、Reconciler、OCR/VLM blocked boundary、PDF / Office / image / scanned target-blocked visibility、binary source object traceability、file status lifecycle 和 dependency probe。
- 可并行工作包：ObjectStore 与 QueueBackend 可分开做；ParserWorker 和 IndexWorker 在 queue contract 稳定后并行；Reconciler / DeadLetter 在 durable store contract 稳定后并行。
- Coordinator 锁点：`workspace_task_runtime.py`、public `/workspace/file` 和 `/workspace/ingest` response、schema compatibility。
- 下游交接：PHASE04 消费 index manifest/chunks/citation lineage；PHASE10/12 消费 ingest status、restart recovery、blocked diagnostics；PHASE13 消费 job latency/retry/dead-letter metrics。
- PR / commit 建议：拆成 `feat(ingestion): add object and queue boundaries`、`feat(workers): add local parser index workers`、`test(ingestion): cover reconciler and blocked ocr evidence`。

## 禁止范围

- 不要求真实部署 PostgreSQL、RabbitMQ、Redis、MinIO / S3 或 OCR / VLM provider。
- 不让测试依赖外部服务。
- 不绕过 `ParseGateway` 和 Program 2 durable lineage。
- blocked OCR / VLM 不得 fake success 或 fake index。

## 验收闸门

- local object store bytes round-trip 通过。
- local queue enqueue / consume / ack / fail / dead_letter 通过。
- ParserWorker 消费 parse_requested 并持久化 parse snapshot / document version。
- IndexWorker 消费 index_requested 并持久化 index manifest / chunks。
- RabbitMQ 未配置时返回 dependency probe / target-blocked evidence，而不是测试失败或假成功。
- Redis 未配置时 local fallback 可运行，Redis boundary 返回 dependency probe / target-blocked evidence。
- OCR / VLM 未配置时 image / scanned 进入 blocked，blocked 不创建 fake index。
- Reconciler 能检测 parse_succeeded_without_index 和 index_chunks_missing。
- file status lifecycle transitions 可追踪，至少覆盖 queued -> parsing -> parsed -> indexing -> indexed，以及 blocked / failed / dead_letter / cancelled 中的失败路径。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/knowledge/storage/**`
- `src/backend/zuno/knowledge/ingestion/**`
- `src/backend/zuno/knowledge/indexing/**`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`
- `tests/knowledge/**`

## 需要修改的文件

- `src/backend/zuno/knowledge/storage/**`
- `src/backend/zuno/knowledge/workers/**`
- `src/backend/zuno/knowledge/ingestion/**`
- `tests/knowledge/**`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 执行拆解

1. 写 ObjectStore bytes focused test。
2. 写 QueueBackend local lifecycle focused test。
3. 写 ParserWorker / IndexWorker focused tests。
4. 写 Reconciler drift detection test。
5. 写 PDF / Office / OCR / VLM target-blocked no fake index focused tests。
6. 写 file status lifecycle focused tests。
7. 实现 local baseline 和 external dependency probe。
8. 确认 existing durable ingest tests 不回退。

## 多 agent 分工

- Workstream A owner。
- Coordinator 只审查 shared API 与 workspace runtime 接入。
- Workstream B 可只读消费 index handoff contract。

## 需要返回的证据

- object store、queue、worker、outbox、dead letter、reconciler tests。
- external adapter target-blocked evidence。
- blocked OCR / VLM 不 fake index evidence。
- PDF / Office / image / scanned / binary source object traceability evidence。
- status / retry / cancel / replay contract evidence。

## Closure Evidence

- Runtime files：`src/backend/zuno/knowledge/storage/local_object_store.py`、`src/backend/zuno/knowledge/ingestion/async_runtime.py`、`src/backend/zuno/knowledge/storage/durable_ingestion_store.py`。
- ObjectStore bytes：`LocalObjectStore.save_bytes/read_bytes/open_stream/verify_sha256/diagnose_object` 覆盖 bytes round-trip、mime sniff、sha256 和 object_missing diagnostics。
- Queue / worker：`LocalQueueBackend` 覆盖 enqueue / consume / ack / fail / dead_letter / replay；`ParserWorker` 消费 `parse_requested` 并持久化 parse job、snapshot 和 document version；`IndexWorker` 消费 `index_requested` 并持久化 index manifest 和 chunks。
- External target-blocked evidence：`RabbitMQQueueBackend.dependency_probe()` 与 `RedisRuntimeStateBoundary.dependency_probe()` 返回 target-blocked，不要求真实 RabbitMQ / Redis。
- OCR / VLM no fake index：image / scanned target-blocked path 只持久化 blocked parse job / snapshot，不创建 `index_requested` 或 fake index manifest。
- Reconciler：`IngestionReconciler` 覆盖 `parse_succeeded_without_index` 和 `index_chunks_missing`。
- Focused tests：`pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider` 通过，`4 passed`。
- Regression tests：`pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider` 通过，`4 passed, 1 warning`；`pytest -q tests/knowledge -p no:cacheprovider` 通过，`54 passed`。


## 停止条件

- 需要真实外部服务才能让测试通过。
- 需要 breaking change `/workspace/ingest` public API 且没有兼容策略。
- worker 设计会导致重复 index 或 citation lineage 丢失。
