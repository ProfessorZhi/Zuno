# PHASE02 Document IR 与 Parser Contract 冻结

status: completed
program: zuno-production-document-ingestion-and-thread-foundation-v1
completed_at: 2026-07-01

## 目标

把文档解析层的核心契约固定下来：parser adapter 输入输出、Document IR 字段、capability matrix、diagnostics、fallback 和 target-blocked 表达。PHASE02 关闭的是“后续实现按什么接口施工”。

## 范围

- 冻结 parser adapter contract。
- 明确 Document IR 的最小字段和可选字段。
- 明确企业知识库入口必须有的版本、hash、parser config、schema version 和派生资产引用策略。
- 给每种文件格式写清 parser capability。
- 补充 focused contract tests，保证后续 PHASE03-PHASE06 不漂移。

## 禁止范围

- 不接入外部生产 parser 服务。
- 不把缺依赖的 Docling / MinerU / Unstructured / OCR 写成 Current。
- 不重写 index / GraphRAG runtime。
- 不更改前端上传 API，除非测试证明 parser contract 已经要求。

## 验收闸门

- parser adapter contract 能表达 `supports`、`parse`、`diagnostics`、`capabilities`、`blocked_reason`。
- Document IR 至少覆盖 source id、block id、block type、text、metadata、source span、parser name、parser version、confidence。
- 可选字段覆盖 page、section path、table cell、bbox、language、code fence、ACL、安全标签。
- 版本字段必须能表达 `document_version_id`、`source_sha256`、`parser_config_hash`、`schema_version` / `ir_schema_version`、`parent_document_version_id`、`derived_from`、`asset_refs`、`redaction_status` 和 `retention_policy` 的 Current 或 Target 边界。
- 版本策略必须声明 parser 升级、OCR 参数变化、文件内容变化和 redaction policy 变化不能静默覆盖旧 IR。
- tests 能证明 unknown format、fallback parser、blocked adapter、diagnostics 都有稳定输出。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_document_ingestion_contract.py -p no:cacheprovider
pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- PHASE01 审计结果。
- `docs/architecture/document-ingestion-foundation.md`
- `src/backend/zuno/knowledge/ingestion/`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `docs/architecture/production-readiness.md`

## 需要修改的文件

- `src/backend/zuno/knowledge/ingestion/**`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `src/backend/zuno/knowledge/ingestion/README.md`
- `.agent/programs/PHASE02_document-ir-and-parser-contract-freeze.md`

## 执行拆解

1. 先写 failing tests，覆盖 adapter capability matrix 和 Document IR 必填字段。
2. 写清 `document_version_id = document_id + source_sha256 + parser_id + parser_version + parser_config_hash + ir_schema_version` 的 local contract；未实现字段必须标为 Target，不写成 Current。
3. 让 unknown / unsupported format 返回稳定 diagnostics，而不是抛散乱异常。
4. 为 fallback adapter 增加明确 `fallback=True` 或等价元数据。
5. 为 target-blocked adapter 增加 `blocked_reason`，例如缺外部依赖、缺 OCR engine、缺生产 worker。
6. 更新 ingestion README，只描述已测试 Current 和明确 Target。
7. 运行 focused tests，失败时先修契约层，不扩大到 GraphRAG。

## 多 agent 分工

- 一个 subagent 可只读比较 current parser contract 和 tests。
- 一个 subagent 可只读检查 Document IR 字段是否能支撑 citation / eval。
- 主线程负责编写 tests、实现、README 和 phase evidence。

## 需要返回的证据

- 新增或更新 tests 名称。
- Document IR 字段表。
- document version / hash / parser config / schema version 字段表。
- parser capability matrix。
- target-blocked adapter 清单。
- focused test 结果。

## PHASE02 证据

### TDD red 证据

先写 tests 后实现，第一次 focused run 失败点符合预期：

- `tests/knowledge/test_document_ingestion_contract.py::test_parser_adapter_contract_exposes_runtime_operations_and_capabilities`：缺 `ParserAdapterContract.operations`。
- `tests/knowledge/test_document_ingestion_contract.py::test_parse_gateway_freezes_document_version_and_schema_fields`：缺 `DocumentMetadata.source_id` 等 version 字段。
- `tests/knowledge/test_parse_gateway_runtime.py::test_parse_gateway_unknown_format_returns_stable_fallback_diagnostics`：缺 `fallback_used`。
- `tests/knowledge/test_parse_gateway_runtime.py::test_parse_gateway_target_blocked_adapter_emits_stable_diagnostic`：缺 `target_blocked`。

