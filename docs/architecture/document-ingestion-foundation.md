# Document Ingestion Foundation

所属运行域：Input & Knowledge、Local Infrastructure。

本文定义企业知识库文档入口：`ParseGateway.submit_parse_job()` 接收 workspace file 后生成 `CanonicalDocumentIR`、`IndexJobManifest`、`document_version_id`、`parse_idempotency_key` 和 `index_idempotency_key`，再交给 `workspace_text_runtime` 与 index handoff。`VLM enrichment adapter`、生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index platform 均属于明确边界，不得在未实现时写成 Current。

## 定位

Document ingestion 负责把 Workspace 文件变成可检索、可引用、可恢复的知识资产。它的完成标准不是“文件上传成功”，而是 source object、parse job、Document IR、citation chunk、index manifest 和 citation lineage 都能形成可追踪闭环。

## 核心对象

- SourceObject：原始文件对象，保存 checksum、object URI、content type、workspace scope。
- WorkspaceFile：用户可见文件状态，连接 workspace、source object、parse/index 状态。
- ParseJob：解析任务，必须有 queued/running/completed/blocked/failed 状态。
- ParseSnapshot：解析输出快照，供重试、审计和 index handoff 使用。
- CanonicalDocumentIR：规范化文档结构，承载 title、blocks、tables、metadata。
- DocumentVersion：一次解析与切块生成的版本。
- DocumentBlock：可定位的文档块。
- SourceSpan：原文起止位置、页码或结构路径。
- CitationChunk：可进入 retrieval context 的引用粒度 chunk。
- ParentChunk：给引用 chunk 提供上下文的父块。
- IndexManifest：记录 index version、chunk config、embedding/rerank config。
- IndexChunk：进入 BM25/vector/graph 的检索单元。
- CitationLineage：从 evidence/citation 回到 source object 和 source span 的链路。

## Contract

```text
SourceObject
-> ParseJob
-> CanonicalDocumentIR
-> DocumentVersion
-> DocumentBlock / SourceSpan
-> CitationChunk / ParentChunk
-> IndexManifest / IndexChunk
-> CitationLineage
```

parser blocked 不得 fake index。没有 source span 的 chunk 不得成为 strict citation。Graph evidence 必须能回到 CitationLineage。

## 当前与短期目标

Current：

- 文本类文档、本地对象存储、durable ingestion store、chunk/index 和 evidence-span hardening surface 已存在。
- GraphRAG evidence lineage 代码已具备基础 surface。
- 本地 PyMuPDF text PDF parser 已跑通 source span citation；损坏 PDF failed，无文本 PDF 返回 needs_ocr，不 fake index。

Short-term：

- Index rehydrate 后 citation lineage 不丢失。
- parser blocked、index blocked 和 missing source span 必须进入 trace。

Future Optional：

- 大量 parser provider。
- OCR/VLM enrichment 平台化；扫描 PDF 仍是 Future/blocked，不属于当前 PHASE12 闭环。
- 外部对象存储和分布式索引。
