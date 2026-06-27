# 工作流 Skill

## When To Use

当任务需要修改 docs、`.agent`、history、验证器、测试，或需要收尾 commit/push 时使用本 skill。

## Mental Model

```text
truth first
  -> scope
  -> minimal edit
  -> sync maps/verifiers/tests
  -> focused verification
  -> commit and push
```

Zuno 工作流不是模板化搬运。每一步都要能回答“这个文件为什么要改、它保护什么边界、验证证明了什么”。

本文负责具体执行步骤、停止条件、验证和收尾规则；任务先由 `task-routing.md` 分流，再进入本文执行。

## Current Truth

Zuno 的本地工作流由以下表面共同组成：

- `AGENTS.md`：仓库唯一 bootloader。
- `.agent/system.yaml`：路径到 skills、templates、docs_sync、verify 的机器可读路由。
- `.agent/references/`：本地项目 skills / lessons / playbooks。
- `.agent/templates/`：只保存执行骨架。
- `.agent/programs/`：当前 active phase 计划。
- `docs/`：正式人类文档真相。

前台文档默认使用中文；历史档案可以保留原文。

复杂任务默认优先考虑多线程 / 多 agent 协作。主线程只做 coordinator；每个线程使用独立 `codex/` 分支、明确写入范围和目标模式提示词，线程内可以按范围开启多 agent 模式。

这里的多 agent 是执行工作流，不是 Zuno runtime 架构目标。近期 runtime 仍保持 Single GeneralAgent，不能因为执行并行而把产品架构写成多 Agent。

## Target Direction

PHASE03 后，长期自动化目标位置是 `tools/agent` 与 `tools/verify`，防回归测试目标位置是 `tests/agent_system`。当前 `.agent/scripts` 是过渡期保留。

并行执行的目标方向是：能拆就拆、能并行就并行、每个线程都是目标模式，但合并必须集中到主线程完成。共享文件和冲突风险高的路径由主线程收口。

## Must Preserve

- 前台文档默认中文。
- `docs/` 只放正式人类真相。
- `.agent/` 只放本地 Agent Skill System、目标设计、当前 program、模板和过渡期 verifier。
- `docs/history/` 保存旧 audit、旧 spec、旧 runbook、旧 UI 原型、旧 phase、旧 program 和被替换设计。
- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html` 是 Target / Proposed 视觉蓝图，不是 Current proof。
- 修改任务必须验证、commit、push，除非验证或 push 被阻塞。
- 多线程 / 多 agent 是默认可用工作方式；如果任务能拆成独立范围，优先使用。
- 每个线程都必须是目标模式；优先打开 Codex UI 目标模式，工具不能直接切换时必须使用 `.agent/templates/target-mode-prompt.md` 写清目标、范围、验收和验证。
- 过时材料移动到 `docs/history/`；旧 audit、旧 spec、旧 runbook、旧 UI 原型和旧 phase/program 不留在前台路径。

## Before Editing

1. `git status --short --branch`
2. 读 `AGENTS.md` 和 `.agent/system.yaml`。
3. 读 `task-routing.md` 选择 route。
4. 读 Current / Target / Roadmap。
5. 读需要的 reference skills：`docs-map.md`、`code-map.md`、`verification-map.md`、`known-pitfalls.md`。
6. 如果涉及目标架构，读 `.agent/architecture/near-term/` 和 `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`。
7. 确认任务允许范围和 forbidden paths。
8. 如果任务可以拆成独立范围，先规划多线程：每个线程一个分支、一个目标模式提示词、一个验收闸门。

## Allowed Changes

- 对准任务目标的最小文档、skill、template、verifier、test 同步。
- 将过时材料移动到 `docs/history/`。
- 更新 `.agent/system.yaml` 以保持 route、docs_sync、verify 一致。
- 启动多个独立线程或子 agent 处理互不重叠的范围。
- 在线程内部使用多 agent 模式处理独立子任务。

## Forbidden Changes

- 不把 Target 行为写成 Current。
- 不在文档/工作流任务里修改 runtime，除非任务明确授权。
- 不提交 transient screenshot、browser snapshot、cache、local report。
- 不创建 `.agent/skills/` 或 `.agent/workflows/`。
- 不恢复旧 root-level Agent 入口。
- 不让多个线程同时编辑同一个共享文件，除非主线程明确负责最终合并。
- 不把执行工作流里的多 agent 写成 Zuno runtime 的当前架构。

## Common Failure Patterns

- 只改一个入口，漏掉 docs-map、current-program、tests 或 verifier。
- 验证失败后先补丁绕过，而不是定位路径、词条或边界根因。
- 把历史材料从前台删除但没有归档。
- 模板和 references 同时保存项目知识，造成双真相。

## Debug Playbooks

### 文档漂移

1. 搜索被改术语的所有前台命中。
2. 分类为 Current、Target、History、Compatibility。
3. 只同步 active surfaces；历史档案保留原文。
4. 更新 verifier/test 的预期词条。

### 仓库卫生

1. `git status --short`
2. 搜索 imports、links、routes、scripts、evals、docs、tests。
3. 确认移动目标仍在仓库内。
4. 移动或归档。
5. 同步 docs、`.agent`、verifier、test。
6. 运行 `git diff --check` 和相关 verifier/test。

### 架构重构

1. 明确 Current / Foundation / Target / Future / History。
2. 目标设计放 `.agent/architecture/near-term/`。
3. 正式结论放 `docs/architecture/`。
4. 执行计划放 `.agent/programs/` 根层。
5. 旧计划和旧设计归档到 `docs/history/`。

### 多线程目标模式

1. 主线程拆分任务，写清每个线程的目标、允许范围、禁止范围、验收闸门和验证命令。
2. 每个线程使用独立 `codex/` 分支；能打开 Codex UI 目标模式时必须打开。
3. 如果工具 API 不能直接打开 UI 目标模式，线程提示词必须显式使用目标模式结构。
4. 每个线程默认可以使用多 agent 模式，但只能在自己的写入范围内协作。
5. 线程完成后必须提交并推送；主线程读取 diff 和验证结果，不只信总结。
6. 主线程按风险顺序合并，解决冲突后运行集成验证。

## Focused Tests

文档 / Agent workflow 最小基线：

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

较大收口可追加：

```powershell
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```

## Docs Sync

每次 docs / `.agent` 修改都检查是否需要同步：

- `AGENTS.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/README.md`
- `.agent/references/current-program.md`
- `.agent/references/docs-map.md`
- `.agent/references/task-routing.md`
- `.agent/references/verification-map.md`
- `.agent/templates/README.md`
- `docs/architecture/README.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`
- verifier scripts and repo tests

## Lessons Learned

- 修改 surface 时，测试和 verifier 是同一变更的一部分，不是事后装饰。
- 历史完成事实不能为了新叙事改写成未完成。
- 最短路径通常是更新现有 skill，而不是新建更多目录。
