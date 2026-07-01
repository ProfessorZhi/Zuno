# PHASE01 Program Truth Source 与 Parser Current 审计

status: completed
program: zuno-production-document-ingestion-and-thread-foundation-v1
completed_at: 2026-07-01

## 目标

打开 Program 1 的执行真相源，先证明当前仓库状态、文档解析代码、fixtures、tests、verifier 和 Current / Target 边界是什么。PHASE01 只关闭“我们知道现在在哪里”，不关闭任何 runtime 能力。

## 范围

- 确认当前 worktree、branch、`git status --short --branch`、最近提交和远端同步状态。
- 读取 `AGENTS.md`、README、`.agent/programs/*`、`.agent/references/current-program.md`、`docs/architecture/architecture.md`、`docs/architecture/production-readiness.md`。
- 审计 `src/backend/zuno/knowledge/ingestion/`、`src/backend/zuno/knowledge/indexing/`、相关 tests 和 fixtures。
- 审计 workspace file / ingest 产品路径是否真正进入 `ParseGateway`，特别检查 `WorkspaceTaskRuntimeService.create_ingest_job()`、`_document_from_file()` 和 `workspace_text_runtime` stub。
- 输出 parser current matrix：支持格式、真实 parser、fallback、target-blocked、测试覆盖、缺口。

## 禁止范围

- 不修改 runtime 行为。
- 不把生产 parser worker、深度 OCR、layout/table/code extraction、外部 index 平台写成 Current。
- 不创建真实 Codex UI 子线程。
- 不改数据库 schema、public API 或兼容路径。

## 验收闸门

- `current.md`、roadmap 和本 phase 文件都声明当前 active program。
- parser current matrix 能回答每种格式：入口、adapter、IR 字段、测试、是否 Current。
- workspace ingest 审计必须明确当前是 `ParseGateway.submit_parse_job()` 闭环，还是仍绕过 parser gateway 直接 index。
- 对 PDF、Office、OCR、扫描件、代码解析的不足必须写成 Remaining Target 或 blocked evidence。
- 审计结果必须给出 PHASE02 的最小实现范围。

## 验证命令

```powershell
git status --short --branch
git log --oneline -5 --decorate
git diff --check
python .agent/scripts/verify_agent_system.py
pytest -q tests/knowledge -p no:cacheprovider
```

## 需要先读取

