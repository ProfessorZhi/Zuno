# Zuno Program3 Thread C 目标模式：根目录与本地产物清理落地

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
codex/program3-thread-c-root-local-artifacts
```

如果无法确认独立 worktree / 独立分支，停止并回报，不要编辑。

## 必读

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `.gitignore`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_repo_structure_consistency.py`

## 目标

让第一次打开 VS Code / Explorer 时，项目根目录和主要一级目录不再被本地产物、缓存、旧入口干扰。

重点审计：

- `.agents`
- `.test-tmp`
- `.local`
- `data`
- `reports`
- `node_modules`
- `__pycache__`
- 其他未跟踪生成物

先判断 tracked / untracked。tracked 文件不能随便删，必须确认它是否正式样例、正式证据或历史档案。

## 允许修改

- `.gitignore`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_repo_structure_consistency.py`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- 必要时 `docs/architecture/roadmap.md`

## 允许清理

只允许删除未跟踪、可再生成、本地缓存类文件夹，例如：

- `__pycache__`
- `.test-tmp`
- 空的退休目录
- 明确 ignored 的本地运行产物

删除前必须确认路径在 repo 内。

## 禁止修改

- 不删除 tracked 数据。
- 不删除正式 examples。
- 不删除 `docs/history`。
- 不删除 `node_modules`，除非确认它未被 Git 跟踪且用户环境不依赖当前安装。
- 不移动 runtime 源码。

## 验证

必须运行：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

## 收尾

提交并推送。提交信息建议：

```text
chore: clean local project layout noise
```

最终回复必须包含：

- branch
- commit hash
- push 状态
- 清理了哪些 untracked/local 目录
- 哪些目录保留以及原因
- tests 结果
