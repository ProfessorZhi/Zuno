# Agent 架构设计工作集

`.agent/architecture/` 存放目标架构设计，不存放按 phase 执行的计划。正式面向人的架构结论仍以 `docs/architecture/` 为准。

## 目录分工

```text
.agent/architecture/
  README.md
  00-architecture-index.md
  glossary.md
  near-term/     近期理想架构
  future/        未来方向
  decisions/     架构决策摘要
```

## 近期理想架构

`near-term/` 是当前最重要的目标架构工作集，描述短期内希望 Zuno 收敛到的分层形态。

核心文件：

- `00-architecture-index.md`：近期目标架构文字入口，用于 program 转化。
- `01-target-runtime-architecture.md`：Web/Electron -> FastAPI -> Application -> GeneralAgent 的主路径。
- `02-context-memory-architecture.md`：Context Orchestrator、raw events、summary、structured memory。
- `03-capability-tool-retrieval-architecture.md`：ToolCard、Capability Selector、MCP/Skill/Action Tool。
- `04-knowledge-graphrag-retrieval-fusion.md`：BM25、Vector、GraphRAG Local/Global/DRIFT、RRF。
- `05-repository-boundaries-and-acceptance-gates.md`：仓库边界、文档瘦身和验收门。

## 未来方向

`future/` 只记录更远的方向，例如 Java business services、microservices、event-driven workers、Coding Agent mode、multi-agent mode。它不是近期执行计划，也不是当前验收目标。

## 架构决策：为什么这样设计

`decisions/` 记录 Agent 侧的轻量决策摘要，用来回答：

- 为什么近期仍然是 monorepo now, service-ready later。
- 为什么同步聊天路径只进入一个 GeneralAgent。
- 为什么 GraphRAG 是被选择的 Knowledge Capability，而不是第二套聊天 runtime。
- 为什么执行计划不放在 architecture，而放在 `.agent/programs/`。

正式 ADR 仍放在 `docs/architecture/decisions/`。

## 和 programs 的边界

- `.agent/architecture/`：描述目标形态和设计原则。
- `.agent/programs/`：描述怎么按 phase 执行、怎么验收、当前卡在哪。

如果一个文件写的是 Phase 05 / Phase 06 / Phase 07 这种执行顺序，它应该平铺在 `.agent/programs/`；如果写的是系统应该长什么样，它应该在 `.agent/architecture/`。
