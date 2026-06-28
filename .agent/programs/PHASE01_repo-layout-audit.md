# PHASE01：Repo Layout 审计
> 状态：active / 当前 phase。

## 目标

审计根目录、`src/backend/zuno`、`docs`、`.agent`、`tools`、`tests` 的杂乱点。

本 phase 要输出全仓目录清理表，而不是直接移动 runtime。至少覆盖：

- 根目录是否只保留必要入口和一等目录。
- `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 等是否属于本地产物、生成物、示例输入、正式证据或历史档案。
- `src/backend` 顶层是否只保留必要源码根；`src/backend/zuno` 内部如何对应 `api / agent / memory / capability / knowledge / platform`。
- `docs/`、`.agent/`、`tools/`、`tests/` 是否各自承担单一职责。
- 哪些目录应该保留、移动、归档、忽略或删除。

## 可并行线程

- root/docs audit：`thread-prompts/THREAD_A_root-docs-agent-hygiene-prompt.md`
- backend layout audit：`thread-prompts/THREAD_B_backend-six-layer-audit-prompt.md`
- tools/tests/generated artifacts audit：`thread-prompts/THREAD_C_tools-tests-generated-artifacts-prompt.md`

## 验收

给出清理表和迁移风险，不直接移动 runtime。

清理表至少包含：

```text
path | current role | target role | action | risk | verifier/test
```
