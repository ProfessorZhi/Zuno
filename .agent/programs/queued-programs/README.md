# Queued Programs

这里保存当前 suite 的后续 program 计划。它们是排队计划，不是当前 active program。

当前 active program 仍以 `.agent/programs/current.md` 为准。只有当 Program 1 完成并由主线程正式切换状态后，Program 2 才能成为 active program。

## 队列

1. `PROGRAM02_runtime-subsystems-parallel.md`
   - Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index 四线程并行。
2. `PROGRAM03_agent-planning-integration.md`
   - 合并 Program 2 成果，实现真实 planning / ReAct / reflection / replan 闭环。
3. `PROGRAM04_enterprise-knowledge-eval-benchmark.md`
   - 企业知识库问答自动化评测，对比 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。

## 使用规则

- queued program 不能写 `state: active`。
- queued program 不能包含 completed evidence。
- queued program 可以写目标、phase、依赖、分支建议、验证命令和验收标准。
- Program 2 的具体线程提示词由 Program 1 PHASE07 生成到 `.agent/programs/thread-prompts/`。
