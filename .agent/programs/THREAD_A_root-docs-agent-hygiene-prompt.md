# Thread A 目标模式提示词：Root / Docs / Agent Hygiene Audit

你必须处于真正 Codex UI 目标模式。

默认在线程内开启多 agent 模式，提高并发：可以拆成 root layout、docs front path、`.agent` boundary 三个内部审计子任务。多 agent 只允许读和审计，不允许并行改文件。

## Branch / Worktree

目标分支：

```text
codex/program3-thread-a-root-docs-agent-hygiene
```

先执行：

```powershell
git fetch origin
git status --short --branch
git log --oneline origin/main..HEAD
```

如果当前 worktree 有未提交改动，或当前分支有未合并本地提交，停止并报告。否则切到本轮独立分支：

```powershell
git switch -C codex/program3-thread-a-root-docs-agent-hygiene origin/main
git status --short --branch
```

## 必读

- `AGENTS.md`
- `.agent/references/workflow.md`
- `.agent/references/current-program.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE01_repo-layout-audit.md`
- `docs/architecture/roadmap.md`

## 任务

只读审计根目录、`docs/`、`.agent/` 是否清楚。

重点看：

- 根目录哪些是一等必要目录，哪些是本地/生成/临时目录。
- `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 应该保留、忽略、移动、归档还是删除。
- `docs/` 前台是否只保留正式真相。
- `.agent/` 是否只承载本地 Agent Skill System。
- Program 1/2 是否只作为历史归档，不再污染 active program。

## 禁止

- 不改文件。
- 不删除目录。
- 不提交。
- 不推送。
- 不实施清理。

## 输出

返回：

1. cwd / branch / HEAD / `git status --short --branch`
2. 审计表：

```text
path | current role | target role | action | risk | verifier/test
```

3. PHASE02 建议执行清单
4. 需要主线程决策的问题
