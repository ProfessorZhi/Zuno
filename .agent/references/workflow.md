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

复杂任务先判断工作模式。挂机模式由主线程作为真正的 Codex UI 目标模式一路执行到底；多线程模式由主线程作为真正的 Codex UI 目标模式 coordinator，拆出粗粒度子线程、准备目标模式提示词、分支边界、禁止范围、验收闸门和验证命令。多线程模式下，用户在 UI 里手动创建目标模式线程；提示词目标模式不等于 Codex UI 目标模式。

线程可以常驻为“工位”，但任务隔离边界是本轮 worktree + `codex/` branch，不是线程标题。每轮任务开始前，主线程先盘点可复用 Codex 线程和 git worktree；有合适可复用线程就复用；没有合适线程才创建新线程。复用或新建线程后必须改线程标题，并确认或切换 worktree、branch、`git status --short --branch`、允许范围和禁止范围。主线程可以自己以目标模式/计划模式单干，也可以把粗粒度任务分配给常驻线程并行执行。

子线程目标模式提示词默认要求线程内开启多 agent 模式，用于提高并发；只有当任务共享文件高冲突、禁止并行或用户明确要求单线程时，才在提示词里写明禁用原因。线程内多 agent 只能在该线程的写入范围内拆独立子任务，不能让多个 agent 同时改同一批文件。

这里的多 agent 是执行工作流，不是 Zuno runtime 架构目标。近期 runtime 仍保持 Single GeneralAgent，不能因为执行并行而把产品架构写成多 Agent。

## Target Direction

PHASE03 后，长期自动化目标位置是 `tools/agent` 与 `tools/verify`，防回归测试目标位置是 `tests/agent_system`。当前 `.agent/scripts` 是过渡期保留。

目标方向是：主线程先确定执行方案。能由一个目标模式线程连续完成就使用挂机模式；能拆成粗粒度独立块就使用多线程模式。多线程模式的重点是分线程工作，不是主线程吞掉所有实现。共享文件和冲突风险高的路径由主线程收口，合并必须集中到主线程完成。线程可以常驻复用，但每轮必须换到或确认新的任务隔离边界。

## Must Preserve

