# Document Ingestion Foundation

## 用途

本文是 Zuno 企业知识库文档入口的正式架构契约。它补足 Program 1 的执行计划无法单独承载的企业级设计问题：原始文件、元数据、Document IR、parse job、index job、幂等、版本、防丢、引用追溯、ACL 继承、多模态解析边界和生产化 Target。

本文不替代 `docs/architecture/architecture.md` 和 `docs/architecture/production-readiness.md`。总架构仍以 `architecture.md` 为准；Current / Target 成熟度边界仍以 `production-readiness.md` 为准。

## 核心判断

Program 1 不是为了多写 parser adapter，而是为了完成企业知识库 Agentic GraphRAG 的入口地基：

```text
workspace file
  -> parse job
  -> CanonicalDocumentIR
  -> index handoff
  -> index manifest
  -> retrieval payload
  -> evidence / citation trace
```

没有稳定 Document IR、source provenance 和 index manifest，后续 GraphRAG、citation、faithfulness eval、unsupported claim check 和企业审计都没有可靠来源。

## Current 代码事实

Current 只能描述代码和测试已经证明的事实：

- `src/backend/zuno/knowledge/ingestion/contracts.py` 已有 `CanonicalDocumentIR`、`DocumentMetadata`、`DocumentBlock`、`DocumentTable`、`DocumentFigure`、`DocumentProvenance`、`ParseDocumentRequest`、`ParseDocumentResult`、`ParseJobSnapshot` 和 `IndexHandoffPayload`。
- `CanonicalDocumentIR.metadata` 已记录 `document_id`、`source_id`、`workspace_id`、`source_uri`、`mime_type`、`hash`、`source_sha256`、`parser_id`、`parser_version`、`parser_config_hash`、`document_version_id`、`schema_version` / `ir_schema_version`、`parent_document_version_id`、`derived_from`、`asset_refs`、`redaction_status`、`retention_policy`、fallback、target-blocked、`acl_scope` 和 `sensitivity_tags`。
- `DocumentBlock` 已记录 `block_id`、`type`、`text`、`source_span`、`language`、`code_fence`、block metadata、`acl_scope`、`sensitivity_tags` 和 `confidence`。
- `SourceSpan` 已能表达 page、slide、sheet、line range、bbox、section path 和 table cell。
- `ParserAdapterContract` 和 `ParserAdapter` 已能表达 `supports`、`parse`、`diagnostics`、`capabilities`、`blocked_reason`、capability status、dependency status、dependency probe、network policy、privacy gate、budget gate、enrichment role 和 external dependency boundary。
- `ParseGateway` 已提供 `parse_document()`、`submit_parse_job()`、`get_job_status()`、`get_job_snapshot()` 和 retry 相关本地 runtime surface。
- `ParseGateway` 已对 unknown format 返回稳定 fallback diagnostics，并对 target-blocked adapter 返回稳定 warning diagnostics；这不表示外部 parser / OCR / VLM 已成为 Current。
- `ParseGateway` 已提供本地 in-process parser worker lifecycle：`accepted`、`running`、`succeeded`、`failed`、`blocked`、`retrying`、`cancelled`、`dead_letter` 的 snapshot 语义，记录 `parse_idempotency_key`、`parse_attempt_id`、`attempt_count`、failure snapshot、parser diagnostics、retry policy 和 metrics。生产 DB-backed queue、outbox、worker lease、heartbeat、dead letter queue 和 reconciler 仍是 Target。
- parser matrix 已覆盖 `pdf / docx / pptx / xlsx / txt / md / csv / json / html / image / scanned / code`。PDF、Office、OCR / VLM 等生产级能力仍有 target-blocked 边界，不能写成完整 Current。
- `native` parser 已对 `txt / md / csv / json / html / code` 提供本地 deterministic baseline：Markdown heading hierarchy、link、code fence、table 与 section path；CSV delimiter/header/row/column/table_cell；JSON pointer object/array/value block；HTML script/style 过滤、heading、paragraph、link 和 table；code extension language detection 与 regex import/class/function metadata。CSV / JSON / HTML malformed 输入会生成 diagnostics 并保留 fallback block，不让 parser worker 崩溃。
- `adapter_boundary_metadata()`、adapter dependency probe 和 blocked diagnostics 已能把 Docling / PyMuPDF、Unstructured / MarkItDown、MinerU / OCR / VLM 的缺失依赖、fallback、network policy、privacy gate、budget gate 和 derived enrichment role 写入稳定 metadata。OCR / VLM 当前只能是 target-blocked derived enrichment，不能覆盖 deterministic parser source truth。
- `KnowledgeIndexRuntime` 已能把 `CanonicalDocumentIR` 转为本地 BM25 / vector / graph index job，并产生 `IndexJobManifest`、retrieval payload、source provenance、ACL scopes、sensitivity tags、adapter status、parse job lineage、diagnostics digest 和 citation lineage chunk metadata。
- `IndexJobManifest` 已记录 `parse_job_id`、`parse_attempt_id`、`document_version_id`、`source_sha256`、`parser_config_hash`、`ir_schema_version`、`diagnostics_digest`、parser diagnostics、block/table/figure count；Agentic retrieval evidence provenance 已能从 manifest 继承这些字段。
- `WorkspaceTaskRuntimeService.create_ingest_job()` 已通过 `ParseGateway.submit_parse_job()` 解析 workspace file，返回 `parse_job` 和 `parse_snapshot`，并把 `ParseJobSnapshot` 传给 `KnowledgeIndexRuntime.index_document(..., parse_job_snapshot=...)`，让 `/api/v1/workspace/ingest` 的 index manifest 保留 `parse_job_id`、`parse_attempt_id`、`document_version_id`、`source_sha256` 和 parser diagnostics lineage。旧 `_document_from_file()` / `workspace_text_runtime` 只保留为历史 gap 证据，不再是当前 ingest 闭环。
- Program 2 已新增 `src/backend/zuno/knowledge/storage/`，并把 `LocalObjectStore` 和 `SQLiteDurableIngestionStore` 接入 `WorkspaceTaskRuntimeService`：`/workspace/file` 保存 source object、source hash、storage uri 和 workspace file metadata；`/workspace/ingest` 持久化 parse job、parse snapshot、document version、document blocks、index manifest、index chunks 和 citation lineage；workspace task、events、artifact content/ref 和 feedback 可从 SQLite rehydrate。它仍不是生产 Postgres、MinIO / S3、Redis / outbox / worker lease、external OCR / VLM 或 external index platform。

