# 近期目标架构

## 目的

这个目录是 Zuno 下一轮 refactor 的 canonical Target / Proposed 设计，不是 Current Truth。

旧的 01-19 fragment 已归档到：

- `docs/history/near-term-architecture-fragments/`

## 标准文件

```text
.agent/architecture/near-term/
  README.md
  zuno-ideal-architecture-and-repo-layout.html
  01-target-runtime-architecture.md
  02-context-memory-architecture.md
  03-capability-tool-retrieval-architecture.md
  04-knowledge-graphrag-retrieval-fusion.md
  05-repository-boundaries-and-acceptance-gates.md
```

## 阅读顺序

1. [Target / Proposed Visual Blueprint](zuno-ideal-architecture-and-repo-layout.html)
2. [Target Runtime Architecture](01-target-runtime-architecture.md)
3. [Context Memory Architecture](02-context-memory-architecture.md)
4. [Capability Tool Retrieval Architecture](03-capability-tool-retrieval-architecture.md)
5. [Knowledge GraphRAG Retrieval Fusion](04-knowledge-graphrag-retrieval-fusion.md)
6. [Repository Boundaries And Acceptance Gates](05-repository-boundaries-and-acceptance-gates.md)

## 边界

near-term 指当前 Python/FastAPI、LangGraph、monorepo 内部可以逐步落地的目标架构。它不等于 Java 实现、microservice 拆分、event bus 全面 rollout，也不等于默认 multi-agent 行为。

HTML 蓝图是唯一 canonical Target / Proposed visual blueprint。它不能复制到 `docs/`，也不能当作 Current evidence。

## 执行计划放哪里

按 phase 的执行计划放在 active program roadmap：

- `.agent/programs/implementation-roadmap.md`

不要把 per-phase 文件加回 `.agent/architecture/near-term/`。执行 phase 文件平铺在 `.agent/programs/`，architecture 保持为本 README、一个 HTML 蓝图和五份 Markdown 设计文件。
