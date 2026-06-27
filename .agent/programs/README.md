# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。这里回答“下一步按哪些 phase 做、每个 phase 怎么验收”，不存放理想目标架构，也不同时放多套 active program。

本目录保持一层平铺。每次打开新的执行计划，都从 `PHASE01` 开始编号；执行计划被替换时，旧 phase 文件从当前前台移除，需要保留证据的旧材料移动到 `docs/history/programs/`。

当前 program：

```text
zuno-workflow-doc-system-v1
```

## 当前入口

- [current.md](current.md)：当前状态和当前打开的 phase。
- [implementation-roadmap.md](implementation-roadmap.md)：当前执行计划总目录。
- [PHASE01_workflow-doc-audit.md](PHASE01_workflow-doc-audit.md)：工作流与文档系统只读审计。
- [PHASE02_agent-bootloader-routing.md](PHASE02_agent-bootloader-routing.md)：`AGENTS.md` 与 `.agent/system.yaml` 路由收口。
- [PHASE03_skill-template-program-system.md](PHASE03_skill-template-program-system.md)：skills、templates、programs 的自洽边界。
- [PHASE04_workflow-verifiers-drift-tests.md](PHASE04_workflow-verifiers-drift-tests.md)：工作流 verifier 和漂移测试。
- [PHASE05_closure-history-archive.md](PHASE05_closure-history-archive.md)：program closure 与历史归档。
- [closure-checklist.md](closure-checklist.md)：每个 phase 的收尾验收清单。

## 已排队但不 active 的 program

后续 program 草案放在 `.agent/architecture/future/programs/`。这些文件是排队计划，不是当前执行面，不允许直接把其中 phase 当成 active phase 执行。

## 与 architecture 的边界

- `.agent/architecture/`：理想目标架构，描述系统应该长什么样。
- `.agent/programs/`：当前执行方案，描述按什么 phase 做、哪些文件可改、如何验收。
- `docs/history/programs/`：已完成、被替换或不再当前执行的旧计划和证据。

如果文件写的是 `PHASE01 / PHASE02 / PHASE03` 这种执行顺序，它属于 `.agent/programs/`。如果文件写的是目标分层、长期边界、理想数据流，它属于 `.agent/architecture/`。