## Input Format Support Matrix

当前代码已经有 parser capability matrix，但“矩阵覆盖”和“真实 Current 能力”不是一回事。当前稳定 Current 是低依赖 native parser；PDF、Office、image、scanned 和 binary 仍必须保持 target-blocked 或 fallback diagnostics 边界，不能因为有 fixture 或 adapter contract 就写成生产可用。

| Input Type | Examples | Current Behavior | Launchable Target | Production Scale Target | Status / UI Behavior |
| --- | --- | --- | --- | --- | --- |
| Text | txt | `native` deterministic parser，保留 line range。 | async parse worker 执行同一 native parser，并写 file-level status。 | parser ops metrics、large text streaming、charset diagnostics。 | indexed / failed。 |
| Markdown | md, mdx | `native` parser，保留 heading、link、code fence、table 和 section path；`.mdx` 路由到 `md`。 | async worker，malformed markdown diagnostics 和 citation source span。 | richer Markdown AST、frontmatter / embed policy。 | indexed / failed。 |
| CSV | csv | `native` table parser，保留 delimiter、header、row、column 和 table_cell。 | async worker，large-ish CSV status 和 malformed row diagnostics。 | large CSV streaming、schema inference、column ACL。 | indexed / failed。 |
| JSON | json | `native` JSON parser，保留 object / array / value block 和 JSON pointer。 | async worker，JSONL / malformed JSON diagnostics contract。 | JSONL / streaming、typed schema mapping。 | indexed / failed。 |
| HTML | html, htm | `native` cleanup parser，过滤 script / style，保留 heading、paragraph、link 和 table。 | async worker，browser-rendered HTML parser boundary。 | browser-rendered HTML parser、DOM snapshot provenance。 | indexed / failed。 |
| Code | py, ts, js, java, go | `native` code parser，做扩展名语言识别和 regex import / class / function metadata，不声称完整 AST。 | code-aware worker，line range、symbol summary 和 citation。 | repo-level code graph、dependency graph、language server enrichment。 | indexed / failed。 |
| PDF | pdf | `docling_pymupdf` adapter contract 已登记，但 external dependency 是 `target_blocked`；当前只允许 deterministic fixture / text fallback diagnostics 或 blocked job state，不能写成真实 PDF parser。 | local PDF worker boundary、dependency probe、text layer fallback、blocked visibility。 | production Docling / PyMuPDF worker、layout / table / page image extraction。 | blocked / dependency_probe / retry。 |
| Office | docx, pptx, xlsx, xls | `unstructured_markitdown` adapter contract 已登记，但 external dependency 是 `target_blocked`；fixture 可生成 target-blocked metadata，不代表真实 Office parser Current。 | office worker boundary、dependency probe、source object persistence、blocked diagnostics。 | production Unstructured / MarkItDown worker、slide / sheet / table extraction。 | blocked / dependency_probe / retry。 |
| Image | png, jpg, jpeg, bmp, webp, tiff | `mineru_ocr_vlm` adapter contract 已登记，当前是 target-blocked derived enrichment；缺 provider 时 `submit_parse_job()` 应 blocked。 | OCR / VLM worker boundary、privacy / budget / review gate、diagnostics。 | MinerU / PaddleOCR / VLM provider、figure caption、chart/table understanding。 | blocked / review_required。 |
| Scanned | scanned PDF / scanned image | target-blocked OCR / VLM boundary；scanned PDF 目标上先检测 text layer，无 text layer 再进入 OCR / VLM worker。 | OCR / VLM worker boundary、page image extraction target、human review gate。 | production OCR / VLM pipeline、confidence calibration、review workflow。 | blocked / review_required。 |
| Binary / Unknown | bin, unknown | source object only 或 unknown format fallback diagnostics；不能假装可解析。 | object store + dependency probe + unsupported / blocked 状态。 | custom parser plugins、admin-configured parser policy。 | unsupported / blocked。 |

