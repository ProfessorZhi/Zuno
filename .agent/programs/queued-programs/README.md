# Queued Programs

这里保存当前 suite 的后续 program 计划。它们是排队计划，不是当前 active program。

当前 active program 仍以 `.agent/programs/current.md` 为准。当前处于 no-active 等待态；只有用户明确启动下一轮并由主线程正式切换状态后，Program 2 才能成为 active program。

## 队列

1. `PROGRAM02_enterprise-document-ingestion-platform-v2.md`
   - Program 1B / V2；把 Program 1A 的 local runtime slice 推进到企业级文档输入与持久化平台雏形。
2. `PROGRAM03_runtime-subsystems-parallel.md`
   - Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index 四线程并行。
3. `PROGRAM04_agent-planning-integration.md`
   - 合并 Program 3 成果，实现真实 planning / ReAct / reflection / replan 闭环。
4. `PROGRAM05_enterprise-knowledge-eval-benchmark.md`
   - 企业知识库问答自动化评测，对比 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。

## 使用规则

- queued program 不能写 `state: active`。
- queued program 不能包含 completed evidence。
- queued program 可以写目标、phase、依赖、分支建议、验证命令和验收标准。
- Runtime Subsystems 的具体线程提示词已由 Program 1 PHASE07 生成，并随 Program 1 归档到 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/thread-prompts/`；启动 Program 3 时需要复制或刷新到 `.agent/programs/thread-prompts/` 并重新确认 UI 目标模式。
