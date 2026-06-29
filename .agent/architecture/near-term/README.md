# 近期目标架构

## 目的

这个目录是 Zuno 下一轮 refactor 的 canonical Target / Proposed 设计，不是 Current Truth。

旧的 01-19 fragment 已归档到：

- `docs/history/near-term-architecture-fragments/`

## 标准文件

```text
.agent/architecture/near-term/
  README.md
  00-architecture-index.md
  01-target-runtime-architecture.md
  02-context-memory-architecture.md
  03-capability-tool-retrieval-architecture.md
  04-knowledge-graphrag-retrieval-fusion.md
  05-repository-boundaries-and-acceptance-gates.md
```

## 阅读顺序

1. [Target Architecture Index](00-architecture-index.md)
2. [Target Runtime Architecture](01-target-runtime-architecture.md)
3. [Context Memory Architecture](02-context-memory-architecture.md)
4. [Capability Tool Retrieval Architecture](03-capability-tool-retrieval-architecture.md)
5. [Knowledge GraphRAG Retrieval Fusion](04-knowledge-graphrag-retrieval-fusion.md)
6. [Repository Boundaries And Acceptance Gates](05-repository-boundaries-and-acceptance-gates.md)

## 边界

near-term 指当前 Python/FastAPI、LangGraph、monorepo 内部可以逐步落地的目标架构。它不等于 Java 实现、microservice 拆分、event bus 全面 rollout，也不等于默认 multi-agent 行为。

本目录保持文字为主，便于转化为 `.agent/programs/` 下的执行计划。唯一架构 HTML 展示页是 `docs/architecture.html`；它不能当作 Current evidence。

## 执行计划放哪里

按 phase 的执行计划放在 active program roadmap：

- `.agent/programs/implementation-roadmap.md`

不要把 per-phase 文件加回 `.agent/architecture/near-term/`。执行 phase 文件平铺在 `.agent/programs/`，architecture 保持为本 README、一个文字索引和五份 Markdown 设计文件。
