# Superseded Program Inputs

这里保存当前 suite 被 Program 3 Mega 合并的旧 queued program 计划。它们是历史输入，不是当前 active program，也不再作为 queued pipeline 执行。

当前 active program 以 `.agent/programs/current.md` 为准：

- `state: active`
- `active_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
- `current_phase: PHASE07_security-governance-envelope.md`

## 被合并的计划

1. `PROGRAM04_runtime-subsystems-parallel.md`
   - 原目标：Memory / Context、Capability / Skill / Tool / MCP、Security / Governance、GraphRAG / Index 四线程并行。
   - 新状态：merged_into `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`。
2. `PROGRAM05_agent-planning-integration.md`
   - 原目标：合并 runtime subsystem 成果，实现 planning / ReAct / reflection / replan 闭环。
   - 新状态：merged_into `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`。
3. `PROGRAM06_enterprise-knowledge-eval-benchmark.md`
   - 原目标：企业知识库问答自动化评测，对比 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。
   - 新状态：merged_into `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`。

## 使用规则

- superseded program 不能写 `state: active`。
- superseded program 不能写 completed evidence。
- superseded program 只能作为 Program 3 Mega PHASE01-PHASE15 的输入材料。
- 后续如果重新拆分 program，必须先更新 `.agent/programs/current.md`、roadmap、verifier 和 repo tests。
