# PHASE04 Native Text 与 Structured File Parser

status: planned
program: zuno-production-document-ingestion-and-thread-foundation-v1

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
