# PHASE05 PDF / Office / OCR Adapter 边界

status: planned
program: zuno-production-document-ingestion-and-thread-foundation-v1

## 目标

把 PDF、Office、图片和扫描件解析说清并尽量落地：能本地稳定解析的写成 Current；依赖缺失、质量不足或需要生产 worker 的写成 adapter + local fallback + target-blocked evidence。

## 范围

- PDF：文本、页码、表格 fallback、source span。
- DOCX / PPTX / XLSX：标题、段落、幻灯片、sheet、表格。
- Image / scanned：OCR adapter boundary、blocked reason、fallback diagnostics。
- VLM enrichment adapter：page image / figure image / scanned image 输入，image caption / chart summary / OCR text block 输出，带 model id、prompt version、confidence、derived_from、review_required、privacy gate 和 budget metadata。
- adapter dependency probe：明确依赖存在、缺失、版本不支持和禁用状态。

## 禁止范围

- 不新增付费 OCR / VLM 服务凭据。
- 不把缺失的 Docling / MinerU / Unstructured / OCR engine 写成 Current。
- 不把 VLM 输出当作 source truth；VLM 只能作为 derived enrichment，不能覆盖 deterministic parser 的 source span。
- 不提交大型真实企业文档。
- 不绕过 parser diagnostics 直接吞错误。

## 验收闸门

- PDF / Office / OCR capability matrix 明确 current / fallback / target-blocked。
- 依赖不可用时有稳定 blocked adapter result。
- OCR / VLM 不可用时返回 blocked diagnostics；可用时也必须带 `derived_from`、`confidence` 和 `review_required`。
- VLM 调用前必须有 page limit、budget limit、privacy gate 和 network deny-by-default 的 Target contract。
- 已有 golden fixtures 可通过 parser worker 跑完。
- OCR 或 scanned 未真实完成时，必须在 evidence 中写清不是 Current。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- PHASE01 parser current matrix。
- PHASE02 adapter contract。
- PHASE03 worker lifecycle。
- `docs/architecture/document-ingestion-foundation.md`
- 当前 PDF / Office fixtures。
- `docs/architecture/production-readiness.md`

## 需要修改的文件

- `src/backend/zuno/knowledge/ingestion/**`
- `tests/fixtures/**`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `src/backend/zuno/knowledge/ingestion/README.md`
- `.agent/programs/PHASE05_pdf-office-ocr-adapter-boundaries.md`

## 执行拆解

1. 写 dependency probe tests，覆盖 dependency present / missing。
2. 写 PDF golden fixture test，至少验证 text block、page metadata、diagnostics。
3. 写 DOCX / PPTX / XLSX fixture tests，验证结构块进入 Document IR。
4. 写 OCR blocked adapter test，证明 scanned image 不会被误写成成功解析。
5. 写 VLM enrichment contract / blocked diagnostics test，证明 enrichment 是 derived output，不覆盖 source truth。
6. 实现 adapter boundary 和 fallback。
7. 更新 README 的 Current / Target 边界。
8. 运行 focused tests。

## 多 agent 分工

- 可用 subagent 只读检查本机依赖和 fixtures。
- 可用 subagent 只读比较 production-readiness 中 parser target 边界。
- 主线程负责最终 adapter 表达、tests 和文档。

## 需要返回的证据

- PDF / Office / OCR capability matrix。
- dependency probe 输出摘要。
- blocked adapter examples。
- VLM enrichment contract 与 network / privacy / budget gate 边界。
- golden fixture test 输出。

## 停止条件

- 需要安装大型系统依赖、OCR engine 或外部服务。
- 用户要求真实企业内部资料进入 fixtures。
- adapter fallback 会让 citation source span 丢失且无法标记低置信度。
