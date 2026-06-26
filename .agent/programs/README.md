# Agent Programs

`.agent/programs/` 存放当前可执行的 Agent program，也就是“接下来按哪些 Phase 落地”的工作计划。

它不是正式人类文档真相。正式状态写入 `docs/architecture/roadmap.md`；已经完成或被替换的 program 归档到 `docs/history/programs/`。

## 当前入口

- [current.md](current.md)：当前 active program 指针。
- [zuno-target-runtime-v2/README.md](zuno-target-runtime-v2/README.md)：当前执行计划。
- [zuno-target-runtime-v2/implementation-roadmap.md](zuno-target-runtime-v2/implementation-roadmap.md)：Phase 05-09 路线。
- [zuno-target-runtime-v2/current-phase.md](zuno-target-runtime-v2/current-phase.md)：当前打开的 phase。
- [zuno-target-runtime-v2/closure-checklist.md](zuno-target-runtime-v2/closure-checklist.md)：收尾验收清单。

## 什么时候写 programs

写入 `.agent/programs/` 的内容必须满足至少一个条件：

- 它决定当前要执行哪个 phase。
- 它规定 phase 的验收门。
- 它记录当前 program 的边界、禁止项或收尾规则。
- 它会影响后续 Codex/Agent 如何继续执行。

如果只是描述理想架构，应写到 `.agent/architecture/`。如果是已经完成的旧计划，应移动到 `docs/history/programs/`。

## 当前 program

active program 是：

- `zuno-target-runtime-v2/`

已完成的 Zuno Target Architecture Migration V1 已归档到：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