这张表的关键约束是：`txt / md / csv / json / html / code` 可以写成 Current native deterministic parser；PDF / Office / image / scanned / unknown binary 只能写成 target-blocked boundary、dependency probe、blocked diagnostics 或 Launchable / Production Target。

## Binary Source Object Current / Target

当前 `LocalObjectStore` 已提供 `save_bytes()`、`read_bytes()`、`open_stream()` 和 sha256 verification。Program 3 Mega PHASE03 已用 focused tests 证明 binary object save / read / verify；PHASE12 E2E 已证明 PDF / Office / image / scanned 这类 blocked 文件仍会保存 source object、`source_sha256` 和 `storage_uri`，即使解析 blocked 也不丢原始文件事实。

Launchable Prototype Target 继续要求：

- `save_bytes()`：保存 PDF、Office、image、scanned、unknown binary 的原始 bytes。
- `read_bytes()` / `open_stream()`：支持 worker 以 bytes 或 stream 读取原始对象。
- `verify_sha256()`：验证 object store 内容与 `source_sha256` 一致。
- `mime sniffing`：记录用户声明 MIME 与后端 sniffed MIME 的差异。
- `size_bytes`、`content_type`、`storage_uri`、`source_sha256`：进入 `SourceObject` 和 workspace file metadata。
- `object_missing diagnostics`：对象丢失时返回可审计错误，不让 parser 假成功。

Production Scale Target：

- MinIO / S3 / OSS / COS adapter。
- multipart upload 和 large file streaming。
- object lifecycle policy、retention policy、encryption / access policy。
- derived artifacts：page image、IR JSON、diagnostics JSON、artifact export 都以 object ref 追溯。

数据库仍只保存事实、状态和 metadata；大对象和原始证据进入 object store。

## Async Ingestion Pipeline

成熟输入层目标链路是异步、可恢复、可重试，而不是 API 请求线程同步解析所有重文件：

```text
/workspace/file
  -> SourceObject persisted
  -> WorkspaceFile metadata
  -> /workspace/ingest
  -> ParseJob queued
  -> QueueBackend
  -> ParserWorker
  -> ParseAttempt
  -> CanonicalDocumentIR
  -> DocumentVersion / DocumentBlocks
  -> IndexJob queued
  -> IndexWorker
  -> IndexManifest / IndexChunks / CitationLineage
  -> Retrieval available
```

