# PHASE01 Current Persistence and Infrastructure Inventory

phase_id: PHASE01
task_id: P01-T02
start_commit: 9d10f71cc10ea1880a4a738f4500982d6684ede7
status_boundary: "Compose、配置和 Target Adapter 声明不能单独证明 Server Product Current；Current 至少需要代码与测试或运行证据。"

Server Product Target present does not mean server capability is proven; PostgreSQL, RabbitMQ, MinIO/S3 and external index capabilities are not proven Current until real integration evidence exists.

## 1. Developer / CI Current

| capability | path | symbol | current evidence | boundary |
| --- | --- | --- | --- | --- |
| SQLite durable ingestion store | `src/backend/zuno/knowledge/storage/durable_ingestion_store.py` | `SQLiteDurableIngestionStore` | `tests/knowledge/test_enterprise_ingestion_storage_contract.py`, `tests/api/test_workspace_durable_ingest_runtime.py` | uses `create_engine("sqlite:///...")` and `SQLModel.metadata.create_all()`; not PostgreSQL Current |
| Ingestion SQLModel tables | `src/backend/zuno/knowledge/storage/sqlmodel_models.py` | `SourceObjectTable`, `WorkspaceFileTable`, `ParseJobTable`, `ParseSnapshotTable`, `DocumentVersionTable`, `DocumentBlockTable`, `IndexManifestTable`, `IndexChunkTable`, `WorkspaceTaskTable`, `TaskEventTable`, `ArtifactTable`, `FeedbackTable` | storage and workspace tests | local schema surface only |
| Local object store | `src/backend/zuno/knowledge/storage/local_object_store.py` | `LocalObjectStore` | `tests/knowledge/test_ingestion_async_infrastructure.py` | writes local `file:` URI and validates sha256 |
| Local in-process queue | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `LocalQueueBackend` | `tests/knowledge/test_ingestion_async_infrastructure.py` | supports enqueue/consume/ack/fail/dead letter/replay locally |
| Local parser/index workers | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `ParserWorker`, `IndexWorker`, `IngestionReconciler` | `tests/knowledge/test_ingestion_async_infrastructure.py` | worker evidence is local queue + local store |
| SQLite agent runtime store | `src/backend/zuno/agent/runtime/sqlite_store.py` | `SQLiteAgentRunStore` | `tests/agent/runtime/test_runtime_store.py`, `tests/api/test_workspace_runtime_recovery.py` | stores runs/checkpoints/events/interrupts/plan versions/observations/tool claims in SQLite |
| Runtime checkpointer bridge | `src/backend/zuno/agent/runtime/checkpointer.py` | `RuntimeGraphCheckpointer` | `tests/agent/runtime/test_runtime_restart_persistence.py` | not LangGraph PostgreSQL checkpointer |
| Local trace store | `src/backend/zuno/platform/observability/local_trace_store.py` | `SQLiteLocalTraceStore` | observability/repo tests | local append store, not server observability pipeline |
| Local BM25/vector/graph-shaped index | `src/backend/zuno/knowledge/indexing/runtime.py`, `src/backend/zuno/knowledge/indexing/adapters.py` | `KnowledgeIndexRuntime`, `INDEX_ADAPTER_CONTRACTS` | `tests/knowledge/test_index_jobs_runtime.py`, `tests/e2e/test_pdf_agent_answer.py` | deterministic in-process local adapters; external indexes remain Target |

## 2. Server Product Target Present But Not Proven Current

| capability | path | symbol | status | missing evidence |
| --- | --- | --- | --- | --- |
| PostgreSQL config | `src/backend/zuno/platform/config/config.example.yaml` | `database.sync_endpoint`, `database.async_endpoint` | target declared | real integration run, isolation/lock/fault tests |
| PostgreSQL engine | `src/backend/zuno/platform/database/__init__.py` | `engine`, `async_engine`, `ensure_database` | implementation surface present | domain UoW integration and recovery evidence |
| Alembic | `infra/db/alembic/env.py`, `infra/db/alembic/versions/20260417_01_init_postgresql.py` | `target_metadata`, `upgrade`, `downgrade` | migration surface present | fine-grained migration, backfill/cutover/rollback proof |
| PostgreSQL runtime tables | `src/backend/zuno/platform/database/models/agent_runtime.py` | `AgentRuntimeRunTable`, `AgentRuntimeCheckpointTable`, `AgentRuntimeEventTable`, `AgentRuntimeInterruptTable` | target table models present | real runtime path writing PostgreSQL |
| RabbitMQ | `src/backend/zuno/platform/services/queue/client.py`, `runner.py`, `workers.py` | `QueueClient`, `consume_forever`, `ParseWorker`, `IndexWorker`, `GraphWorker` | target client/worker surface | real ACK/redelivery/duplicate/out-of-order/crash tests |
| RabbitMQ boundary | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `RabbitMQQueueBackend` | explicit local target-blocked boundary | actual server adapter evidence |
| Redis | `src/backend/zuno/platform/services/redis.py` | `RedisClient`, `redis_client` | lazy client surface | real connection and recovery tests |
| Redis boundary | `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `RedisRuntimeStateBoundary` | explicit target-blocked boundary | proof that Redis is non-authoritative |
| MinIO/S3 | `src/backend/zuno/platform/services/storage/minio.py`, `storage/__init__.py` | `MinioClient`, `LazyStorageClient` | target surface | bucket, permission, lifecycle and recovery evidence |
| External vector/graph/search | `src/backend/zuno/knowledge/indexing/adapters.py`, `infra/docker/docker-compose.yml` | `elasticsearch`, `milvus`, `neo4j` | target-blocked adapters / compose services | real index publish, visibility, delete and rebuild evidence |
| Backup/restore | `infra/docker/docker-compose.yml` volumes | `postgres_data`, `redis_data`, `rabbitmq_data`, `minio_data`, `backend_vector_db` | storage volumes declared | backup, restore, PITR and cutover validation not found |

## 3. Environment and Secrets

- `src/backend/zuno/platform/settings.py` loads `ZUNO_CONFIG` / `AGENTCHAT_CONFIG` and local config fallback paths through `Settings`, `resolve_app_config_path`, and `initialize_app_settings`.
- `infra/docker/docker-compose.yml` declares `postgres`, `redis`, `rabbitmq`, `neo4j`, `elasticsearch`, `minio`, `etcd`, `milvus`, `backend`, `worker`, and `frontend`.
- `src/backend/zuno/platform/config/config.example.yaml` contains secret-shaped configuration fields for model providers, tools, object storage, WeChat, Langfuse and LangSmith. These are configuration surfaces, not secret governance Current.

## 4. Unproven Capabilities

- PostgreSQL concurrency, locks, isolation, crash recovery, upgrade/downgrade execution and real domain UoW evidence are not Current.
- RabbitMQ real ACK, lease loss, duplicate/out-of-order delivery and worker crash recovery are not Current.
- Redis is not proven as a non-authoritative cache under eviction/clear/recovery.
- MinIO/S3 object write, read authorization, lifecycle and restore are not Current.
- Milvus/Neo4j/Elasticsearch are not Current runtime indexes.
- Backup/restore and PITR are not implemented evidence.
- Alembic currently has a metadata-wide initial revision; PHASE04 must not treat `create_all()` style surfaces as mature migration evidence.