- `AGENTS.md`
- `README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/references/current-program.md`
- `.agent/references/code-map.md`
- `.agent/references/verification-map.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `src/backend/zuno/knowledge/ingestion/README.md`
- `src/backend/zuno/api/services/workspace_task_runtime.py`

## 需要修改的文件

- `.agent/programs/PHASE01_program-truth-source-and-parser-current-audit.md`
- 如审计发现当前 program 状态漂移，可同步：
  - `.agent/programs/current.md`
  - `.agent/references/current-program.md`
  - verifier / repo tests 的 active program 断言

## 执行拆解

1. 运行 git safety gate，确认 worktree clean 或列出用户未说明改动。
2. 列出 `src/backend/zuno/knowledge/ingestion/` 的 parser 入口、registry、IR、diagnostics、fixtures。
3. 列出 `tests/knowledge/` 与 parser / index handoff 有关的 tests。
4. 审计 `/workspace/file` -> `/workspace/ingest` 当前调用链，确认是否经过 `ParseGateway.submit_parse_job()`，并记录 parse job / index job lineage 缺口。
5. 建立 parser current matrix，至少覆盖 `pdf`、`docx`、`pptx`、`xlsx`、`txt`、`md`、`csv`、`json`、`html`、`image`、`scanned`、`code`。
6. 标记每一项为 `current`、`fallback-current`、`target-blocked` 或 `unknown-needs-test`。
7. 给 PHASE02 输出要冻结的 adapter contract、Document IR 字段、version/idempotency 字段和新增测试建议。

## 多 agent 分工

- 可用 subagent 做只读 parser code audit。
- 可用 subagent 做只读 tests / fixtures audit。
- 主线程负责最终 matrix、Current / Target 判断和文件修改。
- 多个 agent 不得同时改 `.agent/programs/*`。

## 需要返回的证据

- git safety gate 输出摘要。
- parser current matrix。
- tests / fixtures 覆盖表。
- workspace ingest -> ParseGateway gap 审计结论。
- target-blocked 清单。
- PHASE02 输入清单。

## 审计证据

### Git safety gate

- `git fetch --prune`：exit 0。
- `git status --short --branch`：`## codex/zuno-truth-source-production-readiness-baseline...origin/codex/zuno-truth-source-production-readiness-baseline`，无未提交改动。
- `git log --oneline -5 --decorate`：最新提交为 `43e3f313 docs: add ingestion foundation contract`。
- 架构镜像启动检查：`docs/architecture/architecture.md` 与 `.agent/architecture/architecture.md` hash 一致；`docs/architecture/architecture.html` 与 `.agent/architecture/architecture.html` hash 一致。

### 多 agent 审计分工

- 主线程保留最终 Current / Target 判断和文件修改权。
- read-only subagent A 审 parser registry / adapters / contracts。
- read-only subagent B 审 tests / fixtures。
- read-only subagent C 审 workspace ingest -> ParseGateway 调用链。
- read-only subagent D 审 index handoff / citation provenance。
- 四个 subagent 均未修改文件，结果只作为 PHASE01 证据交叉校验。

### Parser current matrix

| 格式 | PHASE01 状态 | 当前证据 | PHASE02 / 后续输入 |
| --- | --- | --- | --- |
| `pdf` | `fallback-current` | `PARSER_CAPABILITY_MATRIX` 路由到 `docling_pymupdf`，但 adapter contract 标记生产 Docling / PyMuPDF worker 为 `target_blocked`；本地测试只证明文本形 PDF fixture 能生成 table/page/bbox。 | 冻结 external adapter 的 target-blocked 表达；不能把真实 PDF layout / OCR 写成 Current。 |
| `docx` | `fallback-current` | 路由到 `unstructured_markitdown`，生产 worker target-blocked；本地 structured-markdown 占位解析和 fixture replay 有测试。 | 修正 fixture truth source，冻结 Office fallback-current 与生产依赖边界。 |
| `pptx` | `fallback-current` | 路由到 `unstructured_markitdown`，本地 slide-title / figure-shaped 文本解析有测试。 | 不声称真实 PPTX layout parser Current。 |
| `xlsx` | `fallback-current` | 路由到 `unstructured_markitdown`，本地表格文本解析有测试。 | 需要 sheet / table_cell contract 更明确，并修正 docx/xlsx fixture manifest 互换问题。 |
| `txt` | `current` | native parser 和 inline runtime test 覆盖 paragraph / line_range。 | PHASE04 可补 golden fixture。 |
| `md` | `current` | native parser 和 fixture 覆盖 heading / link / section_path。 | PHASE04 继续补 code fence / table 层级。 |
| `csv` | `unknown-needs-test` | matrix 存在，但没有 CSV runtime / fixture 测试；当前 native adapter 会走 plain-text 风格解析。 | PHASE04 先写 delimiter/header/row/column/table_cell failing tests。 |
| `json` | `unknown-needs-test` | matrix 存在，但没有 JSON runtime / fixture 测试，也没有 JSON pointer block 证据。 | PHASE04 先写 object/array/json pointer/malformed diagnostics tests。 |
| `html` | `unknown-needs-test` | matrix 存在，但没有 HTML runtime / fixture 测试；当前 adapter 只是 markdown-like parsing。 | PHASE04 先写 script/style filter、heading、paragraph、link、table tests。 |
| `image` | `target-blocked` | OCR/VLM adapter contract 是 `target_blocked`；当前 `_parse_image_ocr` 会把传入文本包装为 `ocr_text`，不能证明真实 OCR。 | PHASE05 必须把 OCR/VLM 不可用时的 blocked diagnostics 固定下来，避免假成功。 |
| `scanned` | `target-blocked` | matrix 存在，但常见图片扩展名路由到 `image`；OCR/VLM runtime 未部署。 | PHASE05 写 scanned / OCR blocked adapter tests。 |
| `code` | `current` | native code block 和 line_range 有 runtime test。 | PHASE04 需要 language / import / class / function regex metadata tests，不能声称完整 AST。 |

### Tests / fixtures 覆盖

- `tests/knowledge` 当前 25 个 tests 通过，覆盖 parser matrix、ParseGateway runtime、job snapshot / retry、index manifest 和 retrieval payload。
- `tests/knowledge/test_document_ingestion_contract.py` 证明 12 类格式都登记在 matrix，但该测试只检查 matrix 字段和 fixture manifest 完整性。
- `tests/knowledge/test_parse_gateway_runtime.py` inline runtime 覆盖 `pdf / docx / pptx / md / txt / image / code`，real fixture replay 覆盖 `pdf / docx / pptx / xlsx / scanned / code / md`。
- `tests/fixtures/parser_golden/manifest.json` 中 `docx_heading_table` 指向 `inputs/xlsx_sheet.xlsx`，`xlsx_sheet` 指向 `inputs/docx_heading_table.docx`；这是 PHASE04 必须修正的 fixture truth-source gap。
- fixture manifest 的 `expected_blocks` 当前未与 parser 输出逐项比对；runtime fixture test 只断言存在一个 expected block。
- 当前没有 `txt / csv / json / html` golden fixture case；PHASE04 必须补齐 native structured parser corpus。
- `.pdf / .docx / .pptx / .xlsx / .png` fixtures 是 text-shaped placeholders，只能证明 deterministic local fallback 行为，不能证明真实二进制解析能力。

### Workspace ingest -> ParseGateway gap

当前 `/workspace/file -> /workspace/ingest` 产品路径仍绕过 `ParseGateway.submit_parse_job()`：

1. `src/backend/zuno/api/v1/workspace.py` 的 `/workspace/ingest` route 调用 `WorkspaceTaskRuntimeService.create_ingest_job()`。
2. `WorkspaceTaskRuntimeService.create_ingest_job()` 用 `cls._document_from_file(file=..., content=...)` 构造 `CanonicalDocumentIR`。
3. 随后直接调用 `cls._knowledge_index_runtime.index_document(...)`。
4. `_document_from_file()` 硬编码 `parser_id="workspace_text_runtime"` 和 `parser_version="phase09-runtime-v1"`，生成单 block paragraph stub。
5. `src/backend/zuno/api/services/workspace_task_runtime.py` 当前没有调用 `ParseGateway` 或 `submit_parse_job()`。

结论：PHASE01 只关闭审计事实；Program 1 的核心 runtime gap 仍必须在后续 phase 中关闭。PHASE02 应先冻结 workspace file -> `ParseDocumentRequest` / parser contract，PHASE06 前必须证明 parse job lineage 进入 index manifest。

### Index handoff / citation provenance gap

当前 index manifest 已记录 `source_block_ids`、`source_provenance`、`acl_scopes`、`sensitivity_tags` 和 `adapter_status`。`source_provenance` 由 Document IR 提供 `document_id / workspace_id / source_uri / mime_type / hash / parser_id / parser_version / confidence / warnings`。

缺口：

- `ParseDocumentResult.job_id` 和 `ParseJobSnapshot.job_id` 没有进入 `CanonicalDocumentIR`、index handoff、`IndexJobManifest`、evidence 或 citation。
- `ParseJobSnapshot` 只有数字 `attempt`，没有稳定 `parse_attempt_id`。
- `DocumentMetadata` 当前使用通用 `hash`，未显式区分 `source_sha256`。
- 当前没有 `document_version_id`、`parser_config_hash`、`ir_schema_version` 或 `diagnostics_digest` 字段。
- Agentic GraphRAG 的 Evidence / Citation contract 有 `provenance: dict`，可以承接新增 lineage，但目前 focused tests 只断言已有 `hash` / source span / citation coverage。

### Target-blocked 清单

- 生产级 Docling / PyMuPDF PDF worker：Target。
- Unstructured / MarkItDown Office worker：Target。
- MinerU / OCR / VLM parser service：Target。
- 真实扫描件 OCR、VLM caption / chart summary：Target，且 VLM 只能是 derived enrichment。
- 生产 DB、object store、queue / outbox、worker lease、dead letter queue、reconciler：Target。
- Elasticsearch / Milvus / Neo4j external index service：Target。

### PHASE02 输入清单

- 冻结 adapter status 语义：`current`、`fallback-current`、`target-blocked`、`unknown-needs-test` 如何映射到 `ParserAdapterContract` 和 diagnostics。
- 扩展 Document IR 字段：`document_version_id`、`source_sha256`、`parser_config_hash`、`ir_schema_version`、`parent_document_version_id`、`derived_from`、`asset_refs`、`redaction_status`、`retention_policy`，并明确哪些是 Current local contract、哪些是 Target。
- 为 unknown / unsupported format、fallback parser metadata、blocked adapter diagnostics 写 focused tests。
- 明确 fallback 目前只是 metadata，不是自动 fallback execution；如要执行 fallback，必须先写测试。
- 把 workspace file 进入 `ParseGateway.submit_parse_job()` 所需的 `ParseDocumentRequest` 字段固定下来。
- 把 image / scanned 在 OCR/VLM 不可用时的 blocked diagnostics 固定下来，避免把 text-shaped placeholder 误写成真实 OCR Current。
- 为 PHASE04 准备 CSV / JSON / HTML / TXT golden fixtures，修正 docx/xlsx manifest input path 互换问题。

### PHASE01 验证结果

```powershell
git diff --check
# exit 0

python .agent/scripts/verify_agent_system.py
# Agent system verification passed.

pytest -q tests/knowledge -p no:cacheprovider
# 25 passed in 0.74s
```

## 停止条件

- 工作树出现用户未说明的冲突修改。
- parser 行为和 docs Current 明显冲突，且需要用户决定是否以代码还是文档为准。
- `tests/knowledge` 大面积失败，且失败根因不是当前文档 program 变更。
