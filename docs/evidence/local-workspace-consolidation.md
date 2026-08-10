# Local Workspace Consolidation 注册清单

状态：CLOSED

收口日期：2026-08-10

冻结基线：20d50b60df6f1c654c77cf9c5bc2c6375e3bcd00

closure_sha：9752a3482a50aed85172e3b6d8318ab1efcc2d4a

本清单记录本机工程工作区治理的最终收口证据。不激活 PROGRAM01 Real Unified Runtime Cutover，不进入 Architecture Deep Review，不改变业务 Runtime。Repository Closure 仍为 CLOSED。

## 一、收口原则

本轮目标是消灭未知状态，不是追求最少 worktree、branch 或 stash。任何 dirty 内容、未进入 main 的 commit、migration、用户文件、benchmark evidence 和 thread prompt，在没有可证明的丢弃依据前均保留。

对象处置采用以下分类：

- ACTIVE_KEEP：当前主工作区，继续作为唯一 active workspace。
- HISTORY_KEEP：内容已进入 main 历史；branch 保留为历史索引，不参与当前开发。
- ARCHIVE_AND_REMOVE_WORKTREE：clean 且 HEAD 已进入 main；只注销 worktree，不删除 branch。
- PRESERVE_UNMERGED：存在 main 没有的独立 commit，保留 branch/worktree。
- PRESERVE_DIRTY：存在未提交修改或未跟踪资产，保留原状。
- OWNER_REQUIRED：明确保留对象，未来仍需 owner 决定，不执行破坏性操作。

## 二、Worktree Registry

### 收口闸门

| 指标 | 收口前 | 收口后 | 结论 |
|---|---:|---:|---|
| 注册 worktree | 47 | 33 | 14 个已证明安全注销 |
| ACTIVE_KEEP 主工作区 | 1 | 1 | 保留 |
| PRESERVE_DIRTY | 7 | 7 | 全部保留，未 reset/clean |
| clean、未合并 worktree | 25 | 25 | 全部保留 |
| UNKNOWN worktree | 2 | 0 | 两个 detached worktree 已证明可归档并注销 |
| stale registration | 0 | 0 | git worktree prune --dry-run 无输出 |

14 个已注销 worktree 的共同证据是：路径存在、已注册、工作区 clean、HEAD 是当前 main 的祖先；其中 12 个是 clean branch worktree，2 个是 clean detached worktree。对应本地 branch 全部保留，未执行 branch 删除。其 disposition 为 ARCHIVE_AND_REMOVE_WORKTREE。

### Dirty worktree：全部 PRESERVE_DIRTY

这些对象不再处于未知状态，而是明确归类为“保留原状、等待未来 owner review”。本轮不对它们执行 reset、clean、remove、prune 或 stash 覆盖。

| Path | Branch / HEAD | Tracked | Untracked | 内容摘要 | Disposition |
|---|---|---:|---:|---|---|
| C:\Users\Administrator\.codex\worktrees\c395\Zuno | detached / 688a50fa5730f8815b2f09050f01eeb42633ae1d | 414 | 0 | PHASE01 implementer prompts；tracked diff 为整批内容变化，不能按 line-ending 推断可丢弃 | PRESERVE_DIRTY |
| F:\agent_project\Zuno\.claude\worktrees\deepseek-phase22-cc-bc | claude/deepseek-phase22-cc-bc / 87f6eeed994d1db28f25ad916e052b3a3cd00992 | 0 | 6 | synthetic benchmark 产物、evidence 和 .hf-cache | PRESERVE_DIRTY |
| F:\agent_project\Zuno\.claude\worktrees\deepseek-phase22-workspace-agent-cutover | claude/deepseek-phase22-workspace-agent-cutover / 242d587c07dc8842d6e6581749caaffe1cda0711 | 0 | 1 | 未跟踪 .claude/，不证明可删除 | PRESERVE_DIRTY |
| F:\agent_project\Zuno-worktrees\phase22-minimax2-audit | detached / 2582f0cc8c258d82cf69b32dd8c6654eab5986e9 | 254 | 0 | 审计现场 tracked 修改；即使表现为批量换行变化也保留 | PRESERVE_DIRTY |
| F:\agent_project\Zuno-worktrees\phase22-owner-facts-postgres | claude/minimax-phase22-owner-facts-postgres / d588889b85f8ff4c4f7fc0c3515791a97d1e7a17 | 9 | 0 | owner-facts、Postgres migration、security/runtime 修改 | PRESERVE_DIRTY |
| F:\agent_project\Zuno-worktrees\phase22-post-integration-closure | claude/minimax-phase22-post-integration-closure / 3d1f5318f9017ec8a8d86aafb1a5ac59f928a0c8 | 2 | 1 | legacy cutover verifier、fixture 和验证修改 | PRESERVE_DIRTY |
| F:\internship-work\resume project\worktrees\codex-gpt5-phase22-canonical-ingestion-001 | codex/phase22-canonical-ingestion-codex-gpt5-controller-001 / 0752e59579400aa6b71c99b00d5dd6db6af3b3be | 0 | 3 | canonical ingestion thread prompt | PRESERVE_DIRTY |