Program 3 Mega 的 local baseline 已用 `LocalQueueBackend` 和 local workers 跑通；RabbitMQ、Redis、PostgreSQL、MinIO / S3 和 external parser workers 没有真实 provider 和 tests 前只能是 adapter boundary / dependency probe / target-blocked evidence。

## Queue / Worker / Outbox / Reconciler

Program 3 Mega 的 PHASE03 已把以下对象落成本地 baseline 或明确 Target boundary：

- **QueueBackend**：Current 是 `LocalQueueBackend`；`RabbitMQQueueBackend` 只做 boundary、dependency probe 和 target-blocked evidence，不能要求外部 broker 才能跑 tests。
- **ParserWorker**：Current 已消费 `parse_requested`，调用 `ParseGateway`，写 parse snapshot、`DocumentVersion` 和 blocks；target-blocked PDF / Office / OCR / VLM 保留 blocked reason。
- **IndexWorker**：Current 已消费 `index_requested`，写 `IndexManifest`、chunks 和 citation lineage；blocked / failed parse 不能进入 fake index。
- **Outbox**：本地 baseline 保留 outbox event contract；生产 DB 事务 outbox operations 仍是 Production Scale Target。
- **DeadLetter**：超过 retry 上限、依赖缺失或策略 blocked 时保留 failure / blocked evidence。
- **Reconciler**：检查 `uploaded_without_parse`、`parse_succeeded_without_index`、`index_chunks_missing`、`blocked_without_diagnostics`、`object_missing`、`citation_lineage_missing`。

这些是输入层进入 launchable enterprise baseline 的结构骨架；真实 RabbitMQ / Redis / Postgres / MinIO / OCR / VLM 仍是 Production Scale Target。

## File-level Lifecycle

产品、API 和 trace 必须能表达文件级生命周期，不只表达最终是否有 answer：

```text
uploaded
  -> queued
  -> parsing
  -> parsed
  -> indexing
  -> indexed
  -> failed / blocked / dead_letter / cancelled
```

文件列表和 diagnostics 至少要能展示 `file_id`、`filename`、`mime_type`、`size_bytes`、`source_sha256`、`storage_uri` / `source_ref`、`parse_status`、`index_status`、`parser_id`、`document_version_id`、`index_job_id`、`blocked_reason`、`dependency_probe`、`retry_count`、`last_error` 和 `retry / cancel / reparse / reindex / rebuild_graph / view_diagnostics` actions。

## Program 1 Local Runtime Slice

Program 1 已关闭本地可验证 ingestion runtime slice：

```text
/workspace/file
  -> Workspace file registry
  -> /workspace/ingest
  -> ParseDocumentRequest
  -> ParseGateway.submit_parse_job()
  -> ParseJobSnapshot
  -> CanonicalDocumentIR
  -> build_index_handoff_payload()
  -> KnowledgeIndexRuntime.index_document()
  -> IndexJobManifest
  -> retrieval payload
  -> evidence / citation source tracing
```

当前 workspace 附件和知识库文件进入同一 Parse Gateway，不再由 `_document_from_file()` 生成 `workspace_text_runtime` stub 作为产品闭环。

## Production Target Infrastructure

以下是企业级生产目标，不是当前完成事实：

```text
Object Store
  raw_file_blob
  extracted_page_image
  parsed_ir_artifact
  parser_diagnostics_artifact

Metadata DB
  documents
  document_versions
  parser_jobs
  parser_attempts
  document_blocks
  index_jobs
  index_manifests
  audit_events

Queue / Outbox
  parse_requested
  parse_succeeded
  index_requested
  index_succeeded
  dead_letter

Index Layer
  BM25
  vector
  graph
  evidence / citation store
```

生产化时，object store 保存原始文件和派生产物，metadata DB 保存版本和任务事实，queue / outbox 负责异步可靠投递，index layer 负责 BM25、vector、graph 和 evidence / citation 检索面。

## Program 1 / Program 2 边界

已归档的 Program 1 是 `zuno-production-document-ingestion-and-thread-foundation-v1`。它不是完整企业级文档输入层，而是一个扎实的解析链路地基：

