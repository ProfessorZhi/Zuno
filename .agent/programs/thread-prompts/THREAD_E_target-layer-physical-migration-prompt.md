# Zuno Program3 Thread E 目标模式：Target Layer 物理迁移

你必须使用 Codex UI 目标模式。本线程默认开启多 agent 模式，但多个 agent 不得同时编辑同一文件。

## Setup Gate

先确认：

```powershell
pwd
git status --short --branch
git branch --show-current
```

如果不是独立 worktree 或不是 `codex/program3-thread-e-target-layer-migration` 分支，先在本 worktree 创建或切换到该分支。若无法确认，停止。

## 必读

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `src/backend/zuno/README.md`
- `tests/repo/test_backend_facade_layers.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tools/scripts/verify_repo_structure.py`

## 目标

这轮必须走一大步，把 `src/backend/zuno` 下面的旧中层目录尽量迁入目标层，不再只用 README 解释。

目标方向：

```text
src/backend/zuno/
  api/
  agent/
  memory/
  capability/
  knowledge/
  platform/
  resources/
  compatibility/
```

优先迁移：

1. `config/` -> `platform/config/`
2. `database/` -> `platform/database/`
3. `schema/` -> `api/schema/` 或 `api/dto/`
4. `tools/` -> `capability/tools/`
5. `middleware/` -> `api/middleware/` 或 `platform/middleware/`
6. `mcp_servers/` -> `capability/mcp_servers/`
7. `evals/` -> `platform/evals/`
8. 评估 `core/`、`services/`、`utils/` 是否能收敛到 `compatibility/runtime_legacy/`，或拆到目标层。

允许使用 import alias / compatibility layer，但目标是减少 `src/backend/zuno` 顶层目录数量。不要只新增 README。

## 允许修改

- `src/backend/zuno/api/**`
- `src/backend/zuno/agent/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/platform/**`
- `src/backend/zuno/config/**`
- `src/backend/zuno/database/**`
- `src/backend/zuno/schema/**`
- `src/backend/zuno/tools/**`
- `src/backend/zuno/middleware/**`
- `src/backend/zuno/mcp_servers/**`
- `src/backend/zuno/evals/**`
- `src/backend/zuno/core/**`
- `src/backend/zuno/services/**`
- `src/backend/zuno/utils/**`
- import consumers required by physical moves
- repo structure verifier / repo tests
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`

## 禁止

- 不改 DB schema 内容。
- 不改变 API response shape。
- 不改变 retrieval / GraphRAG semantics。
- 不做无测试的大删除。
- 不为了视觉清爽牺牲 import compatibility。

## 验证

至少运行：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_backend_facade_layers.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

如果迁移影响 API、DB、tool、retrieval 或 agent imports，必须补跑相关 focused tests。

## 收尾

提交并推送。提交信息建议：

```text
refactor: migrate backend directories into target layers
```

最终报告必须列出：

- 移走了哪些顶层目录。
- 还剩哪些顶层目录。
- 每个剩余目录为什么本轮不能动。
- 验证结果。
