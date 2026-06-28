# Thread C 目标模式提示词：Tools / Tests / Generated Artifacts Audit

你必须处于真正 Codex UI 目标模式。

默认在线程内开启多 agent 模式，提高并发：可以拆成 tools/tests、gitignore/generated artifacts、verifier coverage 三个内部审计子任务。多 agent 只允许读和审计，不允许并行改文件。

## Branch / Worktree

目标分支：

```text
codex/program3-thread-c-verifiers-tests
```

先执行：

```powershell
git fetch origin
git status --short --branch
git log --oneline origin/main..HEAD
```

如果当前 worktree 有未提交改动，或当前分支有未合并本地提交，停止并报告。否则切到本轮独立分支：

```powershell
git switch -C codex/program3-thread-c-verifiers-tests origin/main
git status --short --branch
```

## 必读

- `AGENTS.md`
- `.agent/references/verification-map.md`
- `.agent/references/workflow.md`
- `.agent/programs/PHASE01_repo-layout-audit.md`
- `.agent/programs/PHASE05_hygiene-verifier-closure.md`
- `.gitignore`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_repo_hygiene.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tests/repo/test_agent_system.py`

## 任务

只读审计 `tools/`、`tests/`、`examples/`、`infra/`、`.gitignore` 和生成物边界。

重点看：

- 哪些目录是工具、测试、示例、infra，哪些是生成物或本地缓存。
- `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 是否被正确忽略或需要分类。
- Program 3 的目录规则应该进入哪些 verifier / repo tests。
- 当前 verifier 是否还能防止旧 active / queued / history 边界漂移。
- PHASE05 需要新增哪些检查。

## 禁止

- 不改文件。
- 不删除生成物。
- 不提交。
- 不推送。

## 输出

返回：

1. cwd / branch / HEAD / `git status --short --branch`
2. guardrail 表：

```text
rule | current coverage | missing coverage | target verifier/test | risk
```

3. `.gitignore` 建议
4. PHASE05 verifier/test 修改建议
5. 需要主线程统一合并的规则
