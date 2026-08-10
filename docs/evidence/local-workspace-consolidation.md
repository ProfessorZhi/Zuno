# Local Workspace Consolidation 注册清单

状态：`OPEN`

快照日期：2026-08-10

Git 基线：`main` 与 `origin/main` 当前均为 `4fe1cbb13a8c46bd796e3554455459c6ef0e15b5`。

本清单是项目级 Maintenance / Consolidation 证据，不激活 `PROGRAM01 Real Unified Runtime Cutover`，也不改变 `Repository Closure: CLOSED` 的结论。它只记录本机工程工作区治理状态。

## 一、Worktree Registry

分类采用保守语义：

- `ACTIVE`：当前主工作区或已确认仍在使用；本轮不动。
- `DIRTY_OWNER_REQUIRED`：存在未提交内容；owner 和处置方式未确认前禁止 reset、clean、remove、prune。
- `CLEAN_ARCHIVABLE_CANDIDATE`：clean 且 HEAD 已进入 `main` 历史，只是候选，尚未得到归档授权。
- `CLEAN_UNMERGED_CANDIDATE`：clean 但仍有未进入 `main` 的独立提交，不能删除。
- `UNKNOWN`：来源或用途无法从本地证据确认，默认保留。

快照结论：47 个注册 worktree 全部路径有效；`git worktree prune --dry-run` 无输出；没有 `DELETE_SAFE`。

| 分类 | 数量 | 说明 |
|---|---:|---|
| `ACTIVE` | 1 | `F:\agent_project\Zuno`，当前主工作区 |
| `DIRTY_OWNER_REQUIRED` | 7 | 外部 worktree 有未提交内容 |
| `CLEAN_ARCHIVABLE_CANDIDATE` | 12 | clean，HEAD 是 `main` 的祖先 |
| `CLEAN_UNMERGED_CANDIDATE` | 25 | clean，但有独立提交 |
| `UNKNOWN` | 2 | clean detached worktree |

### Dirty forensic inventory

以下 7 个 worktree 是本轮必须保留的 owner-required 集合。`HEAD`、变更数量和最近变更时间来自本地 Git / 文件系统快照；没有把分支名称当作 owner 证明。

| Path | Branch | HEAD | Tracked | Untracked | HEAD 已进入 main | Ahead / Behind main | 最近变更 | 建议 |
|---|---|---|---:|---:|---|---|---|---|
| `C:\Users\Administrator\.codex\worktrees\c395\Zuno` | detached | `688a50fa5730` | 414 | 0 | 是 | 0 / 987 | 2026-07-16 09:13:32 | `OWNER_REQUIRED`；保留原状 |
| `F:\agent_project\Zuno\.claude\worktrees\deepseek-phase22-cc-bc` | `claude/deepseek-phase22-cc-bc` | `87f6eeed994d` | 0 | 6 | 否 | 18 / 121 | 2026-08-03 19:17:53 | `OWNER_REQUIRED`；保留未跟踪产物 |
| `F:\agent_project\Zuno\.claude\worktrees\deepseek-phase22-workspace-agent-cutover` | `claude/deepseek-phase22-workspace-agent-cutover` | `242d587c07dc` | 0 | 1 | 是 | 0 / 104 | 2026-08-05 20:13:21 | `OWNER_REQUIRED`；不清理 `.claude/` |
| `F:\agent_project\Zuno-worktrees\phase22-minimax2-audit` | detached | `2582f0cc8c25` | 254 | 0 | 是 | 0 / 70 | 2026-08-06 13:46:19 | `OWNER_REQUIRED`；保留修改 |
| `F:\agent_project\Zuno-worktrees\phase22-owner-facts-postgres` | `claude/minimax-phase22-owner-facts-postgres` | `d588889b85f8` | 9 | 0 | 否 | 1 / 52 | 2026-08-08 13:09:51 | `OWNER_REQUIRED`；涉及 migration / owner facts，不动 |
| `F:\agent_project\Zuno-worktrees\phase22-post-integration-closure` | `claude/minimax-phase22-post-integration-closure` | `3d1f5318f901` | 2 | 1 | 否 | 4 / 55 | 2026-08-08 13:01:41 | `OWNER_REQUIRED`；保留 fixture 和验证器修改 |
| `F:\internship-work\resume project\worktrees\codex-gpt5-phase22-canonical-ingestion-001` | `codex/phase22-canonical-ingestion-codex-gpt5-controller-001` | `0752e5957940` | 0 | 3 | 否 | 8 / 122 | 2026-08-03 14:54:06 | `OWNER_REQUIRED`；保留 thread prompt |

Dirty worktree 的实际修改范围包括 retrieval / runtime 大量 tracked 修改、Phase22 owner-facts migration、legacy cutover 验证器、synthetic benchmark 产物和 thread prompt。它们不是可再生缓存，不能按目录大小处理。

