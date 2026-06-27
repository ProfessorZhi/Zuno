# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。这里回答“下一步按哪些 phase 做、每个 phase 怎么验收”，不存放理想目标架构。

本目录保持一层平铺。不要在当前前台再新建 `.agent/programs/<program>/` 或 `implementation-phases/` 子目录。执行计划被替换时，旧计划从当前前台移除；需要保留证据的旧材料移动到 `docs/history/programs/`。

## 当前入口

- [current.md](current.md)：当前状态和当前打开的 phase。
- [implementation-roadmap.md](implementation-roadmap.md)：当前执行计划总目录。
- [phase-05-memory-engine.md](phase-05-memory-engine.md)：Phase 05 记忆引擎。
- [phase-06-capability-tool-retrieval.md](phase-06-capability-tool-retrieval.md)：Phase 06 能力与工具检索。
- [phase-07-graphrag-llm-entity-extraction.md](phase-07-graphrag-llm-entity-extraction.md)：Phase 07 GraphRAG、LLM 实体抽取与检索融合。
- [phase-08-langgraph-runtime.md](phase-08-langgraph-runtime.md)：Phase 08 GeneralAgent LangGraph 运行时。
- [phase-09-product-trace-eval-closure.md](phase-09-product-trace-eval-closure.md)：Phase 09 产品边界、Trace 与 Eval 收口。
- [closure-checklist.md](closure-checklist.md)：每个 phase 的收尾验收清单。

## 与 architecture 的边界

- `.agent/architecture/`：理想目标架构，描述系统应该长什么样。
- `.agent/programs/`：当前执行方案，描述按什么 phase 做、哪些文件可改、如何验收。
- `docs/history/programs/`：已完成、被替换或不再当前执行的旧计划和证据。

如果文件写的是 `Phase 05 / Phase 06 / Phase 07` 这种执行顺序，它属于 `.agent/programs/`。如果文件写的是目标分层、长期边界、理想数据流，它属于 `.agent/architecture/`。
