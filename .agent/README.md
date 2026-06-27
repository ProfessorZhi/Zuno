# Agent 工作流库

`.agent/` 是 Zuno 的 Agent 工作流库，不是正式架构真相本身。正式结论放在 `docs/`，这里放执行时需要的参考、程序、目标架构草图、模板和验证脚本。

## 和 AGENTS.md 的关系

```text
AGENTS.md              仓库唯一入口：规则、边界、阅读顺序、任务路由
.agent/references/    当前程序、文档地图、代码地图、任务路由、工作流、验证地图、命令和已知坑
.agent/programs/      当前可执行 Agent program；按 phase 的执行计划放这里
.agent/architecture/  目标架构设计工作集；不放 phase 执行计划
.agent/scripts/       验证器和本地操作辅助
.agent/templates/     可复用提示与报告模板
```

执行时先按 `AGENTS.md` 路由，再进入 `.agent/references/task-routing.md` 和 `.agent/references/workflow.md`，然后按对应参考和验证命令执行。

## 语言规则

- 新写或重写的 Agent 文档默认使用中文。
- 英文术语可以保留，但要配中文解释。
- 历史档案放在 `docs/history/`，可以保留原文。

## 跟踪结构

```text
.agent/
  README.md
  architecture/
    near-term/
    future/
    decisions/
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

- `.agent/references/`：轻量导航。这里放类似 skill 的任务路由、统一工作流、文档地图、代码地图和验证地图。
- `.agent/programs/`：执行计划。按 phase 推进的 active program 放这里，完成后归档到 `docs/history/programs/`。
- `.agent/architecture/near-term/`：近期目标架构设计，包含 `zuno-ideal-architecture-and-repo-layout.html` 和五份 canonical Markdown。
- `.agent/architecture/future/`：未来方向，只记录 Java、microservices、event/workers、multi-agent 等 horizon，不作为近期验收目标。
- `.agent/architecture/decisions/`：Agent 侧轻量决策摘要，说明为什么这样分层、为什么暂不做某些方向；正式 ADR 仍在 `docs/architecture/decisions/`。
- `.agent/scripts/`：验证器和本地操作辅助。
- `.agent/templates/`：可复用提示和 closure report。

## 操作规则

- 先从 `docs/architecture/` 读取正式真相。
- `.agent/references/` 只做精简导航，不承载长篇目标设计。
- `.agent/programs/` 承载按 phase 的执行计划，不放进 `.agent/architecture/`。
- 修改任务必须验证、commit、push，除非被阻塞。
- 只读侦察不 commit、不 push。

## 知识提升规则

```text
临时发现 -> .agent/local/notes/    ignored
单次调查证据 -> 外部结果目录或 docs/history/
可复用经验 -> .agent/references/known-pitfalls.md
稳定操作流程 -> .agent/references/workflow.md
任务触发路由 -> .agent/references/task-routing.md
所有任务通用规则 -> AGENTS.md
已实现、已验证、面向人的事实 -> docs/
```
