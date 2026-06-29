# PHASE09：目标布局视觉兼容壳退休

> 状态：已完成并归档。此 phase 是 Program 3 definition 修正，不是 Program 4。

## 目标

让 `src/backend/zuno` 的第一层目录更贴近目标架构表达，继续收敛到 `api / agent / memory / capability / knowledge / platform / resources / compatibility` 为主的可读结构。

本 phase 不推进 runtime architecture upgrade，不移动 `services/`、`core/`、`schema/` 等仍承载当前 runtime 或 public compatibility 的目录。

## 范围

- 退休三个只剩兼容语义的顶层目录：
  - `src/backend/zuno/mcp_servers/`
  - `src/backend/zuno/middleware/`
  - `src/backend/zuno/evals/`
- 用非目录兼容模块承接旧 import：
  - `src/backend/zuno/mcp_servers.py`
  - `src/backend/zuno/middleware.py`
  - `src/backend/zuno/evals.py`
- 更新 repo structure verifier、repo tests、legacy import guards 和当前架构文档。

## 决策

从第一性原则看，目录树要表达当前主要架构边界，而不是每条历史 import path。`mcp_servers/`、`middleware/`、`evals/` 的实现已经分别在 `capability/mcp/servers/`、`platform/middleware/`、`tools/evals/zuno/`，继续保留顶层目录只会制造“目标架构还是没收敛”的错觉。

旧 import path 仍属于 public compatibility surface，所以不能直接删除；本 phase 把它们降级为 `.py` 兼容模块，既保留行为，又不再占用顶层目录视觉空间。

## 验收

- `src/backend/zuno` 不再出现 `mcp_servers/`、`middleware/`、`evals/` 三个目录。
- 旧 import path 继续可用：
  - `zuno.mcp_servers.*`
  - `zuno.middleware.*`
  - `zuno.evals.*`
- `tools/scripts/verify_repo_structure.py` 明确检查兼容模块存在，并禁止这三个目录恢复。
- Program 4 保持 queued draft / not active；本 phase 不打开 runtime architecture upgrade。

## 验证命令

- `pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py -p no:cacheprovider`
- `pytest -q tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `python .agent/scripts/verify_repo_hygiene.py`
- `python tools/scripts/verify_docs_entrypoints.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`