### Clean candidate inventory

以下只是可供后续 owner review 的候选，不是删除授权。

`CLEAN_ARCHIVABLE_CANDIDATE`：

- `C:\Users\Administrator\.codex\worktrees\goal04-phase18\Zuno`
- `C:\Users\Administrator\.codex\worktrees\zuno-master-architecture-implementation-v1\Zuno`
- `F:\agent_project\Zuno\.claude\worktrees\claude-deepseek-phase22-backend-semantic-legacy-cleanup`
- `F:\agent_project\Zuno\.claude\worktrees\deepseek-phase22-feature-flag-cutover`
- `F:\agent_project\Zuno\.claude\worktrees\deepseek-phase22-retire-phase08-legacy-cutover`
- `F:\agent_project\Zuno-worktrees\phase22-antigravity-finalization`
- `F:\agent_project\Zuno-worktrees\phase22-approved-integration`
- `F:\agent_project\Zuno-worktrees\phase22-benchmark-readiness`
- `F:\agent_project\Zuno-worktrees\phase22-final-audit-v3`
- `F:\agent_project\Zuno-worktrees\phase22-runtime-cutover-v2`
- `F:\agent_project\Zuno-worktrees\phase22-runtime-tool-final-cutover`
- `F:\internship-work\resume project\worktrees\codex-gpt5-dispatch-docs-001`

`CLEAN_UNMERGED_CANDIDATE`：

- `F:\agent_project\minimax4-phase22-snapshot-worktree`
- `F:\agent_project\minimax4-phase22-worktree`
- `F:\agent_project\Zuno\.claude\worktrees\claude-deepseek-graphrag-evidence-arch`
- `F:\agent_project\Zuno\.claude\worktrees\deepseek1-b12`
- `F:\agent_project\Zuno\.claude\worktrees\deepseek2-phase22`
- `F:\agent_project\Zuno\.claude\worktrees\minimax2-phase22-cc-d`
- `F:\agent_project\zuno-minimax1-cc-a`
- `F:\agent_project\Zuno-minimax3-phase22-canonical-hash-scope`
- `F:\agent_project\Zuno-minimax3-phase22-cc-d`
- `F:\agent_project\Zuno-worktrees\codex-phase22-real-synthetic-benchmark-readiness`
- `F:\agent_project\Zuno-worktrees\phase22-minimax2-hardening`
- `F:\agent_project\Zuno-worktrees\phase22-repository-gate-repair`
- `F:\internship-work\resume project\worktrees\cc-ds-phase22-runtime-three-index-b`
- `F:\internship-work\resume project\worktrees\cc-mm-phase22-runtime-live-corpus-a`
- `F:\internship-work\resume project\worktrees\cc-mm-phase22-runtime-live-env-c`
- `F:\internship-work\resume project\worktrees\claude-deepseek-a`
- `F:\internship-work\resume project\worktrees\claude-deepseek-b`
- `F:\internship-work\resume project\worktrees\claude-deepseek-cc-ds-1`
- `F:\internship-work\resume project\worktrees\claude-deepseek-probe`
- `F:\internship-work\resume project\worktrees\claude-minimax-a`
- `F:\internship-work\resume project\worktrees\claude-minimax-b`
- `F:\internship-work\resume project\worktrees\claude-minimax-cc-mm-1`
- `F:\internship-work\resume project\worktrees\claude-minimax-cc-mm-2`
- `F:\internship-work\resume project\worktrees\claude-minimax-probe`
- `F:\internship-work\resume project\worktrees\codex-gpt5-phase22-canonical-controller-001`

`UNKNOWN`：

- `F:\agent_project\Zuno\.claude\worktrees\preflight-pr128`
- `F:\agent_project\Zuno-worktrees\pr129-product-wiring`

## 二、Branch / Stash Registry

### Branch 汇总

- 本地 branch：96；其中 43 个被 worktree 绑定，53 个未绑定。
- 被 worktree 绑定的 branch：14 个 tip 已在 `main` 历史，29 个仍有独立提交。
- 未绑定 branch：40 个 tip 已在 `main` 历史，13 个仍有独立提交。
- 只有 1 个 branch tip 与 `main` 完全相同；“已在 main 历史”不等于可以自动删除。
- remote branch：112；本轮不执行 `remote prune`。

当前没有 branch 被标记为 `DELETE_SAFE`。后续逐分支确认 `Program / Phase / Agent / Session / PR` 后，再分为 `KEEP`、`ARCHIVE_TAG`、`DELETE_SAFE`、`OWNER_REQUIRED` 或 `UNKNOWN`。

### Stash 清单

4 个 stash 全部保留，当前均为 `OWNER_REQUIRED`：

