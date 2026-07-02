# Input Layer And Document Processing

本文说明企业知识库文件如何进入 Zuno runtime。格式矩阵和成熟度边界仍以 `document-ingestion-foundation.md` 和 `production-readiness.md` 为准。

## Current Local Slice

当前已证明：

- `src/backend/zuno/knowledge/storage/local_object_store.py` 提供 `save_bytes()`、`read_bytes()`、`open_stream()` 和 sha256 verification。
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py` 和 `sqlmodel_models.py` 保存 source object、workspace file、parse job / snapshot、document version / blocks、index manifest / chunks 和 citation lineage。
- `src/backend/zuno/knowledge/ingestion/async_runtime.py` 提供 `LocalQueueBackend`、`RabbitMQQueueBackend` dependency probe、`RedisRuntimeStateBoundary` local fallback、`ParserWorker`、`IndexWorker`、dead letter 和 `IngestionReconciler`。
- `ParseGateway` 支持 native deterministic parser：txt、md、csv、json、html、code。
- PDF、Office、image、scanned、OCR / VLM 在未配置生产 provider 时进入 target-blocked diagnostics，不创建 fake index。
- PHASE12 E2E 已证明 binary source object 保存 sha256 / storage_uri，即使解析 blocked 仍可追溯。

对应测试包括 `tests/knowledge/test_ingestion_async_infrastructure.py`、`tests/api/test_workspace_durable_ingest_runtime.py`、`tests/knowledge/test_document_ingestion_contract.py`、`tests/evals/test_agentic_graphrag_product_baseline.py` 和 `tests/evals/test_agentic_graphrag_regression_summary.py`。

## 输入链路

```text
workspace file upload
  -> source object
  -> workspace file metadata
  -> parse_requested
  -> ParserWorker / ParseGateway
  -> DocumentVersion / DocumentBlocks
  -> index_requested
  -> IndexWorker / KnowledgeIndexRuntime
  -> IndexManifest / IndexChunks / CitationLineage
  -> retrieval / cited artifact
```

每个阶段都必须保留 workspace_id、file_id、source_sha256、document_version_id、parse_job_id、parse_attempt_id、parser diagnostics 和 index manifest lineage。

## 格式边界

| 类型 | Current | Target |
| --- | --- | --- |
| txt / md / csv / json / html / code | native deterministic parser，可进入本地 parse / index / retrieval。 | 更丰富的 chunk policy 和质量指标。 |
| PDF | dependency probe / target-blocked diagnostics；不 fake success。 | Docling / PyMuPDF worker。 |
| Office | dependency probe / target-blocked diagnostics；不 fake success。 | Unstructured / MarkItDown worker。 |
| image / scanned | OCR / VLM target-blocked diagnostics；不 fake index。 | MinerU / OCR / VLM enrichment worker。 |
| binary / unknown | source object only 或 unsupported diagnostics。 | admin-configured parser policy。 |

## Launchable Prototype Target

- Document ingestion 专题文档与正式 architecture 总纲互相引用，但不复制 phase log。
- PHASE15 archive 保留 blocked no fake index、dead letter、reconciler、restart recovery 和 binary traceability evidence。
- Product API file-level status 保持 queued、parsing、parsed、indexing、indexed、blocked、failed 可解释。

## Production Scale Target

以下仍不是 Current：

- 真实 PostgreSQL / MinIO / S3 / RabbitMQ / Kafka / Redis。
- worker lease、heartbeat、distributed outbox operations。
- external OCR / VLM runtime。
- external index platform。
- 大规模 document operations dashboard。

## 不变量

- blocked parser 不能创建 fake index。
- source object 是原始事实，不被 parser output 覆盖。
- citation lineage 必须能回到 source object、document version、block 和 index chunk。