### 新增 / 更新 tests

- `test_parser_adapter_contract_exposes_runtime_operations_and_capabilities`
- `test_parse_gateway_freezes_document_version_and_schema_fields`
- `test_parse_gateway_unknown_format_returns_stable_fallback_diagnostics`
- `test_parse_gateway_target_blocked_adapter_emits_stable_diagnostic`

### Document IR 字段表

| 对象 | Current 字段 |
| --- | --- |
| `DocumentMetadata` | `document_id`、`source_id`、`workspace_id`、`source_uri`、`mime_type`、`hash`、`source_sha256`、`parser_id`、`parser_version`、`parser_config_hash`、`document_version_id`、`schema_version`、`ir_schema_version`、`parent_document_version_id`、`derived_from`、`asset_refs`、`redaction_status`、`retention_policy`、`fallback_used`、`fallback_reason`、`target_blocked`、`blocked_reason`、`acl_scope`、`sensitivity_tags`。 |
| `DocumentBlock` | `block_id`、`type`、`text`、`source_span`、`language`、`code_fence`、`metadata`、`acl_scope`、`sensitivity_tags`、`confidence`。 |
| `ParserDiagnostic` | `code`、`message`、`severity`、`parser_id`、`format`、`metadata`。 |

### Version / hash / config / schema

- `source_sha256`：从 `source_bytes` 或 `source_text` 计算；无内容时保留 request hash。
- `parser_config_hash`：对 `ParseDocumentRequest.parser_config` 做 canonical JSON 后 sha256；request 显式传入 hash 时优先使用。
- `schema_version` / `ir_schema_version`：当前默认 `canonical-document-ir-v1`。
- `document_version_id` local contract：`document_id:source_sha256:parser_id:parser_version:parser_config_hash:ir_schema_version`。
- `parent_document_version_id`、`derived_from`、`asset_refs`、`redaction_status`、`retention_policy` 已进入 Current contract；生产 artifact store 和 version DB 仍是 Target。

### Parser capability matrix

- `native`：`current`，支持 `txt / md / csv / json / html / code`，并暴露 `supports()`、`capabilities()`、`diagnostics()`。
- `docling_pymupdf`：`target-blocked`，支持 `pdf` 的 contract surface，但生产 worker 未部署。
- `mineru_ocr_vlm`：`target-blocked`，支持 `image / scanned` 的 contract surface，但 OCR / VLM runtime 未部署。
- `unstructured_markitdown`：`target-blocked`，支持 `docx / pptx / xlsx / unknown` 的 deterministic fallback surface，生产 worker 未部署。

### Diagnostics / fallback / blocked evidence

- unknown format 现在返回 `unknown_format_fallback` warning diagnostic，并在 `DocumentMetadata` 标记 `fallback_used=True` 与 `fallback_reason`。
- target-blocked adapter 现在返回 `target_blocked_adapter` warning diagnostic，并在 `DocumentMetadata` 标记 `target_blocked=True` 与 `blocked_reason`。
- 该实现只冻结 local contract；不会把 Docling、Unstructured、MinerU、OCR 或 VLM 写成 Current。

### 修改文件

- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `src/backend/zuno/knowledge/ingestion/adapters.py`
- `src/backend/zuno/knowledge/ingestion/router.py`
- `src/backend/zuno/knowledge/ingestion/gateway.py`
- `src/backend/zuno/knowledge/ingestion/README.md`
- `docs/architecture/document-ingestion-foundation.md`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_parse_gateway_runtime.py`

### Focused test 结果

```powershell
pytest -q tests/knowledge/test_document_ingestion_contract.py -p no:cacheprovider
# 8 passed

pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
# 16 passed
```

## 停止条件

- 需要引入新第三方 parser 依赖且会影响环境锁文件。
- 现有 parser contract 与 public API DTO 冲突，需要用户决策。
- tests 显示当前 Document IR 无法兼容已有 index handoff。
