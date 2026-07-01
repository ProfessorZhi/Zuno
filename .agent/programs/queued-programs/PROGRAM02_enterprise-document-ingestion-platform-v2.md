# PROGRAM02 Enterprise Document Ingestion Platform V2

state: queued
program: zuno-enterprise-document-ingestion-platform-v2
depends_on: zuno-production-document-ingestion-and-thread-foundation-v1

## 命名边界

这是 Program 1 的 V2 / Program 1B，不是篡改已归档的 Program 1A。

- Program 1A：`zuno-production-document-ingestion-and-thread-foundation-v1`，已完成并归档，关闭 `workspace ingest -> ParseGateway -> CanonicalDocumentIR -> index manifest -> citation lineage` local runtime slice。
- Program 1B / V2：`zuno-enterprise-document-ingestion-platform-v2`，把 Program 1A 的 local slice 升级为企业级文档输入与持久化平台雏形。

队列文件使用 `PROGRAM02_...`，只表示它是当前 suite 中 Program 1A 之后的下一项；业务口径仍是 Program 1 V2。

## 目标

把 Program 1A 已完成的 `workspace ingest -> ParseGateway -> Document IR -> Index Manifest -> Citation Lineage` 本地闭环，升级为可上线企业级雏形：文件由后端持久化保存，parse / index / job 状态落库，queue / worker 有可替换 adapter，OCR / VLM / PDF / Office 有明确 adapter boundary，服务重启后文档、任务、索引和引用 lineage 不丢。

## 不是目标

- 不是马上做百万文档。
- 不是马上接完整 OCR / VLM 生产服务。
- 不是马上接 Elasticsearch / Milvus / Neo4j。
- 不是马上做 Kafka 级分布式平台。
- 不是重写 `GeneralAgent` 主循环。
- 不是同时推进 Memory、Tool、Planning 或 Eval program。

## 必须完成

```text
文件输入层持久化
Document IR 持久化
parse job / attempt 持久化
index manifest / chunks 持久化
backend durable store
queue adapter boundary
local worker runner
workspace ingest status API
retry / cancel / replay API
OCR / VLM target-blocked 或 optional adapter
restart recovery test
```

## 目标架构

```text
Frontend Upload / Workspace Attachment
  -> FastAPI /workspace/file or /workspace/files/upload
  -> SourceObjectStore
       raw file / text / bytes
       source_sha256
  -> Metadata DB
       workspace_files
       source_objects
  -> /workspace/ingest
  -> ParseJobStore
       parse_jobs
       parse_attempts
  -> Queue Backend
       local queue / Redis queue boundary
  -> Parser Worker
       ParseGateway
       native / pdf / office / OCR / VLM adapter boundary
  -> Document Store
       document_versions
       document_blocks
       IR artifact
  -> Index Queue
  -> Index Worker
       KnowledgeIndexRuntime
       index_jobs
       index_chunks
       citation_lineage
  -> Agent Retrieval
  -> Cited Answer / Artifact / Trace
```

## 后端模块建议

优先复用现有代码边界；确需新增时，建议落在：

```text
src/backend/zuno/knowledge/storage/
  contracts.py
  local_object_store.py
  durable_ingestion_store.py
  durable_index_store.py
  sqlmodel_models.py

src/backend/zuno/knowledge/workers/
  queue.py
  local_queue.py
  redis_queue.py
  parser_worker.py
  index_worker.py

src/backend/zuno/api/services/
  workspace_file_service.py
  workspace_ingest_service.py
```

如果阶段风险过高，可以先把 store / worker 放在 `knowledge/ingestion/` 下，但长期目标仍是分出 `knowledge/storage` 和 `knowledge/workers`。

## 数据模型最小边界

V2 至少覆盖以下实体，先用 SQLModel / SQLite，本地开发可迁移到 Postgres-compatible schema：

- `source_objects`：原始文件事实源、storage uri、source hash、ACL、sensitivity。
- `workspace_files`：前端和 workspace 可见 file_id，关联 source object。
- `document_versions`：parser version、parser config、IR schema 和 IR artifact。
- `document_blocks`：block、source span、metadata、ACL、sensitivity。
- `parse_jobs`：parse idempotency、status、blocked reason、failure reason。
- `parse_attempts`：attempt no、worker id、diagnostics、metrics。
- `index_jobs`：knowledge space、document version、parse lineage、target status。
- `index_chunks`：content、metadata、citation lineage、ACL、sensitivity。
- `ingestion_dead_letters`：不可恢复或需人工处理的 parse / index 失败。

## Queue / Redis 策略

不要为了“用了 Redis”硬接。V2 必须先定义 `QueueBackend`：

```text
enqueue()
dequeue()
ack()
fail()
lease()
```

- `LocalQueueBackend`：默认本地和 tests 使用。
- `RedisQueueBackend`：配置 `ZUNO_QUEUE_BACKEND=redis` 时启用；如果当前依赖不可用，先提供 dependency probe 和 adapter skeleton，不让无 Redis 环境失败。

Redis 在 Production Scale Target 中用于 parse / index / ocr queue、worker lease、SSE event bridge、rate limit 和 OCR / VLM budget。

## OCR / VLM / PDF / Office 边界

