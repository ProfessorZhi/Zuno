# 02 Input / Document Ingestion

updated: 2026-07-12  
status: normative-target-module-design  
module_number: 02

所属运行域：Product & API、Async Data Plane、Knowledge & Memory Runtime、Durable Infrastructure。

> 本文合并原 `document-ingestion-foundation.md` 与 `input-layer-and-document-processing.md`，作为 Input / Document Ingestion 的正式模块入口。

## 1. 模块定位

Input / Document Ingestion 负责把用户输入和原始资料转换成可恢复、可版本化、可追踪、可交给 Agent Core 或 Knowledge 使用的标准内部表示。

模块存在两条输入路径：

```text
在线任务输入
    用户问题、附件引用、知识空间选择、输出要求

知识摄取输入
    PDF、DOCX、PPTX、XLSX、URL、Git、对象存储或其他数据源
```

在线任务请求最终交给 Agent Core；知识摄取任务经过解析和质量检查后交给 Knowledge 建立检索索引。

## 2. Owner 边界

Input / Ingestion 负责：

```text
Upload / Connector 接入
SourceObject
WorkspaceFile
DocumentVersion
Object Store 原始文件引用
MIME / 文件类型检测
恶意文件与大小 Gate
ParseJob / ParseSnapshot
Parser 路由
PDF / DOCX / PPTX / XLSX 解析
OCR / VLM enrichment orchestration
CanonicalDocumentIR
DocumentBlock
原始 SourceSpan
Parser Quality
Ingestion Job 状态
Index Handoff Contract
```

Input / Ingestion 不负责：

```text
Agent 任务规划
BM25 / Vector / Graph 检索
Fusion / Rerank
EvidenceLedger
最终 Citation 绑定
模型 Provider 路由
```

Knowledge 负责 RetrievalChunk、ParentChunk、CitationChunk、Embedding、BM25、Vector、Graph 和检索；Input 负责忠实反映原始资料。

## 3. 核心对象

- `SourceObject`：原始文件对象，保存 checksum、object URI、content type、workspace scope。
- `WorkspaceFile`：用户可见文件状态，连接 workspace、source object、parse/index 状态。
- `ParseJob`：解析任务，状态至少包含 queued/running/completed/blocked/failed。
- `ParseSnapshot`：不可变解析输出快照，供重试、审计和 index handoff 使用。
- `CanonicalDocumentIR`：规范化文档结构，承载 title、blocks、tables、figures、metadata。
- `DocumentVersion`：一次摄取、解析和标准化生成的版本。
- `DocumentBlock`：可定位的标题、段落、表格、代码、图片等结构单元。
- `SourceSpan`：页码、bbox、char offset、结构路径等原文定位信息。
- `ParserQualityReport`：文本覆盖率、乱码率、OCR 置信度、空页比例等质量指标。
- `IndexableDocumentSnapshot`：Input 向 Knowledge 的稳定交接 Contract。
- `ExternalJobHandle`：Agent Core 等待异步摄取任务时使用的外部任务引用。

## 4. 数据链路

```text
UI / Connector
→ Upload API
→ SourceObject
→ Object Store
→ WorkspaceFile
→ DocumentVersion
→ ParseJob
→ Parser / OCR / VLM
→ CanonicalDocumentIR
→ DocumentBlock + SourceSpan
→ ParserQualityGate
→ IndexableDocumentSnapshot
→ Knowledge Indexing
```

用户提问链路：

```text
UI Input
→ FastAPI DTO
→ Workspace / Knowledge Scope
→ RuntimeRequest / AttachmentRef
→ Agent Core InputGate
```

## 5. Input 与 Knowledge 的 Handoff

```python
class IndexableDocumentSnapshot(BaseModel):
    workspace_id: str
    source_object_id: str
    document_id: str
    document_version_id: str
    canonical_ir_ref: str
    canonical_ir_hash: str
    ir_schema_version: str
    block_manifest_ref: str
    source_span_manifest_ref: str
    parser_name: str
    parser_version: str
    parser_config_hash: str
    parse_quality: dict
    acl_policy_ref: str
    sensitivity_tags: list[str]
    retention_policy_ref: str
    content_hash: str
    requested_index_targets: list[str]
    created_at: datetime
```

Knowledge 返回：

```python
class KnowledgeVersionManifest(BaseModel):
    knowledge_version_id: str
    knowledge_space_id: str
    document_version_id: str
    chunk_policy_version: str
    embedding_model_version: str
    graph_extractor_version: str
    bm25_index_version: str | None
    vector_index_version: str | None
    graph_index_version: str | None
    status: str
    validation_result_ref: str
```

## 6. SourceSpan 所有权

Input 是原始 SourceSpan 的权威 Owner：

```text
PDF page
bbox
char_start / char_end
block_id
structure_path
```

Knowledge 只保存 `source_span_refs`，不得重新猜测或修改 SourceSpan。

