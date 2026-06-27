# Zuno Local Agent Skill System

`.agent/` 是 Zuno 的本地 Agent Skill System，不是正式架构真相本身。正式结论放在 `docs/`；这里沉淀“在 Zuno 里怎么正确做事”的 skills、lessons、playbooks、当前执行计划、目标架构草图和模板。

## 和 AGENTS.md 的关系

```text
AGENTS.md              仓库唯一入口：规则、边界、阅读顺序、任务路由
.agent/system.yaml     机器可读路由：路径 -> skills -> templates -> verify
.agent/references/    本地项目 skills、lessons、playbooks、任务路由和已知坑
.agent/programs/      当前可执行 Agent program；按 phase 的执行计划放这里
.agent/architecture/  目标架构设计工作集；不放 phase 执行计划
.agent/templates/     skill 执行模板和报告骨架
.agent/scripts/       过渡期保留的验证器；长期自动化目标位置是 tools/agent 与 tools/verify
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

- `.agent/references/`：本地 skill library。这里放类似 skill 的任务路由、统一工作流、文档地图、代码地图、验证地图、常见坑、debug playbook 和 lessons learned。
- `.agent/programs/`：执行计划。按 phase 推进的 active program 放这里，完成后归档到 `docs/history/programs/`。
- `.agent/architecture/near-term/`：近期目标架构设计，包含 `zuno-ideal-architecture-and-repo-layout.html` 和五份 canonical Markdown。
- `.agent/architecture/future/`：未来方向，只记录 Java、microservices、event/workers、multi-agent 等 horizon，不作为近期验收目标。
- `.agent/architecture/decisions/`：Agent 侧轻量决策摘要，说明为什么这样分层、为什么暂不做某些方向；正式 ADR 仍在 `docs/architecture/decisions/`。
- `.agent/templates/`：skill 执行骨架，只放格式，不沉淀项目知识。
- `.agent/scripts/`：过渡期验证器。新自动化优先放 `tools/agent/` 或 `tools/verify/`，防回归测试放 `tests/agent_system/`。

## 操作规则

- 先从 `docs/architecture/` 读取正式真相。
- `.agent/system.yaml` 只写路由规则，不写长知识。
- `.agent/references/` 承载可复用项目 skill，不写一次性调查流水账。
- `.agent/programs/` 承载按 phase 的执行计划，不放进 `.agent/architecture/`。
- 每个新执行计划都从 `PHASE01` 开始；旧 active phase 文件从 `.agent/programs/` 当前前台移除。
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
