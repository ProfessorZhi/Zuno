# PHASE04 document-ingestion-parse-runtime

status: active

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

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge tests/fixtures/parser_golden -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```
