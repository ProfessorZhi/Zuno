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

Claude Code worker 可以作为多线程模式的执行工位使用。每个 worker 必须绑定唯一身份：

```text
agent=<coordinator 或 worker 名>
model=<canonical model 或 launcher>
worker=<短编号，例如 minimax-a / deepseek-b / codex-gpt5-001>
session_id=<Claude Code / Codex session id>
worktree=<绝对路径>
branch=<codex/...>
```

worker 的 branch、commit、evidence 文件、PR 标题和 PR 描述都必须带身份标签。默认命名：

- worktree：`F:\internship-work\resume project\worktrees\<agent>-<model>-<worker>`
- branch：`codex/<task>-<agent>-<model>-<worker>`
- evidence：`docs/evidence/<task>-<agent>-<model>-<worker>.md`
- commit：`<type>(<area>): <task> [agent=<agent> model=<model> worker=<worker>]`
- PR title：`<task> [agent=<agent> model=<model> worker=<worker>]`

worker 完成后只能提交自己的 branch，并返回身份、session、commit、验证、风险、时间和成本回执。push / PR 可以由 worker 执行，也可以由主线程执行；合并只能由主线程 coordinator 完成。coordinator 必须读取 diff、验证结果和 evidence，不只信 worker 总结。通过的文件或 commit 才能合并回 Zuno 目标分支；未通过的 worker branch 保持隔离或删除。

Codex coordinator 调度 Claude Code worker 的标准生命周期：

