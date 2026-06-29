# PHASE06：Final Six-Layer Guard And Closure

> 状态：planned。目标 PR：Program3 PR6。

## 目标

完成 Program3 closure：`src/backend/zuno` 顶层只保留六层目标目录和必要文件 / alias module。

## 最终允许结构

```text
src/backend/zuno/
  __init__.py
  main.py
  api/
  agent/
  memory/
  capability/
  knowledge/
  platform/
```

短期 public import alias 可保留为 `.py` 文件，但不能再恢复旧顶层目录。

## 验收

- `verify_repo_structure.py` 的 backend top-level directory allowlist 收紧到六层目录。
- `DIRECTORY_MAP.md` 从迁移地图更新为 closure summary。
- `.agent/programs/` 移除 PHASE01-06 active files，并把 Program3 完整归档到 `docs/history/programs/zuno-repo-layout-cleanup-v1/`。
- `AGENTS.md`、`.agent/references/current-program.md`、`docs/architecture/roadmap.md` 改为 Program3 completed，Program4 仍 queued / not active。

## 验证命令

- `git diff --check`
- `python tools/scripts/verify_repo_structure.py`
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `python .agent/scripts/verify_repo_hygiene.py`
- `python tools/scripts/verify_docs_entrypoints.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`
- `pytest -q --durations=50 -p no:cacheprovider`