```text
workspace file
  -> /workspace/ingest
  -> ParseGateway.submit_parse_job()
  -> ParseJobSnapshot
  -> CanonicalDocumentIR
  -> KnowledgeIndexRuntime.index_document(parse_job_snapshot=...)
  -> IndexJobManifest
  -> retrieval payload
  -> citation provenance
```

Program 1 的优势是链路语义、Document IR、parser contract、native parser fixtures、index manifest lineage 和 citation lineage 已经打通；不足是状态仍大多是 local / in-process / in-memory。

Program 2 `zuno-enterprise-document-ingestion-platform-v2` 已完成并归档。它把 Program 1 的 local runtime slice 升级为 Product V1 local durable ingestion baseline：

```text
文件对象存储
+ SQLModel / SQLite durable store
+ parse job / attempt persistence
+ document version / block / IR artifact persistence
+ index job / chunk persistence
+ SQLite / local file store backed workspace task state
+ OCR / VLM / PDF / Office blocked diagnostics persistence
+ restart recovery tests
```

Program 2 的 Product V1 验收不是分布式 queue 或百万文档，而是服务重启后 file、parse job、document version、index manifest、index chunk、citation lineage、task、events、artifact content/ref 和 feedback 不丢。Production Scale Target 才包括 Postgres、object store、Redis / Kafka、outbox、worker lease、heartbeat、dead letter reconciler、external OCR / VLM 和 external index platform。

Program 3 Mega `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1` 当前 active。它承接 Program 2 的 durable baseline，并把原 Program 3 async infrastructure、Runtime Subsystems、Planning Integration 和 Enterprise Eval Benchmark 合并为一个 full closure program。文档入口相关的 PHASE03 目标是完成 enterprise ingestion async infrastructure baseline：

```text
PostgreSQL-compatible fact store boundary
+ ObjectStore binary support
+ QueueBackend / LocalQueueBackend
+ RabbitMQ boundary
+ Redis runtime state boundary
+ ParserWorker / IndexWorker
+ outbox / dead letter / reconciler
+ OCR / VLM worker boundary
+ ingest status / retry / cancel / replay
```

Program 3 Mega 的 Current 只能来自本轮真实代码、focused tests、E2E、trace / eval 或 verifier evidence。真实 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM 和 external index 没有 provider 接入与测试前，只能写成 Target / target-blocked evidence。

PHASE11 还必须补齐 KnowledgeSpaceConfig 与 Change Impact Preview，让知识库初始化和后续修改能明确触发 metadata-only、ACL refresh、reparse、vector rebuild、graph rebuild 或 OCR / VLM job。文件内容、parser config、chunk policy、OCR 参数和 redaction policy 变化都必须保留 document_version / index_manifest lineage，不得覆盖旧引用。

## Program 2 数据模型目标

Program 2 已定义并验证以下 durable entities：

- `source_objects`：原始文件事实源、storage uri、source hash、ACL、sensitivity。
- `workspace_files`：前端和 workspace 可见 file id，关联 source object。
- `document_versions`：parser id / version / config、IR schema、IR artifact、status。
- `document_blocks`：block type、text、source span、metadata、ACL、sensitivity。
- `parse_jobs`：parse idempotency key、status、attempt count、blocked reason、failure reason。
- `parse_attempts`：当前 Product V1 用 `ParseJobSnapshot` 保存 attempt count、diagnostics 和 metrics；独立 attempt table 仍是 Target。
- `index_jobs`：当前 Product V1 用 `index_manifests` 保存 knowledge space、document version、parse lineage 和 target status；独立 queue job table 仍是 Target。
- `index_chunks`：content、metadata、citation lineage、ACL、sensitivity。
- `workspace_tasks`、`task_events`、`artifacts`、`feedback`：workspace 产品闭环的可恢复事实。
- `ingestion_dead_letters`：不可恢复或需人工处理的 parse / index 失败，仍是后续 Target。

## 核心对象

### Source Object

原始文件对象必须有稳定 hash 和存储引用：

- `source_uri`
- `source_sha256`
- `mime_type`
- `workspace_id`
- `owner`
- `acl_scope`
- `sensitivity_tags`
- `retention_policy`

