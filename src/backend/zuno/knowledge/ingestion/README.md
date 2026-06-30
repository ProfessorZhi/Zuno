# Knowledge Ingestion 边界

PHASE04 status: runtime-current-production-target

## 当前角色

`knowledge/ingestion/` 是 Document Ingestion / Parse Gateway 的正式 owner 入口。当前已经落地的是可测试 runtime owner surface：

- Parser Capability Matrix：登记格式、默认 parser、fallback、结构保留、证据锚点、timeout、resource budget 和 sandbox policy。
- Canonical Document IR：统一 document metadata、block、table、figure、source span、ACL、sensitivity tags 和 provenance。
- Parser router contract：按文件扩展名或格式选择 native、Docling/PyMuPDF、MinerU/OCR/VLM 或 Unstructured/MarkItDown 路径。
- Index handoff payload：把 Document IR block 归一给 BM25、vector、GraphRAG、evidence 和 citation。
- Parser adapter registry：把 `native`、`docling_pymupdf`、`mineru_ocr_vlm` 和 `unstructured_markitdown` 作为可调度 adapter surface 管起来。
- Parse Gateway runtime：`ParseGateway` 能从 `source_text`、`source_bytes` 或 `file://` fixture 生成 `CanonicalDocumentIR`、parser diagnostics、job status 和 index handoff。
- Legacy chunk normalizer：旧 `ChunkModel` 可归一为 `CanonicalDocumentIR`，为旧 pipeline 迁移留出明确 seam。
- Parser golden fixture manifest：登记 PDF 表格、扫描件、PPTX、DOCX、XLSX、代码和 Markdown 链接的验收样例，并绑定真实 `input_path`。

当前 production parser runtime 仍在 `platform/services/convert_files/`、`platform/services/pipeline/` 和 `platform/services/rag/` 等旧路径中；PHASE04 不迁移这些重 runtime，也不把生产级 Docling / MinerU / Unstructured 平台写成 Current。

## Target role

目标状态下，这里继续承载 parser adapter、Document IR normalization、chunk/provenance、解析任务状态、parser metrics 和 parser golden tests。它向 Knowledge 层提供可引用、可追踪、可重放的文档解析结果，不直接承载 API 路由、队列 worker 或模型 provider。

## 允许新增内容

- contract、类型、router policy、adapter registry、fixture 索引、deterministic runtime surface 和 focused tests。
- 从旧路径迁移前的 ownership note。
- 面向 PHASE08 / PHASE09 / PHASE10 的 handoff contract。

## 禁止事项

- 禁止在 PHASE04 直接迁移生产 parser platform、pipeline manager、队列 worker 或 API 上传逻辑。
- 禁止破坏 `zuno.services.convert_files.*`、`zuno.services.pipeline.*`、`zuno.services.rag.*` 旧 import path。
- 禁止把 Parse Gateway 写成已经完成的生产 runtime。

## Focused tests

- `pytest -q tests/knowledge/test_document_ingestion_contract.py -p no:cacheprovider`
- `pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider`
- `pytest -q tests/knowledge tests/api -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
