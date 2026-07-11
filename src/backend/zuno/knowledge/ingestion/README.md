# Knowledge Ingestion 边界

PHASE02-PHASE05 status: contract-current-runtime-current-production-target

## 当前角色

`knowledge/ingestion/` 是 Document Ingestion / Parse Gateway 的正式 owner 入口。当前已经落地的是可测试 runtime owner surface：

- Parser Capability Matrix：登记格式、默认 parser、fallback、结构保留、证据锚点、timeout、resource budget 和 sandbox policy。
- Parser adapter contract：每个 adapter 都能表达 `supports`、`parse`、`diagnostics`、`capabilities`、`blocked_reason`、`capability_status` 和 external dependency boundary。
- Parser adapter boundary：外部 parser contract 当前记录 dependency status、dependency probe、network policy、privacy gate、budget gate 和 enrichment role；本地 PyMuPDF text PDF parser 是 current slice，Docling layout enrichment、Unstructured / MarkItDown、MinerU / OCR / VLM 仍按 target 或 blocked boundary 处理。
- Canonical Document IR：统一 document metadata、block、table、figure、source span、ACL、sensitivity tags 和 provenance；metadata 当前已包含 `source_id`、`source_sha256`、`document_version_id`、`parser_config_hash`、`schema_version` / `ir_schema_version`、`derived_from`、`asset_refs`、`redaction_status`、`retention_policy`、fallback 和 target-blocked 字段。
- Source span provenance contract：`build_source_span_provenance()` 当前把 `document_id`、`source_object_id`、`document_version_id`、`page_number`、`section_path`、`block_id`、`chunk_id`、`char_start`、`char_end`、`normalized_text`、`raw_text`、`parent_chunk_id`、`neighbor_chunk_ids`、`source_uri`、`file_name`、`content_hash`、`parser_name` 和 `parser_version` 归一到 handoff metadata；缺失 page / char offset 时保留 `null`，不猜测 span。
- Citation-sized chunk handoff：当前 `build_index_handoff_payload()` 会为每个 source block 生成一个 `parent_context` chunk 和若干 `citation` chunks；BM25 / vector / GraphRAG / evidence / citation handoff 使用 citation chunks，并在 metadata 中保留 `parent_chunk_id`、`neighbor_chunk_ids`、`parent_context` 和 `citation_chunking` 配置。
- Parser router contract：按文件扩展名或格式选择 native、Docling/PyMuPDF、MinerU/OCR/VLM 或 Unstructured/MarkItDown 路径；真实 `%PDF` bytes/file 走 PyMuPDF，旧文本 fixture 仍可走 deterministic fallback。
- Index handoff payload：把 Document IR block 归一给 BM25、vector、GraphRAG、evidence 和 citation。
- Parser adapter registry：把 `native`、`docling_pymupdf`、`mineru_ocr_vlm` 和 `unstructured_markitdown` 作为可调度 adapter surface 管起来。
- Parse Gateway runtime：`ParseGateway` 能从 `source_text`、`source_bytes` 或 `file://` fixture 生成 `CanonicalDocumentIR`、parser diagnostics、job status 和 index handoff；真实 text PDF 会保留 page/bbox/char SourceSpan，unknown format 会返回稳定 fallback diagnostics，target-blocked adapter 会返回稳定 warning diagnostics。
- Local parser worker lifecycle：`submit_parse_job()` / `retry_parse_job()` / `cancel_parse_job()` 当前提供 in-process job lifecycle，覆盖 `accepted`、`running`、`succeeded`、`failed`、`blocked`、`retrying`、`cancelled` 和 `dead_letter` 的本地 snapshot 语义，并记录 idempotency key、attempt id、failure snapshot、diagnostics、retry policy 和 metrics。
- Native parser runtime：`native` 当前覆盖 `txt / md / csv / json / html / code` 的低依赖解析；Markdown 保留 heading / link / code fence / table，CSV 保留 delimiter / header / row / column / table_cell，JSON 保留 JSON pointer，HTML 过滤 script/style 并保留 heading / paragraph / link / table，code 只做扩展名语言识别和 regex import/class/function metadata，不声称完整 AST 语义。
- OCR / VLM boundary：`mineru_ocr_vlm` 当前是 blocked derived enrichment adapter；diagnostics 和 job snapshot 会保留 `derived_enrichment`、deny-by-default network policy、privacy gate、budget gate 和 review_required，不把 OCR / VLM 输出写成 source truth。
- Legacy chunk normalizer：旧 `ChunkModel` 可归一为 `CanonicalDocumentIR`，为旧 pipeline 迁移留出明确 seam。
- Parser golden fixture manifest：登记 PDF 表格、扫描件、PPTX、DOCX、XLSX、TXT、Markdown、CSV、JSON、HTML 和代码的验收样例，并绑定真实 `input_path`。

当前 production parser runtime 仍在 `platform/services/convert_files/`、`platform/services/pipeline/` 和 `platform/services/rag/` 等旧路径中；本目录不迁移这些重 runtime，也不把生产级 Docling / MinerU / Unstructured / OCR / VLM 平台、DB-backed queue、outbox、worker lease、heartbeat、dead letter queue 或 reconciler 写成 Current。

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
