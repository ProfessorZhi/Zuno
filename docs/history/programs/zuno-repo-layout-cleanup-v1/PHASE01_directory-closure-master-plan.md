# PHASE01：Program3 Directory Closure Master Plan

> 状态：active。Program 3 continuation / Directory Surface Alignment V1。

## 目标

把 Program 3 从“六层 facade 起步”重写为真正的目录结构收口 program。整个 Program3 结束时，`src/backend/zuno` 顶层必须收敛到六层目标目录：

```text
api / agent / memory / capability / knowledge / platform
```

允许保留的顶层文件只有 `__init__.py`、`main.py` 和受控 alias module。`compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 不能继续作为完成态顶层目录存在。

## 范围

- 固定 Program3 多 PR / 多 phase 执行计划。
- 固定最终目录树和每个旧顶层目录的目标归属。
- 固定每个 PR 的边界、验收、验证命令和禁止范围。
- 明确 Program 4 仍是 queued / not active；Program3 只做目录结构收口，不做 runtime architecture upgrade。

## 不做

- 不一次性移动 `services/`、`core/` 或高风险主循环。
- 不改 public API、DB schema、eval baseline 或前端行为。
- 不把 Target 写成 Current。
- 不把多个高风险迁移混进同一个 PR。

## 验收

- `.agent/programs/` 包含 PHASE01-06，且每个 phase 对应一个可独立 PR。
- `src/backend/zuno/DIRECTORY_MAP.md` 写清最终树、当前树、旧目录到六层目标的迁移表。
- verifier/test 允许 Program3 处于迁移中，但必须禁止新增未登记顶层目录。
- Program3 final guard 阶段会把 allowlist 收紧到六层目标目录。

## PR / Phase 拆分

| PR | Phase | 目标 | 完成后顶层变化 |
| --- | --- | --- | --- |
| PR1 | PHASE01 | 重写计划、目录地图和 guardrails | 不搬代码，只固定 Program3 DoD |
| PR2 | PHASE02 | 下沉 `config/`、`database/`、`compatibility/` 到 `platform/` | 顶层少 `config/database/compatibility` |
| PR3 | PHASE03 | 收口 `resources/`、`schema/`、`tools/` | 顶层少 `resources/schema/tools` |
| PR4 | PHASE04 | 让 `services/` 变薄，迁移低风险小模块 | 顶层 `services/` 只剩兼容 facade |
| PR5 | PHASE05 | 让 `core/` 变薄，Agent 主入口进入 `agent/` | 顶层 `core/` 只剩兼容 facade |
| PR6 | PHASE06 | Final guard：顶层只允许六层目录 | 完成 Program3 closure |

## 验证命令

- `pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider`
- `pytest -q tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`
