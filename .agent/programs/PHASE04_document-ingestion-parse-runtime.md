# PHASE04 document-ingestion-parse-runtime

status: completed

## 目标

让 `src/backend/zuno/knowledge/ingestion` 从 contract owner 推进到真实 Parse Gateway runtime owner。

## 范围

- 接通 parser adapters、Document IR normalization、chunk metadata、provenance、ACL 和 parser job status。
- 至少覆盖 PDF、DOCX/PPTX、Markdown/TXT、图片 OCR、代码文件五类主格式。
- 保留 parser golden fixtures，支持失败样例回放。

## 禁止范围

- 不把旧 `platform/services/convert_files` 静默删除。
- 不把 parser matrix 当作 runtime 完成证据。
- 不在根目录遗留解析临时文件。

## 验收闸门

- focused tests 能对五类格式生成 Canonical Document IR。
- IR 中 block、source、provenance、ACL 和 parser diagnostics 可断言。
- parser job 失败能返回可追踪 error，不吞错。

## 完成证据

- `src/backend/zuno/knowledge/ingestion/gateway.py` 提供 deterministic `ParseGateway` runtime surface，支持 `parse_document`、`submit_parse_job` 和 `get_job_status`。
- `src/backend/zuno/knowledge/ingestion/adapters.py` 提供 parser adapter registry，不再只停留在 matrix contract。
- `src/backend/zuno/knowledge/ingestion/normalizer.py` 提供 legacy `ChunkModel` 到 `CanonicalDocumentIR` 的归一入口。
- `tests/fixtures/parser_golden/inputs/` 已补真实 fixture 输入，`manifest.json` 绑定 `input_path`。
- `tests/knowledge/test_parse_gateway_runtime.py` 覆盖 PDF、DOCX、PPTX、XLSX、Markdown/TXT、图片 OCR、代码文件、source anchors、failure diagnostics 和 job replay。

## Current / Target 边界

Current 是可测试的 Parse Gateway runtime owner surface；不是生产级 Docling / MinerU / Unstructured 平台迁移完成，也不是 PHASE05 index runtime 完成。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge tests/fixtures/parser_golden -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```
