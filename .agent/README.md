# Zuno Local Agent Skill System

`.agent/` 是 Zuno 的本地 Agent Skill System，不是正式架构真相本身。正式结论放在 `docs/`；这里沉淀“在 Zuno 里怎么正确做事”的 skills、lessons、playbooks、当前执行计划、目标架构镜像、模块设计镜像和模板。

## 和 AGENTS.md 的关系

```text
AGENTS.md              仓库唯一入口：规则、边界、阅读顺序、任务路由
.agent/system.yaml     机器可读路由：路径 -> skills -> templates -> verify
.agent/references/     本地项目 skills、lessons、playbooks、任务路由和已知坑
.agent/programs/       当前可执行 Agent program；按 phase 的执行计划放这里
.agent/architecture/   总架构四个 canonical 镜像文件
.agent/modules/        逻辑模块的实施级设计镜像
.agent/templates/      skill 执行模板和报告骨架
.agent/scripts/        过渡期验证器；长期自动化目标位置是 tools/agent 与 tools/verify
```

执行时先按 `AGENTS.md` 路由，再进入 `.agent/references/task-routing.md` 和 `.agent/references/workflow.md`，然后按对应参考和验证命令执行。

复杂任务先判断工作模式：挂机模式由主线程作为真正的 Codex UI 目标模式一路执行到底；多线程模式由主线程作为真正的 Codex UI 目标模式 coordinator，给粗粒度子线程准备目标模式提示词、分支边界和验收闸门，再由用户在 UI 里手动创建真正的目标模式子线程。提示词目标模式不等于 Codex UI 目标模式。线程内可按范围开启多 agent 模式；这里的多 agent 是执行协作方式，不改变 Zuno runtime 的 Single GeneralAgent 主线。

## 语言规则

- 新写或重写的 Agent 文档默认使用中文。
- 英文术语可以保留，但要配中文解释。
- 历史档案放在 `docs/history/`，可以保留原文。

## 跟踪结构

```text
.agent/
  README.md
  architecture/
    README.md
    architecture.md
    architecture-views.md
    architecture.html
  modules/
    README.md
    06-agent-core-planning-control.md
  system.yaml
  references/
    task-routing.md
    workflow.md
  programs/
  templates/
  scripts/
```

本地临时目录由 `.gitignore` 忽略：

```text
.agent/local/
.agent/local/notes/
.agent/local/tmp/
.agent/local/logs/
.agent/local/secrets/
```

不要在 local-only 目录里保留 tracked placeholder。

## 各目录作用

- `.agent/architecture/`：只保留 `README.md`、`architecture.md`、`architecture-views.md`、`architecture.html` 四个总架构镜像文件。
- `.agent/modules/`：逻辑模块的实施级设计镜像。当前 Agent Core 位于 `06-agent-core-planning-control.md`。
- `.agent/references/`：本地 skill library。这里放任务路由、统一工作流、文档地图、代码地图、验证地图、常见坑、debug playbook 和 lessons learned。
- `.agent/programs/`：执行计划。按 phase 推进的 active program 放这里，完成后归档到 `docs/history/programs/`。
- `.agent/templates/`：skill 执行骨架，只放格式，不沉淀项目知识。
- `.agent/scripts/`：过渡期验证器。新自动化优先放 `tools/agent/` 或 `tools/verify/`，防回归测试放 `tests/agent_system/`。

正式文档位置：

```text
docs/architecture/   总架构四个 canonical 文件
docs/modules/        十一个逻辑模块设计
docs/status/         Current 与差距
docs/decisions/      ADR
docs/governance/     工程治理
docs/history/        历史归档
```

## 操作规则

- 先从 `docs/architecture/` 读取总架构，再从 `docs/modules/` 读取对应模块设计。
- `.agent/system.yaml` 只写路由规则，不写长知识。
- `.agent/references/` 承载可复用项目 skill，不写一次性调查流水账。
- `.agent/programs/` 承载按 phase 的执行计划，不放进 `.agent/architecture/` 或 `.agent/modules/`。
- 模块设计不得放入 `.agent/architecture/`。
- 每个新执行计划都从 `PHASE01` 开始；旧 active phase 文件从 `.agent/programs/` 当前前台移除。
- 大任务默认多用目标模式；共享文件多或风险集中时使用挂机模式，由主线程执行到底。
- 可并行时使用多线程模式：主线程拆成粗粒度线程，每个线程都必须带目标、范围、禁止范围、验收闸门和验证命令。
- 多线程模式下，主线程先盘点可复用 Codex 线程和 git worktree；有合适可复用线程就复用，没有合适线程才创建新线程。
- 主线程必须先完成线程盘点，再生成或投递线程提示词；完整子线程提示词写入 `.agent/programs/thread-prompts/`，不要直接贴在主对话里。
- 复用或新建线程后必须改线程标题；每个子线程提示词默认要求线程内开启多 agent 模式。
- 多线程模式要求用户在 UI 里手动创建真正的目标模式子线程；提示词目标模式不等于 Codex UI 目标模式。
- 多线程默认允许线程内多 agent 协作，但主线程负责审查 diff、合并冲突、跑集成验证和最终提交。
- 修改任务必须验证、commit、push，除非被阻塞。
- 只读侦察不 commit、不 push。

## 知识提升规则

```text
临时发现 -> .agent/local/notes/    ignored
单次调查证据 -> 外部结果目录或 docs/history/
可复用经验 -> .agent/references/<domain-skill>.md 或 known-pitfalls.md
稳定操作流程 -> .agent/references/workflow.md
任务触发路由 -> .agent/references/task-routing.md
所有任务通用规则 -> AGENTS.md
已实现、已验证、面向人的事实 -> docs/
```