| Ref | SHA | 文件数 | 来源 / Purpose | 建议 |
|---|---|---:|---|---|
| `stash@{0}` | `690318a59313c873cafb6e15dc000dd589b2ca74` | 65 | `codex/phase22-closure-audit`；preexisting user change before phase22 closure | 保留，确认归档前不得 drop |
| `stash@{1}` | `23329a6458ff746b3dbee98e48ad320120ca6d87` | 1 | `main`；minimax1 `.claude` gitignore addition | 保留，确认是否已进入 main |
| `stash@{2}` | `67f99f71f920b78b5564283774bdc27020e15b6a` | 6 | canonical ingestion worker runtime scope quarantine | 保留，确认与 Phase22 ingestion 的关系 |
| `stash@{3}` | `b7bce1a7ca644ca5da8b18320be942cd2584caf9` | 44 | `main`；pre-phase-split safety snapshot | 保留，属于历史安全快照候选 |

本轮未执行 `git stash clear`、`git branch --merged | ... | delete` 或任何 stash / branch 批量清理。

## 三、本地产物与根目录 Registry

| 路径 | 当前事实 | 处置建议 |
|---|---|---|
| `runtime-tenant.db`、`runtime-workspace.db` | 已删除；删除前确认只有 schema、所有表 0 行 | 根因已修复为 `tmp_path`；测试会话结束时有 SQLite root-artifact 闸门 |
| `F:\agent_project\Zuno\.local` | 395 文件、98 目录、约 85 MB；主要是 eval dataset / diagnostics / reports | 保留可复现本地证据；后续按 active、历史、重复产物分类 |
| `F:\agent_project\Zuno\.local\.local\direct-manifest-test` | 6 个历史 placeholder 文件，最后修改 2026-07-30；修复后未新增 | 不搬运；确认无引用后再作为精确清理候选 |
| `F:\agent_project\Zuno\.claude\worktrees` | 10 个真实注册 worktree，约 600 MB；其中 2 个 dirty | 必须通过 Git worktree 生命周期处理，不能当 cache 删除 |
| `F:\agent_project\Zuno\node_modules` | 15502 文件、1953 目录、约 411 MB | 正常可再生依赖，暂不处理 |
| `F:\agent_project\Zuno\.qoder` | 75 文件、38 目录、约 1.6 MB | 仅在确认 Qoder 不再使用后清理 |
| `.pytest_cache`、`.test-tmp`、`.agents` | 可再生；当前 `.test-tmp` / `.agents` 无文件 | 低优先级精确清理候选 |
| `.agent/local`、`.venv`、根 `tmp` | 当前不存在 | 无动作 |

### 两个根因修复

1. `tests/agent/test_workspace_single_controller_cutover.py` 不再使用 repo-relative `Path("runtime-*.db")`，改为 pytest `tmp_path`。
2. 新增测试会话级 root SQLite 产物闸门；测试结束后若 root 出现 `.db` / `.sqlite` / `.sqlite3`，直接失败。
3. 新增 `resolve_local_artifact_path()`，所有 canonical RAG Eval output root 在函数入口和 CLI 入口统一锚定：显式 `.local/...` 只解析为 `<repo>/.local/...`，不会因从 `.local` 启动而产生 `.local/.local/...`。
4. 现有 `.local/.local` 是历史产物，不是本轮修复后重新生成的证据；本轮不搬移它。

## 四、Consolidation Gate

已满足：

- 所有 47 个 registered worktree 路径有效。
- `git worktree prune --dry-run` 无 stale registration。
- root SQLite 文件为 0。
- 相关测试通过，且测试后 root SQLite 文件仍为 0。
- `.local/.local` 现有历史文件未新增。
- repo hygiene、repo structure、documentation entrypoint 和 `git diff --check` 验证保持可执行。

仍未满足：

- 7 个 dirty worktree 尚无确认 owner / disposition。
- 53 个未绑定本地 branch 尚未完成逐项归属。
- 4 个 stash 尚未完成 owner / purpose / asset review。
- 2 个 clean detached worktree 仍是 `UNKNOWN`。

因此 `Local Workspace Consolidation` 仍为 `OPEN`，但已经从“不可解释的本地现场”收敛为可执行的 owner review 队列。下一步应先处理 dirty worktree 和 stash owner，不得激活 Program1，也不得开始架构 deep review。

## 可复现命令

```powershell
git worktree list --porcelain
git worktree prune --dry-run
git status --short --branch
git branch --all --verbose --no-abbrev
git stash list
python -m pytest -q tests/evals/test_rag_eval_paths.py tests/evals/test_rag_eval_local_launcher.py tests/evals/test_stackless_compare_matrix.py tests/agent/test_workspace_single_controller_cutover.py::test_missing_product_tenant_context_fails_closed tests/repo/test_repo_hygiene.py -p no:cacheprovider
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```
