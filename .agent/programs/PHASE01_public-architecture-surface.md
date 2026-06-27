# PHASE01：公开封面与架构叙事收口

## 目标

让第一次打开 GitHub 的人 5 分钟读懂 Zuno 当前是什么、目标是什么、下一步是什么。

## 范围

- `README.md`
- `docs/architecture/README.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`
- `docs/architecture/diagrams.md`

## 必须表达

- Zuno 是 local-first Agent Workspace。
- 当前主线是 Single GeneralAgent Runtime、Memory、Capability、Knowledge / RAG / GraphRAG、Evidence / Trace / Eval。
- Target 和 Current 不混写。
- Domain Pack 只作为历史或兼容语境出现，不再作为公开主线。
- 架构图保持少节点、浅色、淡紫边框、Mermaid 可渲染。

## 不做

- 不移动 runtime 代码。
- 不改 API、DTO、DB schema、依赖、Docker 或 eval baseline。
- 不把未实现的 LangGraph runtime、生产级 Memory DB 持久化、完整前端 trace 面板写成 Current。

## 验收

- README 能说明 Zuno 是什么、怎么运行、怎么验证、怎么读 docs。
- `docs/architecture/diagrams.md` 至少包含 Current Runtime、Target Runtime、Maintenance Workflow 三张 Mermaid 图。
- `docs/architecture/roadmap.md` 指向当前 `zuno-architecture-surface-cleanup-v1` program。
- 运行 `git diff --check`、docs verifier 和 repo docs tests 通过。
