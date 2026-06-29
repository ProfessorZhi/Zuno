# Zuno Program3 Thread B 目标模式：src/backend/zuno 中层目录清爽化第一批落地

你必须使用 Codex UI 目标模式。本线程默认开启多 agent 模式，但多个 agent 不得同时编辑同一文件。

## 工作模式

这是 Program3 continuation：`zuno-repo-layout-cleanup-v1`。

每轮开始必须先确认：

```powershell
pwd
git status --short --branch
git branch --show-current
```

如果当前不是独立 worktree 或不是独立 `codex/` 分支，先在本 worktree 内创建或切换到：

```text
codex/program3-thread-b-backend-zuno-cleanup
```

如果无法确认独立 worktree / 独立分支，停止并回报，不要编辑。

## 必读

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `src/backend/zuno/README.md`
- `tests/repo/test_backend_facade_layers.py`
- `tools/scripts/verify_repo_structure.py`

## 目标

从 PHASE06 的 inventory 中选第一批最安全的中层目录做真实落地，让 `src/backend/zuno` 更接近六层封面：

```text
api / agent / memory / capability / knowledge / platform
```

优先处理低风险对象：

- `config/`、`database/`、`platform/` 的职责说明和 facade 边界
- `schema/` 与 `api/` 的 DTO 归属说明
- `tools/`、`system_skills/`、`prompts/`、`fixtures/` 的资源分类
- 明确哪些目录是 migration-source，哪些是 target-layer，哪些是 app-resource

允许做的实际清理：

1. 增加或修正目录 README。
2. 增加 facade re-export，但不改 runtime 行为。
3. 移动非常小、无副作用、测试能覆盖的 helper / contract 文件。
4. 更新 repo structure verifier，让目录职责可回归验证。
5. 如果发现某个目录不能动，把“为什么不能动”写入 PHASE08，不要硬搬。

## 允许修改

- `src/backend/zuno/**/README.md`
- `src/backend/zuno/platform/**`
- `src/backend/zuno/api/**`
- `src/backend/zuno/schema/**`
- `src/backend/zuno/config/**`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_backend_facade_layers.py`
- `tests/repo/test_repo_structure_consistency.py`

## 禁止修改

- 不一次性移动 `services/`。
- 不拆 `general_agent.py`。
- 不改 public API schema 行为。
- 不改 DB schema。
- 不碰 GraphRAG runtime 行为。
- 不为了视觉清爽破坏 import compatibility。

## 验证

必须运行：

```powershell
git diff --check
pytest -q tests/repo/test_backend_facade_layers.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
```

## 收尾

提交并推送。提交信息建议：

```text
chore: tighten backend directory boundaries
```

最终回复必须包含：

- branch
- commit hash
- push 状态
- 哪些目录更清楚了
- 哪些目录仍不能物理移动
- tests 结果