OCR / VLM 是 derived enrichment worker，不是默认 parser source truth。

V2 必须持久化以下状态：

- available
- missing
- disabled
- blocked
- succeeded
- failed

缺少依赖、模型、外部服务、预算、网络授权或 privacy gate 时，必须写入 blocked diagnostics，不能 fake success，也不能 fake index。

## PHASE01 Truth Source 与 Gap Audit

目标：

- 确认 Program 1A 已归档，不改历史 evidence。
- 审计 `ParseGateway`、`WorkspaceTaskRuntimeService`、`KnowledgeIndexRuntime` 的内存状态。
- 列出 `_tasks`、`_files`、`_ingest_jobs`、`_artifacts`、`_feedback`、parse jobs、index jobs 等需要持久化的状态。
- 确认 DB/session 工具、SQLModel、迁移工具、Redis 依赖现状。

验收：

- 输出 current gap matrix、storage target matrix、API compatibility map。
- 不修改 runtime。

## PHASE02 Durable Storage Contract

目标：

- 定义 SourceObject、WorkspaceFile、DocumentVersion、DocumentBlock、ParseJob、ParseAttempt、IndexJob、IndexChunk、DeadLetter 的 SQLModel schema。
- 定义 repository / store interface。

验收：

- store contract tests 通过。
- SQLite round-trip 通过。
- schema 保持 Postgres-compatible，不引入 Postgres 强依赖。

## PHASE03 Local Object Store 与 File Input Layer

目标：

- 把 workspace file 从纯内存注册升级为后端 source object。
- 支持保存 source content、source bytes 或 file ref。
- 计算 `source_sha256`。

验收：

- 上传 / 注册文件后，source object 和 workspace file 可从 store 读取。
- 服务重启后 file metadata 不丢。

## PHASE04 Parse Job Store 与 Worker Queue

目标：

- `ParseGateway` 支持 job_store 注入。
- 新增 `QueueBackend` interface。
- 实现 `LocalQueueBackend`。
- Redis 可用时实现 `RedisQueueBackend` adapter 或 skeleton。

验收：

- parse job 创建后落库。
- retry 只新增 attempt，不覆盖 job lineage。
- blocked 不 index。
- dead_letter 可查询。

## PHASE05 Document IR Persistence

目标：

- Parse 成功后保存 document_version、document_blocks 和 IR artifact。
- `document_version_id` 稳定。
- `source_sha256`、`parser_config_hash`、`ir_schema_version` 可查询。

验收：

- 同一文件同一 parser config 重复 ingest 不生成冲突 version。
- parser config 变化生成新 version。

## PHASE06 Index Persistence 与 Retrieval Rehydrate

目标：

- `KnowledgeIndexRuntime` 支持 durable index store。
- index manifest 和 chunks 落库。
- 服务重启后能从 DB 重新 query。
- `citation_lineage` 不丢。

验收：

- `ingest -> index -> restart -> query -> citation_lineage` 仍存在。

## PHASE07 OCR / VLM / PDF / Office Enterprise Adapter Boundary

目标：

- 将 PDF / Office / OCR / VLM 的 dependency probe、blocked diagnostics、privacy gate、network gate、budget gate 持久化到 parse attempt diagnostics。

验收：

- scanned / image 没配置 OCR / VLM 时进入 blocked。
- blocked reason 落库。
- 不 fake index。

## PHASE08 Workspace API Durable Closure

目标：

- `/workspace/file`、`/workspace/ingest`、`/workspace/task`、artifact、feedback 的关键状态从 store 读写。
- 前端刷新或后端 service rehydrate 后仍能查询。

验收：

- API tests 证明 file / ingest / task / artifact / feedback 持久化。

## PHASE09 Queue Optional Runtime

目标：

- 如果 Redis 配置存在，parse / index job 可走 Redis queue。
- 如果 Redis 不存在，local queue 通过 tests。

验收：

- QueueBackend contract tests 通过。
- Redis backend 可 dependency-probe。
- 无 Redis 环境不失败。

## PHASE10 Verification, Docs Sync, Closure

目标：

- 更新 architecture、production-readiness、document-ingestion-foundation。
- 把 Current 改成 launchable enterprise ingestion prototype。
- 明确 Remaining Production Scale Target。
- 归档 Program 1 V2。

验收：

- knowledge tests、workspace API tests、storage tests、restart recovery tests、repo verifiers、workflow verifiers 通过。

## 完成标准

1. 原始文件或文本内容由后端持久化，不只存在前端或内存。
2. `workspace_files`、`source_objects`、`parse_jobs`、`parse_attempts`、`document_versions`、`index_jobs`、`index_chunks` 落库。
3. `ParseGateway` 可使用 durable store。
4. `KnowledgeIndexRuntime` 可使用 durable store。
5. `QueueBackend` 有 local 和 Redis 边界。
6. OCR / VLM / PDF / Office 缺依赖时 blocked reason 落库。
7. parse failed / blocked 不创建 fake index。
8. retry 新增 attempt，不覆盖旧 lineage。
9. 服务重启后能查 file、parse job、document version、index manifest、chunk、citation_lineage。
10. Agent 问答能用持久化 index chunk 生成 cited artifact。
11. focused tests 和 verifiers 通过。