```text
SourceSpan Definition
    Owner = Input

Retrieval Chunk
    Owner = Knowledge

Chunk → SourceSpan Mapping
    Owner = Knowledge，但引用 Input 定义
```

## 7. Block 与 Chunk 的边界

Input 输出文档结构单元：

```text
HeadingBlock
ParagraphBlock
TableBlock
CodeBlock
FigureBlock
CitationUnit
```

Knowledge 根据检索策略创建：

```text
ParentChunk
CitationChunk
EntityChunk
CommunitySummary
```

Input 不根据某个 Embedding 模型决定检索 Chunk 大小。

## 8. Parser 路由与质量降级

Parser 选择不能只根据扩展名，应同时考虑：

```text
MIME
是否扫描件
文本覆盖率
表格与版面复杂度
文件大小
已知 Parser 能力
成本与延迟预算
```

推荐降级链：

```text
Native Parser
→ Layout Parser
→ OCR
→ VLM Enrichment
→ Human Review / BLOCKED
```

每次解析至少产生：

```text
text_coverage
layout_coverage
table_detection_count
image_count
ocr_confidence
garbled_text_ratio
empty_page_ratio
```

解析失败或 SourceSpan 缢失时不得 fake index。

## 9. 状态模型

### WorkspaceFile

```text
UPLOADED
→ PROCESSING
→ READY
→ BLOCKED
→ FAILED
→ DELETED
```

### ParseJob

```text
QUEUED
→ RUNNING
→ COMPLETED
→ BLOCKED
→ FAILED
→ CANCELLED
```

### Index Handoff

```text
PENDING
→ ACCEPTED
→ INDEXING
→ READY
→ BLOCKED
→ FAILED
```

前端只展示状态，不是状态事实源。所有状态必须从后端持久化恢复。

## 10. 幂等与版本

建议幂等键：

```text
parse_idempotency_key
    sha256(workspace_id + source_checksum + parser_config_hash)

index_idempotency_key
    sha256(document_version_id + chunk_policy_version + index_target_versions)
```

文件内容或解析配置变化时创建新 DocumentVersion，不覆盖旧版本。

## 11. 增量更新与删除传播

```text
源文件更新
→ 新 Source Snapshot / DocumentVersion
→ 新 KnowledgeVersion
→ 新版本激活
→ 旧版本停止服务但保留审计

源文件删除
→ Tombstone
→ BM25 删除
→ Vector 删除
→ Graph 删除
→ Cache 失效
→ Reconciliation 验证
```

Input 负责产生版本和删除事件；Knowledge 负责索引传播。

## 12. 临时附件

对话附件仍走 Input 模块：

```text
Upload
→ temporary SourceObject
→ ParseJob
→ CanonicalDocumentIR
→ thread-scoped KnowledgeSnapshot
→ Agent Core AttachmentRef
```

区别只在 retention：

```text
企业知识库文件 = long_term
对话附件 = thread_scoped / temporary
```

Agent Core 不应在 Graph Node 内直接调用 PyMuPDF。

## 13. Agent Core 等待 Contract

```python
class IngestionPort(Protocol):
    async def submit(self, request: SubmitIngestionRequest) -> ExternalJobHandle: ...
    async def get_status(self, job_id: str) -> ExternalJobStatus: ...
    async def cancel(self, job_id: str) -> None: ...
```

```text
SUBMIT_INGESTION
→ ExternalJobHandle
→ WAIT_EXTERNAL
→ LangGraph interrupt
→ DocumentReady / KnowledgeVersionReady
→ resume
```

## 14. 当前基线

Current：

- upload / knowledge DTO、local storage、parser/indexing surface 和 SSE/API surface 已存在。
- 文本类文档、本地对象存储、durable ingestion store、chunk/index 和 evidence-span hardening surface 已存在。
- 本地 PyMuPDF text PDF parser 已跑通 page / bbox / char offset SourceSpan citation。
- 损坏 PDF 返回 failed；无文本 PDF 返回 needs_ocr，不 fake index。

Target Gap：

- PostgreSQL durable ingestion facts。
- Queue / Outbox / Worker Lease / Heartbeat / DLQ / Reconciler。
- 完整 ParserQualityGate 与自动降级。
- 增量同步与删除传播。
- 多 Connector 和 OCR/VLM 平台化。

## 15. 完成证据

```text
上传后可恢复 SourceObject / DocumentVersion / ParseJob
真实 PDF 生成 SourceSpan
扫描 PDF 明确 BLOCKED 或走 OCR
进程重启后 ParseJob 可恢复
重复投递不重复解析
删除文件后所有索引完成删除传播
Index rehydrate 后 CitationLineage 不丢失
Agent Core 可等待摄取并从原 Checkpoint 恢复
```

只有代码、持久化、故障注入测试和运行证据完成后，Target 才能写为 Current。