# Thread B 目标模式提示词：Backend / src Six-Layer Audit

你必须处于真正 Codex UI 目标模式。

默认在线程内开启多 agent 模式，提高并发：可以拆成 `src/backend` 顶层、`src/backend/zuno` 内部结构、tests/import 风险三个内部审计子任务。多 agent 只允许读和审计，不允许并行改文件。

## Branch / Worktree

目标分支：

```text
codex/program3-thread-b-backend-six-layer-audit
```

先执行：

```powershell
git fetch origin
git status --short --branch
git log --oneline origin/main..HEAD
```

如果当前 worktree 有未提交改动，或当前分支有未合并本地提交，停止并报告。否则切到本轮独立分支：

```powershell
git switch -C codex/program3-thread-b-backend-six-layer-audit origin/main
git status --short --branch
```

## 必读

- `AGENTS.md`
- `src/backend/zuno/AGENTS.md`
- `.agent/references/runtime-call-chain.md`
- `.agent/references/code-map.md`
- `.agent/programs/PHASE01_repo-layout-audit.md`
- `.agent/programs/PHASE03_backend-six-layer-migration-plan.md`
- `docs/architecture/target-architecture.md`

## 任务

只读审计 `src/backend` 和 `src/backend/zuno` 的目录结构。

目标六层是：

```text
src/backend/zuno/
  api/
  agent/
  memory/
  capability/
  knowledge/
  platform/
```

重点看：

- `src/backend` 顶层除 `zuno/` 外的目录是否必要，例如 `fastapi_jwt_auth`。
- `src/backend/zuno` 当前目录如何映射到六层目标。
- 哪些目录可以先做 facade / re-export，哪些需要后续物理迁移。
- 哪些移动会影响 public API、imports、tests、runtime。
- 每层应该跑哪些 focused tests。

## 禁止

- 不改代码。
- 不移动文件。
- 不改 import。
- 不提交。
- 不推送。

## 输出

返回：

1. cwd / branch / HEAD / `git status --short --branch`
2. 映射表：

```text
current path | target layer | move type | public API risk | tests | rollback
```

3. `src/backend` 顶层清理建议
4. 六层迁移顺序建议
5. 必须由主线程统一处理的高冲突文件