### Document Version

文档版本不等于文件名，也不等于 document id。推荐版本键：

```text
document_version_id
  = document_id
  + source_sha256
  + parser_id
  + parser_version
  + parser_config_hash
  + ir_schema_version
```

parser 升级、OCR 参数变化、文件内容变化、redaction policy 变化都生成新 `document_version_id`，不覆盖旧 IR。

### Parser Job

parser job 表达一次解析请求：

- `parse_job_id`
- `parse_idempotency_key`
- `workspace_id`
- `document_id`
- `document_version_id`
- `source_sha256`
- `parser_id`
- `parser_version`
- `parser_config_hash`
- `status`
- `attempt_count`
- `blocked_reason`
- `failure_reason`
- `metrics`

### Parser Attempt

parser attempt 表达一次 worker 尝试：

- `parse_attempt_id`
- `parse_job_id`
- `lease_owner`
- `lease_until`
- `heartbeat_at`
- `started_at`
- `finished_at`
- `diagnostics_digest`
- `artifact_refs`

### Index Manifest

index manifest 必须记录从 parser 到 index 的 lineage：

- `index_job_id`
- `index_idempotency_key`
- `knowledge_space_id`
- `document_version_id`
- `parse_job_id`
- `parse_attempt_id`
- `source_sha256`
- `ir_schema_version`
- `parser_config_hash`
- `block_count`
- `table_count`
- `figure_count`
- `diagnostics_digest`
- `acl_scopes`
- `sensitivity_tags`

## 幂等与防重复

Program 1 应先用本地可验证 key 固定语义，生产化时再落到 DB 唯一键：

```text
parse_idempotency_key
  = workspace_id
  + source_sha256
  + parser_id
  + parser_version
  + parser_config_hash

index_idempotency_key
  = knowledge_space_id
  + document_version_id
  + index_target
  + index_version
```

同一 key 的重复请求不能生成互相冲突的 IR 或 index manifest。retry 只能产生新的 attempt，不应悄悄覆盖旧 version。

## Job 状态语义

Program 1 应区分以下状态：

- `accepted`：请求已接收，尚未执行。
- `running`：worker 正在解析。
- `succeeded`：解析成功并产生 `CanonicalDocumentIR`。
- `failed`：parser 运行失败，例如 decode error、malformed input、unexpected exception。
- `blocked`：能力或策略阻塞，例如 OCR engine missing、VLM disabled、file too large、network denied、security policy block。
- `retrying`：retry policy 允许重试，新的 attempt 将继承 job lineage。
- `cancelled`：用户、预算或策略取消。
- `dead_letter`：超过 retry 上限或需要人工处理。

当前 `ParseJobSnapshot` 覆盖本地 queued / running / succeeded / failed / blocked / dead_letter 等 baseline；Program 3 Mega 还用 local queue、dead letter 和 reconciler focused tests 证明本地行为。DB-backed queue、worker lease、heartbeat 和生产 dead letter operations 仍是 Production Scale Target。

## 防丢机制

生产目标需要 outbox、lease 和 reconciler：

- **Outbox**：DB 事务内同时写 `parser_jobs` 和 `outbox_events`，防止“DB 有任务但队列消息丢失”。
- **Lease**：worker 领取任务后写 `lease_owner`、`lease_until`、`heartbeat_at`，worker 死亡后任务可重新领取。
- **Dead Letter**：超过 retry 上限或 blocked 的任务进入 dead letter，保留 blocked reason、retry policy 和人工处理入口。
- **Reconciler**：周期性检查 `uploaded_without_parse`、`parsed_without_index`、`manifest_block_mismatch`、`acl_index_drift`、`citation_version_missing`。

Program 1 / Program 3 的 local slice 已实现 snapshot / replay / diagnostics、local dead letter 和 reconciler baseline；生产 outbox、lease、heartbeat 和 distributed reconciler operations 仍是 Target。

## ACL 与 Sensitivity 继承

ACL 和 sensitivity 必须从 workspace file 继承到 document version、block、index manifest、retrieval payload 和 citation：

```text
workspace file acl
  -> DocumentMetadata.acl_scope
  -> DocumentBlock.acl_scope
  -> IndexJobManifest.acl_scopes
  -> RetrievalCandidate.acl_scope
  -> EvidenceItem.source_provenance
  -> Citation source tracing
```