1. `fetch origin main --prune`，记录当前 `origin/main` SHA，确认主仓库只作为最终集成仓库。
2. 按任务性质分流：简单、大量、重复、低冲突任务派 worker；跨模块架构、安全、并发、恢复、幂等、合并和 production readiness 判断由 coordinator 保留。
3. 为每个 worker 创建或复用独立 worktree、独立 `codex/` branch 和唯一身份；worktree 目录必须位于 `F:\internship-work\resume project\worktrees\`。
4. 用 prompt 文件启动 `claude-<provider> --output-format stream-json --verbose`，不要把多行 prompt、JSON 或 commit message 直接嵌入多层 PowerShell 参数。
5. 从 final `type=result` 事件保存 Claude Code 生成的 `session_id`、token、cost 和 duration；后续同一 PR / handoff 用 `--resume <session_id>` 复用，而不是手写或猜测 session id。
6. worker 完成后提交自己的 branch，返回 handoff 回执；同一 PR 的多次 resume、验证重跑和补丁追加到同一 worker cost ledger。
7. coordinator 审查 `git diff origin/main..HEAD`、commit、evidence、测试输出、风险声明和成本账，并给出评分。
8. 评分通过且无阻断项时，coordinator 才能 push / 开 PR / 合并；评分不足时要求 rework、拆小重派、换模型或拒绝。
9. 合并前确认目标分支已包含最新 main，不覆盖并发修改；合并后运行集成验证并 push。
10. 验证和 push 完成后，临时 worktree 可以删除；被拒绝或未完成的 worktree 保持隔离，直到明确处理。

Coordinator 审查评分按 100 分执行，并在 PR / closure 报告里留下结论：

```text
identity and traceability: 10
scope containment and no unrelated churn: 15
requirement fit and correctness: 20
tests and reproducible verification: 15
evidence quality and honesty: 10
security / approval / audit / no bypass: 15
cost and time efficiency: 5
integration risk and merge readiness: 10
```

默认判定：

- `>= 85`：可以接受，但仍需 coordinator 合并前验证。
- `70 - 84`：request changes 或拆小后重派。
- `< 70`：reject / reassign。
- 任一安全门绕过、Target 写成 Current、伪造测试、覆盖并发修改、缺身份标签、缺可复现 evidence，直接 block，不受总分抵消。

时间和成本统计采用双账：

- API 成本账：记录 `stream-json --verbose` 返回的 `total_cost_usd`、`modelUsage.*.costUSD`、`input_tokens`、`cache_read_input_tokens`、`cache_creation_input_tokens`、`output_tokens`、`duration_ms`、`duration_api_ms` 和 `session_id`。这是按当时 API token 价格估算的成本。
- 平台额度账：记录 provider 后台实际扣减口径，例如 `token`、`request`、`percent`、`credit` 或 `unknown`。当无法从平台后台读到实际扣减时，不能把 API 成本账说成真实平台扣费；只标为 `provider_quota_basis=unknown` 或人工核对。

成本和耗时默认按“单个 agent 的一次 PR / handoff”统计，不按一轮聊天统计。一个 PR 里如果有多次 Claude Code resume、补丁、验证或重跑，必须汇总到该 PR 的 worker cost ledger；一轮对话内多个 worker / 多个 PR 要分别列账，再给 coordinator 总计。

调度策略以开发速度和额度成本平衡为目标：

- Claude Code `claude-minimax` / `claude-deepseek` 优先处理简单、大量、重复、低架构判断的工作，例如批量文档同步、证据表格整理、脚本输出归档、下载依赖、环境探测、格式修复、重复测试运行、低风险搬运和候选 diff 初稿。
- Codex / coordinator 优先处理复杂架构判断、跨模块设计、失败根因定位、高风险 runtime 改动、安全边界、并发/幂等/恢复语义、最终 review、合并顺序、冲突解决和集成验证。
- Claude Code worker 解决不了时，先返回 blocker、命令、日志和已尝试路径；coordinator 再决定是指导 worker 继续、换模型、拆小任务，还是自己接手。
- 下载、Docker、依赖安装、镜像拉取、长耗时重复命令可以先派给 Claude Code worker 试跑；涉及凭据、宿主机破坏性清理、生产 secret、强制覆盖和无法回滚的操作必须由 coordinator 审查后执行。

## Target Direction

PHASE03 后，长期自动化目标位置是 `tools/agent` 与 `tools/verify`，防回归测试目标位置是 `tests/agent_system`。当前 `.agent/scripts` 是过渡期保留。

目标方向是：主线程先确定执行方案。能由一个目标模式线程连续完成就使用挂机模式；能拆成粗粒度独立块就使用多线程模式。多线程模式的重点是分线程工作，不是主线程吞掉所有实现。共享文件和冲突风险高的路径由主线程收口，合并必须集中到主线程完成。线程可以常驻复用，但每轮必须换到或确认新的任务隔离边界。

## Must Preserve

- 前台文档默认中文。
- 项目根目录保持干净，只放稳定项目入口和配置；临时截图、浏览器截图、PDF 预览、测试产物、本地报告和缓存必须放入 `.local/`、`tmp/`、受控 reports 路径或正式 docs assets。
- `docs/` 只放正式人类真相。
- `.agent/` 只放本地 Agent Skill System、目标设计、当前 program、模板和过渡期 verifier。
- `docs/history/` 保存旧 audit、旧 spec、旧 runbook、旧 UI 原型、旧 phase、旧 program 和被替换设计。
- `docs/architecture/` 是唯一正式总架构文档源；`.agent/` 不保存 architecture/module 正文镜像。
- 修改任务必须验证、commit、push，除非验证或 push 被阻塞。
- 两种默认工作模式是挂机模式和多线程模式；选择哪一种取决于任务能否拆成粗粒度、低冲突的独立范围。
- 常驻线程只是执行工位；每轮任务必须以 worktree + `codex/` branch 作为隔离边界。
- 多线程模式先盘点可复用 Codex 线程和 git worktree；有合适可复用线程就复用；没有合适线程才创建新线程。
- 复用或新建线程后必须改线程标题；子线程目标模式提示词默认要求线程内开启多 agent 模式。
- 每个 Claude Code worker / Codex 子线程都必须有唯一 `agent + model + worker` 身份，并把身份写入 branch、commit、evidence、PR 标题和 PR 描述。
- 每个 worker 必须返回时间和成本回执；API token 成本账与平台额度账分开记录。
- 成本和时间统计以每个 agent 的一次 PR / handoff 为基本单位，不以一轮对话为基本单位。
- 简单、大量、重复、下载/环境/格式类任务优先交给 Claude Code worker；Codex coordinator 保留给复杂判断、规划、review、合并和高风险修复。
- 主线程 coordinator 负责最终审查、合并、集成验证和 push；worker 不得把自己的完成总结当作合并依据。
- 多线程模式中，每个子线程都必须是真正的 Codex UI 目标模式；工具不能直接切换 UI 目标模式时，主线程只能输出 `.agent/templates/target-mode-prompt.md` 风格的提示词，并等待用户在 UI 里手动创建目标模式线程。
- 过时材料移动到 `docs/history/`；旧 audit、旧 spec、旧 runbook、旧 UI 原型和旧 phase/program 不留在前台路径。

## Before Editing

1. `git status --short --branch`
2. 读 `AGENTS.md` 和 `.agent/system.yaml`。
3. 读 `task-routing.md` 选择 route。
4. 架构任务先读 `docs/architecture/architecture.md`、`architecture-views.md` 和 `architecture.html`。
5. 读 Current / Target / Roadmap。
6. 读需要的 reference skills：`docs-map.md`、`code-map.md`、`verification-map.md`、`known-pitfalls.md`。
7. 如果涉及目标架构，只读 `docs/` 正式架构源和明确引用的历史 evidence；不要恢复 `.agent/architecture/` 镜像。
8. 确认任务允许范围和 forbidden paths。
9. 判断使用挂机模式还是多线程模式；如果任务可以拆成粗粒度独立范围，先规划多线程：每个常驻线程绑定或切换一个本轮 worktree / `codex/` 分支、一个目标模式提示词、一个验收闸门，并由用户在 UI 里手动创建或确认真正的目标模式线程。
10. 如果使用 Claude Code worker，先写明 `agent`、`model`、`worker`、`session_id` 获取方式、worktree、branch、PR 标题格式、验证命令、成本预算和回执字段。
11. 分配任务时先区分“重复执行型”和“复杂判断型”：重复执行型默认派 Claude Code worker，复杂判断型默认由 coordinator 亲自做或先拆解后派发。
12. 分配给 Claude Code worker 前，先写清本次 PR / handoff 的评分标准、阻断项、允许合并条件和 session resume 规则。

## Allowed Changes

- 对准任务目标的最小文档、skill、template、verifier、test 同步。
- 将过时材料移动到 `docs/history/`。
- 更新 `.agent/system.yaml` 以保持 route、docs_sync、verify 一致。
- 在多线程模式下，为多个独立线程准备粗粒度目标模式提示词、分支和验收闸门。
- 在线程内部使用多 agent 模式处理独立子任务。
- 为 Claude Code worker 追加身份、成本、时间和 PR handoff 回执字段。
- 把简单重复任务拆给 Claude Code worker，把复杂判断、最终集成和合并留给 coordinator。

## Forbidden Changes

- 不把 Target 行为写成 Current。
- 不在文档/工作流任务里修改 runtime，除非任务明确授权。
- 不提交 transient screenshot、browser snapshot、cache、local report。
- 不在项目根目录遗留临时图片、截图、PDF 预览、测试报告或导出物。
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
- 在错误 workspace 落文件，导致 main 和 worktree 产生分叉。
- 用嵌套 PowerShell 直接透传多行 prompt、JSON 或带引号参数，导致参数被二次解析。
- Claude Code worker prompt 里嵌套引号，导致 `git commit -m` 被截断成无信息标题。
- 只记录 `total_cost_usd`，却没有说明它是 API 估算账，不等于平台后台实际扣费或百分比额度。
- worker 提交了 commit 或 PR，但没有在标题、描述、evidence 中写清 `agent + model + worker`，导致后续审查和成本归因断裂。
- 把一轮对话的总 token / cost 当成单个 agent PR 成本，导致无法判断哪个 worker、哪个 PR、哪类任务消耗最高。
- 为了省 coordinator token 把复杂架构判断直接外包给低成本 worker，最后产生返工和更高总成本。
- 测试时没隔离 PATH，真实 launcher 冒出来，假 runner 结果失真。

## Debug Playbooks

### 文档漂移

1. 搜索被改术语的所有前台命中。
2. 分类为 Current、Target、History、Compatibility。
3. 只同步 active surfaces；历史档案保留原文。
4. 更新 verifier/test 的预期词条。

### 仓库卫生

1. `git status --short`
2. 检查根目录是否出现临时图片、截图、PDF 预览、测试报告、缓存或导出物。
3. 搜索 imports、links、routes、scripts、evals、docs、tests。
4. 确认移动目标仍在仓库内。
5. 移动、归档或删除本轮生成物。
6. 同步 docs、`.agent`、verifier、test。
7. 运行 `git diff --check` 和相关 verifier/test。

### 命令行安全

1. 先确认 `Get-Location` 和 `git rev-parse --show-toplevel`，再改文件。
2. 读写仓库文件优先用绝对路径和 `-LiteralPath`，不要依赖当前目录猜测。
3. 结构化输入先写文件，再让脚本读文件；不要把多行 prompt 或 JSON 直接塞进会再次解析的命令行。
4. 调试 worker / launcher / metrics 时，在测试里隔离 `PATH`，只保留测试桩、`git` 和 `powershell`。
5. 如果发现文件落到错误 workspace，先停，再核对 worktree、branch 和当前目录。
6. Claude Code worker prompt 需要包含 commit message 时，优先把完整提示词写入临时 prompt 文件再传入，或避免在 prompt 内嵌套会被 shell 二次解析的引号。

### Claude Code worker dispatch

1. coordinator 先 fetch `origin/main`，记录基线 SHA。
2. 每个 worker 使用独立 worktree 和 `codex/` branch；目录放在 `F:\internship-work\resume project\worktrees\` 下。
3. 每个 worker 名称必须唯一，并写成 `agent + model + worker`，例如 `claude-minimax-a`、`claude-deepseek-b`、`codex-gpt5-dispatch-docs-001`。
4. worker prompt 必须声明允许范围、禁止范围、验证命令、提交格式、PR 标题格式、成本预算和回执字段。
5. 使用 `claude-<provider> --output-format stream-json --verbose` 获取 `session_id`、token、cost 和 duration；不要用只返回文本的格式做成本审计。
6. 成本回执以单个 agent PR / handoff 为单位；同一 worker 为同一 PR 多次 resume 或重跑验证时，追加到该 PR ledger 并汇总。
7. 成本回执必须同时写 API 成本账和平台额度账；平台额度不可见时写 `provider_quota_basis=unknown`。
8. worker 完成后必须返回：identity、session_id、branch、commit SHA、changed files、validation、risk、duration、api_cost_usd_estimated、provider_quota_basis。
9. coordinator 审查 `git diff origin/main..HEAD`、验证结果和 evidence 后，才允许 push/开 PR/合并。
10. PR 标题和描述必须包含 `agent=<agent> model=<model> worker=<worker>`；没有身份标签的 PR 视为不合格 handoff。
11. 合并、集成验证和 push 只由 coordinator 收口；临时 worktree 在合并完成后可删除。
12. coordinator 必须给 worker PR / handoff 打分；缺 identity、缺 evidence、缺验证、越权改共享文件或绕过安全门时直接 block。
13. 同一 PR 的后续修复必须优先 `--resume <session_id>`，只有 session 不可恢复、任务重切或换模型时才开新 session，并在 cost ledger 说明原因。

### Dispatch triage

优先派给 Claude Code worker：

1. 批量搜索、批量替换、格式统一、表格整理、证据文件生成。
2. 下载公开依赖、拉镜像、跑安装探测、收集环境错误。
3. 重复测试运行、日志摘录、失败样本分类、PR 描述草稿。
4. 低冲突、单目录、可明确验证的小代码补丁。

优先留给 Codex coordinator：

1. 模块 Owner、phase 状态、Target / Current / Future / History 判定。
2. 需要跨模块一致性的架构或 runtime 改动。
3. 安全、审批、secret、idempotency、recovery、并发和持久化语义。
4. 合并顺序、冲突解决、最终 verification gate、production readiness 判定。

升级路径：

1. worker 一次失败时，返回 blocker 和日志，coordinator 指导下一步。
2. 同一 blocker 连续出现两次时，coordinator 重新切分任务或换模型。
3. 同一 blocker 仍无法解除，coordinator 接手根因定位或停止等待外部状态变化。

### 架构重构

1. 明确 Current / Foundation / Target / Future / History。
2. 总架构文字只同步到 `docs/architecture/architecture.md`；图形关系变化时同步 `architecture-views.md` 并重新生成 HTML。
3. 目标设计放 `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/`。
4. 正式结论放 `docs/architecture/`。
5. 执行计划放 `.agent/programs/` 根层。
6. 旧计划和旧设计归档到 `docs/history/`。

### 挂机模式

1. 主线程本身必须是真正的 Codex UI 目标模式。
2. 主线程负责计划、实现、验证、提交和推送。
3. 主线程可以使用多 agent / subagent 辅助审计或实现，但目标、范围、禁止范围和验收闸门不能漂移。
4. 共享文件多、runtime 风险高、schema/API/DB 变更或用户要求一路执行时，优先使用挂机模式。

### 多线程模式

1. 主线程本身必须是真正的 Codex UI 目标模式，并负责 coordinator 工作。
2. 主线程拆出粗粒度子线程；每个线程要执行一大块互相独立的工作。
3. 主线程先盘点可复用 Codex 线程和 git worktree。
4. 主线程必须在生成、改写或投递线程提示词之前完成线程盘点；不能先写提示词再回头找线程。
5. 有合适可复用线程就复用；没有合适线程才创建新线程。
6. 复用或新建线程后必须改线程标题，让侧边栏能看出本轮任务、phase 和职责。
7. 主线程写清每个线程的目标、允许范围、禁止范围、验收闸门和验证命令。
8. 线程可以常驻，但每轮任务必须重新确认或切换独立 worktree 和独立 `codex/` 分支。
9. 每个子线程也必须是真正的 Codex UI 目标模式；提示词目标模式不等于 Codex UI 目标模式。
10. 工具 API 不能直接打开 UI 目标模式时，主线程只输出线程提示词文件路径，等待用户在 UI 里手动创建目标模式线程，或改为挂机模式。
11. 子线程目标模式提示词默认要求线程内开启多 agent 模式；只有高冲突或用户明确要求单线程时，才在提示词中禁用并说明原因。
12. 每个线程默认可以使用多 agent 模式，但只能在自己的写入范围内协作。
13. 多线程提示词统一放在 `.agent/programs/thread-prompts/`，不要和 `PHASE*.md` 混放。
14. 主线程不能在主对话里直接粘贴完整子线程提示词；主对话只报告线程盘点结果、提示词文件路径和下一步动作。
15. 下一轮提示词或临时多线程执行方案更新时，主线程默认替换或清理旧提示词和旧临时执行方案；只有用户明确要求归档时才归档。正式 completed program 的归档规则仍按 `docs/history/programs/` 执行。
16. 写入线程完成后必须提交并推送；只读审计线程返回报告和干净 `git status` 即可。主线程读取 diff、验证结果或审计证据，不只信总结。
17. 主线程按风险顺序合并，解决冲突后运行集成验证。
18. 每个写入线程 / Claude Code worker 的 commit、PR 和 evidence 都必须带 `agent + model + worker` 身份标签。
19. worker handoff 必须包含时间与成本回执；API 成本估算和平台额度扣减不得混写。
20. 主线程 coordinator 是唯一合并 owner；worker PR 只表示候选贡献，不表示可自动合并。
21. 成本和时间按每个 agent PR / handoff 统计；一轮聊天里的多个 worker 不合并成单账。
22. 多线程任务分配优先把简单重复工作交给 Claude Code worker，把复杂判断和最终收口留给 coordinator。

### Program Closure 自维护审查

每个 program 结束前必须做 workflow / docs self-review。它的目的不是多写总结，而是确认这轮暴露出的新规则、新坑和新边界已经进入正确的长期位置。

检查顺序：

1. `AGENTS.md`：全仓硬规则、工作模式、收尾规则是否需要更新。
2. `.agent/system.yaml`：route、docs_sync、verify 是否覆盖新工作流。
3. `.agent/references/`：新的 skill、lesson、pitfall、debug playbook 是否已沉淀。
4. `.agent/templates/`：是否需要新的目标模式提示词、phase 模板或 closure report 骨架。
5. `.agent/programs/`：是否只保留当前 active program，或处于明确无 active program 的等待状态。
6. `docs/history/programs/`：completed program 是否归档，旧 phase 是否离开当前前台。
7. `docs/architecture/architecture.md`：是否仍只描述 Current。
8. `docs/architecture/architecture.md`：是否需要吸收新的 Target 边界。
9. `docs/architecture/architecture.md`：是否反映最新 program 状态。
10. verifier / tests：能机器检查的规则是否已进入脚本或 repo tests。

如果用户提醒“以后注意”，不能只留在对话里。先分类：临时提醒进入 ignored local notes；可复用经验进入 `.agent/references/known-pitfalls.md` 或对应 skill；稳定操作规则进入 `workflow.md`；任务触发规则进入 `task-routing.md`；全仓硬规则进入 `AGENTS.md`；能机器检查的规则进入 verifier/test。

## Architecture Documentation Governance

涉及架构、Agent Runtime、RAG、GraphRAG、Memory、Tool Layer、Hooks、Trace、Eval、部署、中间件或前后端契约时，必须读取 `.agent/references/architecture-docs-map.md`、`.agent/references/documentation-governance.md`、`.agent/references/architecture-update-policy.md`、`.agent/references/diagram-inventory.md` 和 `.agent/references/current-target-future-rules.md`。

`docs/architecture/` 是 human-facing formal architecture source；`docs/architecture/architecture.html` 是展示聚合页，不是唯一事实来源；`.agent/references/` 是 Agent-facing operating memory。不要只改其中一个表面。

`docs/architecture/architecture.md` 是唯一文字总架构文档；`.agent/` 只维护 Agent 路由和执行工作流。架构 HTML 继续读取 `docs/architecture/architecture-views.md`，不生成第二套架构正文。

## Agent Workflow Self-Maintenance

当用户提出新的长期工作方式要求时，不能只在本轮回答里说“以后注意”。必须按 `.agent/references/workflow-governance.md`、`.agent/references/workflow-update-policy.md` 和 `.agent/references/workflow-maintenance-checklist.md` 判断是否更新 AGENTS.md、`.agent/references/`、`.agent/templates/`、`.agent/programs/`、`docs/architecture/`、`docs/architecture/architecture.html`、verifier 或 tests。

如果新规则影响未来生成内容，必须同步更新 `.agent/templates/`；如果规则需要防漂移，必须同步 verifier 或 repo tests。

## Focused Tests

文档 / Agent workflow 最小基线：

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Windows PowerShell Rules

当前仓库路径包含空格和 `&`，program 命令默认兼容 Windows PowerShell 5.1。执行 program phase 时必须优先读取 `.agent/programs/powershell-runbook.md`。

- 进入仓库使用 `Set-Location -LiteralPath`。
- 不使用 Bash `&&`、`export`、`source`、`rm -rf`、`grep -R`。
- 外部命令后检查 `$LASTEXITCODE`。
- Python 优先使用 `.venv\Scripts\python.exe`，否则使用 `python`。
- pytest 使用 `& $Python -m pytest ... -p no:cacheprovider`。
- 临时目录删除使用 `Remove-Item -LiteralPath ... -Recurse -Force`。

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
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- verifier scripts and repo tests

Program closure 还必须执行一次 Program Closure 自维护审查，确认本轮新增经验没有只停留在 final answer 或聊天上下文里。

## Lessons Learned

- 修改 surface 时，测试和 verifier 是同一变更的一部分，不是事后装饰。
- 历史完成事实不能为了新叙事改写成未完成。
- 最短路径通常是更新现有 skill，而不是新建更多目录。
- 自主维护靠“提醒分类、规则沉淀、验证自动化、历史归档”，不是靠 Codex 记住上一轮对话。
