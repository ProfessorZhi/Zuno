# PHASE04 Document Ingestion Parse Gateway

status: active

## 目标

把文档解析从“工具层隐含能力”提升为正式 Document Ingestion / Parse Gateway，支撑企业知识库、GraphRAG、citation 和 eval。

企业知识库场景里，文档解析是后续所有能力的前置依赖。RAG 需要稳定 chunk，GraphRAG 需要实体和关系抽取输入，citation 需要页码、bbox、slide、sheet、line range，DLP 需要 block-level ACL 和敏感标签，eval 需要知道答案证据来自哪个解析器和哪个 source span。因此解析层不能只是“能读出一点文本”，而要输出可追踪、可评测、可重放的 Document IR。

Parser router 目标矩阵：

```text
native parser       -> TXT / MD / Code / HTML / CSV / JSON
Docling/PyMuPDF4LLM -> PDF, layout-heavy docs, tables, page anchors
MinerU/OCR/VLM      -> scanned PDF, images, formulas, figures, low-quality OCR
Unstructured/MarkItDown -> DOCX / PPTX / XLSX / long-tail office formats
```

所有 parser adapter 都必须归一到同一种结构化 Markdown / JSON IR，并保留 `document_id`、`workspace_id`、`source_uri`、`parser_id`、`parser_version`、`confidence`、`page`、`bbox`、`section_path`、`table_cell`、`slide`、`sheet`、`line_range`、`acl_scope` 和 `sensitivity_tags`。

## 步骤

- [ ] 建立 Parser Capability Matrix，覆盖 PDF、DOCX、PPTX、XLSX、TXT、MD、CSV、JSON、HTML、图片/扫描件、代码文件。
- [ ] 输出 `docs/architecture/parser-capability-matrix.md` 或在正式架构文档中加入同等表格，列出 `format`、`default_parser`、`fallback`、`structure_kept`、`evidence_anchor`、`tests`。
- [ ] 定义 Canonical Document IR，包含 document metadata、blocks、tables、figures、page/slide/line anchor、bbox、ACL、provenance。
- [ ] 接入 parser router，区分 native parser、PDF/Office parser、OCR/VLM parser 和 long-tail fallback。
- [ ] 为 native、Docling/PyMuPDF4LLM、MinerU/OCR/VLM、Unstructured/MarkItDown 分别定义 adapter contract、timeout、resource budget 和 fallback reason。
- [ ] 定义 chunking、metadata、evidence anchor、index handoff。
- [ ] 建立 parser golden fixtures：PDF 表格、扫描件、PPTX slide、DOCX heading/table、XLSX sheet、代码文件、Markdown 链接。
- [ ] 将 parser result 接入 BM25/vector/GraphRAG/evidence/citation 的 handoff contract。
- [ ] 写 focused tests 证明多格式解析 contract。

## 输入 / 输出文件

输入：

- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/capability/**` 中既有解析工具或文件工具。
- parser 相关依赖和历史工具代码。

输出：

- `src/backend/zuno/knowledge/ingestion/**`
- Canonical Document IR contract。
- parser router contract。
- parser golden fixtures。
- index handoff payload：BM25、vector、GraphRAG extraction、Evidence/Citation。

## 依赖与阻塞

- 依赖 PHASE02 ownership matrix，Document Ingestion 归属 `knowledge/ingestion` 或明确等价边界。
- PHASE08 的 GraphRAG indexing 和 Evidence/Citation 必须消费本 phase 的 IR 或 handoff payload。
- PHASE09 的 DLP / ACL 检查必须读取本 phase 的 `acl_scope`、`sensitivity_tags` 和 source span。
- PHASE10 retrieval eval 必须能回到 parser_id、parser_version 和 source_span。

## 验收

- 每个支持格式都有默认解析路径和 fallback 策略。
- 解析结果能进入 BM25、vector、GraphRAG 和 citation。
- 每个 chunk 都能回溯到原文件、页码/slide/sheet/line、parser 和 ACL scope。
- parser 失败时返回结构化 failure reason，不吞异常、不伪造空文档。
- OCR 和高成本 parser 有 timeout、resource budget 和 sandbox policy。
- 只有 parser contract tests 和 golden fixtures 通过后，才能把对应格式写入 Current；依赖存在不等于格式支持已完成。

## 验证

```powershell
pytest -q tests/knowledge tests/api -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```
