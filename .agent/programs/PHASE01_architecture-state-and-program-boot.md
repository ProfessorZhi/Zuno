# PHASE01 架构状态与 Program 启动

status: completed

## 目标

打开 `zuno-architecture-detail-and-execution-plan-v1`，把当前状态从 no-active 切换为 active，并固定本 program 只做架构文档、架构图 HTML 和执行计划。

## 范围

允许修改 `.agent/programs/`、`.agent/references/current-program.md`、`docs/architecture/architecture.md`、`README.md`、`docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/programs/README.md` 和验证器中与 active program 状态相关的规则。

## 需要修改的文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/references/current-program.md`
- `docs/architecture/architecture.md`
- `README.md`
- `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/programs/README.md`
- `.agent/scripts/verify_agent_system.py`
- `tests/repo/test_agent_system.py`

## 禁止修改的文件

- `src/backend/zuno/**`
- API / DB / frontend runtime 文件。
- 历史归档 program 内容。

## 验收闸门

- 当前 program 名称、state、current_phase 在 `.agent/programs/current.md` 和 `.agent/references/current-program.md` 中一致。
- `.agent/programs/` 中 PHASE 文件从 `PHASE01` 开始且连续。
- 文档保留 `Codex 执行协作`、`不是 Zuno runtime 架构`、`不是多线程模式` 这些边界。

## 验证命令

```powershell
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## 需要返回的证据

- branch
- modified files
- active program state
- validation commands and results

## 历史影响

本阶段不移动历史材料。