检索前 ACL gate 和输出后 DLP 不能互相替代。检索前必须避免越权召回，输出后必须避免敏感内容泄露。

## Citation Lineage

答案引用必须能追到原始文件和 parser attempt：

```text
answer citation
  -> citation_id
  -> evidence_id
  -> index chunk id
  -> document block id
  -> document_version_id
  -> parse_job_id / parse_attempt_id
  -> source_sha256
  -> source_uri
```

如果 parser 升级后产生新 version，旧 answer citation 仍指向旧 `document_version_id`，不能被新解析结果静默改写。

## 多模态解析边界

确定性 parser 是 source truth；OCR / VLM 是 derived enrichment，不是默认真相源。

VLM enrichment adapter 的目标 contract：

```text
input:
  page_image
  figure_image
  scanned_image

output:
  image_caption
  chart_summary
  ocr_text_block

metadata:
  model_id
  prompt_version
  confidence
  derived_from
  review_required
  privacy_gate_result
  budget_used
```

策略：

- 默认 network deny，除非显式允许。
- page limit、budget limit 和 privacy gate 必须先于 VLM 调用。
- VLM 输出要带 `derived_from` 和 `review_required`，不能覆盖原始 source span。
- OCR / VLM 输出必须记录 confidence、model_id、prompt_version、derived_from、review_required、privacy_gate 和 budget_gate；这些字段是 derived evidence，不是 source truth。
- scanned PDF 应优先检测 text layer；没有 text layer 时才进入 OCR / VLM worker target。
- scanned / image 在 OCR engine 或 VLM 不可用时应返回 blocked diagnostics，而不是假成功。
- blocked OCR / VLM、PDF 或 Office 解析不能创建 fake index；E2E 和 Eval 必须能证明 blocked reason、dependency probe、worker event 和 index status 可追溯。
- 高风险或低置信 OCR / VLM 输出必须进入 human review 或 blocked/review_required 状态，不允许直接作为高置信引用证据。

## Program 1 Phase 映射

| Phase | 本文要求 |
| --- | --- |
| PHASE01 | 审计 workspace ingest 是否绕过 ParseGateway，并列出 parser current matrix。 |
| PHASE02 | 冻结 Document IR、document version、parser config hash、schema version 和 parser contract。 |
| PHASE03 | 固定 job status、idempotency、retry、blocked、dead letter target、lease / outbox target。 |
| PHASE04 | 强化低依赖格式，作为 eval corpus 和 fixtures 基础。 |
| PHASE05 | 明确 PDF / Office / OCR / VLM adapter 和 enrichment 边界。 |
| PHASE06 | 把 parse lineage 写进 index manifest 和 citation source tracing。 |
| PHASE07 | 为后续 Runtime Subsystems 生成线程提示词时，把 ingestion lineage 作为共享输入事实。 |
| PHASE08 | closure summary 必须列 Current、Remaining Target、blocked evidence 和未接生产基础设施。 |

## Program 1 最小闭环

Program 1 已完成的最小可验收代码闭环：

```text
1. create_ingest_job 调用 ParseGateway.submit_parse_job()
2. parse succeeded 后用 result.document 进入 KnowledgeIndexRuntime.index_document()
3. ingest job 返回 parse_job_id、parse snapshot、diagnostics、index_job
4. parse failed / blocked 时不创建 fake index
5. native md/csv/json/html/code fixtures 和 tests 补强
6. index manifest 增加 parse lineage
```

以上是 Program 1 已完成的 local runtime slice；Program 2：`zuno-enterprise-document-ingestion-platform-v2` 已进一步完成 Product V1 local durable ingestion baseline。生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index platform 和 online eval 仍是 Production Scale Target。

## 验证要求

Program 1 应至少用以下证据关闭相关 phase：

- parser current matrix。
- Document IR contract tests。
- parser job lifecycle tests。
- native format golden fixtures。
- PDF / Office / OCR / VLM blocked diagnostics tests。
- parse -> index manifest lineage tests。
- workspace ingest -> ParseGateway -> index handoff focused tests。
- docs / verifier / repo tests。