### Clean、未合并 worktree：全部 PRESERVE_UNMERGED

以下 25 个 worktree clean，但 HEAD 含有 main 没有的独立提交；本轮不注销：

- F:\agent_project\minimax4-phase22-snapshot-worktree
- F:\agent_project\minimax4-phase22-worktree
- F:\agent_project\Zuno\.claude\worktrees\claude-deepseek-graphrag-evidence-arch
- F:\agent_project\Zuno\.claude\worktrees\deepseek1-b12
- F:\agent_project\Zuno\.claude\worktrees\deepseek2-phase22
- F:\agent_project\Zuno\.claude\worktrees\minimax2-phase22-cc-d
- F:\agent_project\zuno-minimax1-cc-a
- F:\agent_project\Zuno-minimax3-phase22-canonical-hash-scope
- F:\agent_project\Zuno-minimax3-phase22-cc-d
- F:\agent_project\Zuno-worktrees\codex-phase22-real-synthetic-benchmark-readiness
- F:\agent_project\Zuno-worktrees\phase22-minimax2-hardening
- F:\agent_project\Zuno-worktrees\phase22-repository-gate-repair
- F:\internship-work\resume project\worktrees\cc-ds-phase22-runtime-three-index-b
- F:\internship-work\resume project\worktrees\cc-mm-phase22-runtime-live-corpus-a
- F:\internship-work\resume project\worktrees\cc-mm-phase22-runtime-live-env-c
- F:\internship-work\resume project\worktrees\claude-deepseek-a
- F:\internship-work\resume project\worktrees\claude-deepseek-b
- F:\internship-work\resume project\worktrees\claude-deepseek-cc-ds-1
- F:\internship-work\resume project\worktrees\claude-deepseek-probe
- F:\internship-work\resume project\worktrees\claude-minimax-a
- F:\internship-work\resume project\worktrees\claude-minimax-b
- F:\internship-work\resume project\worktrees\claude-minimax-cc-mm-1
- F:\internship-work\resume project\worktrees\claude-minimax-cc-mm-2
- F:\internship-work\resume project\worktrees\claude-minimax-probe
- F:\internship-work\resume project\worktrees\codex-gpt5-phase22-canonical-controller-001

## 三、Branch Registry

- 本地 branch：96；删除 0，全部 HISTORY_KEEP 或 PRESERVE_UNMERGED。
- 收口后绑定 worktree 的 branch：31（含 main）；其中 main 为 ACTIVE_KEEP，其余 30 个保持现状。
- 未绑定 local branch：65。
- 未绑定 branch 中，52 个 tip 已进入 main 历史，分类为 HISTORY_KEEP；13 个仍有独立提交，分类为 PRESERVE_UNMERGED。
- remote ref：112；本轮不执行 remote prune 或远端 branch 删除。

### 未绑定 branch 的分类规则

每个 branch 均以 merge-base / --is-ancestor 和提交谱系分类：已进入 main 的 branch 保留为 HISTORY_KEEP，未进入 main 的 branch 保留为 PRESERVE_UNMERGED。没有 branch 被标记为 DELETE_SAFE，也没有用磁盘占用或 branch 数量作为删除理由。

收口前的 40 个未绑定历史 branch，加上本轮注销 worktree 后释放的 12 个已合入 branch，共 52 个 HISTORY_KEEP。原先的 13 个独立 branch 全部继续为 PRESERVE_UNMERGED：

- agent/deepseek/phase22-benchmark-runtime-pr97
- claude/deepseek-phase22-retire-phase08-legacy-cutover
- claude/minimax-phase22-legacy-cutover-audit
- claude/minimax-phase22-legacy-cutover-audit-v2
- claude/minimax-phase22-legacy-cutover-audit-v2-fixed
- claude/minimax-phase22-nonbackend-legacy-cleanup
- claude-minimax/phase22-synthetic-benchmark
- codex/goal05-phase22-chunk-projection-cleanup
- codex/goal05-phase22-completion-rollback-retirement
- codex/goal05-phase22-removal-ledger-sync
- codex/phase22-final-closure
- codex/zuno-worktree-workflow-docs
- integration/goal01-control-plane-model-ingestion

其中 codex/phase22-closure-audit 仍保留其现有 remote tracking，不执行删除或 remote prune。

## 四、Stash Registry

4 个 stash 全部保留；drop 0：

