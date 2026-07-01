# Queued Programs

这里保存当前 suite 的后续 program 计划。它们是排队计划，不是当前 active program。

当前 active program 仍以 `.agent/programs/current.md` 为准。当前状态是 no-active；Program 3-5 仍是 queued program。

## 队列

1. `PROGRAM03_runtime-subsystems-parallel.md`
   - Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index 四线程并行。
2. `PROGRAM04_agent-planning-integration.md`
   - 合并 Program 3 成果，实现真实 planning / ReAct / reflection / replan 闭环。
3. `PROGRAM05_enterprise-knowledge-eval-benchmark.md`
   - 企业知识库问答自动化评测，对比 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。

## 使用规则

- queued program 不能写 `state: active`。
- queued program 不能包含 completed evidence。
- queued program 可以写目标、phase、依赖、分支建议、验证命令和验收标准。
- Runtime Subsystems 的历史线程提示词已由 Program 1 PHASE07 生成，并随 Program 1 归档到 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/thread-prompts/`；启动 Program 3 时需要结合 Program 2 durable ingestion closure 重新复制或刷新到 `.agent/programs/thread-prompts/`，并重新确认 UI 目标模式。
