# 目标架构设计工作集索引

## 用途

本文件替代旧的 near-term HTML 蓝图，作为 `.agent/architecture/near-term/` 的文字入口。它面向 Agent 执行，不面向展示；正式展示页只有 `docs/architecture/architecture.html`。

## 目标形态

```text
Local-first Agent Workspace
  -> Single Controller Agent
  -> Summary Compression
  -> Structured Extraction
  -> Context / Memory
  -> Capability / Tool / MCP / ToolCard
  -> Knowledge / RAG / GraphRAG / Native BM25 / RRF
  -> Evidence / Citation / Trace / Eval
  -> Platform / Storage / Security / Observability
```

## 读取顺序

1. `00-architecture-index.md`：目标架构文字入口。
2. `01-target-runtime-architecture.md`：Web/Electron -> FastAPI -> Application -> GeneralAgent 主路径。
3. `02-context-memory-architecture.md`：Context Builder、working memory、long-term memory、graph memory。
4. `03-capability-tool-retrieval-architecture.md`：ToolCard、Capability Selector、MCP、permission、budget。
5. `04-knowledge-graphrag-retrieval-fusion.md`：basic / local / global / drift、BM25、Vector、GraphRAG、RRF。
6. `05-repository-boundaries-and-acceptance-gates.md`：仓库边界、文档瘦身和验收门。

## 与展示页的关系

- `docs/architecture/architecture.html`：唯一架构 HTML 展示页，适合人快速浏览。
- `docs/architecture/architecture.md`：十类架构视图的 Mermaid 源。
- `.agent/architecture/near-term/*.md`：面向 Agent 的目标设计文本，用于拆 program 和验收。

## Program 转化规则

当目标架构要进入实现时，不直接修改本目录为 phase 文件。执行计划应进入：

- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/current.md`
- 必要时新增平铺 `PHASE*.md`

每个 program 必须说明：

- 要实现哪个目标边界。
- 不改哪些 Current 行为。
- 哪些能力仍是 Target / Future。
- 验证命令和验收证据。

## 非目标

- 不把 Zuno 近期默认改成多 Agent runtime。
- 不把微服务、event-driven worker、Coding Agent mode 写成 Current。
- 不把 `docs/architecture/architecture.html` 的展示图当作 Current 证据。
- 不在 `.agent/architecture/` 保存新的 HTML 展示页。