- 前台文档默认中文。
- `docs/` 只放正式人类真相。
- `.agent/` 只放本地 Agent Skill System、目标设计、当前 program、模板和过渡期 verifier。
- `docs/history/` 保存旧 audit、旧 spec、旧 runbook、旧 UI 原型、旧 phase、旧 program 和被替换设计。
- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html` 是 Target / Proposed 视觉蓝图，不是 Current proof。
- 修改任务必须验证、commit、push，除非验证或 push 被阻塞。
- 两种默认工作模式是挂机模式和多线程模式；选择哪一种取决于任务能否拆成粗粒度、低冲突的独立范围。
- 常驻线程只是执行工位；每轮任务必须以 worktree + `codex/` branch 作为隔离边界。
- 多线程模式先盘点可复用 Codex 线程和 git worktree；有合适可复用线程就复用；没有合适线程才创建新线程。
- 复用或新建线程后必须改线程标题；子线程目标模式提示词默认要求线程内开启多 agent 模式。
- 多线程模式中，每个子线程都必须是真正的 Codex UI 目标模式；工具不能直接切换 UI 目标模式时，主线程只能输出 `.agent/templates/target-mode-prompt.md` 风格的提示词，并等待用户在 UI 里手动创建目标模式线程。
- 过时材料移动到 `docs/history/`；旧 audit、旧 spec、旧 runbook、旧 UI 原型和旧 phase/program 不留在前台路径。

## Before Editing

1. `git status --short --branch`
2. 读 `AGENTS.md` 和 `.agent/system.yaml`。
3. 读 `task-routing.md` 选择 route。
4. 读 Current / Target / Roadmap。
5. 读需要的 reference skills：`docs-map.md`、`code-map.md`、`verification-map.md`、`known-pitfalls.md`。
6. 如果涉及目标架构，读 `.agent/architecture/near-term/` 和 `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`。
7. 确认任务允许范围和 forbidden paths。
8. 判断使用挂机模式还是多线程模式；如果任务可以拆成粗粒度独立范围，先规划多线程：每个常驻线程绑定或切换一个本轮 worktree / `codex/` 分支、一个目标模式提示词、一个验收闸门，并由用户在 UI 里手动创建或确认真正的目标模式线程。

## Allowed Changes

- 对准任务目标的最小文档、skill、template、verifier、test 同步。
- 将过时材料移动到 `docs/history/`。
- 更新 `.agent/system.yaml` 以保持 route、docs_sync、verify 一致。
- 在多线程模式下，为多个独立线程准备粗粒度目标模式提示词、分支和验收闸门。
- 在线程内部使用多 agent 模式处理独立子任务。

## Forbidden Changes

- 不把 Target 行为写成 Current。
- 不在文档/工作流任务里修改 runtime，除非任务明确授权。
- 不提交 transient screenshot、browser snapshot、cache、local report。
- 不创建 `.agent/skills/` 或 `.agent/workflows/`。
- 不恢复旧 root-level Agent 入口。
- 不让多个线程同时编辑同一个共享文件，除非主线程明确负责最终合并。
- 不把执行工作流里的多 agent 写成 Zuno runtime 的当前架构。
- 不把提示词目标模式当成 Codex UI 目标模式。

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

### 挂机模式

1. 主线程本身必须是真正的 Codex UI 目标模式。
2. 主线程负责计划、实现、验证、提交和推送。
3. 主线程可以使用多 agent / subagent 辅助审计或实现，但目标、范围、禁止范围和验收闸门不能漂移。
4. 共享文件多、runtime 风险高、schema/API/DB 变更或用户要求一路执行时，优先使用挂机模式。

### 多线程模式

1. 主线程本身必须是真正的 Codex UI 目标模式，并负责 coordinator 工作。
2. 主线程拆出粗粒度子线程；每个线程要执行一大块互相独立的工作。
3. 主线程先盘点可复用 Codex 线程和 git worktree。
4. 有合适可复用线程就复用；没有合适线程才创建新线程。
5. 复用或新建线程后必须改线程标题，让侧边栏能看出本轮任务、phase 和职责。
6. 主线程写清每个线程的目标、允许范围、禁止范围、验收闸门和验证命令。
7. 线程可以常驻，但每轮任务必须重新确认或切换独立 worktree 和独立 `codex/` 分支。
8. 每个子线程也必须是真正的 Codex UI 目标模式；提示词目标模式不等于 Codex UI 目标模式。
9. 工具 API 不能直接打开 UI 目标模式时，主线程只输出线程提示词，等待用户在 UI 里手动创建目标模式线程，或改为挂机模式。
10. 子线程目标模式提示词默认要求线程内开启多 agent 模式；只有高冲突或用户明确要求单线程时，才在提示词中禁用并说明原因。
11. 每个线程默认可以使用多 agent 模式，但只能在自己的写入范围内协作。
12. 写入线程完成后必须提交并推送；只读审计线程返回报告和干净 `git status` 即可。主线程读取 diff、验证结果或审计证据，不只信总结。
13. 主线程按风险顺序合并，解决冲突后运行集成验证。

### Program Closure 自维护审查

每个 program 结束前必须做 workflow / docs self-review。它的目的不是多写总结，而是确认这轮暴露出的新规则、新坑和新边界已经进入正确的长期位置。

检查顺序：

1. `AGENTS.md`：全仓硬规则、工作模式、收尾规则是否需要更新。
2. `.agent/system.yaml`：route、docs_sync、verify 是否覆盖新工作流。
3. `.agent/references/`：新的 skill、lesson、pitfall、debug playbook 是否已沉淀。
4. `.agent/templates/`：是否需要新的目标模式提示词、phase 模板或 closure report 骨架。
5. `.agent/programs/`：是否只保留当前 active program，或处于明确无 active program 的等待状态。
6. `docs/history/programs/`：completed program 是否归档，旧 phase 是否离开当前前台。
7. `docs/architecture/current-architecture.md`：是否仍只描述 Current。
8. `docs/architecture/target-architecture.md`：是否需要吸收新的 Target 边界。
9. `docs/architecture/roadmap.md`：是否反映最新 program 状态。
10. verifier / tests：能机器检查的规则是否已进入脚本或 repo tests。

如果用户提醒“以后注意”，不能只留在对话里。先分类：临时提醒进入 ignored local notes；可复用经验进入 `.agent/references/known-pitfalls.md` 或对应 skill；稳定操作规则进入 `workflow.md`；任务触发规则进入 `task-routing.md`；全仓硬规则进入 `AGENTS.md`；能机器检查的规则进入 verifier/test。

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

Program closure 还必须执行一次 Program Closure 自维护审查，确认本轮新增经验没有只停留在 final answer 或聊天上下文里。

## Lessons Learned

- 修改 surface 时，测试和 verifier 是同一变更的一部分，不是事后装饰。
- 历史完成事实不能为了新叙事改写成未完成。
- 最短路径通常是更新现有 skill，而不是新建更多目录。
- 自主维护靠“提醒分类、规则沉淀、验证自动化、历史归档”，不是靠 Codex 记住上一轮对话。
