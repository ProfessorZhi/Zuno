# PHASE04 Document Ingestion Parse Gateway

status: pending

## 目标

把文档解析从“工具层隐含能力”提升为正式 Document Ingestion / Parse Gateway，支撑企业知识库、GraphRAG、citation 和 eval。

## 步骤

- [ ] 建立 Parser Capability Matrix，覆盖 PDF、DOCX、PPTX、XLSX、TXT、MD、CSV、JSON、HTML、图片/扫描件、代码文件。
- [ ] 定义 Canonical Document IR，包含 document metadata、blocks、tables、figures、page/slide/line anchor、bbox、ACL、provenance。
- [ ] 接入 parser router，区分 native parser、PDF/Office parser、OCR/VLM parser 和 long-tail fallback。
- [ ] 定义 chunking、metadata、evidence anchor、index handoff。
- [ ] 写 focused tests 证明多格式解析 contract。

## 验收

- 每个支持格式都有默认解析路径和 fallback 策略。
- 解析结果能进入 BM25、vector、GraphRAG 和 citation。
- OCR 和高成本 parser 有 timeout、resource budget 和 sandbox policy。

## 验证

```powershell
pytest -q tests/knowledge tests/api -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```
