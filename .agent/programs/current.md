# 当前执行状态

当前 active program 就是 `.agent/programs/` 根目录这一层。不要再进入子目录找当前计划。

## 状态

- Phase 00-04 已完成，详细文件和证据已归档到 `docs/history/programs/zuno-target-runtime-v2/`。
- 当前待打开 phase：Phase 05 记忆引擎。
- 当前执行顺序以 [implementation-roadmap.md](implementation-roadmap.md) 和各 phase 文件为准。

## 当前计划文件

- [implementation-roadmap.md](implementation-roadmap.md)
- [phase-05-memory-engine.md](phase-05-memory-engine.md)
- [phase-06-capability-tool-retrieval.md](phase-06-capability-tool-retrieval.md)
- [phase-07-graphrag-llm-entity-extraction.md](phase-07-graphrag-llm-entity-extraction.md)
- [phase-08-langgraph-runtime.md](phase-08-langgraph-runtime.md)
- [phase-09-product-trace-eval-closure.md](phase-09-product-trace-eval-closure.md)
- [closure-checklist.md](closure-checklist.md)

## 停止线

不要在 Phase 05 没有聚焦测试、文档边界同步和收口证据前打开 Phase 06。不要在能力选择没有稳定 ToolCard trace 前打开 Phase 07。不要在 GraphRAG LLM 实体抽取、retrieval/fusion trace 稳定前打开 Phase 08。

正式面向人的状态汇总在 `docs/architecture/roadmap.md`。最新完成 program 归档在 `docs/history/programs/zuno-target-architecture-migration-v1/`。
