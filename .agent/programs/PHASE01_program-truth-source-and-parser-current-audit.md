# PHASE01 Program Truth Source 与 Parser Current 审计

status: active
program: zuno-production-document-ingestion-and-thread-foundation-v1

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

## 停止条件

- 工作树出现用户未说明的冲突修改。
- parser 行为和 docs Current 明显冲突，且需要用户决定是否以代码还是文档为准。
- `tests/knowledge` 大面积失败，且失败根因不是当前文档 program 变更。
