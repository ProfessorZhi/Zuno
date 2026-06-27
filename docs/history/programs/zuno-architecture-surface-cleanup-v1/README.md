# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。这里回答“下一步按哪些 phase 做、每个 phase 怎么验收”，不存放理想目标架构。

本目录保持一层平铺。不要在当前前台再新建 `.agent/programs/<program>/` 或 `implementation-phases/` 子目录。每次打开新的执行计划，都从 `PHASE01` 开始编号；执行计划被替换时，旧 phase 文件从当前前台移除，需要保留证据的旧材料移动到 `docs/history/programs/`。

当前 program：

```text
zuno-architecture-surface-cleanup-v1
```

## 当前入口

- [current.md](current.md)：当前状态和当前打开的 phase。
- [implementation-roadmap.md](implementation-roadmap.md)：当前执行计划总目录。
- [PHASE01_public-architecture-surface.md](PHASE01_public-architecture-surface.md)：公开封面与架构叙事收口。
- [PHASE02_local-agent-skill-system.md](PHASE02_local-agent-skill-system.md)：本地 Agent Skill System 收口。
- [PHASE03_tools-tests-guardrails.md](PHASE03_tools-tests-guardrails.md)：tools / tests 工作流防回归。
- [PHASE04_backend-facade-layers.md](PHASE04_backend-facade-layers.md)：后端六层 facade 分层。
- [PHASE05_large-file-light-split.md](PHASE05_large-file-light-split.md)：大文件轻拆。
- [PHASE06_architecture-diagrams-html.md](PHASE06_architecture-diagrams-html.md)：架构图与 HTML 展示页。
- [closure-checklist.md](closure-checklist.md)：每个 phase 的收尾验收清单。

## 与 architecture 的边界

- `.agent/architecture/`：理想目标架构，描述系统应该长什么样。
- `.agent/programs/`：当前执行方案，描述按什么 phase 做、哪些文件可改、如何验收。
- `docs/history/programs/`：已完成、被替换或不再当前执行的旧计划和证据。

如果文件写的是 `PHASE01 / PHASE02 / PHASE03` 这种执行顺序，它属于 `.agent/programs/`。如果文件写的是目标分层、长期边界、理想数据流，它属于 `.agent/architecture/`。
