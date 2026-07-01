# PHASE04 Native Text 与 Structured File Parser

status: completed
program: zuno-production-document-ingestion-and-thread-foundation-v1
completed_at: 2026-07-01

## 目标

把本地可控的 native parser 做扎实，优先覆盖企业知识库常见低依赖格式：TXT、Markdown、CSV、JSON、HTML 和代码文件。这些格式应成为后续评测和 fixtures 的稳定输入。

## 范围

- TXT / Markdown：章节、标题、链接、代码块、source span。
- CSV / JSON：结构化字段、行列位置、schema hints、table metadata。
- HTML：正文抽取、标题层级、链接、表格、脚本样式过滤。
- Code：语言识别、函数 / 类 / import 的轻量 metadata、code block IR。

## 禁止范围

- 不接入浏览器渲染型网页抓取。
- 不实现完整 AST parser 或语言服务器。
- 不把 HTML 清洗写成安全沙箱。
- 不改变 GraphRAG extraction 逻辑。

## 验收闸门

- 每种 native 格式至少有一个 golden fixture。
- 输出 Document IR 保留 block type、source span、section path 或 table/code metadata。
- Markdown 至少覆盖 heading hierarchy、link、code fence、table 和 `section_path`。
- CSV 至少覆盖 delimiter/header、row index、column name 和 `table_cell`。
- JSON 至少覆盖 JSON pointer path、object / array block 和 malformed diagnostics。
- HTML 至少覆盖 script/style 过滤、heading、paragraph、link 和 table。
- Code 至少覆盖 language、imports、class/function regex metadata 和 line range；不声称完整 AST 语义。
- malformed CSV / JSON / HTML 有 diagnostics，不导致 parser worker 崩溃。
- code parser 能识别语言和基本结构，但不声称完整语义理解。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- PHASE02 Document IR contract。
- PHASE03 parser worker lifecycle。
- `docs/architecture/document-ingestion-foundation.md`
- `tests/fixtures/` 或当前 parser golden fixture 路径。
- `src/backend/zuno/knowledge/ingestion/`

## 需要修改的文件

- `src/backend/zuno/knowledge/ingestion/**`
- `tests/fixtures/**`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `.agent/programs/PHASE04_native-text-and-structured-file-parsers.md`

## 执行拆解

1. 为 Markdown heading / link / code fence 写 golden fixture test。
2. 为 CSV 表头、行号、单元格定位写 golden fixture test。
3. 为 JSON object / array 路径 metadata 写 golden fixture test。
4. 为 HTML title / heading / table / link 写 golden fixture test。
5. 为 Python 或通用 code 文件写 language / code block metadata test。
6. 逐个实现最小 parser 增强。
7. 检查 malformed input diagnostics。
8. 更新 parser capability matrix。

## 多 agent 分工

- 一个 subagent 可只读审计 fixture 命名和覆盖。
- 一个 subagent 可只读比较 Document IR 是否足够支撑 citation。
- 主线程负责 tests、parser 实现和文档同步。

## 需要返回的证据

- 新增 fixtures 列表。
- 每种格式的 IR 示例摘要。
- malformed input diagnostics 示例。
- focused test 输出。

## 停止条件

- fixture 需要引入二进制大文件且没有合适存放位置。
- code parser 需求扩大到完整 AST / LSP。
- HTML parser 需求扩大到联网抓取或动态渲染。

## 执行证据

本 phase 按 TDD 关闭。先新增 fixtures 和 focused tests，再实现 native adapter 增强。

首次红灯：

```powershell
pytest -q tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
```

结果：`9 failed, 25 passed`。失败点集中在 Markdown link metadata、CSV table/cell block、JSON pointer、HTML link/table、code language/symbol metadata 和 malformed CSV / JSON / HTML diagnostics。

## 新增和修正 fixtures

- 新增 `tests/fixtures/parser_golden/inputs/plain_text.txt`。
- 新增 `tests/fixtures/parser_golden/inputs/markdown_structured.md`。
- 新增 `tests/fixtures/parser_golden/inputs/csv_table.csv`。
- 新增 `tests/fixtures/parser_golden/inputs/json_policy.json`。
- 新增 `tests/fixtures/parser_golden/inputs/html_policy.html`。
- 扩展 `tests/fixtures/parser_golden/inputs/code_file.py`，覆盖 import、class 和 function regex metadata。
- 修正 `tests/fixtures/parser_golden/manifest.json` 中 `docx_heading_table` 与 `xlsx_sheet` 的 input path 互换问题，并把 TXT / Markdown / CSV / JSON / HTML 加入 manifest。

## Native IR 摘要

| Format | Current local output |
| --- | --- |
| TXT | 非空行生成 paragraph block，保留 line_range。 |
| Markdown | heading hierarchy 写入 `section_path`，link block 写入 `href` / `label`，code fence 写入 `language` / `code_fence`，table block 写入 headers、row_count、column_count 和 `table_cell`。 |
| CSV | table block 写入 delimiter、headers、row_count、column_count；每个 cell 生成 `table_cell` block，保留 row index、column index、column name 和 `source_span.table_cell`。 |
| JSON | object / array / value 分别生成 `json_object`、`json_array`、`json_value` block，metadata 保留 JSON pointer 和 path。 |
| HTML | 使用 Python `HTMLParser` 做静态解析，过滤 script/style，保留 heading、paragraph、link 和 table；不做浏览器渲染或安全沙箱声明。 |
| Code | 用扩展名识别语言，用 regex 提取 import、class 和 function metadata；不声称完整 AST 或 LSP 语义。 |

## Malformed Diagnostics

- malformed CSV：row length 与 header length 不一致时返回 warning diagnostic，仍生成 table / cell block，并把 malformed metadata 写入相关 block。
- malformed JSON：`json.JSONDecodeError` 转为 warning diagnostic 和 fallback paragraph block，不让 parser worker 崩溃。
- malformed HTML：缺失闭合结构时返回 warning diagnostic；严重不闭合且 parser 无法产出结构化块时生成 fallback paragraph block，并写入 malformed metadata。

## 变更文件

- `src/backend/zuno/knowledge/ingestion/adapters.py`
- `src/backend/zuno/knowledge/ingestion/router.py`
- `src/backend/zuno/knowledge/ingestion/README.md`
- `tests/fixtures/parser_golden/manifest.json`
- `tests/fixtures/parser_golden/inputs/plain_text.txt`
- `tests/fixtures/parser_golden/inputs/markdown_structured.md`
- `tests/fixtures/parser_golden/inputs/csv_table.csv`
- `tests/fixtures/parser_golden/inputs/json_policy.json`
- `tests/fixtures/parser_golden/inputs/html_policy.html`
- `tests/fixtures/parser_golden/inputs/code_file.py`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `docs/architecture/document-ingestion-foundation.md`

## 验证结果

```powershell
git diff --check
pytest -q tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
```

结果：`34 passed`。`git diff --check` 通过；PowerShell profile 的 Terminal-Icons warning 不属于仓库 diff 检查失败。