| Ref | SHA | 文件数 | 来源 / purpose | Disposition |
|---|---|---:|---|---|
| stash@{0} | 690318a59313c873cafb6e15dc000dd589b2ca74 | 65 | codex/phase22-closure-audit；preexisting user change before phase22 closure | OWNER_REQUIRED |
| stash@{1} | 23329a6458ff746b3dbee98e48ad320120ca6d87 | 1 | main；minimax1 .claude gitignore addition | OWNER_REQUIRED |
| stash@{2} | 67f99f71f920b78b5564283774bdc27020e15b6a | 6 | canonical ingestion worker runtime scope quarantine | OWNER_REQUIRED |
| stash@{3} | b7bce1a7ca644ca5da8b18320be942cd2584caf9 | 44 | main；pre-phase-split safety snapshot | OWNER_REQUIRED |

OWNER_REQUIRED 在 stash 语境表示“明确知道对象是什么，但未来使用 owner 仍需决定”；它不是未知对象，也不是本轮删除许可。本轮未执行 git stash clear 或 git stash drop。

## 五、本地产物与根目录 Registry

| 路径 | 收口事实 | Disposition |
|---|---|---|
| runtime-tenant.db、runtime-workspace.db | 已删除；删除前确认只有空 schema；根因已修复为 tmp_path，测试会话级闸门阻止 root SQLite 回归 | DELETE_SAFE |
| F:\agent_project\Zuno\.local | 其它本地 eval dataset / diagnostics / reports 保留；本轮不做泛化清理 | HISTORY_KEEP |
| F:\agent_project\Zuno\.local\.local\direct-manifest-test | 6 个历史 placeholder 已确认无精确代码/fixture/launcher 引用后删除；空 .local\.local 已删除 | DELETE_SAFE |
| F:\agent_project\Zuno\.claude\worktrees | Git worktree 生命周期管理；dirty 资产仍保留 | PRESERVE_DIRTY / PRESERVE_UNMERGED |
| F:\agent_project\Zuno\node_modules | 可再生依赖，本轮不处理 | HISTORY_KEEP |

### 根因修复证据

1. tests/agent/test_workspace_single_controller_cutover.py 不再在 repo-relative 路径写入 runtime-*.db，改用 pytest tmp_path。
2. tests/conftest.py 新增测试会话级 root SQLite 产物闸门；测试结束时若 root 出现 .db / .sqlite / .sqlite3，直接失败。
3. tools/evals/zuno/rag_eval/paths.py 新增 resolve_local_artifact_path()；canonical RAG Eval output root 在函数入口和 CLI 入口统一锚定到 <repo>/.local/...，不会因从 .local 启动而产生 .local/.local/...。
4. direct-manifest-test 仅作为回归测试名保留在测试代码中；历史 .local\.local 目录已清除，收口后不应重新生成。

## 六、Final Closure Gate

最终验收记录如下：

| Gate | 结果 |
|---|---|
| main == origin/main | PASS；冻结基线为 20d50b60df6f1c654c77cf9c5bc2c6375e3bcd00，收口提交后再次校验 |
| main worktree clean | PASS |
| registered worktree path integrity | PASS |
| stale worktree | 0 |
| dirty worktree disposition | 7/7 PRESERVE_DIRTY |
| UNKNOWN worktree | 0 |
| local branch classification | 96/96 已分类；删除 0 |
| stash classification | 4/4 已分类；删除 0 |
| root *.db / *.sqlite / *.sqlite3 | 0 |
| .local\.local historical placeholder | 0 |
| repo hygiene / structure / docs entrypoints | PASS |
| git diff --check | PASS |
| Program1 | NOT ACTIVATED |
| active implementation program | none |

收口指标：

~~~yaml
closure_sha: 9752a3482a50aed85172e3b6d8318ab1efcc2d4a
worktree_count_before: 47
worktree_count_after: 33
dirty_preserved_count: 7
branch_keep_count: 96
branch_deleted_count: 0
stash_keep_count: 4
stash_deleted_count: 0
unknown_count: 0
root_sqlite_count: 0
historical_local_placeholder_count: 0
~~~

因此 Local Workspace Consolidation = CLOSED。后续对 7 个 dirty worktree、13 个未合并 branch、4 个 stash 的处理应作为明确 owner 的独立任务，不再阻塞本阶段，也不得回写为“已删除”。

## 可复现命令

~~~powershell
git worktree list --porcelain
git worktree prune --dry-run
git status --short --branch
git branch --all --verbose --no-abbrev
git stash list
python -m pytest -q tests/evals/test_rag_eval_paths.py tests/evals/test_rag_eval_local_launcher.py tests/evals/test_stackless_compare_matrix.py tests/agent/test_workspace_single_controller_cutover.py::test_missing_product_tenant_context_fails_closed tests/repo/test_repo_hygiene.py -p no:cacheprovider
python -m pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_local_launcher.py tests/evals/test_stackless_compare_matrix.py tests/evals/test_rag_eval_paths.py -p no:cacheprovider
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
git diff --check
~~~
